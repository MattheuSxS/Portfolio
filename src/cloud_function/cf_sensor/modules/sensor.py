import time
import random
import datetime

from faker import Faker


class FakeSensorData:

    def __init__(self, country:str = 'en_US') -> None:
        self.fake   = Faker(country)
        self.fake.seed_instance(0)


    def temperatura(self) -> dict:
        """
        Generates fake sensor data.
        Returns:
            dict: A dictionary containing fake sensor data.
        """

        return {
            "sensor_id": self.fake.unique.uuid4(),
            "timestamp": datetime.datetime.now().isoformat(),
            "temperature": round(random.uniform(5.0, 30.0), 2),
            "humidity": round(random.uniform(30.0, 70.0), 2),
            "pressure": round(random.uniform(1000.0, 1020.0), 2)
        }


    def warehouse(self, warehouse_id:str, data_dict: dict) -> dict:
        """
        Generates fake sensor data for a given warehouse.
        Args:
            warehouse_id (str): The ID of the warehouse.
            data_dict (dict): The sensor data dictionary.
        Returns:
            dict: A dictionary containing the warehouse ID and sensor data.
        """

        return {
            "warehouse_id": warehouse_id,
            **data_dict,
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
                "Warehouse_SP",
                "Warehouse_RJ",
                "Warehouse_DF",
                "Warehouse_BA",
                "Warehouse_MA"
            ]

        for index in list_warehouse:
            yield self.warehouse(index, self.temperatura())
            time.sleep(1)


if __name__ == "__main__":
    test = FakeSensorData()

    print("Generating fake sensor data...")
    for i in range(5):
        for _ in test.generate_sensor_data():
            print(_)
