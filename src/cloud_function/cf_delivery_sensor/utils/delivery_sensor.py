import uuid
import time
import math
import random
import logging
from typing import List
from zoneinfo import ZoneInfo
from datetime import datetime
from dataclasses import dataclass

try:
    from utils.pub_sub import HighThroughputPublisher
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
    difficulty: str  # "easy", "medium", "hard"
    timestamp: str
    remaining_distance: float  # km
    estimated_time: float  # minutes


class DeliverySystem():
    """
        A delivery management system that simulates and monitors package deliveries in real-time.

        The DeliverySystem class orchestrates the entire delivery process by managing clients,
        vehicles, and deliveries. It provides functionality to create deliveries, simulate
        vehicle movement, monitor delivery progress, and generate reports. The system publishes
        real-time delivery status updates to a message queue for external consumption.

        Key Features:
            - Real-time delivery simulation with movement tracking
            - Distance calculation using Haversine formula
            - Intelligent vehicle assignment (prefers local vehicles)
            - Continuous monitoring with configurable intervals
            - Bulk message publishing for status updates
            - Comprehensive delivery history and reporting

        Attributes:
            publisher (HighThroughputPublisher): Message publisher for delivery status updates
            clients (List[Client]): List of registered clients
            vehicles (List[Vehicle]): List of available delivery vehicles
            deliveries (List[Delivery]): Currently active deliveries in progress
            history (List[Delivery]): Completed deliveries for reporting

        Example:
            >>> system = DeliverySystem("my-project", "delivery-topic", client_data, vehicle_data)
            >>> delivery = system.create_delivery(client_id=123)
            >>> metrics = system.monitor_deliveries(interval=10)
            >>> report = system.generate_report()

            The system assumes Earth as a perfect sphere for distance calculations and uses
            a 1-hour time step for movement simulation. Deliveries are marked as complete
            when within 100 meters of the destination.
        """
    def __init__(self, project_id: str, topic_id: str, client_list: List[List] = None, vehicle_list: List[List] = None):
        self.publisher = HighThroughputPublisher(project_id, topic_id)
        self.clients = self._generate_clients(client_list)
        self.vehicles = self._generate_fleet(vehicle_list)
        self.deliveries = []
        self.history = []
        self.STATUS = ['delivered', 'not_delivered', 'wrong_address', 'other_problems']
        self.STATUS_PROBABILITIES = [0.80, 0.10, 0.07, 0.03]

        self.DELIVERY_DIFFICULTY = ['easy', 'medium', 'hard']
        self.DELIVERY_DIFFICULTY_PROBABILITIES = [0.70, 0.20, 0.10]


    def _generate_clients(self, client_list: List[List] = None) -> List[Client]:
        """
            Generate a list of Client objects from client data.

            Args:
                client_list (List[List], optional): A list of lists where each inner list
                    contains the data needed to instantiate a Client object. Defaults to None.

            Returns:
                List[Client]: A list of Client objects created from the provided client data.

            Raises:
                TypeError: If client_list contains data that cannot be unpacked for Client instantiation.
        """
        return [Client(*client_data) for client_data in client_list]


    def _generate_fleet(self, vehicle_list: List[List] = None) -> List[Vehicle]:
        """
        Generate a fleet of Vehicle objects from a list of vehicle data.

        Args:
            vehicle_list (List[List], optional): A list containing vehicle data where each
                inner list contains the parameters needed to initialize a Vehicle object.
                Defaults to None.

        Returns:
            List[Vehicle]: A list of Vehicle objects created from the provided vehicle data.

        Raises:
            TypeError: If vehicle_list contains invalid data types for Vehicle initialization.
            ValueError: If vehicle_data doesn't contain the required parameters for Vehicle.
        """
        return [Vehicle(*vehicle_data) for vehicle_data in vehicle_list]


    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
            Calculate the great circle distance between two points on Earth using the Haversine formula.

            Args:
                lat1 (float): Latitude of the first point in decimal degrees
                lon1 (float): Longitude of the first point in decimal degrees
                lat2 (float): Latitude of the second point in decimal degrees
                lon2 (float): Longitude of the second point in decimal degrees

            Returns:
                float: Distance between the two points in kilometers

            Note:
                This method uses the Haversine formula which assumes Earth is a perfect sphere
                with radius 6371 km. For more precise calculations over short distances,
                consider using more sophisticated geodesic calculations.
        """
        R = 6371  # Radius of the Earth in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon/2) * math.sin(dlon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c


    def create_delivery(self, client_id: int) -> Delivery:
        """
            Creates a new delivery for the specified client.

            This method finds a client by ID, selects an appropriate vehicle (preferring
            local vehicles when available), and creates a new delivery with calculated
            distance and estimated delivery time.

            Args:
                client_id (int): The unique identifier of the client for whom to create the delivery.

            Returns:
                Delivery: A new Delivery object with assigned vehicle, status set to "in_route",
                        calculated remaining distance, and estimated delivery time.

            Raises:
                StopIteration: If no client with the specified client_id is found.

            Note:
                - Prefers vehicles at the same location as the client when available
                - Falls back to any available vehicle if no local vehicles exist
                - Logs a warning when using non-local vehicles
                - Estimated time is calculated in minutes based on distance and vehicle speed
        """
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
            difficulty=random.choices(self.DELIVERY_DIFFICULTY, weights=self.DELIVERY_DIFFICULTY_PROBABILITIES, k=1)[0],
            timestamp=datetime.now(ZoneInfo('Europe/Dublin')).isoformat(),
            remaining_distance=self.calculate_distance(
                vehicle.latitude, vehicle.longitude,
                client.latitude, client.longitude
            ),
            estimated_time=0
        )

        delivery.estimated_time = (delivery.remaining_distance / vehicle.average_speed) * 60
        self.deliveries.append(delivery)

        return delivery


    def _simulate_movement(self):
        """
            Simulates the movement of delivery vehicles and updates delivery status.

            This method processes all deliveries with "in_route" status, simulating their
            progress by reducing remaining distance based on vehicle speed over a 1-hour
            time period. When deliveries reach their destination (within 100m tolerance),
            they are marked as "delivered" and moved to history.

            The method performs the following operations:
            - Calculates distance traveled based on vehicle average speed over 1 hour
            - Updates remaining distance and estimated time for each delivery
            - Marks deliveries as "delivered" when within 100m of destination
            - Creates message entries for completed deliveries with delivery details
            - Publishes completion messages asynchronously
            - Moves completed deliveries from active list to history

            Side effects:
            - Modifies delivery.remaining_distance and delivery.estimated_time
            - Changes delivery.status to "delivered" for completed deliveries
            - Updates delivery.timestamp for completed deliveries
            - Adds completed deliveries to self.history
            - Removes completed deliveries from self.deliveries
            - Publishes messages via self.publisher
        """
        messages = []


        for delivery in [e for e in self.deliveries if e.status == "in_route"]:
            km_per_second = delivery.vehicle.average_speed / 3600
            delivery.remaining_distance = max(0, delivery.remaining_distance - km_per_second * 3600)  # 1 hour

            delivery.estimated_time = (delivery.remaining_distance / delivery.vehicle.average_speed) * 60

            if delivery.remaining_distance <= 0.1:  # 100m tolerance
                delivery.status = random.choices(self.STATUS, weights=self.STATUS_PROBABILITIES, k=1)[0]
                delivery.timestamp = datetime.now(ZoneInfo('Europe/Dublin')).isoformat()

                entry = {
                    "delivery_id":           delivery.id,
                    "vehicle_id":            delivery.vehicle.id,
                    "vehicle_location":      delivery.vehicle.location,
                    "purchase_id":           delivery.client.id,
                    "customer_name":         delivery.client.name,
                    "customer_address":      delivery.client.address,
                    "remaining_distance_km": int(delivery.remaining_distance),
                    "estimated_time_min":    int(delivery.estimated_time),
                    "delivery_difficulty":   delivery.difficulty,
                    "status":                delivery.status,
                    "created_at":            delivery.timestamp,
                }
                messages.append({
                    "data": entry,
                    "delivery_id": str(delivery.id)
                })

                self.history.append(delivery)
                self.deliveries.remove(delivery)

        self.publisher.publish_bulk_async(messages)


    def _display_status(self):
        """
            Display and publish the current status of all deliveries being processed.

            Logs a summary of the number of deliveries being processed with a timestamp,
            then publishes detailed status information for each delivery to a message queue.

            For each delivery, publishes the following information:
            - Timestamp of the status update
            - Delivery ID and client details (name, address)
            - Remaining distance in kilometers (rounded to 2 decimal places)
            - Estimated delivery time in minutes (rounded to nearest minute)
            - Vehicle ID and current location
            - Current delivery status

            Returns early if no deliveries are present in self.deliveries.

            Side Effects:
                - Logs an info message with processing timestamp and delivery count
                - Publishes bulk messages to self.publisher with delivery status data
        """
        timestamp = datetime.now(ZoneInfo('Europe/Dublin'))
        logging.info(f"⏰ {timestamp.strftime('%H:%M:%S')} - Processing {len(self.deliveries):,} deliveries")

        if not self.deliveries:
            return

        messages = []
        for delivery in self.deliveries:
            entry = {
                    "delivery_id":           delivery.id,
                    "vehicle_id":            delivery.vehicle.id,
                    "vehicle_location":      delivery.vehicle.location,
                    "purchase_id":           delivery.client.id,
                    "customer_name":         delivery.client.name,
                    "customer_address":      delivery.client.address,
                    "remaining_distance_km": int(delivery.remaining_distance),
                    "estimated_time_min":    int(delivery.estimated_time),
                    "delivery_difficulty":   delivery.difficulty,
                    "status":                delivery.status,
                    "created_at":            delivery.timestamp,
            }
            messages.append({
                "data": entry,
                "delivery_id": str(delivery.id)
            })

        self.publisher.publish_bulk_async(messages)


    def monitor_deliveries(self, interval: int = 5):
        """
            Monitors delivery progress by continuously simulating movement and updating status.

            This method runs a continuous monitoring loop that simulates delivery vehicle movement,
            displays current status, and publishes metrics at regular intervals. The monitoring
            continues until all deliveries are completed or the process is interrupted.

            Args:
                interval (int, optional): Time in seconds between monitoring cycles. Defaults to 5.

            Returns:
                dict: Publisher metrics containing delivery performance data and statistics.

            Raises:
                KeyboardInterrupt: When monitoring is manually interrupted by user input.

            Note:
                The method will automatically shutdown the system when all deliveries are completed.
                Status updates and movement simulation occur on each monitoring cycle.
        """
        try:
            while True:
                self._simulate_movement()
                self._display_status()

                if not self.deliveries:
                    logging.info("All deliveries completed. Stopping monitor.")
                    break

                time.sleep(interval)

            return self.publisher.get_metrics()

        except KeyboardInterrupt:
            logging.info("Monitoring stopped")
            raise


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