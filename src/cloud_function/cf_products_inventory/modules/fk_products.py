import json
import random
from faker import Faker
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from faker.providers import DynamicProvider


class FkCommerce:
    def __init__(self, country: str = 'en_US'):
        self.fake = Faker(country)
        self.fake.seed_instance(0)
        self.fake.add_provider(
            DynamicProvider(
                provider_name="product_categories",
                elements=["Electronics", "Clothing", "Groceries", "Furniture",
                         "Toys", "Beauty", "Sports", "Office Supplies"])
        )
        self.product_conditions = ["New", "Used - Like New", "Used - Good", "Used - Fair", "Refurbished"]
        self._init_description_templates()


    def _init_description_templates(self):
        """
            Initializes the description templates for various product categories.

            This method sets up a dictionary `self.description_templates` containing
            template strings and associated placeholder lists for different product
            categories such as "Electronics", "Clothing", and "Groceries". Each category
            includes:
                - 'templates': List of template strings with placeholders.
                - Other keys: Lists of possible values for placeholders (e.g., 'features', 'benefits', etc.).

            Also initializes `self.default_template`, a generic template and placeholder
            set to be used when a specific category is not found.

            The templates and placeholder values are intended for generating dynamic,
            category-specific product descriptions.
        """
        self.description_templates = {
            "Electronics": {
                "templates": [
                    "The {name} features {features}. {benefits} With its {specs}, it's perfect for {use_cases}.",
                    "Experience {benefits} with the {name}. This {category} offers {features} and {specs} for {use_cases}."
                ],
                "features": [
                    "advanced technology", "innovative design", "cutting-edge components",
                    "high-performance hardware", "sleek modern styling", "energy-efficient operation"
                ],
                "benefits": [
                    "delivers exceptional performance", "provides reliable operation",
                    "offers intuitive controls", "ensures long-lasting durability",
                    "guarantees user satisfaction"
                ],
                "specs": [
                    "powerful processor", "high-resolution display", "extended battery life",
                    "advanced cooling system", "premium build quality", "fast charging capability"
                ],
                "use_cases": [
                    "professional work and entertainment", "both home and office use",
                    "demanding applications", "everyday computing needs",
                    "mobile productivity and gaming"
                ]
            },
            "Clothing": {
                "templates": [
                    "This {name} is made from {material} for {comfort}. The {design} design offers {features}.",
                    "Designed for {comfort}, the {name} features {material} construction with {design} details."
                ],
                "material": [
                    "premium cotton", "breathable linen", "soft polyester blend",
                    "durable denim", "stretchy spandex", "organic bamboo fibers"
                ],
                "comfort": [
                    "all-day comfort", "superior breathability", "maximum flexibility",
                    "a perfect fit", "year-round wearability", "easy movement"
                ],
                "design": [
                    "slim-fit", "relaxed", "tailored", "athletic", "oversized", "classic"
                ],
                "features": [
                    "multiple pockets", "adjustable elements", "reinforced stitching",
                    "moisture-wicking properties", "wrinkle resistance", "easy care"
                ]
            },
            # Similar structures for other categories...
            "Groceries": {
                "templates": [
                    "Our premium {name} is {qualities}, {sourced} for {benefits}.",
                    "Enjoy {qualities} {name}, carefully {sourced} to ensure {benefits}."
                ],
                "qualities": [
                    "organically grown", "naturally sweet", "rich in flavor",
                    "packed with nutrients", "locally produced", "hand-selected"
                ],
                "sourced": [
                    "from sustainable farms", "from trusted growers", "at peak ripeness",
                    "with traditional methods", "using ethical practices", "with care for the environment"
                ],
                "benefits": [
                    "optimal freshness and taste", "your health and well-being",
                    "the finest culinary experience", "your complete satisfaction",
                    "nutritious meal preparation"
                ]
            }
        }

        self.default_template = {
            "templates": [
                "The {name} offers {features} for {benefits}. Perfect for {use_cases}."
            ],
            "features": [
                "excellent quality", "reliable performance", "innovative design",
                "superior materials", "exceptional value"
            ],
            "benefits": [
                "your complete satisfaction", "all your needs", "enhancing your experience",
                "meeting high standards", "exceeding expectations"
            ],
            "use_cases": [
                "a variety of applications", "both professional and personal use",
                "daily requirements", "special occasions", "long-term use"
            ]
        }


    def generate_product_description(self, product: Dict) -> str:
        """
            Generates a product description based on the product's category and predefined templates.

            Args:
                product (Dict): A dictionary containing product information. Must include at least
                    'name' and 'category' keys.

            Returns:
                str: A generated product description string, formatted and capitalized, ending with a period.

            The method selects a template based on the product's category, fills in placeholders with
            random values from the template data, and ensures the description is properly formatted.
        """
        category = product["category"]
        template_data = self.description_templates.get(category, self.default_template)

        replacements = {
            "name": product["name"],
            "category": category.lower(),
            **{
                key: random.choice(values)
                for key, values in template_data.items()
                if key != "templates"
            }
        }

        template = random.choice(template_data["templates"])
        description = template.format(**replacements)

        description = description[0].upper() + description[1:]
        if not description.endswith('.'):
            description += '.'

        return description

    def generate_product_name(self, category: str) -> str:
        """
            Generates a random product name based on the specified category.

            The product name is composed of a random adjective, a noun corresponding to the given category,
            and a random number between 1 and 1000.

            Args:
                category (str): The category of the product (e.g., "Electronics", "Clothing", etc.).

            Returns:
                str: A randomly generated product name.

            Raises:
                KeyError: If the provided category is not in the predefined list of categories.
        """
        adjectives = ["Premium", "Pro", "Smart", "Eco", "Advanced", "Luxury", "Ultra", "Wireless"]
        nouns = {
            "Electronics": ["Phone", "Tablet", "Laptop", "Headphones", "Speaker", "Monitor"],
            "Clothing": ["Shirt", "Pants", "Jacket", "Dress", "Shoes", "Hat"],
            "Groceries": ["Coffee", "Chocolate", "Pasta", "Oil", "Snacks", "Tea"],
            "Furniture": ["Chair", "Table", "Sofa", "Desk", "Cabinet", "Bed"],
            "Toys": ["Action Figure", "Doll", "Puzzle", "Game", "Building Set", "Stuffed Animal"],
            "Beauty": ["Shampoo", "Perfume", "Cream", "Makeup", "Serum", "Brush"],
            "Sports": ["Ball", "Racket", "Mat", "Dumbbell", "Bike", "Gloves"],
            "Office Supplies": ["Pen", "Notebook", "Stapler", "Folder", "Calculator", "Paper"]
        }
        return f"{random.choice(adjectives)} {random.choice(nouns[category])} {random.randint(1, 1000)}"


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
                return self.fake.date_time_between(start_date=start_date, end_date=end_date).strftime('%Y-%m-%d')

            case 'datetime':
                return self.fake.date_time_between(start_date=start_date, end_date=end_date).strftime('%Y-%m-%d %H:%M:%S')

            case 'datetime_v1':
                return self.fake.date_time_between_dates(
                datetime_start  = (datetime.now() - timedelta(days=90)),
                datetime_end    = datetime.now()
                ).strftime('%Y-%m-%d %H:%M:%S')

    def generate_products(self, num_products: int = 20) -> List[Dict]:
        """
            Generate a list of fake product dictionaries with randomized attributes.

            Args:
                num_products (int, optional): The number of products to generate. Defaults to 20.

            Returns:
                List[Dict]: A list of dictionaries, each representing a product with fields such as
                    product_id, name, category, brand, price, weight, dimensions, condition, in_stock,
                    sku, manufacturer, created_at, and description.
        """
        products = []
        for _ in range(num_products):
            category = self.fake.product_categories()
            product = {
                "product_id": f"PD##{self.fake.uuid4()}",
                "name": self.generate_product_name(category),
                "category": category,
                "brand": self.fake.company(),
                "price": round(random.uniform(1, 999), 2),
                "weight": round(random.uniform(0.1, 20), 2),
                "dimensions": {
                    "length": round(random.uniform(1, 200), 1),
                    "width": round(random.uniform(1, 100), 1),
                    "height": round(random.uniform(1, 50), 1)
                },
                "condition": random.choice(self.product_conditions),
                "in_stock": random.randint(0, 1000),
                "sku": self.fake.bothify(text='???-####-???'),
                "manufacturer": self.fake.company(),
                "description": None,  # Will be set later
                "created_at": self.generate_date(start_date='-2y', end_date='now'),
                "updated_at": None,
                "deleted_at": None
            }
            product["description"] = self.generate_product_description(product)
            products.append(product)

        return products

    def generate_inventory(self, products, num_locations=5):
        locations = [self.fake.city() for _ in range(num_locations)]
        inventory = []

        for product in products:
            for location in locations:
                inventory.append({
                    "inventory_id": f"IN##{self.fake.uuid4()}",
                    "product_id": product["product_id"],
                    "location": location,
                    "quantity": random.randint(0, 500),
                    "last_restock": self.generate_date(start_date='-6m', end_date='now'),
                    "aisle": self.fake.bothify(text='?##'),
                    "shelf": random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']),
                    "created_at": str(self.generate_date(start_date='-2y', end_date='now', option='datetime')),
                })
        return inventory

    #TODO: Transfer this to a separate module [ Delivery Locations ]
    # def generate_delivery_locations(self, num_locations=50):
    #     locations = []
    #     for _ in range(num_locations):
    #         city = self.fake.city()
    #         locations.append({
    #             "location_id": f"LC##{self.fake.uuid4()}",
    #             "address": self.fake.street_address(),
    #             "city": city,
    #             'neighborhood': None,
    #             "state": self.fake.state(),
    #             "postal_code": self.fake.postcode(),
    #             "country": self.fake.country(),
    #             "coordinates": {
    #                 "latitude": float(self.fake.latitude()),
    #                 "longitude": float(self.fake.longitude())
    #             },
    #             "delivery_zone": random.choice(['Urban', 'Suburban', 'Rural']),
    #             "delivery_difficulty": random.choice(['Easy', 'Medium', 'Hard']),
    #             "created_at": self.generate_date(start_date='-2y', end_date='now'),
    #             "fk_associate_id": None,
    #         })
    #     return locations


# Generate complete dataset
    def generate_complete_dataset(self, quantity: int) -> Dict[str, List[Dict]]:
        products            = self.generate_products(quantity)
        inventory           = self.generate_inventory(products)
        # locations           = self.generate_delivery_locations(100)
        # processing_times    = self.generate_processing_times(products, locations)

        return \
            {
                "tb_products": products,
                "tb_inventory": inventory
            }

# Example usage
if __name__ == "__main__":
    test = FkCommerce()
    print("Generating fake commerce data...")
    data = test.generate_complete_dataset(1)
    print("Fake commerce data generated successfully!")
    print(type(data))

    # Print sample data
    print("\nSample Product:")
    print(json.dumps(data["tb_products"][0], indent=2))

    print("\nSample Inventory Record:")
    print(json.dumps(data["tb_inventory"][0], indent=2))

    print("\nGenerated at:")
    print(data["generated_at"])

    # print("\nSample Delivery Location:")
    # print(json.dumps(data["delivery_locations"][0], indent=2))

    # print("\nSample Processing Time:")
    # print(json.dumps(data["processing_times"][0], indent=2))