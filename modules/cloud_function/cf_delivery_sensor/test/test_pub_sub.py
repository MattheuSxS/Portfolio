# import json
# import time
# import types
# import pytest
# import threading
# from concurrent import futures
# from modules.cloud_function.cf_delivery_sensor.src.utils.pub_sub import HighThroughputPublisher


# class FakeFuture(futures.Future):
#     def __init__(self, result="msg-123"):
#         super().__init__()
#         self.set_result(result)

# class FakePublisherClient:
#     def __init__(self, *args, **kwargs):
#         self.published = []
#         self.shutdown_called_with = None

#     def topic_path(self, project_id, topic_id):
#         return f"projects/{project_id}/topics/{topic_id}"

#     def publish(self, topic_path, data, delivery_id):
#         # Record the call and return a resolved Future
#         self.published.append(
#             {"topic_path": topic_path, "data": data, "delivery_id": delivery_id}
#         )
#         return FakeFuture(result="fake-message-id")

#     def shutdown(self, timeout=None):
#         self.shutdown_called_with = timeout


# @pytest.fixture(autouse=True)
# def patch_pubsub_client(monkeypatch):
#     # Patch google.cloud.pubsub_v1.PublisherClient to FakePublisherClient
#     import google.cloud.pubsub_v1 as pubsub_v1

#     monkeypatch.setattr(pubsub_v1, "PublisherClient", FakePublisherClient)

#     # Provide minimal types used in init
#     class BatchSettings:
#         def __init__(self, max_bytes=None, max_latency=None, max_messages=None):
#             self.max_bytes = max_bytes
#             self.max_latency = max_latency
#             self.max_messages = max_messages

#     class LimitExceededBehavior:
#         BLOCK = "BLOCK"

#     class PublishFlowControl:
#         def __init__(self, message_limit=None, byte_limit=None, limit_exceeded_behavior=None):
#             self.message_limit = message_limit
#             self.byte_limit = byte_limit
#             self.limit_exceeded_behavior = limit_exceeded_behavior

#     class PublisherOptions:
#         def __init__(self, enable_message_ordering=False, flow_control=None):
#             self.enable_message_ordering = enable_message_ordering
#             self.flow_control = flow_control

#     types_module = types.SimpleNamespace(
#         BatchSettings=BatchSettings,
#         LimitExceededBehavior=LimitExceededBehavior,
#         PublishFlowControl=PublishFlowControl,
#         PublisherOptions=PublisherOptions,
#     )
#     monkeypatch.setattr(pubsub_v1, "types", types_module)


# def test_publish_message_basic(monkeypatch):
#     publisher = HighThroughputPublisher("proj", "topic")

#     future = publisher.publish_message({"k": "v"}, "delivery-1")
#     assert isinstance(future, futures.Future)
#     assert future.result() == "fake-message-id"

#     fake_client: FakePublisherClient = publisher.publisher_client
#     assert len(fake_client.published) == 1

#     call = fake_client.published[0]
#     assert call["topic_path"] == publisher.topic_path
#     assert json.loads(call["data"].decode("utf-8")) == {"k": "v"}
#     assert call["delivery_id"] == "delivery-1"

#     # Counters updated
#     assert publisher.total_published == 1
#     # message_counter may be reset by logger tick; ensure it is >= 0
#     assert publisher.message_counter >= 0


# def test_get_metrics(monkeypatch):
#     publisher = HighThroughputPublisher("proj", "topic")

#     # Simulate some publishes
#     for i in range(3):
#         publisher.publish_message({"i": i}, f"id-{i}")

#     metrics = publisher.get_metrics()
#     assert set(metrics.keys()) == {"messages_last_sec", "total_published", "uptime_sec", "avg_rate"}
#     assert metrics["total_published"] == 3
#     assert metrics["uptime_sec"] >= 0
#     assert metrics["avg_rate"] >= 0


# def test_context_manager_shutdown_calls(monkeypatch):
#     with HighThroughputPublisher("proj", "topic") as publisher:
#         publisher.publish_message({"a": 1}, "d1")

#     # After context exit, publisher_client.shutdown called with timeout 15.0
#     fake_client: FakePublisherClient = publisher.publisher_client
#     assert fake_client.shutdown_called_with == 15.0


# def test_shutdown_executor(monkeypatch):
#     publisher = HighThroughputPublisher("proj", "topic")

#     # Submit a trivial task to ensure executor is running
#     fut = publisher.executor.submit(lambda: 42)
#     assert fut.result() == 42

#     # Call shutdown
#     publisher.shutdown()

#     # Submitting after shutdown should raise
#     with pytest.raises(RuntimeError):
#         publisher.executor.submit(lambda: 1)


# def test_publish_bulk_async_small_set(monkeypatch):
#     publisher = HighThroughputPublisher("proj", "topic")

#     messages = [{"data": {"n": i}, "delivery_id": f"id-{i}"} for i in range(20)]
#     publisher.publish_bulk_async(messages)

#     fake_client: FakePublisherClient = publisher.publisher_client
#     assert len(fake_client.published) == 20
#     assert publisher.total_published == 20


# def test_publish_bulk_async_handles_chunk_error(monkeypatch):
#     publisher = HighThroughputPublisher("proj", "topic")

#     # Make publish_message raise for certain item
#     original_publish = publisher.publish_message

#     def flaky_publish(data, delivery_id):
#         if delivery_id == "bad":
#             raise RuntimeError("boom")
#         return original_publish(data, delivery_id)

#     monkeypatch.setattr(publisher, "publish_message", flaky_publish)

#     messages = [
#         {"data": {"ok": 1}, "delivery_id": "good-1"},
#         {"data": {"bad": 1}, "delivery_id": "bad"},
#         {"data": {"ok": 2}, "delivery_id": "good-2"},
#     ]

#     publisher.publish_bulk_async(messages)

#     fake_client: FakePublisherClient = publisher.publisher_client
#     # Only two successful publishes
#     assert len(fake_client.published) == 2
#     assert publisher.total_published == 2


# def test_publish_bulk_async_timeout(monkeypatch):
#     publisher = HighThroughputPublisher("proj", "topic")

#     # Replace executor with one that returns futures that never complete to provoke timeout
#     class HangingExecutor:
#         def __init__(self):
#             self.shutdown_called = False

#         def submit(self, fn, *args, **kwargs):
#             # Return a future that never completes
#             return futures.Future()

#         def shutdown(self, wait=True):
#             self.shutdown_called = True

#     hanging = HangingExecutor()
#     monkeypatch.setattr(publisher, "executor", hanging)

#     # Use enough messages to create at least one chunk (any size works; function uses 500 chunk size)
#     messages = [{"data": {"i": i}, "delivery_id": f"id-{i}"} for i in range(10)]
#     # This should not raise due to internal timeout handling
#     publisher.publish_bulk_async(messages)

#     # No successful publishes recorded
#     fake_client: FakePublisherClient = publisher.publisher_client
#     assert len(fake_client.published) == 0
#     assert publisher.total_published == 0


# def test_thread_safety_on_counters(monkeypatch):
#     publisher = HighThroughputPublisher("proj", "topic")

#     def worker(idx):
#         publisher.publish_message({"i": idx}, f"id-{idx}")

#     threads = [threading.Thread(target=worker, args=(i,)) for i in range(50)]
#     for t in threads:
#         t.start()
#     for t in threads:
#         t.join()

#     assert publisher.total_published == 50
#     fake_client: FakePublisherClient = publisher.publisher_client
#     assert len(fake_client.published) == 50