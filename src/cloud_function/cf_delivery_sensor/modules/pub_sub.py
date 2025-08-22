#TODO: I must finish this
import time
import json
import logging
import threading
from concurrent import futures
from dataclasses import dataclass
from google.cloud import pubsub_v1
from typing import List, Dict, Tuple


@dataclass
class PublishResult:
    successful: int = 0
    failed: int = 0
    errors: List[Tuple[str, Exception]] = None  # (delivery_id, error)

    def __init__(self):
        self.successful = 0
        self.failed = 0
        self.errors = []

    def add_success(self):
        self.successful += 1

    def add_error(self, delivery_id: str, error: Exception):
        self.failed += 1
        self.errors.append((delivery_id, error))

    def __str__(self):
        return f"✅ {self.successful:,} successful, ❌ {self.failed:,} failed"


class HighThroughputPublisher():
    def __init__(self, project_id: str, topic_id: str):
        self.project_id = project_id
        self.topic_id = topic_id
        self.publish_result = PublishResult()


        self.publisher_client = pubsub_v1.PublisherClient(
            client_options={
                "api_endpoint": "pubsub.googleapis.com:443",
                "quota_project_id": project_id,
            },
            batch_settings=pubsub_v1.types.BatchSettings(
                max_bytes=10 * 1024 * 1024,     # 10MB por batch
                max_latency=0.5,                # 500ms max latency
                max_messages=1000               # 1000 mensagens por batch
            ),
            publisher_options=pubsub_v1.types.PublisherOptions(
                enable_message_ordering=False,
                flow_control=pubsub_v1.types.PublishFlowControl(
                    message_limit=10000,        # 10K mensagens em buffer
                    byte_limit=100 * 1024 * 1024, # 100MB buffer
                    limit_exceeded_behavior=pubsub_v1.types.LimitExceededBehavior.BLOCK
                )
            )
        )

        self.topic_path = self.publisher_client.topic_path(project_id, topic_id)

        self.executor = futures.ThreadPoolExecutor(
            max_workers=50,  # 50 threads para alto throughput
            thread_name_prefix="pubsub_publisher"
        )

        self.message_counter = 0
        self.last_print_time = time.time()
        self.lock = threading.Lock()


    def publish_message(self, message_data: dict, delivery_id: str):
        try:
            data = json.dumps(message_data).encode("utf-8")

            future = self.publisher_client.publish(
                self.topic_path,
                data=data,
                delivery_id=delivery_id
            )

            with self.lock:
                self.message_counter += 1
                current_time = time.time()
                if current_time - self.last_print_time >= 1.0:  # Log a cada segundo
                    logging.info(f"📤 Publishing rate: {self.message_counter}/sec")
                    self.message_counter = 0
                    self.last_print_time = current_time

            return future

        except Exception as e:
            logging.error(f"❌ Failed to publish message {delivery_id}: {e}")
            raise


    def publish_bulk_async(self, messages: list):
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

        # Aguarda conclusão
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

        logging.info(f"✅ Bulk publish complete: {successful:,}/{len(messages):,} "
                    f"messages in {duration:.2f}s ({rate:,.0f} msgs/sec)")


    def _publish_chunk(self, chunk: list):
        successful = 0
        for message_data in chunk:
            try:
                self.publish_message(message_data["data"], message_data["delivery_id"])
            except Exception as e:
                logging.error(f"Failed to publish in chunk: {e}")

        return successful

    def shutdown(self):
        """Clean shutdown"""
        self.executor.shutdown(wait=True)
        logging.info("Publisher shutdown complete")