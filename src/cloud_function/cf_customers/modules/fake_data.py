import logging
from faker import Faker


logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)

class FakeData:

    def __init__(self, country:str = 'pt_BR', num_records:int = 5) -> None:
        self.fake           = Faker(country)
        self.num_records    = num_records
        self.fake.seed_instance(0)


    def dict_customers(self) -> dict[str, dict]:
        return \
            dict(
                associate_id  = [self.fake.unique.uuid4() for _ in range(self.num_records)],
                name          = [self.fake.first_name() for _ in range(self.num_records)],
                last_name     = [self.fake.last_name() for _ in range(self.num_records)],
                age           = [self.fake.random_int(min=18, max=100) for _ in range(self.num_records)],
            )

    def dict_card(self) -> dict[str, dict]:

        return \
            dict(
                card_id                 = f"card_{self.fake.unique.uuid4()}",
                card_number             = self.fake.unique.random_int(
                                            min=1000_0000_0000_0000,
                                            max=9999_9999_9999_9999),
                card_expiration_date    = self.fake.date_between_dates(
                                            date_start='now',
                                            date_end='+3y'),
                card_code_security      = self.fake.unique.random_int(min=100, max=999)
            )

    #TODO (developer)
    # def get_address(self) -> dict[str, dict]:
    #     from mimesis import Address
    #     from mimesis.locales import Locale
    #     import random

    #     addr = Address(Locale.PT_BR)

    #     return \
    #         {
    #             "rua": addr.street_name(),
    #             "numero": addr.street_number(),
    #             "cidade": addr.city(),
    #             "estado": addr.state(abbr=True),
    #             "cep": addr.postal_code(),
    #             "geolocalizacao": (addr.latitude(), addr.longitude())
    #         }



if __name__ == "__main__":
    test = FakeData()
    print(test.dict_card())
