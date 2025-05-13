from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError


class PubSub:
    def __init__(self, project_id:str, topic_id:str, subscriber:str, option:int = 1) -> None:
        self.project_id = project_id
        self.topic_id   = topic_id
        self.subscriber = subscriber

        match option:
            case 1:
                self.client = pubsub_v1.PublisherClient()
            case 2:
                self.client = pubsub_v1.SubscriberClient()
            case _:
                raise Exception ("Invalid option! Choose [1] = Publisher | [2] Subscriber")


    def publisher(self, menssage:str):
        """
        Publishes a message to a Google Cloud Pub/Sub topic.

        Args:
            menssage (str): The message to be published.

        Returns:
            None
        """

        topic_path = self.client.topic_path(self.project_id, self.topic_id)

        self.client.publish(topic_path, menssage.encode("utf-8"))


    #TODO (developer)
    # def subscriber(self, menssage:dict):

    #     # The `subscription_path` method creates a fully qualified identifier
    #     # in the form `projects/{project_id}/subscriptions/{subscription_id}`
    #     subscription_path = self.client.subscription_path(self.project_id, self.subscriber)

    #     def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    #         print(f"Received {message}.")
    #         message.ack()

    #     streaming_pull_future = self.subscriber.subscribe(subscription_path, callback=callback)
    #     print(f"Listening for messages on {subscription_path}..\n")

        # Wrap subscriber in a 'with' block to automatically call close() when done.
        # with subscriber:
        #     try:
        #         # When `timeout` is not set, result() will block indefinitely,
        #         # unless an exception is encountered first.
        #         streaming_pull_future.result(timeout=timeout)
        #     except TimeoutError:
        #         streaming_pull_future.cancel()  # Trigger the shutdown.
                # streaming_pull_future.result()  # Block until the shutdown is complete.


if __name__ == "__main__":
    # projects/default-project-mts/topics/tp-pj-streaming
    t = PubSub("default-project-mts", "tp-pj-streaming", "tp-pj-streaming-subs", 1)
    t.publisher('{"hello": "2131"}')