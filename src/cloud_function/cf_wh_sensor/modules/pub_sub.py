#TODO: I must implement the new pub/sub module!
import logging
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError


class PubSub:
    """
        A class for interacting with Google Cloud Pub/Sub, providing methods to publish messages to
        a topic and pull messages from a subscription.

        Attributes:
            project_id (str): The Google Cloud project ID.
            topic_id (str): The Pub/Sub topic ID.
            client (pubsub_v1.PublisherClient): The Pub/Sub publisher client instance.

        Methods:
            publisher(menssage: str):
                Publishes a message to the specified Pub/Sub topic.

            pull_messages(subscription_id: str, max_messages: int = 10, timeout: int = 10) -> list:
                Pulls messages from the specified Pub/Sub subscription.
    """
    def __init__(self, project_id:str, topic_id:str) -> None:
        self.project_id = project_id
        self.topic_id = topic_id
        self.client = pubsub_v1.PublisherClient()


    def publisher(self, menssage:str):
        """
        Publishes a message to a specified Google Cloud Pub/Sub topic.

        Args:
            menssage (str): The message to be published to the topic.

        Raises:
            Exception: If publishing the message fails, the exception is logged and re-raised.
        """
        try:
            topic_path = self.client.topic_path(self.project_id, self.topic_id)
            self.client.publish(topic_path, menssage.encode("utf-8"))

        except Exception as e:
            logging.error(f"Failed to publish message: {str(e)}")
            raise


    def pull_messages(self, subscription_id:str, max_messages:int = 10, timeout:int = 10) -> list:
        """
        Pulls messages from a Google Cloud Pub/Sub subscription.

        Args:
            subscription_id (str): The ID of the subscription to pull messages from.
            max_messages (int): The maximum number of messages to pull.
            timeout (int): The timeout for pulling messages.

        Returns:
            list: A list of pulled messages.
        """
        subscription_path = self.client.subscription_path(self.project_id, subscription_id)
        response = self.client.pull(subscription_path, max_messages=max_messages, timeout=timeout)
        return response.received_messages



if __name__ == "__main__":
    t = PubSub("mts-default-portofolio", "wh_sensor_topic")
    t.publisher('{"hello": "2131"}')