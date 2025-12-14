import pytest
from datetime import datetime
from modules.cloud_function.cf_wh_sensor.src.utils.fk_sensor import FakeWhSensorData


STATE_ID_MAP = {
    "SP": "SP##e3e70682-c209-4cac-a29f-6fbed82c07cd",
    "SC": "SC##f728b4fa-4248-4e3a-8a5d-2f346baa9455",
    "DF": "DF##eb1167b3-67a9-4378-bc65-c1e582e2e662",
    "BA": "BA##23a7711a-8133-4876-b7eb-dcd9e87a1613",
    "AM": "AM##b4862b21-fb97-4435-8856-1712e8e5216a",
}


def test_temperature_keys_and_ranges():
    sensor = FakeWhSensorData()
    data = sensor._temperature("SP")

    assert set(data.keys()) == {"sensor_id", "time_stamp", "temperature", "humidity", "pressure"}
    assert data["sensor_id"] == STATE_ID_MAP["SP"]

    # time_stamp is ISO-8601 parseable
    parsed = datetime.fromisoformat(data["time_stamp"])
    assert isinstance(parsed, datetime)

    # value ranges
    assert 5.0 <= data["temperature"] <= 30.0
    assert 30.0 <= data["humidity"] <= 70.0
    assert 1000.0 <= data["pressure"] <= 1020.0


@pytest.mark.parametrize(
    "warehouse_id,suffix",
    [
        ("WH_Smithville_SP", "SP"),
        ("WH_Lambertstad_SC", "SC"),
        ("WH_Lake_Michelle_DF", "DF"),
        ("WH_New_Kristen_BA", "BA"),
        ("WH_North_Allison_AM", "AM"),
    ],
)
def test_warehouse_maps_suffix_to_sensor_id(warehouse_id, suffix):
    sensor = FakeWhSensorData()
    data = sensor.warehouse(warehouse_id)

    assert data["warehouse_id"] == warehouse_id
    assert data["sensor_id"] == STATE_ID_MAP[suffix]
    # Basic sanity on other fields
    assert 5.0 <= data["temperature"] <= 30.0
    assert 30.0 <= data["humidity"] <= 70.0
    assert 1000.0 <= data["pressure"] <= 1020.0
    datetime.fromisoformat(data["time_stamp"])  # no exception


def test_generate_sensor_data_yields_all_in_order(monkeypatch):

    sensor = FakeWhSensorData()
    items = list(sensor.generate_sensor_data())

    assert len(items) == 5
    expected_warehouses = [
        "WH_Smithville_SP",
        "WH_Lambertstad_SC",
        "WH_Lake_Michelle_DF",
        "WH_New_Kristen_BA",
        "WH_North_Allison_AM",
    ]
    assert [it["warehouse_id"] for it in items] == expected_warehouses

    # Validate mapping and value shapes for each yielded item
    for it in items:
        suffix = it["warehouse_id"][-2:]
        assert it["sensor_id"] == STATE_ID_MAP[suffix]
        assert 5.0 <= it["temperature"] <= 30.0
        assert 30.0 <= it["humidity"] <= 70.0
        assert 1000.0 <= it["pressure"] <= 1020.0
        datetime.fromisoformat(it["time_stamp"])  # no exception


def test_warehouse_with_invalid_suffix_raises_keyerror():
    sensor = FakeWhSensorData()
    with pytest.raises(KeyError):
        sensor.warehouse("WH_Invalid_XX")