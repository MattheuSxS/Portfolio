import re
import pytest
from datetime import datetime, timedelta
from modules.cloud_function.cf_products_inventory.src.utils.fk_vehicle import GeneratorDeliveryVehicle


@pytest.fixture
def generator():
    return GeneratorDeliveryVehicle(country='pt_BR')


def parse_date(date_str):
    # Supports 'YYYY-MM-DD' and ISO datetime strings
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        try:
            # Attempt ISO datetime parsing
            return datetime.fromisoformat(date_str).date()
        except ValueError:
            pytest.fail(f"Invalid date format: {date_str}")


def test_generate_board_motorcycle_format(generator):
    plate = generator.generate_board('motorcycle')
    assert re.match(r'^(JKL|MNO|PQR)\d{4}$', plate), f"Motorcycle plate has wrong format: {plate}"


def test_generate_board_non_motorcycle(generator):
    for vtype in ['van', 'truck']:
        plate = generator.generate_board(vtype)
        assert isinstance(plate, str) and len(plate) > 0


def test_generate_vehicle_structure_and_values(generator):
    vehicle = generator.generate_vehicle()

    # Basic structure
    expected_keys = {
        'vehicle_id', 'location', 'type', 'brand', 'model', 'year', 'license_plate',
        'capacity_kg', 'average_speed_km_h', 'fuel_efficiency_km_l', 'status',
        'manufacture_date', 'last_maintenance', 'next_maintenance',
        'tracker', 'insurance', 'driver', 'created_at', 'updated_at'
    }
    assert expected_keys.issubset(vehicle.keys())

    # Types and ranges
    assert vehicle['type'] in generator.VEHICLE_TYPES
    specs = generator.VEHICLE_TYPES[vehicle['type']]
    assert vehicle['brand'] in specs['brand']
    assert vehicle['model'] in specs['model']
    assert specs['capacity_kg'][0] <= vehicle['capacity_kg'] <= specs['capacity_kg'][1]
    assert isinstance(vehicle['average_speed_km_h'], float)
    assert isinstance(vehicle['fuel_efficiency_km_l'], float)

    # Status validity
    assert vehicle['status'] in generator.STATUS

    # Dates coherence
    manufacture_date = parse_date(vehicle['manufacture_date'])
    last_maintenance = parse_date(vehicle['last_maintenance'])
    next_maintenance = parse_date(vehicle['next_maintenance'])

    assert vehicle['year'] == manufacture_date.year
    assert manufacture_date <= last_maintenance, "Last maintenance should be after manufacture date"
    assert next_maintenance == last_maintenance + timedelta(days=180)

    # Insurance block
    insurance = vehicle['insurance']
    assert isinstance(insurance, dict)
    for key in ['insurer', 'policy_number', 'validity']:
        assert key in insurance and insurance[key]
    # validity should be a date string
    _ = parse_date(insurance['validity'])

    # Driver block (optional)
    driver = vehicle['driver']
    if driver is not None:
        assert isinstance(driver, dict)
        for key in ['name', 'cnh', 'cnh_validity']:
            assert key in driver and driver[key] is not None
        _ = parse_date(driver['cnh_validity'])

    # created_at present and parseable (date or datetime)
    _ = parse_date(vehicle['created_at'])

    # updated_at can be None initially
    assert vehicle['updated_at'] is None


def test_generate_fleet_size_and_item_validity(generator):
    qty = 5
    fleet = generator.generate_fleet(qty)
    assert isinstance(fleet, list)
    assert len(fleet) == qty
    for v in fleet:
        assert isinstance(v, dict)
        assert v['type'] in generator.VEHICLE_TYPES
        # Ensure license plate generated according to type rules at least minimally
        if v['type'] == 'motorcycle':
            assert re.match(r'^(JKL|MNO|PQR)\d{4}$', v['license_plate'])
        else:
            assert isinstance(v['license_plate'], str) and len(v['license_plate']) > 0