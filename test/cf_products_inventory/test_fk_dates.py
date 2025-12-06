# ************************************************************************************************************************************ #
#                                    Adiciona o diretório raiz ao sys.path para permitir imports relativos                             #
# ************************************************************************************************************************************ #
import sys
from pathlib import Path


root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

# ************************************************************************************************************************************ #
#                                TEST TO ~~> src/cloud_function/cf_products_inventory/utils/fk_dates.py                                #
# ************************************************************************************************************************************ #
import re
import pytest
from datetime import datetime, timedelta
from src.cloud_function.cf_products_inventory.utils.fk_dates import GeneratorDate


def test_generate_date_returns_date_in_expected_format_and_range():
    gen = GeneratorDate()
    start = datetime(2020, 1, 1, 0, 0, 0)
    end = datetime(2020, 12, 31, 23, 59, 59)

    result = gen.generate_date(start_date=start, end_date=end, option='date')

    # Validate format YYYY-MM-DD
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", result), "Date format should be YYYY-MM-DD"

    # Validate within range
    dt = datetime.strptime(result, "%Y-%m-%d")
    assert start.date() <= dt.date() <= end.date()


def test_generate_date_returns_datetime_in_expected_format_and_range():
    gen = GeneratorDate()
    start = datetime(2021, 6, 1, 12, 0, 0)
    end = datetime(2021, 6, 30, 18, 30, 0)

    result = gen.generate_date(start_date=start, end_date=end, option='datetime')

    # Validate format YYYY-MM-DD HH:MM:SS
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", result), "Datetime format should be YYYY-MM-DD HH:MM:SS"

    # Validate within range
    dt = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
    assert start <= dt <= end


def test_generate_date_datetime_v1_within_last_90_days():
    gen = GeneratorDate()

    result = gen.generate_date(option='datetime_v1')

    # Validate format
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", result)

    dt = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    lower_bound = now - timedelta(days=90)
    assert lower_bound <= dt <= now


def test_generate_date_invalid_option_raises_value_error():
    gen = GeneratorDate()
    with pytest.raises(ValueError) as excinfo:
        gen.generate_date(option='invalid')

    # Check message matches the implementation
    assert str(excinfo.value) == "Option must be either 'date', 'datetime' or 'datetime_v1'."