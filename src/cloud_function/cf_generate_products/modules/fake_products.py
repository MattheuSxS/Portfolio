import json
import random
from faker import Faker
from datetime import datetime, timedelta
from faker.providers import DynamicProvider


class FakeCommerceData:
    def __init__(self, country: str = 'pt_BR') -> None:
        self.fake = Faker(country)
        self.fake.seed_instance(0)
        self.fake.add_provider(
            DynamicProvider(
                provider_name="product_categories",
                elements=["Electronics", "Clothing", "Groceries", "Furniture",
                          "Toys", "Beauty", "Sports", "Office Supplies"])
        )
        self.product_conditions = ["New", "Used - Like New", "Used - Good", "Used - Fair", "Refurbished"]
        self.schema_product = {
            "product_id": None,
            "name": None,
            "category": None,
            "brand": None,
            "price": None,
            "weight": None,
            "dimensions": {
                "length": None,
                "width": None,
                "height": None
            },
            "condition": None,
            "in_stock": None,
            "sku": None,
            "description": None,
            "manufacturer": None,
            "created_at": None
        }


    def generate_product_name(self, category):
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


    def generate_products(self, num_products=20):
        products = []
        for _ in range(num_products):
            category = self.fake.product_categories()
            products.append({
                "product_id": self.fake.uuid4(),
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
                "description": self.fake.paragraph(nb_sentences=3),
                "manufacturer": self.fake.company(),
                "created_at":  self.generate_date(start_date='-2y', end_date='now') #self.fake.date_time_between(start_date='-2y', end_date='now').strftime('%Y-%m-%d')
            })
        return products

    def generate_inventory(self, products, num_locations=5):
        locations = [self.fake.city() for _ in range(num_locations)]
        inventory = []

        for product in products:
            for location in locations:
                inventory.append({
                    "inventory_id": self.fake.uuid4(),
                    "product_id": product["product_id"],
                    "location": location,
                    "quantity": random.randint(0, 500),
                    "last_restock": self.generate_date(start_date='-6m', end_date='now'),
                    "aisle": self.fake.bothify(text='?##'),
                    "shelf": random.choice(['A', 'B', 'C', 'D', 'E'])
                })
        return inventory

    def generate_delivery_locations(self, num_locations=50):
        locations = []
        for _ in range(num_locations):
            city = self.fake.city()
            locations.append({
                "location_id": self.fake.uuid4(),
                "address": self.fake.street_address(),
                "city": city,
                "state": self.fake.state(),
                "postal_code": self.fake.postcode(),
                "country": self.fake.country(),
                "coordinates": {
                    "latitude": float(self.fake.latitude()),
                    "longitude": float(self.fake.longitude())
                },
                "delivery_zone": random.choice(['Urban', 'Suburban', 'Rural']),
                "delivery_difficulty": random.choice(['Easy', 'Medium', 'Hard'])
            })
        return locations

    def generate_processing_times(self, products, locations):
        processing_data = []
        for product in random.sample(products, min(20, len(products))):
            for location in random.sample(locations, min(10, len(locations))):
                base_time = random.randint(1, 5)  # days
                processing_data.append({
                    "processing_id": self.fake.uuid4(),
                    "product_id": product["product_id"],
                    "location_id": location["location_id"],
                    "normal_processing_time": base_time,
                    "expedited_processing_time": max(1, base_time - 1),
                    "peak_season_multiplier": round(random.uniform(1.2, 2.5), 1),
                    "last_updated": self.generate_date(start_date='-60d', end_date='now')
                })
        return processing_data

# Generate complete dataset
    def generate_complete_dataset(self):
        print("Generating fake data...")
        products            = self.generate_products(50)
        inventory           = self.generate_inventory(products)
        locations           = self.generate_delivery_locations(100)
        processing_times    = self.generate_processing_times(products, locations)

        dataset = {
            "products": products,
            "inventory": inventory,
            "delivery_locations": locations,
            "processing_times": processing_times,
            "generated_at": self.generate_date(option='datetime_v1')
        }

        # Save to JSON file
        with open('fake_commerce_data.json', 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)

        print("Data generation complete. Saved to 'fake_commerce_data.json'")
        return dataset

# Example usage
if __name__ == "__main__":
    test = FakeCommerceData()
    print("Generating fake commerce data...")
    data = test.generate_complete_dataset()
    print("Fake commerce data generated successfully!")

    # Print sample data
    print("\nSample Product:")
    print(json.dumps(data["products"][0], indent=2))

    print("\nSample Inventory Record:")
    print(json.dumps(data["inventory"][0], indent=2))

    print("\nSample Delivery Location:")
    print(json.dumps(data["delivery_locations"][0], indent=2))

    print("\nSample Processing Time:")
    print(json.dumps(data["processing_times"][0], indent=2))