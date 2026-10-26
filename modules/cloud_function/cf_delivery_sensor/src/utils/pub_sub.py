import time
import json
import logging
import threading
from concurrent import futures
from google.cloud import pubsub_v1


class HighThroughputPublisher():
    """
        A high-performance Google Cloud Pub/Sub publisher optimized for throughput and reliability.

        This class provides an optimized publisher implementation for Google Cloud Pub/Sub with features
        designed for high-throughput scenarios including batching, flow control, concurrent processing,
        and comprehensive monitoring capabilities.

        Key Features:
            - Optimized batch settings (10MB, 500ms latency, 1000 messages per batch)
            - Flow control with 100MB buffer and 10K message limit
            - Concurrent publishing using ThreadPoolExecutor (50 workers)
            - Real-time metrics tracking and logging
            - Bulk async publishing with chunking
            - Thread-safe operations with proper locking
            - Graceful shutdown handling

        Performance Characteristics:
            - Designed for high message volumes (10K+ messages/sec)
            - Automatic batching to reduce API calls
            - Flow control to prevent memory issues
            - Concurrent chunk processing for bulk operations

        Usage Example:
            ```python
            publisher = HighThroughputPublisher("my-project", "my-topic")

            # Single message
            future = publisher.publish_message({"key": "value"}, "delivery-123")

            # Bulk messages
            messages = [{"data": {...}, "delivery_id": "id"} for ...]
            publisher.publish_bulk_async(messages)

            # Get metrics
            metrics = publisher.get_metrics()

            # Cleanup
            publisher.shutdown()
            ```

        Attributes:
            project_id (str): Google Cloud project identifier
            topic_id (str): Pub/Sub topic name
            publisher_client (PublisherClient): Configured Pub/Sub client with optimized settings
            topic_path (str): Full topic path for publishing
            executor (ThreadPoolExecutor): Thread pool for concurrent operations
            message_counter (int): Messages published in current second
            total_published (int): Total messages published since initialization
            start_time (float): Publisher initialization timestamp
            last_print_time (float): Last metrics logging timestamp
            lock (threading.Lock): Thread synchronization lock

        Thread Safety:
            All public methods are thread-safe. Internal counters and metrics are protected
            by threading locks to ensure data consistency during concurrent access.
    """

    def __init__(self, project_id: str, topic_id: str):
        self.project_id = project_id
        self.topic_id = topic_id

        self.publisher_client = pubsub_v1.PublisherClient(
            client_options={
                "api_endpoint": "pubsub.googleapis.com:443",
                "quota_project_id": project_id,
            },
            batch_settings=pubsub_v1.types.BatchSettings(
                max_bytes=10 * 1024 * 1024,
                max_latency=0.5,
                max_messages=1000
            ),
            publisher_options=pubsub_v1.types.PublisherOptions(
                enable_message_ordering=False,
                flow_control=pubsub_v1.types.PublishFlowControl(
                    message_limit=10000,
                    byte_limit=100 * 1024 * 1024,
                    limit_exceeded_behavior=pubsub_v1.types.LimitExceededBehavior.BLOCK
                )
            )
        )

        self.topic_path = self.publisher_client.topic_path(project_id, topic_id)

        self.executor = futures.ThreadPoolExecutor(
            max_workers=25,
            thread_name_prefix="pubsub_publisher"
        )

        self.message_counter = 0
        self.total_published = 0
        self.start_time = time.time()
        self.last_print_time = time.time()
        self.lock = threading.Lock()


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("⏳ Shutting down publisher client and flushing buffer...")
        self.publisher_client.shutdown(15.0)  # Tempo limite para o shutdown
        self.executor.shutdown(wait=True)
        logging.info("✅ Publisher client and executor shut down successfully.")


    def publish_message(self, message_data: dict, delivery_id: str) -> futures.Future:
        """
            Publishes a message to the configured Pub/Sub topic with delivery tracking.

            This method serializes the message data to JSON, publishes it to the Pub/Sub topic
            with the specified delivery ID as an attribute, and maintains publishing statistics
            with thread-safe counters. Logs publishing rate and total message count periodically.

            Args:
                message_data (dict): The message payload to be published as JSON.
                delivery_id (str): Unique identifier for the delivery, added as message attribute.

            Returns:
                futures.Future: A Future object representing the publish operation that will
                            contain the message ID when the publish completes successfully.

            Raises:
                Exception: Re-raises any exception that occurs during message publishing,
                        after logging the error with the delivery ID for debugging.

            Note:
                - Uses thread-safe locking for counter updates
                - Logs publishing statistics every second
                - Message data is JSON-encoded and UTF-8 encoded before publishing
        """
        try:
            data = json.dumps(message_data).encode("utf-8")

            future = self.publisher_client.publish(
                self.topic_path,
                data=data,
                delivery_id=delivery_id
            )

            with self.lock:
                self.message_counter += 1
                self.total_published += 1

                current_time = time.time()
                if current_time - self.last_print_time >= 1.0:
                    logging.info(
                        f"📤 Publishing rate: {self.message_counter}/sec | "
                        f"📊 Total sent: {self.total_published}"
                    )
                    self.message_counter = 0
                    self.last_print_time = current_time

            return future

        except Exception as e:
            logging.error(f"❌ Failed to publish message {delivery_id}: {e}")
            raise


    def publish_bulk_async(self, messages: list) -> None:
        """
            Publishes a list of messages asynchronously in chunks using thread pool executor.

            This method divides the messages into chunks of 500 and processes them concurrently
            to improve throughput. Each chunk is published independently with error handling
            and timeout protection.

            Args:
                messages (list): List of messages to be published. If empty, the method returns early.

            Returns:
                None

            Raises:
                Exception: Logs errors that occur during chunk processing but does not re-raise them.

            Notes:
                - Uses a chunk size of 500 messages per batch
                - Each chunk has a 30-second timeout
                - Logs detailed performance metrics including success rate, duration, and throughput
                - Updates the total_published counter internally
                - Handles TimeoutError and general exceptions gracefully with logging
        """
        if not messages:
            return

        logging.info(f"🚀 Starting bulk publish of {len(messages):,} messages")
        start_time = time.time()

        chunk_size = 500
        chunks = [messages[i:i + chunk_size] for i in range(0, len(messages), chunk_size)]

        futures_list = []
        for chunk in chunks:
            future = self.executor.submit(self._publish_chunk, chunk)
            futures_list.append(future)

        successful = 0
        for future in futures_list:
            try:
                result = future.result(timeout=30.0)
                successful += result
            except futures.TimeoutError:
                logging.warning("⏰ Chunk timeout")
            except Exception as e:
                logging.error(f"💥 Chunk error: {e}")

        end_time = time.time()
        duration = end_time - start_time
        rate = len(messages) / duration if duration > 0 else 0

        logging.info(
            f"✅ Bulk publish complete: {successful:,}/{len(messages):,} "
            f"messages in {duration:.2f}s ({rate:,.0f} msgs/sec) | "
            f"📊 Total published so far: {self.total_published:,}"
        )


    def _publish_chunk(self, chunk: list) -> int:
        """
            Publishes a chunk of messages to the pub/sub system and returns the count of successful publications.

            Args:
                chunk (list): A list of dictionaries containing message data, where each dictionary
                            should have 'data' and 'delivery_id' keys.

            Returns:
                int: The number of messages that were successfully published from the chunk.

            Raises:
                Logs errors for any failed message publications but does not raise exceptions.
        """
        successful = 0
        for message_data in chunk:
            try:
                self.publish_message(message_data["data"], message_data["delivery_id"])
                successful += 1
            except Exception as e:
                logging.error(f"Failed to publish in chunk: {e}")

        return successful


    def get_metrics(self) -> dict:
        """
            Retrieve current performance metrics for the Pub/Sub publisher.

            This method provides a thread-safe way to access real-time statistics
            about message publishing performance and system uptime.

            Returns:
                dict: A dictionary containing the following metrics:
                    - messages_last_sec (int): Number of messages published in the last second
                    - total_published (int): Total number of messages published since start
                    - uptime_sec (float): Time elapsed since publisher initialization in seconds
                    - avg_rate (float): Average publishing rate in messages per second

            Note:
                This method is thread-safe and uses internal locking to ensure
                consistent metric calculations during concurrent access.
        """
        with self.lock:
            uptime = time.time() - self.start_time
            avg_rate = self.total_published / uptime if uptime > 0 else 0
            metrics = {
                "messages_last_sec": self.message_counter,
                "total_published": self.total_published,
                "uptime_sec": round(uptime, 2),
                "avg_rate": round(avg_rate, 2)  # msgs/sec
            }
        return metrics


    def shutdown(self) -> None:
        """
            Gracefully shuts down the publisher by stopping the executor and waiting for all tasks to complete.

            This method ensures that all pending publish operations are completed before the publisher
            is terminated. It blocks until all threads in the executor have finished their work.

            Returns:
                None
        """
        self.executor.shutdown(wait=True)
        logging.info("Publisher shutdown complete")