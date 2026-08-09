import re
import pytest
from modules.cloud_function.cf_products_inventory.src.utils.fk_products import FkCommerce


@pytest.fixture
def fk():
    return FkCommerce(country="en_US")


def test_generate_product_name_valid_category(fk: FkCommerce):
    name = fk.generate_product_name("Electronics")
    # Format: "<Adj> <Noun> <Number>"
    parts = name.split(" ")
    assert len(parts) >= 3
    assert parts[-1].isdigit()
    assert int(parts[-1]) >= 1 and int(parts[-1]) <= 1000


def test_generate_product_name_invalid_category_raises_keyerror(fk: FkCommerce):
    with pytest.raises(KeyError):
        fk.generate_product_name("InvalidCategory")


def test_generate_product_description_formatting(fk: FkCommerce):
    product = {
        "name": fk.generate_product_name("Clothing"),
        "category": "Clothing",
    }
    desc = fk.generate_product_description(product)
    assert isinstance(desc, str)
    assert desc[0].isupper()
    assert desc.endswith(".")


def test_generate_products_basic_structure(fk: FkCommerce):
    num = 10
    products = fk.generate_products(num)
    assert isinstance(products, list)
    assert len(products) == num

    required_fields = {
        "product_id", "name", "category", "brand", "price", "weight", "dimensions",
        "condition", "in_stock", "sku", "manufacturer", "description", "created_at",
        "updated_at", "deleted_at"
    }

    for p in products:
        # Field presence
        assert required_fields.issubset(p.keys())

        # Types and value checks
        assert isinstance(p["product_id"], str)
        assert p["product_id"].startswith("PD##")
        assert isinstance(p["name"], str)
        assert isinstance(p["category"], str)
        assert isinstance(p["brand"], str)
        assert isinstance(p["price"], float)
        assert 1.0 <= p["price"] <= 999.0
        assert isinstance(p["weight"], float)
        assert 0.1 <= p["weight"] <= 20.0

        # dimensions
        dims = p["dimensions"]
        assert set(dims.keys()) == {"length", "width", "height"}
        assert all(isinstance(dims[k], float) for k in dims)

        # condition
        assert p["condition"] in [
            "New", "Used - Like New", "Used - Good", "Used - Fair", "Refurbished"
        ]

        # stock
        assert isinstance(p["in_stock"], int)
        assert 0 <= p["in_stock"] <= 1000

        # SKU pattern ???-####-???
        assert isinstance(p["sku"], str)
        # assert re.fullmatch(r"[A-Z0-9]{3}-\d{4}-[A-Z0-9]{3}", p["sku"]) is not None

        # manufacturer
        assert isinstance(p["manufacturer"], str)

        # description
        assert isinstance(p["description"], str)
        assert p["description"].endswith(".")
        assert p["description"][0].isupper()

        # timestamps existence
        assert p["created_at"] is not None
        assert p["updated_at"] is None
        assert p["deleted_at"] is None


def test_generate_inventory_structure_and_count(fk: FkCommerce):
    products = fk.generate_products(3)
    inventory = fk.generate_inventory(products)

    # There are 5 locations declared; inventory rows should be products * 5
    assert len(inventory) == len(products) * 5

    required_fields = {
        "inventory_id", "product_id", "location", "region", "coordinates",
        "quantity", "last_restock", "aisle", "shelf", "created_at"
    }

    for item in inventory:
        assert required_fields.issubset(item.keys())

        assert isinstance(item["inventory_id"], str)
        assert item["inventory_id"].startswith("IN##")

        # product_id should match one of generated products
        assert item["product_id"] in {p["product_id"] for p in products}

        # location and region
        assert isinstance(item["location"], str)
        assert isinstance(item["region"], str)

        # coordinates
        coords = item["coordinates"]
        assert isinstance(coords, dict)
        assert set(coords.keys()) == {"latitude", "longitude"}
        assert isinstance(coords["latitude"], (float, int))
        assert isinstance(coords["longitude"], (float, int))

        # quantity
        assert isinstance(item["quantity"], int)
        assert 0 <= item["quantity"] <= 500

        # aisle pattern ?##
        assert isinstance(item["aisle"], str)
        re.fullmatch(r'[A-Za-z]\d{2}', item["aisle"]) is not None
        assert len(item["aisle"]) == 3, f"Aisle '{item['aisle']}' Doen't have 3 characters"
        assert item["aisle"][1:].isdigit(), f"last 2 '{item['aisle']}' are not digits"

        # shelf single letter A-J
        assert item["shelf"] in list("ABCDEFGHIJ")

        # created_at string of datetime
        assert isinstance(item["created_at"], str)
        assert len(item["created_at"]) > 0


def test_generate_complete_dataset(fk: FkCommerce):
    qtd_products = 4
    qtd_vehicles = 7
    dataset = fk.generate_complete_dataset(qtd_products, qtd_vehicles)

    assert set(dataset.keys()) == {"tb_products", "tb_inventory", "tb_vehicles"}

    # Products count
    assert isinstance(dataset["tb_products"], list)
    assert len(dataset["tb_products"]) == qtd_products

    # Inventory count should be products * 5 locations
    assert isinstance(dataset["tb_inventory"], list)
    assert len(dataset["tb_inventory"]) == qtd_products * 5

    # Vehicles count
    assert isinstance(dataset["tb_vehicles"], list)
    assert len(dataset["tb_vehicles"]) == qtd_vehicles