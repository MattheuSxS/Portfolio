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


    def _simulate_movement(self):
        """
            Simulates the movement of deliveries that are currently in route.

            This method updates the position and status of all deliveries with "in_route" status by:
            - Calculating distance traveled based on vehicle average speed over a 1-hour period
            - Updating remaining distance (ensuring it doesn't go below 0)
            - Recalculating estimated delivery time in minutes
            - Marking deliveries as "delivered" when within 100m tolerance of destination
            - Moving completed deliveries from active list to history with timestamp

            The simulation assumes a 1-hour time step and uses vehicle average speed in km/h.
            Deliveries are considered complete when remaining distance is <= 0.1 km (100m).
        """
        for delivery in [e for e in self.deliveries if e.status == "in_route"]:
            km_per_second = delivery.vehicle.average_speed / 3600
            delivery.remaining_distance = max(0, delivery.remaining_distance - km_per_second * 3600)  # 1 hour

            delivery.estimated_time = (delivery.remaining_distance / delivery.vehicle.average_speed) * 60

            if delivery.remaining_distance <= 0.1:  # 100m tolerance
                delivery.status = "delivered"
                delivery.timestamp = datetime.now().isoformat()
                self.history.append(delivery)
                self.deliveries.remove(delivery)


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
        timestamp = datetime.now()
        logging.info(f"⏰ {timestamp.strftime('%H:%M:%S')} - Processing {len(self.deliveries):,} deliveries")

        if not self.deliveries:
            return

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
                    self.publisher.shutdown()
                    break

                time.sleep(interval)

            return self.publisher.get_metrics()

        except KeyboardInterrupt:
            logging.info("Monitoring stopped")
            raise


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