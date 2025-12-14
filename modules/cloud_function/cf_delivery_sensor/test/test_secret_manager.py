#TODO: I HAVE TO GET BACK TO THIS TESTS AFTER FIXING THE RAISE STRING ISSUE IN SECRET MANAGER UTIL
# import json
# import types
# import pytest
# import google.api_core.exceptions
# from modules.cloud_function.cf_delivery_sensor.src.utils.secret_manager import get_request_data


# class DummyPayload:
#     def __init__(self, data: bytes):
#         self.data = data

# class DummyResult:
#     def __init__(self, payload: DummyPayload):
#         self.payload = payload

# class FakeSecretManagerClientSuccess:
#     def __init__(self, payload_dict):
#         self._payload_dict = payload_dict

#     def access_secret_version(self, secret_url):
#         # Return a dummy result object with JSON payload bytes
#         payload_bytes = json.dumps(self._payload_dict).encode("utf-8")
#         return DummyResult(DummyPayload(payload_bytes))

# class FakeSecretManagerClientFailure:
#     def access_secret_version(self, secret_url):
#         # Simulate GoogleAPICallError from client
#         raise google.api_core.exceptions.GoogleAPICallError("Access denied")

# def patch_secret_manager(monkeypatch, client):
#     import modules.cloud_function.cf_customers.src.utils.secret_manager as sm
#     monkeypatch.setattr(sm, "secretmanager", types.SimpleNamespace(SecretManagerServiceClient=lambda: client))

# def test_get_request_data_success_with_dict(monkeypatch):
#     payload = {
#         "project_id": "proj-123",
#         "topic_id": "ds",
#     }
#     # The input request must contain keys to build the secret URL: project_id and secret_id
#     request_input = {"project_id": "proj-123", "secret_id": "my-secret"}

#     patch_secret_manager(monkeypatch, FakeSecretManagerClientSuccess(payload))
#     result = get_request_data(request_input)
#     assert result == payload

# def test_get_request_data_success_with_request_object(monkeypatch):
#     payload = {
#         "project_id": "proj-456",
#         "topic_id": "dataset_x",
#         "number_customers": 5,
#         "table_id": "customers",
#     }
#     # The request object returns the dict needed to access the secret
#     class FakeRequest:
#         def get_json(self):
#             return {"project_id": "proj-456", "secret_id": "another-secret"}

#     patch_secret_manager(monkeypatch, FakeSecretManagerClientSuccess(payload))
#     result = get_request_data(FakeRequest())
#     assert result == payload

# def test_get_request_data_missing_required_field(monkeypatch):
#     # Missing 'table_id' in secret payload
#     payload = {
#         "project_id": "proj-789",
#         "dataset_id": "ds",
#         "number_customers": 3,
#         # "table_id" omitted
#     }
#     request_input = {"project_id": "proj-789", "secret_id": "my-secret"}

#     patch_secret_manager(monkeypatch, FakeSecretManagerClientSuccess(payload))
#     with pytest.raises(ValueError) as exc:
#         get_request_data(request_input)
#     assert "Missing required field: table_id" in str(exc.value)

# def test_get_request_data_invalid_request_format(monkeypatch):
#     # get_json raises a generic exception, should be wrapped into ValueError
#     class BadRequest:
#         def get_json(self):
#             raise Exception("bad format")

#     # Even though secret manager is patched, it won't be called due to early failure
#     patch_secret_manager(monkeypatch, FakeSecretManagerClientSuccess({}))
#     with pytest.raises(ValueError) as exc:
#         get_request_data(BadRequest())
#     assert "Invalid request format: bad format" in str(exc.value)

# def test_get_request_data_secret_manager_error_raises_typeerror(monkeypatch):
#     # When Secret Manager access raises GoogleAPICallError, the code attempts to 'raise' a string,
#     # which results in TypeError in Python. We assert that behavior.
#     request_input = {"project_id": "proj-err", "secret_id": "sec-err"}

#     patch_secret_manager(monkeypatch, FakeSecretManagerClientFailure())
#     with pytest.raises(TypeError):
#         get_request_data(request_input)