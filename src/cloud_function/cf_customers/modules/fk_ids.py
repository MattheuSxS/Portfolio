from faker import Faker
from random import choice
from datetime import date, timedelta


class FakeDataPerson:
    """
    FakeDataPerson generates fake customer and card data for testing purposes.

    Attributes:
        fake (Faker): An instance of the Faker class initialized with the specified locale.

    Args:
        country (str, optional): Locale code for generating fake data. Defaults to 'pt_BR'.

    Methods:
        dict_customers() -> dict[str, dict]:
            Generates a dictionary containing fake customer data, including associate ID, name, last name, CPF, email, phone, and birthday.

        dict_card() -> dict[str, dict]:
            Generates a dictionary containing fake card data, including card ID, card number, expiration date, security code, and card flag.
    """

    def __init__(self, country:str = 'pt_BR') -> None:
        self.fake = Faker(country)
        # self.fake.seed_instance(0)

    def dict_customers(self) -> dict[str, dict]:

        full_name = f"{self.fake.first_name()} {self.fake.last_name()}"
        fk_birthday = (date.today() - timedelta(days=6570)) # 18 years ago
        return \
            {
                "associate_id": f"ID##{self.fake.unique.uuid4()}",
                "name":         full_name.split()[0],
                "last_name":    full_name.split()[1],
                "cpf":          self.fake.unique.cpf(),
                "email":        f"{full_name.replace(' ', '.')}@{self.fake.domain_name()}",
                "phone":        self.fake.unique.phone_number(),
                "birth_date":   str(self.fake.date_between_dates(date_start=date(1925, 1, 1), date_end=fk_birthday)),
                "created_at":   None,
                "updated_at":   None,
                "deleted_at":   None
            }


    def dict_card(self) -> dict[str, dict]:
        card_flags = choice(['visa', 'mastercard', 'amex'])
        return \
           {
                "card_id":              f"CARD##{self.fake.unique.uuid4()}",
                "card_holder_name":     None,
                "card_type":            choice(['Credit', 'Debit']),
                "card_number":          self.fake.credit_card_number(card_type=card_flags),
                "card_expiration_date": self.fake.credit_card_expire(start='now', end='+10y', date_format='%m/%y'),
                "card_code_security":   self.fake.credit_card_security_code(card_type=card_flags),
                "card_flag":            card_flags,
                "Enabled":              True,
                "created_at":           None,
                "updated_at":           None,
                "deleted_at":           None,
                "fk_associate_id":      None

           }


if __name__ == "__main__":
    print("Generate 5 fake data for customers")
    for _ in range(5):
        fake_data = FakeDataPerson()
        print("------------ Data Customer ------------")
        for key, value in fake_data.dict_customers().items():
            print(f"{key}: {value}")
        print("------------ Data Card ------------")
        for key, value in fake_data.dict_card().items():
            print(f"{key}: {value}")
        print("-" * 40)
        print()
