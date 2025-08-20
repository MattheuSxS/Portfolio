#TODO: I must finish the delivery simulation tomorrow
import uuid
import json
import time
import math
import random
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta
import os


@dataclass
class Client:
    id: str
    location: str
    name: str
    address: str
    latitude: float
    longitude: float


@dataclass
class Vehicle:
    id: int
    location: str
    average_speed: float  # km/h
    capacity: int
    latitude: float
    longitude: float


@dataclass
class Delivery:
    id: int
    client: Client
    status: str  # "pending", "in_route", "delivered"
    vehicle: Vehicle
    timestamp: str
    remaining_distance: float  # km
    estimated_time: float  # minutes


class DeliverySystem:
    def __init__(self, client_list: List[List] = None, vehicle_list: List[List] = None):
        self.clients = self._generate_clients(client_list)
        self.vehicles = self._generate_fleet(vehicle_list)
        self.deliveries = []
        self.history = []


    def _generate_clients(self, client_list: List[List] = None) -> List[Client]:

        return [
            Client(*client_data) for client_data in client_list
        ]


    def _generate_fleet(self, vehicle_list: List[List] = None) -> List[Vehicle]:

        return [
            Vehicle(*vehicle_data) for vehicle_data in vehicle_list
        ]


    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates distance in km using Haversine formula"""
        R = 6371  # Radius of the Earth in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon/2) * math.sin(dlon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c


    def create_delivery(self, client_id: int) -> Delivery:
        """Assigns a delivery to a vehicle in the same location"""
        client = next(c for c in self.clients if c.id == client_id)

        # Filtra veículos da mesma localidade
        local_vehicles = [v for v in self.vehicles if v.location == client.location]

        if not local_vehicles:
            # Fallback: usa qualquer veículo se não houver na localidade
            vehicle = random.choice(self.vehicles)
            # logging.warning(f"No local vehicles found for {client.location}. Using vehicle from {vehicle.location}")
        else:
            vehicle = random.choice(local_vehicles)

        delivery = Delivery(
            id=f"DEL##{str(uuid.uuid4())}",
            client=client,
            status="in_route",
            vehicle=vehicle,
            timestamp=datetime.now().isoformat(),
            remaining_distance=self.calculate_distance(
                vehicle.latitude, vehicle.longitude,
                client.latitude, client.longitude
            ),
            estimated_time=0
        )
        delivery.estimated_time = (delivery.remaining_distance / vehicle.average_speed) * 60
        self.deliveries.append(delivery)
        return delivery


    def simulate_movement(self):
        """Updates the position of vehicles and the status of deliveries"""
        for delivery in [e for e in self.deliveries if e.status == "in_route"]:
            # Reduce distance based on speed
            km_per_second = delivery.vehicle.average_speed / 3600
            delivery.remaining_distance = max(0, delivery.remaining_distance - km_per_second * 3600)  # 1 hour

            delivery.estimated_time = (delivery.remaining_distance / delivery.vehicle.average_speed) * 60

            # If arrived at destination
            if delivery.remaining_distance <= 0.1:  # 100m tolerance
                delivery.status = "delivered"
                delivery.timestamp = datetime.now().isoformat()
                self.history.append(delivery)
                self.deliveries.remove(delivery)


    def monitor_deliveries(self, interval: int = 5, project_id: str = None, topic_id: str = None):
        """Simulates real-time update and publishes status to GCP Pub/Sub if configured"""
        # Try to configure Pub/Sub client using provided args or environment variables
        publisher = None
        topic_path = None
        try:
            from google.cloud import pubsub_v1  # may raise ImportError if library not installed

            proj = project_id or os.environ.get("GCP_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
            topic = topic_id or os.environ.get("PUBSUB_TOPIC")
            if proj and topic:
                publisher = pubsub_v1.PublisherClient()
                topic_path = publisher.topic_path(proj, topic)
            else:
                print("Pub/Sub not configured (missing project or topic). Running local only.")
        except Exception as e:
            # If Pub/Sub client not available or configuration missing, continue without publishing
            print(f"Pub/Sub disabled: {e}")

        try:
            while True:
                self.simulate_movement()
                self._display_status(publisher, topic_path)

                # Stop monitoring as soon as there are no more active deliveries
                if not self.deliveries:
                    print("All deliveries completed. Stopping monitor.")
                    break

                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped")


    def _display_status(self, publisher=None, topic_path=None):
        """Displays the current status of deliveries and publishes each delivery as a separate JSON message to Pub/Sub when available"""
        timestamp = datetime.now()
        print(f"\n{timestamp.strftime('%H:%M:%S')} - Delivery Status:")

        deliveries = []
        for delivery in self.deliveries:
            entry = {
                "timestamp": timestamp.isoformat(),
                "id": delivery.id,
                "client": delivery.client.name,
                "address": delivery.client.address,
                "remaining_distance_km": round(delivery.remaining_distance, 2),
                "estimated_time_min": round(delivery.estimated_time, 0),
                "vehicle_id": delivery.vehicle.id,
                "vehicle_location": delivery.vehicle.location,
                "status": delivery.status
            }
            deliveries.append(entry)

        if not deliveries:
            print("No deliveries in progress")
            return

        for entry in deliveries:
            if publisher and topic_path:
                try:
                    data = json.dumps(entry).encode("utf-8")
                    # publish returns a future; don't block the loop.
                    future = publisher.publish(topic_path, data, delivery_id=entry["id"])

                    # attach a callback that captures the delivery id
                    def _make_cb(delivery_id):
                        def _cb(fut):
                            try:
                                fut.result()
                            except Exception as exc:
                                print(f"Failed to publish delivery {delivery_id}: {exc}")
                        return _cb

                    future.add_done_callback(_make_cb(entry["id"]))
                except Exception as e:
                    print(f"Failed to publish status for {entry['id']} to Pub/Sub: {e}")


    def generate_report(self):
        """Generates a JSON report of completed deliveries"""
        return json.dumps([
            {
                "id": e.id,
                "client": e.client.name,
                "address": e.client.address,
                "total_time": (datetime.fromisoformat(e.timestamp) - datetime.fromisoformat(e.timestamp)).total_seconds() / 60,
                "vehicle": e.vehicle.id
            }
            for e in self.history
        ], indent=2)

# Example usage
if __name__ == "__main__":
    system = DeliverySystem()

    # Create deliveries for all clients
    for client in system.clients:
        system.create_delivery(client.id)

    # Start monitoring (Ctrl+C to stop)
    system.monitor_deliveries()

    # Generate final report
    print("\nDelivery Report:")
    print(system.generate_report())