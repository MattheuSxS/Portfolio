import re
import math
import pytest
from modules.cloud_function.cf_customers.src.utils.fk_address import FakeDataAddress


@pytest.fixture
def fk():
    return FakeDataAddress()


def test_get_random_address_structure_and_types(fk):
    addr = fk.get_random_address()

    required_keys = {
        'address_id', 'address', 'neighborhood', 'city', 'state', 'postal_code',
        'region', 'latitude', 'longitude', 'created_at', 'updated_at',
        'deleted_at', 'fk_associate_id'
    }
    assert required_keys.issubset(addr.keys())

    assert isinstance(addr['address_id'], str) and addr['address_id'].startswith("ADDR##")
    assert isinstance(addr['address'], str) and len(addr['address']) > 0
    assert isinstance(addr['neighborhood'], str) and len(addr['neighborhood']) > 0
    assert isinstance(addr['city'], str) and len(addr['city']) > 0
    assert isinstance(addr['state'], str) and addr['state'] in fk.capitais_coords
    assert isinstance(addr['postal_code'], str) and len(addr['postal_code']) > 0
    assert isinstance(addr['region'], str) and len(addr['region']) > 0

    assert re.fullmatch(r"-?\d+\.\d{6}", addr['latitude']) is not None
    assert re.fullmatch(r"-?\d+\.\d{6}", addr['longitude']) is not None

    assert addr['created_at'] is None
    assert addr['updated_at'] is None
    assert addr['deleted_at'] is None
    assert addr['fk_associate_id'] is None


def test_lat_lon_within_expected_range_near_capital(fk):
    for _ in range(20):
        addr = fk.get_random_address()
        uf = addr['state']
        info = fk.capitais_coords[uf]

        lat = float(addr['latitude'])
        lon = float(addr['longitude'])

        assert math.isfinite(lat) and math.isfinite(lon)
        assert abs(lat - info['lat']) <= 0.051
        assert abs(lon - info['lon']) <= 0.051

        assert addr['city'] == info['city']
        assert addr['region'] == info['region']


def test_multiple_addresses_have_unique_ids(fk):
    ids = set()
    for _ in range(50):
        addr = fk.get_random_address()
        assert addr['address_id'].startswith("ADDR##")
        ids.add(addr['address_id'])
    assert len(ids) == 50