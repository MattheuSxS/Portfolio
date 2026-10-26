import time
import random
from faker import Faker
from datetime import datetime


class FakeWhSensorData:
    """
        FakeWhSensorData is a class for generating fake warehouse sensor data for testing and development purposes.

        Attributes:
            fake (Faker): An instance of the Faker class for generating fake data.

            country (str, optional): Locale code for generating localized fake data. Defaults to 'en_US'.

        Methods:
            temperature() -> dict:
                Generates a dictionary containing fake sensor data, including sensor ID, timestamp, temperature,
                humidity, and pressure.

            warehouse(warehouse_id: str, data_dict: dict) -> dict:
                Combines a warehouse ID with a sensor data dictionary into a single dictionary.

            generate_sensor_data():
                Yields fake sensor data for a predefined list of warehouses, simulating real-time data generation with a delay.

            # process_batch(pubsub, batch_size: int) -> int:
            #     Processes and publishes a batch of fake warehouse sensor data using a provided PubSub publisher.
            #     Returns the total number of messages sent, and raises exceptions to trigger batch retries.
    """
    def __init__(self, country:str = 'en_US', anomaly_chance: bool = False, anomaly_state: str = "SP", anomaly_type: str = None) -> None:
        self.fake   = Faker(country)
        self.fake.seed_instance(0)
        self.last_value = None
        self.anomaly_chance = anomaly_chance
        self.anomaly_state = anomaly_state
        self.anomaly_type = anomaly_type


    def _apply_anomaly(self, value: float, type: str) -> float:
        """
        Applies a specified anomaly to a given value based on the anomaly type.
        Args:
            value (float): Normal generated value
            type (str): Type of anomaly to apply (e.g., 'temperature_spike', 'humidity_drop', 'pressure_drop')
        Returns:
            float: Value with anomaly applied
        """
        ANOMALY_TYPES = {
            'temperature_spike': {
                'fields': ['temperature'],
                'multiplier': (2.0, 5.0),
                'message': "🔥 Spike Temperature"
            },
            'humidity_drop': {
                'fields': ['humidity'],
                'multiplier': (0.1, 0.5),
                'message': "💧 Critical Humidity Drop!"
            },
            'pressure_drop': {
                'fields': ['pressure'],
                'multiplier': (0.7, 0.9),
                'message': "🌀 Atmospheric Pressure Drop!"
            }
    }
        multiplier = random.uniform(*ANOMALY_TYPES[type]['multiplier'])
        return round(value * multiplier, 2)


    def _temperature(self, state_id:str) -> dict:
        """
            Generates fake sensor data for a given state ID,
            including
                - temperature
                - humidity
                - pressure

            Optionally applies anomalies based on the configuration.

            Args:
                state_id (str): The ID of the state for which to generate sensor data.
            Returns:
                dict: A dictionary containing fake sensor data.
        """

        _state_id = \
        {
            "SP": "SP##e3e70682-c209-4cac-a29f-6fbed82c07cd",
            "SC": "SC##f728b4fa-4248-4e3a-8a5d-2f346baa9455",
            "DF": "DF##eb1167b3-67a9-4378-bc65-c1e582e2e662",
            "BA": "BA##23a7711a-8133-4876-b7eb-dcd9e87a1613",
            "AM": "AM##b4862b21-fb97-4435-8856-1712e8e5216a"
        }

        temperature = round(random.uniform(5.0, 30.0), 2)
        humidity = round(random.uniform(30.0, 70.0), 2)
        pressure = round(random.uniform(1000.0, 1020.0), 2)

        if self.anomaly_chance == True and state_id == self.anomaly_state:
            match self.anomaly_type:
                case 'temperature_spike':
                    temperature = self._apply_anomaly(temperature, self.anomaly_type)
                case 'humidity_drop':
                    humidity = self._apply_anomaly(humidity, self.anomaly_type)
                case 'pressure_drop':
                    pressure = self._apply_anomaly(pressure, self.anomaly_type)

        return {
            "sensor_id":    _state_id[state_id],
            "time_stamp":   datetime.now().isoformat(),
            "temperature":  temperature,
            "humidity":     humidity,
            "pressure":     pressure
        }


    def warehouse(self, warehouse_id:str) -> dict:
        """
        Generates fake sensor data for a given warehouse.
        Args:
            warehouse_id (str): The ID of the warehouse.
        Returns:
            dict: A dictionary containing the warehouse ID and sensor data.
        """

        return {
            "warehouse_id": warehouse_id,
            **self._temperature(warehouse_id[-2:]),
        }


    def generate_sensor_data(self):
        """
        Generates fake sensor data for a given warehouse.
        Args:
            warehouse_id (str): The ID of the warehouse.
        Returns:
            dict: A dictionary containing the warehouse ID and sensor data.
        """

        list_warehouse = \
            [
                "WH_Smithville_SP",
                "WH_Lambertstad_SC",
                "WH_Lake_Michelle_DF",
                "WH_New_Kristen_BA",
                "WH_North_Allison_AM"
            ]

        for index in list_warehouse:
            yield self.warehouse(index)
            time.sleep(1)


if __name__ == "__main__":
    anomaly_type = random.choice(['temperature_spike', 'humidity_drop', 'pressure_drop'])
    test = FakeWhSensorData(anomaly_chance=True, anomaly_state="SP", anomaly_type=anomaly_type)

    print("Generating fake sensor data...")
    for i in range(2):
        for _ in test.generate_sensor_data():
            print(_)