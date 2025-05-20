from faker import Faker

#TODO: Develop a better way to generate fake data
class Fakeproducts:
    """
    A class to generate fake product data using the Faker library.
    """

    def __init__(self, country: str = 'en_US') -> None:
        """
        Initializes the Fakeproducts class with a specified country for localization.

        Args:
            country (str): The country code for localization (default is 'pt_BR').
        """
        self.fake = Faker(country)
        self.fake.seed_instance(0)  # Seed the random number generator for reproducibility

    def generate_product(self) -> dict:
        """
        Generates fake product data.

        Returns:
            dict: A dictionary containing fake product data.
        """
        return {
            "product_id": self.fake.unique.uuid4(),
            "product_name": self.fake.unique.word(),
            "product_description": self.fake.sentence(),
            "price": round(self.fake.random.uniform(10.0, 1000.0), 2),
            "quantity": self.fake.random.randint(1, 100),
            "category": self.fake.word()
        }


if __name__ == "__main__":
    fake_product = Fakeproducts()
    print(fake_product.generate_product())