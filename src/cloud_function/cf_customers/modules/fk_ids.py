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
        """
            Generate a dictionary representing a customer with fake data.

            Returns:
                dict[str, dict]: A dictionary containing customer information, including:
                    - associate_id (str): Unique identifier for the associate.
                    - name (str): Customer's first name.
                    - last_name (str): Customer's last name(s).
                    - cpf (str): Unique CPF number.
                    - email (str): Customer's email address.
                    - phone (str): Unique phone number.
                    - birth_date (str): Customer's birth date as a string (between 1925-01-01 and 18 years ago).
                    - created_at (None): Placeholder for creation timestamp.
                    - updated_at (None): Placeholder for update timestamp.
                    - deleted_at (None): Placeholder for deletion timestamp.
        """

        full_name = f"{self.fake.first_name()} {self.fake.last_name()}"
        fk_birthday = (date.today() - timedelta(days=6570)) # 18 years ago
        return \
            {
                "associate_id": f"ID##{self.fake.unique.uuid4()}",
                "name":         full_name.split()[0],
                "last_name":    " ".join(full_name.split()[1:4]),
                "cpf":          self.fake.unique.cpf(),
                "email":        f"{full_name.replace(' ', '.')}@{self.fake.domain_name()}".lower(),
                "phone":        self.fake.unique.phone_number(),
                "birth_date":   str(self.fake.date_between_dates(date_start=date(1925, 1, 1), date_end=fk_birthday)),
                "created_at":   None,
                "updated_at":   None,
                "deleted_at":   None
            }


    def dict_card(self) -> dict[str, dict]:
        """
            Generates a dictionary representing a card with randomized and placeholder data.

            Returns:
                dict[str, dict]: A dictionary containing card information with the following keys:
                    - "card_id" (str): A unique identifier for the card.
                    - "card_holder_name" (str or None): The name of the card holder (currently None).
                    - "card_type" (str): The type of card, either 'Credit' or 'Debit'.
                    - "card_number" (str): A randomly generated card number matching the selected card flag.
                    - "card_expiration_date" (str): The expiration date of the card in 'MM/YY' format.
                    - "card_code_security" (str): The card's security code (CVV/CVC).
                    - "card_flag" (str): The card network, e.g., 'visa', 'mastercard', or 'amex'.
                    - "Enabled" (bool): Indicates if the card is enabled (always True).
                    - "created_at" (None): Placeholder for the creation timestamp.
                    - "updated_at" (None): Placeholder for the update timestamp.
                    - "deleted_at" (None): Placeholder for the deletion timestamp.
                    - "fk_associate_id" (None): Placeholder for a foreign key to an associate.
        """
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
    for _ in range(10):
        fake_data = FakeDataPerson()
        print("------------ Data Customer ------------")
        for key, value in fake_data.dict_customers().items():
            print(f"{key}: {value}")
        print("------------ Data Card ------------")
        # for key, value in fake_data.dict_card().items():
        #     print(f"{key}: {value}")
        print("-" * 40)
        print()
