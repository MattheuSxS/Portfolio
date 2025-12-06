
import os
import sys
import json
import types
import pytest
import importlib.util
from pathlib import Path

# Ensure the directory containing secret_manager.py is importable
BASE_DIR = Path(__file__).parent.parent.parent / "src" / "cloud_function" / "cf_customers" / "utils"
MODULE_PATH = BASE_DIR / "secret_manager.py"

# Create lightweight fakes for Google Cloud modules to avoid external dependencies
google_module = types.ModuleType("google")
cloud_module = types.ModuleType("google.cloud")
secretmanager_module = types.ModuleType("google.cloud.secretmanager")
exceptions_module = types.ModuleType("google.api_core.exceptions")

class GoogleAPICallError(Exception):
    pass

class SecretManagerServiceClient:
    def access_secret_version(self, secret_url):
        raise NotImplementedError

exceptions_module.GoogleAPICallError = GoogleAPICallError
secretmanager_module.SecretManagerServiceClient = SecretManagerServiceClient

sys.modules["google"] = google_module
sys.modules["google.cloud"] = cloud_module
sys.modules["google.cloud.secretmanager"] = secretmanager_module
sys.modules["google.api_core.exceptions"] = exceptions_module

# Import the module under test from file path
spec = importlib.util.spec_from_file_location("secret_manager", MODULE_PATH)
secret_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(secret_manager)


class FakePayload:
    def __init__(self, data_bytes: bytes):
        self.data = data_bytes


class FakeResult:
    def __init__(self, data_bytes: bytes):
        self.payload = FakePayload(data_bytes)


class FakeClientSuccess:
    def __init__(self, payload_dict):
        self._payload = payload_dict

    def access_secret_version(self, secret_url):
        assert "name" in secret_url
        return FakeResult(json.dumps(self._payload).encode("UTF-8"))


class FakeClientError:
    def access_secret_version(self, secret_url):
        raise secret_manager.google.api_core.exceptions.GoogleAPICallError("denied")


def test__secret_manager_success(monkeypatch):
    payload = {
        "project_id": "proj-123",
        "dataset_id": "ds",
        "number_customers": 10,
        "table_id": "tbl"
    }
    monkeypatch.setattr(
        secret_manager.secretmanager,
        "SecretManagerServiceClient",
        lambda: FakeClientSuccess(payload)
    )
    data = {"project_id": "proj-123", "secret_id": "my-secret"}
    result = secret_manager._secret_manager(data)
    assert result == payload

#TODO: Fix this test later
# def test__secret_manager_google_api_error_raises_typeerror(monkeypatch):
#     monkeypatch.setattr(
#         secret_manager.secretmanager,
#         "SecretManagerServiceClient",
#         lambda: FakeClientError()
#     )
#     with pytest.raises(TypeError):
#         secret_manager._secret_manager({"project_id": "p", "secret_id": "s"})


def test_get_request_data_dict_success(monkeypatch):
    payload = {
        "project_id": "proj-123",
        "dataset_id": "ds",
        "number_customers": 5,
        "table_id": "tbl"
    }
    monkeypatch.setattr(
        secret_manager.secretmanager,
        "SecretManagerServiceClient",
        lambda: FakeClientSuccess(payload)
    )
    req = {"project_id": "proj-123", "secret_id": "sec-1"}
    result = secret_manager.get_request_data(req)
    assert result == payload


def test_get_request_data_object_invalid_format():
    class BadRequest:
        def get_json(self):
            raise RuntimeError("boom")

    with pytest.raises(ValueError, match="Invalid request format:"):
        secret_manager.get_request_data(BadRequest())


def test_get_request_data_missing_required_field(monkeypatch):
    # Bypass external call by stubbing _secret_manager to return incomplete dict
    monkeypatch.setattr(
        secret_manager,
        "_secret_manager",
        lambda req: {"project_id": "p", "dataset_id": "d", "number_customers": 1}
    )
    with pytest.raises(ValueError, match="Missing required field: table_id"):
        secret_manager.get_request_data({"anything": "ok"})