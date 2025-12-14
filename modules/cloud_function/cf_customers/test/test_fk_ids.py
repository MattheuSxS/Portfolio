import re
import pytest
from datetime import date, timedelta, datetime
from modules.cloud_function.cf_customers.src.utils.fk_ids import FakeDataPerson


@pytest.fixture
def generator():
    return FakeDataPerson()


def test_dict_customers_structure_and_types(generator):
    data = generator.dict_customers()

    required_keys = {
        "associate_id",
        "name",
        "last_name",
        "gender",
        "cpf",
        "email",
        "phone",
        "birth_date",
        "created_at",
        "updated_at",
        "deleted_at",
    }
    assert required_keys.issubset(data.keys())

    assert isinstance(data["associate_id"], str)
    assert data["associate_id"].startswith("ID##")

    assert isinstance(data["name"], str) and data["name"]
    assert isinstance(data["last_name"], str)

    assert data["gender"] in {"M", "F", "O"}

    # CPF format (pt_BR): 000.000.000-00
    assert isinstance(data["cpf"], str)
    assert re.fullmatch(r"\d{3}\.\d{3}\.\d{3}-\d{2}", data["cpf"]) is not None

    # Basic email format check
    assert isinstance(data["email"], str)
    assert re.fullmatch(r"[^@]+@[^@]+\.[^@]+", data["email"]) is not None
    assert data["email"] == f"{data['name'].lower()}.{data['last_name'].lower().replace(' ', '.')}" + "@" + data["email"].split("@")[1]

    assert isinstance(data["phone"], str)

    # Birth date within range [1925-01-01, today - 18 years]
    assert isinstance(data["birth_date"], str)
    bd = datetime.strptime(data["birth_date"], "%Y-%m-%d").date()
    min_bd = date(1925, 1, 1)
    max_bd = date.today() - timedelta(days=6570)  # 18 years
    assert min_bd <= bd <= max_bd

    # Timestamps are placeholders (None)
    assert data["created_at"] is None
    assert data["updated_at"] is None
    assert data["deleted_at"] is None


def test_dict_customers_ids_are_unique_across_multiple_calls():
    gen = FakeDataPerson()
    ids = {gen.dict_customers()["associate_id"] for _ in range(50)}
    # Expect all unique due to Faker.unique usage
    assert len(ids) == 50


def test_dict_card_structure_and_values(generator):
    card = generator.dict_card()

    required_keys = {
        "card_id",
        "card_holder_name",
        "card_type",
        "card_number",
        "card_expiration_date",
        "card_code_security",
        "card_flag",
        "Enabled",
        "created_at",
        "updated_at",
        "deleted_at",
        "fk_associate_id",
    }
    assert required_keys.issubset(card.keys())

    assert isinstance(card["card_id"], str)
    assert card["card_id"].startswith("CARD##")

    assert card["card_holder_name"] is None

    assert card["card_type"] in {"Credit", "Debit"}

    assert isinstance(card["card_number"], str) and len(card["card_number"]) >= 12

    # Expiration format MM/YY and plausible month
    assert isinstance(card["card_expiration_date"], str)
    assert re.fullmatch(r"(0[1-9]|1[0-2])/\d{2}", card["card_expiration_date"]) is not None

    assert isinstance(card["card_code_security"], str)
    assert re.fullmatch(r"\d{3,4}", card["card_code_security"]) is not None

    assert card["card_flag"] in {"visa", "mastercard", "amex"}

    assert isinstance(card["Enabled"], bool)

    assert card["created_at"] is None
    assert card["updated_at"] is None
    assert card["deleted_at"] is None
    assert card["fk_associate_id"] is None


def test_dict_card_ids_are_unique_across_multiple_calls():
    gen = FakeDataPerson()
    ids = {gen.dict_card()["card_id"] for _ in range(50)}
    assert len(ids) == 50


def test_email_derived_from_name_and_domain(generator):
    data = generator.dict_customers()
    # Email should contain domain and first+last joined by dot
    # We can't guarantee exact names due to Faker randomness, but ensure pattern:
    local_part, domain = data["email"].split("@", 1)
    assert "." in local_part
    assert re.fullmatch(r"[a-z0-9._-]+", local_part) is not None
    assert re.fullmatch(r"[a-z0-9.-]+\.[a-z]{2,}$", domain) is not None