import types
import logging
from modules.cloud_function.cf_customers.src.utils import transformation as tr


def test_hide_cpf_valid_with_formatting():
    cpf = "123.456.789-01"
    assert tr._hide_cpf(cpf) == "123.***.***-01"


def test_hide_cpf_valid_digits_only():
    cpf = "12345678901"
    assert tr._hide_cpf(cpf) == "123.***.***-01"


def test_hide_cpf_invalid_length_logs_and_defaults(caplog):
    caplog.set_level(logging.WARNING)
    cpf = "12345678"  # invalid length
    assert tr._hide_cpf(cpf) == "000.000.000-00"
    assert any("Invalid CPF format" in rec.message for rec in caplog.records)


def test_hide_card_valid_with_hyphens(capsys):
    card = "1234-5678-9012-3456"
    masked = tr._hide_card(card)
    # Should print clean digits
    out = capsys.readouterr().out.strip()
    assert out == "1234567890123456"
    # First 3, last 3 visible, middle masked
    assert masked.startswith("123")
    assert masked.endswith("456")
    assert set(masked[3:-3]) == {"*"}


def test_hide_card_invalid_length_uses_raw_length_and_defaults(caplog):
    caplog.set_level(logging.WARNING)
    # 12 digits -> invalid, but with spaces it becomes > 13 characters; ensure invalid by passing short without separators
    card = "123456789012"  # 12 chars, invalid per code len(card_number) between 13 and 19
    assert tr._hide_card(card) == "0000 0000 0000 0000"
    assert any("Invalid card number length" in rec.message for rec in caplog.records)


def test_hide_data_masks_cpf_and_card():
    data = [
        {
            "customers": {"cpf": "987.654.321-00"},
            "cards": {"card_number": "1111 2222 3333 4444"}
        }
    ]
    result = tr.hide_data(data)
    assert result[0]["customers"]["cpf"] == "987.***.***-00"
    # First 3 and last 3 digits shown; spaces are stripped when masking
    masked_card = result[0]["cards"]["card_number"]
    assert masked_card.startswith("111")
    assert masked_card.endswith("444")
    assert set(masked_card[3:-3]) == {"*"}


class FixedDateTime(tr.datetime.__class__):
    @classmethod
    def now(cls):
        # Return a fixed datetime matching the format used
        class FixedDT:
            def strftime(self, fmt):
                return "2025-01-01 12:34:56"
        return FixedDT()


def test_add_columns_adds_expected_fields(monkeypatch):
    # Patch the datetime class imported in module to return fixed time
    monkeypatch.setattr(tr, "datetime", types.SimpleNamespace(now=FixedDateTime.now))

    data = [
        {
            "customers": {
                "associate_id": 42,
                "name": "Ada",
                "last_name": "Lovelace",
            },
            "cards": {
                "card_number": "1234-5678-9012-3456",
            },
            "address": {
                "street": "Main",
            },
        }
    ]
    result = tr.add_columns(data)

    item = result[0]
    assert item["customers"]["created_at"] == "2025-01-01 12:34:56"
    assert item["customers"]["updated_at"] is None

    assert item["cards"]["card_holder_name"] == "Ada Lovelace"
    assert item["cards"]["created_at"] == "2025-01-01 12:34:56"
    assert item["cards"]["updated_at"] is None
    assert item["cards"]["fk_associate_id"] == 42

    assert item["address"]["created_at"] == "2025-01-01 12:34:56"
    assert item["address"]["updated_at"] is None
    assert item["address"]["fk_associate_id"] == 42


def test_split_data_splits_correctly():
    data = [
        {
            "customers": {"id": 1, "cpf": "000.000.000-00"},
            "cards": {"id": 10, "card_number": "0000"},
            "address": {"id": 100, "street": "A"},
        },
        {
            "customers": {"id": 2, "cpf": "111.111.111-11"},
            "cards": {"id": 20, "card_number": "1111"},
            "address": {"id": 200, "street": "B"},
        },
    ]
    res = tr.split_data(data)
    assert list(res.keys()) == ["tb_customers", "tb_cards", "tb_address"]
    assert res["tb_customers"] == [data[0]["customers"], data[1]["customers"]]
    assert res["tb_cards"] == [data[0]["cards"], data[1]["cards"]]
    assert res["tb_address"] == [data[0]["address"], data[1]["address"]]