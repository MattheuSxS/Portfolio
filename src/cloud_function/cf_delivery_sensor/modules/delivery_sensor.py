#TODO: I must finish the delivery simulation tomorrow
import os
import uuid
import json
import time
import math
import random
import logging
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta

# try:
#     from modules.pub_sub import PubSub
# except ImportError:
#     from pub_sub import PubSub


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
        """
        Create Client instances from an iterable of client argument lists.

        Args:
            client_list (List[List] | Iterable[Iterable]): An iterable where each element is itself
                an iterable of positional arguments to be unpacked into the Client constructor.
                Although the parameter has a default of None, the function expects a concrete iterable
                of argument sequences.

        Returns:
            List[Client]: A list of Client objects constructed from the provided argument sequences.

        Raises:
            TypeError: If client_list is None or not iterable, or if an inner element cannot be unpacked
                into the Client constructor.
            Exception: Any exception raised by the Client(...) constructor (e.g., ValueError) will propagate.

        Notes:
            - Each inner iterable is passed as positional arguments using unpacking: Client(*client_data).
            - Ensure each inner iterable supplies the correct number and types of arguments expected
              by the Client initializer.

        Example:
            client_data = [
                ["Alice", "alice@example.com"],
                ["Bob", "bob@example.com"],
            ]
            clients = self._generate_clients(client_data)
        """
        return [Client(*client_data) for client_data in client_list]


    def _generate_fleet(self, vehicle_list: List[List] = None) -> List[Vehicle]:
        """
        Generates a fleet of Vehicle objects from a list of vehicle data.

        Args:
            vehicle_list (List[List], optional): A list of lists where each inner list contains 
                the data required to initialize a Vehicle object. Defaults to None.

        Returns:
            List[Vehicle]: A list of Vehicle objects created using the provided vehicle data.
        """
        return [Vehicle(*vehicle_data) for vehicle_data in vehicle_list]


    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
            Calculate the great-circle distance between two geographic coordinates using the Haversine formula.

            Args:
                lat1 (float): Latitude of the first point in decimal degrees.
                lon1 (float): Longitude of the first point in decimal degrees.
                lat2 (float): Latitude of the second point in decimal degrees.
                lon2 (float): Longitude of the second point in decimal degrees.

            Returns:
                float: Distance between the two points in kilometers.

            Notes:
                - This function assumes a spherical Earth with radius 6371 km.
                - Input coordinates must be provided in decimal degrees. The function does not
                validate input ranges (e.g., lat in [-90, 90], lon in [-180, 180]); providing
                out-of-range values may yield incorrect results.
                - The Haversine formula is suitable for most distance calculations; for very high
                precision over long distances or when ellipsoidal corrections are required,
                use a geodesic library (e.g., geographiclib).

            Example:
                >>> calculate_distance(52.5200, 13.4050, 48.8566, 2.3522)
                878.8  # approximate distance in kilometers (Berlin to Paris)
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
            Create and register a Delivery for the given client ID.

            This method:
            - Finds the client in self.clients by matching client.id == client_id.
            - Selects a vehicle:
                - Prefer a random vehicle located at the client's location.
                - If no such local vehicle exists, select a random vehicle from self.vehicles
                    and log a warning indicating the vehicle's location.
            - Computes the remaining distance between the chosen vehicle and the client
                using self.calculate_distance(vehicle.latitude, vehicle.longitude,
                client.latitude, client.longitude).
            - Creates a Delivery with a generated ID ("DEL##{uuid4}"), status "in_route",
                an ISO-formatted timestamp, the computed remaining_distance, and computes
                estimated_time in minutes as (remaining_distance / vehicle.average_speed) * 60.
            - Appends the created Delivery to self.deliveries and returns it.

            Parameters
            ----------
            client_id : int
                    Identifier of the client for whom the delivery is created.

            Returns
            -------
            Delivery
                    The newly created Delivery object (and also appended to self.deliveries).

            Side effects
            ------------
            - Appends the new Delivery to self.deliveries.
            - Emits a logging.warning if no vehicle is available at the client's location.
            - Uses random.choice to pick vehicles (non-deterministic selection).

            Raises
            ------
            StopIteration
                    If no client with the provided client_id exists in self.clients (due to
                    using next(...) without a default).
            ZeroDivisionError
                    If the selected vehicle has average_speed == 0 when computing estimated_time.

            Notes
            -----
            - Requires that self provides attributes: clients, vehicles, deliveries, and a
                method calculate_distance(lat1, lon1, lat2, lon2).
            - Relies on modules/objects: random (for vehicle selection), logging,
                uuid (for ID generation), and datetime (for timestamp).
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


    def simulate_movement(self):
        """
            Simulate movement for all deliveries that are currently en route.

            This method advances each delivery by one simulated hour and updates its
            state accordingly. For every delivery in self.deliveries with
            status == "in_route" it:

            - Computes the vehicle speed in km/s using delivery.vehicle.average_speed (km/h).
            - Advances the delivery by one hour (reducing remaining_distance).
            - Recomputes estimated_time expressed in minutes based on remaining_distance
                and vehicle.average_speed.
            - If the remaining_distance is less than or equal to 0.1 km (100 m tolerance),
                marks the delivery as "delivered", sets delivery.timestamp to the current
                ISO-formatted datetime, appends the delivery to self.history, and removes it
                from self.deliveries.

            Side effects:
            - Mutates delivery objects (remaining_distance, estimated_time, status,
                timestamp).
            - Modifies self.history and self.deliveries.
            - Uses datetime.now() for timestamps.

            Units and edge cases:
            - Assumes delivery.vehicle.average_speed is in km/h and delivery.remaining_distance
                is in km.
            - estimated_time is stored in minutes.
            - A zero or very small average_speed may cause division-by-zero or very large
                estimated_time values; callers should ensure sensible vehicle speeds.
            - Iteration is performed over a snapshot of in-route deliveries to allow safe
                removal from self.deliveries during the loop.

            Returns:
            - None
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


    def monitor_deliveries(self, interval: int = 5):
        """
            Monitor deliveries by repeatedly simulating movement and displaying status.

            This method enters a loop that:
            - Calls self.simulate_movement() to update delivery positions/state.
            - Calls self._display_status() to present current status to logs/UI.
            - Waits for the specified interval (in seconds) between iterations.
            - Exits the loop automatically when self.deliveries is empty (all deliveries completed).

            Parameters
            ----------
            interval : int
                Number of seconds to sleep between monitoring iterations. Defaults to 5.

            Behavior and side effects
            -------------------------
            - Mutates internal state via simulate_movement().
            - Produces output via _display_status() and logging.
            - Blocks the calling thread while running.
            - Returns when all deliveries are completed or when monitoring is interrupted.

            Exceptions
            ----------
            - KeyboardInterrupt is caught internally; an informational log is written and the method returns.
            - Passing a negative interval will propagate a ValueError from time.sleep.
        """
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

        # Publica em lote
        self.publisher.publish_bulk_async(messages)

    def shutdown(self):
        """Chamar no final da aplicação"""
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