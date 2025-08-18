import time
import random
import datetime
from faker import Faker


class FakeWhSensorData:
    def __init__(self, country:str = 'en_US') -> None:
        self.fake   = Faker(country)
        self.fake.seed_instance(0)


    def temperature(self) -> dict:
        """
        Generates fake sensor data.
        Returns:
            dict: A dictionary containing fake sensor data.
        """

        return {
            "sensor_id": self.fake.unique.uuid4(),
            "time_stamp": datetime.datetime.now().isoformat(),
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
                "WH_Smithville_SP",
                "WH_Lambertstad_SC",
                "WH_Lake_Michelle_DF",
                "WH_New_Kristen_BA",
                "WH_North_Allison_AM"
            ]

        for index in list_warehouse:
            yield self.warehouse(index, self.temperature())
            time.sleep(1)


    # def process_batch(self, pubsub, batch_size: int) -> int:
    #     """
    #         Processes a batch of fake warehouse sensor data and publishes each data point using the provided PubSub publisher.

    #         Args:
    #             pubsub (PubSub): An object with a 'publisher' method for publishing messages.
    #             batch_size (int): The number of batches to process.

    #         Returns:
    #             int: The total number of messages successfully sent.

    #         Raises:
    #             Exception: Re-raises any exception encountered during message publishing to trigger a batch retry.
    #     """
    #     messages_sent = 0
    #     data_dict = self.generate_sensor_data()
    #     for _ in range(batch_size):
    #         for data in data_dict:
    #             try:
    #                 message = json.dumps(data)
    #                 pubsub.publisher(message)
    #                 messages_sent += 1
    #                 logging.debug(f"Message published: {message[:100]}...")  # Log truncated message
    #             except Exception as e:
    #                 logging.warning(f"Failed to publish message: {str(e)}")
    #                 raise  # Re-raise to trigger batch retry

    #     return messages_sent

if __name__ == "__main__":
    test = FakeWhSensorData()

    print("Generating fake sensor data...")
    for i in range(5):
        for _ in test.generate_sensor_data():
            print(_)
