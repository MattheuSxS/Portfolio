import logging
from pathlib import Path
import pytest

import importlib.util

BASE_DIR = Path(__file__).parent.parent.parent / "src" / "cloud_function" / "cf_customers" / "utils"
MODULE_PATH = BASE_DIR / "transformation.py"

@pytest.fixture(scope="module")
def transformation_module():
    path = MODULE_PATH
    spec = importlib.util.spec_from_file_location("transformation", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_hide_cpf_valid_formats(transformation_module):
    assert transformation_module._hide_cpf("12345678901") == "123.***.***-01"
    assert transformation_module._hide_cpf("123.456.789-01") == "123.***.***-01"


def test_hide_cpf_invalid_logs_warning(transformation_module, caplog):
    with caplog.at_level(logging.WARNING):
        result = transformation_module._hide_cpf("123")
    assert result == "000.000.000-00"
    assert any("Invalid CPF format" in r.message for r in caplog.records)


def test_hide_card_valid_numeric(transformation_module):
    # 16 digits: first 3 + 10 asterisks + last 3
    assert transformation_module._hide_card("1234567890123456") == "123**********456"


def test_hide_card_valid_with_spaces(transformation_module):
    # Length including spaces is 19, accepted by current validation
    assert transformation_module._hide_card("1234 5678 9012 3456") == "123**********456"
    assert transformation_module._hide_card("1234-5678-9012-3456") == "123**********456"

def test_hide_card_invalid_lengths_and_logging(transformation_module, caplog):
    with caplog.at_level(logging.WARNING):
        assert transformation_module._hide_card("123456789012") == "0000 0000 0000 0000"  # too short
        assert transformation_module._hide_card("12345678901234567890") == "0000 0000 0000 0000"  # too long

    assert any("Invalid card number length" in r.message for r in caplog.records)


def test_hide_data_masks_in_place_and_logs(transformation_module, caplog):
    data = [
        {
            "customers": {"cpf": "12345678901"},
            "cards": {"card_number": "1234567890123456"},
        }
    ]
    with caplog.at_level(logging.INFO):
        returned = transformation_module.hide_data(data)
    # In-place
    assert returned is data
    # Masked values
    assert data[0]["customers"]["cpf"] == "123.***.***-01"
    assert data[0]["cards"]["card_number"] == "123**********456"
    # Log
    assert any("Sensitive data hidden successfully." in r.message for r in caplog.records)


def test_add_columns_adds_expected_fields(transformation_module, monkeypatch):
    class _FakeNow:
        def strftime(self, fmt):
            return "2025-01-02 03:04:05"

    class _FakeDateTime:
        @staticmethod
        def now():
            return _FakeNow()

    monkeypatch.setattr(transformation_module, "datetime", _FakeDateTime)

    data = [
        {
            "customers": {"associate_id": 42, "name": "Alice", "last_name": "Doe"},
            "cards": {"card_number": "1234567890123456"},
            "address": {"street": "Main"},
        }
    ]
    out = transformation_module.add_columns(data)
    assert out == data  # same structure, processed list

    item = out[0]
    # Customers
    assert item["customers"]["created_at"] == "2025-01-02 03:04:05"
    assert item["customers"]["updated_at"] is None
    # Cards
    assert item["cards"]["card_holder_name"] == "Alice Doe"
    assert item["cards"]["created_at"] == "2025-01-02 03:04:05"
    assert item["cards"]["updated_at"] is None
    assert item["cards"]["fk_associate_id"] == 42
    # Address
    assert item["address"]["created_at"] == "2025-01-02 03:04:05"
    assert item["address"]["updated_at"] is None
    assert item["address"]["fk_associate_id"] == 42


def test_split_data_separates_structures(transformation_module):
    data = [
        {
            "customers": {"id": 1},
            "cards": {"id": "c1"},
            "address": {"id": "a1"},
        },
        {
            "customers": {"id": 2},
            "cards": {"id": "c2"},
            "address": {"id": "a2"},
        },
    ]
    out = transformation_module.split_data(data)
    assert set(out.keys()) == {"tb_customers", "tb_cards", "tb_address"}
    assert out["tb_customers"] == [{"id": 1}, {"id": 2}]
    assert out["tb_cards"] == [{"id": "c1"}, {"id": "c2"}]
    assert out["tb_address"] == [{"id": "a1"}, {"id": "a2"}]