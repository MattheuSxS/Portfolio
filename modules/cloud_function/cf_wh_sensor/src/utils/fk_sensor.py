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
    def __init__(self, country:str = 'en_US') -> None:
        self.fake   = Faker(country)
        self.fake.seed_instance(0)


    def _temperature(self, state_id:str) -> dict:
        """
        Generates fake sensor data.
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
        return {
            "sensor_id":    _state_id[state_id],
            "time_stamp":   datetime.now().isoformat(),
            "temperature":  round(random.uniform(5.0, 30.0), 2),
            "humidity":     round(random.uniform(30.0, 70.0), 2),
            "pressure":     round(random.uniform(1000.0, 1500.0), 2)
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
    test = FakeWhSensorData()

    print("Generating fake sensor data...")
    for i in range(5):
        for _ in test.generate_sensor_data():
            print(_)