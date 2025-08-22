import uuid
import json
import time
import math
import random
import logging
from typing import List
from datetime import datetime
from dataclasses import dataclass

try:
    from modules.pub_sub import HighThroughputPublisher
except ImportError:
    from pub_sub import HighThroughputPublisher



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


class DeliverySystem():
    def __init__(self, project_id: str, topic_id: str, client_list: List[List] = None, vehicle_list: List[List] = None):
        self.publisher = HighThroughputPublisher(project_id, topic_id)
        self.clients = self._generate_clients(client_list)
        self.vehicles = self._generate_fleet(vehicle_list)
        self.deliveries = []
        self.history = []


    def _generate_clients(self, client_list: List[List] = None) -> List[Client]:
        return [Client(*client_data) for client_data in client_list]


    def _generate_fleet(self, vehicle_list: List[List] = None) -> List[Vehicle]:
        return [Vehicle(*vehicle_data) for vehicle_data in vehicle_list]


    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371  # Radius of the Earth in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon/2) * math.sin(dlon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c


    def create_delivery(self, client_id: int) -> Delivery:
        client = next(c for c in self.clients if c.id == client_id)

        local_vehicles = [v for v in self.vehicles if v.location == client.location]

        if not local_vehicles:
            vehicle = random.choice(self.vehicles)
            logging.warning(f"No local vehicles found for {client.location}. Using vehicle from {vehicle.location}")
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
        for delivery in [e for e in self.deliveries if e.status == "in_route"]:
            km_per_second = delivery.vehicle.average_speed / 3600
            delivery.remaining_distance = max(0, delivery.remaining_distance - km_per_second * 3600)  # 1 hour

            delivery.estimated_time = (delivery.remaining_distance / delivery.vehicle.average_speed) * 60

            if delivery.remaining_distance <= 0.1:  # 100m tolerance
                delivery.status = "delivered"
                delivery.timestamp = datetime.now().isoformat()
                self.history.append(delivery)
                self.deliveries.remove(delivery)


    def monitor_deliveries(self, interval: int = 5):
        try:
            while True:
                self.simulate_movement()
                self._display_status()

                if not self.deliveries:
                    logging.info("All deliveries completed. Stopping monitor.")
                    self.shutdown()
                    break

                time.sleep(interval)
        except KeyboardInterrupt:
            logging.info("Monitoring stopped")


    def _display_status(self):
        timestamp = datetime.now()
        logging.info(f"⏰ {timestamp.strftime('%H:%M:%S')} - Processing {len(self.deliveries):,} deliveries")

        if not self.deliveries:
            return

        # Prepara mensagens em lote
        messages = []
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
            messages.append({
                "data": entry,
                "delivery_id": str(delivery.id)
            })

        self.publisher.publish_bulk_async(messages)


    def shutdown(self):
        self.publisher.shutdown()


    def generate_report(self):
        """
            Generate a JSON-formatted report from the object's delivery history.

            Returns:
                str: A JSON string (pretty-printed with indent=2) representing a list of delivery records. Each record
                is a JSON object with the following fields:
                    - id: the event identifier (from e.id)
                    - client: the client name (from e.client.name)
                    - address: the client address (from e.client.address)
                    - total_time: total time in minutes for the delivery event, computed as the difference between
                    two ISO-8601 timestamps converted via datetime.fromisoformat and divided by 60 (seconds → minutes)
                    - vehicle: the vehicle identifier (from e.vehicle.id)

            Notes:
                - Expects self.history to be an iterable of event-like objects with attributes:
                id, client (with .name and .address), timestamp (ISO-8601 string), and vehicle (with .id).
                - timestamp values must be parseable by datetime.fromisoformat; otherwise a ValueError will be raised.
                - Currently the implementation computes total_time by subtracting the same timestamp (e.timestamp - e.timestamp),
                which yields 0.0 minutes. To obtain a meaningful duration, ensure event objects supply distinct start/end
                timestamps or adjust the calculation to use the appropriate timestamp fields.
                - The method returns a serialized JSON string and does not modify the underlying event objects.
        """
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