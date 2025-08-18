#TODO: I must finish the delivery simulation tomorrow
import json
import time
import math
import random
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta

# Estrutura de dados
@dataclass
class Client:
    id: str
    name: str
    address: str
    latitude: float
    longitude: float

@dataclass
class Vehicle:
    id: int
    capacity: int
    latitude: float
    longitude: float
    average_speed: float  # km/h

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
    def __init__(self):
        self.clients = self._generate_clients()
        self.vehicles = self._generate_fleet()
        self.deliveries = []
        self.history = []

    def _generate_clients(self) -> List[Client]:
        """Generates clients with realistic addresses and coordinates"""
        test = ['SALE##df308c64-60ae-4aea-821a-f2e62e2c6da7', 'WH_Smithville_RJ', -22.9068, -43.1729, 'ID##e734bb3f-c01c-41bb-886e-7f014cb38f34', 'Maria Luísa', 'Condomínio Enrico Vasconcelos 72, São Luís - MA', -2.555438, -44.306828]
        return [
            Client(test[4], test[5], test[6], test[7], test[8]),
            Client(2, "Maria Santos", "Rua Oscar Freire, 500", -23.5586, -46.6734),
            Client(3, "Carlos Oliveira", "Av. Faria Lima, 2000", -23.5679, -46.6916),
            Client(4, "Ana Costa", "Rua Augusta, 1500", -23.5542, -46.6608),
            Client(5, "Pedro Rocha", "Alameda Santos, 800", -23.5612, -46.6555)
        ]

    def _generate_fleet(self) -> List[Vehicle]:
        """Generates delivery vehicles"""
        return [
            Vehicle(1, 20, -2.555438, -44.306828, 90),  # Distribution center
            Vehicle(2, 15, -23.5505, -46.6339, 25),
            Vehicle(3, 10, -23.5505, -46.6339, 35)
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
        """Assigns a delivery to an available vehicle"""
        client = next(c for c in self.clients if c.id == client_id)
        vehicle = random.choice(self.vehicles)

        delivery = Delivery(
            id=len(self.deliveries) + 1,
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
        delivery.estimated_time = (delivery.remaining_distance / vehicle.average_speed) * 60  # minutes
        self.deliveries.append(delivery)
        return delivery

    def simulate_movement(self):
        """Updates the position of vehicles and the status of deliveries"""
        for delivery in [e for e in self.deliveries if e.status == "in_route"]:
            # Reduce distance based on speed
            km_per_second = delivery.vehicle.average_speed / 3600
            delivery.remaining_distance = max(0, delivery.remaining_distance - km_per_second * 5)  # 5 seconds

            delivery.estimated_time = (delivery.remaining_distance / delivery.vehicle.average_speed) * 60

            # If arrived at destination
            if delivery.remaining_distance <= 0.1:  # 100m tolerance
                delivery.status = "delivered"
                delivery.timestamp = datetime.now().isoformat()
                self.history.append(delivery)
                self.deliveries.remove(delivery)

    def monitor_deliveries(self, interval: int = 5):
        """Simulates real-time update   """
        try:
            while True:
                self.simulate_movement()
                self._display_status()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped")

    def _display_status(self):
        """Displays the current status of deliveries"""
        print(f"\n{datetime.now().strftime('%H:%M:%S')} - Delivery Status:")
        for delivery in self.deliveries:
            print(f"Delivery #{delivery.id} to {delivery.client.name}: "
                  f"{delivery.remaining_distance:.2f}km remaining "
                  f"(~{delivery.estimated_time:.0f} minutes) - "
                  f"Vehicle {delivery.vehicle.id}")

        if not self.deliveries:
            print("No deliveries in progress")

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