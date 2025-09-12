from faker import Faker
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta


class GeneratorDate:
    """
        GeneratorDate is a utility class for generating random dates and datetimes using the Faker library.

        Attributes:
            fake (Faker): An instance of the Faker class initialized with the specified locale.

        Methods:
            __init__(country: str = 'en_US'):
                Initializes the GeneratorDate with a Faker instance for the given country/locale.

            generate_date(start_date=None, end_date=None, option='date'):
                Generates a random date or datetime string within the specified range and format.
    """

    def __init__(self, country: str = 'en_US'):
        self.fake = Faker(country)


    def generate_date(self, start_date=None, end_date=None, option='date'):
        """
            Generates a random date or datetime string within the specified range.

            Args:
                start_date (datetime, optional): The start of the date range. Defaults to None.
                end_date (datetime, optional): The end of the date range. Defaults to None.
                option (str, optional): The format of the output. Must be one of 'date', 'datetime', or 'datetime_v1'.
                    - 'date': Returns a date string in 'YYYY-MM-DD' format.
                    - 'datetime': Returns a datetime string in 'YYYY-MM-DD HH:MM:SS' format.
                    - 'datetime_v1': Returns a datetime string in 'YYYY-MM-DD HH:MM:SS' format,
                    with the date randomly chosen from the last 90 days.

            Returns:
                str: The generated date or datetime string in the specified format.

            Raises:
                ValueError: If the option is not one of 'date', 'datetime', or 'datetime_v1'.
        """
        if option not in ['date', 'datetime', 'datetime_v1']:
            raise ValueError("Option must be either 'date' or 'datetime'.")

        match option:
            case 'date':
                return self.fake.date_time_between(
                    start_date=start_date,
                    end_date=end_date).strftime('%Y-%m-%d')

            case 'datetime':
                return self.fake.date_time_between(
                    start_date=start_date,
                    end_date=end_date).strftime('%Y-%m-%d %H:%M:%S')

            case 'datetime_v1':
                return self.fake.date_time_between_dates(
                    datetime_start=(datetime.now(ZoneInfo('Europe/Dublin')) - timedelta(days=90)),
                    datetime_end=datetime.now(ZoneInfo('Europe/Dublin'))).strftime('%Y-%m-%d %H:%M:%S')