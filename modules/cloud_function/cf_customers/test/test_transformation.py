import pytest
import types
import logging
from modules.cloud_function.cf_customers.src.utils import transformation as tr


def test_hide_card_valid_with_hyphens():
    card = "1234-5678-9012-3456"
    masked = tr._hide_card(card)
    # First 3, last 3 visible, middle masked
    assert masked.startswith("123")
    assert masked.endswith("456")
    assert set(masked[3:-3]) == {"*"}
    # No separator characters remain
    assert masked.isdigit() is False
    assert "-" not in masked and " " not in masked


def test_hide_card_min_length_boundary():
    card = "1234567890123"  # 13 digits, minimum valid raw length
    masked = tr._hide_card(card)
    assert masked == "123" + "*" * 7 + "123"
    assert len(masked) == 13


def test_hide_card_max_length_boundary():
    card = "1234567890123456789"  # 19 digits, maximum valid raw length
    masked = tr._hide_card(card)
    assert masked == "123" + "*" * 13 + "789"
    assert len(masked) == 19


def test_hide_card_with_spaces():
    card = "1234 5678 9012 345"  # raw length 19 -> valid
    masked = tr._hide_card(card)
    assert masked.startswith("123")
    assert masked.endswith("345")
    assert set(masked[3:-3]) == {"*"}


def test_hide_card_empty_string_logs_and_defaults(caplog):
    caplog.set_level(logging.WARNING)
    assert tr._hide_card("") == "0000 0000 0000 0000"
    assert any("Invalid card number length" in rec.message for rec in caplog.records)


def test_hide_card_too_long_invalid(caplog):
    caplog.set_level(logging.WARNING)
    card = "1" * 20  # raw length 20 > 19
    assert tr._hide_card(card) == "0000 0000 0000 0000"
    assert any("Invalid card number length" in rec.message for rec in caplog.records)


def test_hide_cpf_empty_string_logs_and_defaults(caplog):
    caplog.set_level(logging.WARNING)
    assert tr._hide_cpf("") == "000.000.000-00"
    assert any("Invalid CPF format" in rec.message for rec in caplog.records)


def test_hide_cpf_letters_only_logs_and_defaults(caplog):
    caplog.set_level(logging.WARNING)
    assert tr._hide_cpf("abc.def.ghi-jk") == "000.000.000-00"
    assert any("Invalid CPF format" in rec.message for rec in caplog.records)


def test_hide_cpf_extra_digits_invalid(caplog):
    caplog.set_level(logging.WARNING)
    assert tr._hide_cpf("123456789012") == "000.000.000-00"
    assert any("Invalid CPF format" in rec.message for rec in caplog.records)


def test_hide_data_logs_success(caplog):
    caplog.set_level(logging.INFO)
    data = [
        {
            "customers": {"cpf": "12345678901"},
            "cards": {"card_number": "1234567890123"}
        }
    ]
    tr.hide_data(data)
    assert any("Sensitive data hidden successfully." in rec.message for rec in caplog.records)


def test_hide_data_multiple_items():
    data = [
        {
            "customers": {"cpf": "111.111.111-11"},
            "cards": {"card_number": "1234567890123"}
        },
        {
            "customers": {"cpf": "222.222.222-22"},
            "cards": {"card_number": "9876543210987"}
        },
    ]
    result = tr.hide_data(data)
    assert result[0]["customers"]["cpf"] == "111.***.***-11"
    assert result[1]["customers"]["cpf"] == "222.***.***-22"
    assert result[0]["cards"]["card_number"] == "123" + "*" * 7 + "123"
    assert result[1]["cards"]["card_number"] == "987" + "*" * 7 + "987"


def test_hide_data_missing_customers_key_raises():
    with pytest.raises(KeyError):
        tr.hide_data([{"cards": {"card_number": "1234567890123"}}])


def test_split_data_empty_list():
    res = tr.split_data([])
    assert res == {"tb_customers": [], "tb_cards": [], "tb_address": []}


def test_split_data_missing_key_raises():
    with pytest.raises(KeyError):
        tr.split_data([{"customers": {"id": 1}}])


def test_add_columns_multiple_items_share_timestamp(monkeypatch):
    class FixedDT:
        def strftime(self, fmt):
            return "2025-01-01 12:34:56"

    monkeypatch.setattr(tr, "datetime", types.SimpleNamespace(now=lambda: FixedDT()))

    data = [
        {
            "customers": {"associate_id": 1, "name": "A", "last_name": "B"},
            "cards": {"card_number": "1234567890123"},
            "address": {"street": "X"},
        },
        {
            "customers": {"associate_id": 2, "name": "C", "last_name": "D"},
            "cards": {"card_number": "9876543210987"},
            "address": {"street": "Y"},
        },
    ]
    result = tr.add_columns(data)

    assert len(result) == 2
    # All items share the same timestamp since it's computed once
    timestamps = {
        result[0]["customers"]["created_at"],
        result[1]["customers"]["created_at"],
    }
    assert timestamps == {"2025-01-01 12:34:56"}
    assert result[1]["cards"]["card_holder_name"] == "C D"
    assert result[1]["address"]["fk_associate_id"] == 2


def test_add_columns_missing_customer_field_raises():
    data = [
        {
            "customers": {"name": "Ada"},  # missing associate_id and last_name
            "cards": {},
            "address": {},
        }
    ]
    with pytest.raises(KeyError):
        tr.add_columns(data)