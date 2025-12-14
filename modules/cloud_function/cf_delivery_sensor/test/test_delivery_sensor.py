import sys
import types
import pytest
import random
import logging
import importlib
from datetime import datetime
from types import SimpleNamespace
from modules.cloud_function.cf_delivery_sensor.src.utils import delivery_sensor


class FakePublisher:
    def __init__(self, project_id=None, topic_id=None):
        self.project_id = project_id
        self.topic_id = topic_id
        self.published_messages = []

    def publish_bulk_async(self, messages):
        # Store messages for assertions
        self.published_messages.extend(messages or [])

    def get_metrics(self):
        return {
            "project_id": self.project_id,
            "topic_id": self.topic_id,
            "messages_published": len(self.published_messages),
        }

# Patch delivery_sensor.HighThroughputPublisher before importing DeliverySystem
@pytest.fixture(autouse=True)
def patch_publisher(monkeypatch):
    # Ensure the symbol is available for both relative and absolute imports
    # Patch delivery_sensor.HighThroughputPublisher after module import
    yield
    # cleanup handled by monkeypatch automatically


def load_module_with_publisher(monkeypatch):
    # Import the module and patch HighThroughputPublisher
    monkeypatch.setattr(delivery_sensor, "HighThroughputPublisher", FakePublisher)
    return delivery_sensor


def sample_data():
    # Two clients, one in NYC, one in LA
    clients = [
        ["C1", "NYC", "Alice", "123 Broadway, NY", 40.7128, -74.0060],
        ["C2", "LA", "Bob", "456 Sunset Blvd, LA", 34.0522, -118.2437],
    ]
    # Vehicles: one in NYC near Alice, one in SF (non-local to LA client)
    vehicles = [
        [1, "NYC", 60.0, 10, 40.730610, -73.935242],  # ~Manhattan
        [2, "SF", 80.0, 8, 37.7749, -122.4194],       # San Francisco
    ]
    return clients, vehicles


def near_distance(lat1, lon1, lat2, lon2):
    # Rough comparator helper for floating computations
    return abs(lat1 - lat2) < 1e-9 and abs(lon1 - lon2) < 1e-9


def test_calculate_distance_basic(monkeypatch):
    delivery_sensor = load_module_with_publisher(monkeypatch)
    clients, vehicles = sample_data()
    ds = delivery_sensor.DeliverySystem("proj", "topic", clients, vehicles)

    # Known approximate distance between NYC and LA ~ 3936 km (great-circle)
    d = ds.calculate_distance(40.7128, -74.0060, 34.0522, -118.2437)
    assert 3500 < d < 4500

    # Zero distance
    assert ds.calculate_distance(10.0, 20.0, 10.0, 20.0) == pytest.approx(0.0, abs=1e-9)


def test_create_delivery_prefers_local_vehicle(monkeypatch):
    delivery_sensor = load_module_with_publisher(monkeypatch)
    clients, vehicles = sample_data()
    ds = delivery_sensor.DeliverySystem("proj", "topic", clients, vehicles)

    random.seed(42)
    delivery = ds.create_delivery("C1")  # Client in NYC
    assert delivery.client.id == "C1"
    assert delivery.status == "in_route"
    # Vehicle chosen should be from NYC since available
    assert delivery.vehicle.location == "NYC"
    assert delivery.remaining_distance >= 0
    assert delivery.estimated_time >= 0
    # Delivery id format
    assert isinstance(delivery.id, str) and delivery.id.startswith("DEL##")


def test_create_delivery_uses_non_local_when_none_available_and_logs_warning(monkeypatch, caplog):
    delivery_sensor = load_module_with_publisher(monkeypatch)
    # Clients in LA, vehicles only in NYC and SF (no LA vehicles)
    clients, vehicles = sample_data()
    ds = delivery_sensor.DeliverySystem("proj", "topic", clients, vehicles)

    caplog.set_level(logging.WARNING)
    random.seed(1)
    delivery = ds.create_delivery("C2")  # Client in LA, no LA vehicles
    assert delivery.vehicle.location in {"NYC", "SF"}
    assert any("No local vehicles found for LA" in rec.message for rec in caplog.records)


def test_simulate_movement_completes_and_publishes(monkeypatch):
    delivery_sensor = load_module_with_publisher(monkeypatch)
    clients, vehicles = sample_data()
    ds = delivery_sensor.DeliverySystem("proj", "topic", clients, vehicles)

    # Make remaining distance small so one tick completes
    random.seed(0)
    delivery = ds.create_delivery("C1")
    delivery.remaining_distance = 0.05  # 50 meters
    delivery.estimated_time = 1

    # Simulate movement; should mark as completed and publish one message
    ds._simulate_movement()

    # Delivery moved to history and removed from active
    assert len(ds.deliveries) == 0
    assert len(ds.history) == 1
    completed = ds.history[0]
    assert completed.status in ds.STATUS

    # Publisher got one message
    assert isinstance(ds.publisher, FakePublisher)
    assert len(ds.publisher.published_messages) == 1
    m = ds.publisher.published_messages[0]
    assert "data" in m and "delivery_id" in m
    payload = m["data"]
    assert payload["delivery_id"] == completed.id
    assert payload["vehicle_id"] == completed.vehicle.id
    assert payload["status"] in ds.STATUS
    assert isinstance(payload["created_at"], str)


def test_display_status_publishes_for_active_deliveries(monkeypatch, caplog):
    delivery_sensor = load_module_with_publisher(monkeypatch)
    clients, vehicles = sample_data()
    ds = delivery_sensor.DeliverySystem("proj", "topic", clients, vehicles)

    random.seed(2)
    d1 = ds.create_delivery("C1")
    d2 = ds.create_delivery("C2")

    caplog.set_level(logging.INFO)
    ds._display_status()

    # Should publish two status messages
    assert len(ds.publisher.published_messages) == 2
    ids = {m["delivery_id"] for m in ds.publisher.published_messages}
    assert d1.id in ids and d2.id in ids

    # Log includes count of deliveries
    assert any("Processing" in rec.message for rec in caplog.records)


def test_monitor_deliveries_returns_metrics(monkeypatch):
    delivery_sensor = load_module_with_publisher(monkeypatch)
    clients, vehicles = sample_data()
    ds = delivery_sensor.DeliverySystem("proj", "topic", clients, vehicles)

    # Create one delivery with tiny distance so it's completed in first cycle
    random.seed(3)
    d = ds.create_delivery("C1")
    d.remaining_distance = 0.01

    metrics = ds.monitor_deliveries(interval=0)
    assert isinstance(metrics, dict)
    assert metrics["project_id"] == "proj"
    assert metrics["topic_id"] == "topic"
    # Expect at least one message (completion), plus possibly status before completion
    assert metrics["messages_published"] >= 1