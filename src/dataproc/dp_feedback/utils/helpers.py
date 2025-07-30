import json
import random
from faker import Faker
from datetime import datetime, timedelta
from faker.providers import DynamicProvider


import uuid
import random
from datetime import datetime, timedelta
from pyspark.sql.window import Window
from pyspark.sql.types import StringType, FloatType, TimestampType
from pyspark.sql.functions import expr, rand, udf, row_number, floor, when



def sql_query(project_id:str, dataset_id:str) -> dict:
    """
        Generates a SQL query string to select completed orders from a specified BigQuery dataset.

        Args:
            project_id (str): The Google Cloud project ID.
            dataset_id (str): The BigQuery dataset ID.

        Returns:
            str: A formatted SQL query string that selects purchase_id, associate_id, product_id, order_status, and purchase_date
                from the tb_sales table where order_status is "completed", orders the results randomly, and limits the output to 75,000 rows.
    """
    return {
        "tb_sales": f"""
            SELECT
                TBSA.purchase_id,
                CONCAT(TBCU.name, ' ', TBCU.last_name) AS customers_name,
                TBCU.email AS customers_email,
                TBSA.product_id,
                TBPR.name AS product_name,
                TBPR.category,
                TBPR.brand,
                TBSA.purchase_date
            FROM
                `{project_id}.{dataset_id}.tb_sales` AS TBSA
            INNER JOIN
                `{project_id}.{dataset_id}.tb_customers` AS TBCU
            ON
                TBSA.associate_id = TBCU.associate_id
            INNER JOIN
                `{project_id}.{dataset_id}.tb_products` AS TBPR
            ON
                TBSA.product_id = TBPR.product_id
            WHERE
                TBSA.order_status = "completed"
            ORDER BY
                RAND()
            LIMIT 5000;
        """
    }


class FkFeedback:


    def __init__(self, country: str = 'en_US') -> None:
        self.fake = Faker(country)
        self.fake.seed_instance(0)
        self.fake.add_provider(
            DynamicProvider(
                provider_name="product_categories",
                elements=["Electronics", "Clothing", "Groceries", "Furniture",
                         "Toys", "Beauty", "Sports", "Office Supplies"])
            )
        self.feedback_types = ["Product", "Service", "Support", "Delivery", "Website/App"]
        self.sentiment_words = \
            {
                1: ["terrible", "awful", "horrible", "disappointing", "frustrating"],
                2: ["poor", "subpar", "unsatisfactory", "below average", "lacking"],
                3: ["average", "mediocre", "okay", "acceptable", "decent"],
                4: ["good", "solid", "satisfactory", "pleasing", "nice"],
                5: ["excellent", "amazing", "outstanding", "fantastic", "perfect"]
            }
        self.schema_feedback = \
            {
                "feedback_id"       : None,
                "type"              : None,
                "category"          : None,
                "customer_name"     : None,
                "customer_email"    : None,
                "rating"            : None,
                "title"             : None,
                "comment"           : None,
                "fb_date"           : None,
                "verified_purchase" : None,
                "would_recommend"   : None,
                "company_response"  : None,
                "response_date"     : None,
                "product_name"      : None,
                "brand_name"        : None,
                "size"              : None,
                "color"             : None
            }


    def generate_comment(self, rating:int) -> str:
        base_comment = self.fake.paragraph(nb_sentences=3)

        match rating:
            case 1:
                return f"I regret this purchase completely. {base_comment} I will never buy from this company again."
            case 2:
                return f"Not what I expected. {base_comment} The quality was much lower than advertised."
            case 3:
                return f"It's okay, but could be better. {base_comment} I might consider buying again if improvements are made."
            case 4:
                return f"Pretty good overall. {base_comment} I'm satisfied with my purchase."
            case _:
                return f"Absolutely wonderful! {base_comment} Exceeded all my expectations!"


    def generate_fake_feedbacks(self, num_feedbacks:int = 10):
        feedbacks = []
        for _ in range(num_feedbacks):
            date = self.fake.date_time_between(start_date='-180d', end_date='now')
            rating = random.randint(1, 5)
            sentiment = random.choice(self.sentiment_words[rating])
            feedback = self.schema_feedback.copy()
            fake_name = self.fake.name()
            feedback.update({
                "feedback_id"       : f"FB##{self.fake.uuid4()}",
                "type"              : random.choice(self.feedback_types),
                "category"          : self.fake.product_categories(),
                "customer_name"     : fake_name,
                "customer_email"    : f"{fake_name.lower().replace(' ', '.')}{'@'}{self.fake.free_email_domain()}",
                "rating"            : rating,
                "title"             : f"{sentiment.capitalize()} experience with the {self.fake.word().capitalize()}",
                "comment"           : self.generate_comment(rating),
                "fb_date"           : date.strftime("%Y-%m-%d %H:%M:%S"),
                "verified_purchase" : random.choice([True, False]),
                "would_recommend"   : rating >= 4 if random.random() > 0.2 else rating == 3,
                 "company_response" : self.fake.paragraph(nb_sentences=2) if random.random() > 0.7 else None,
                "response_date"     : (date + timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d %H:%M:%S") if random.random() > 0.7 else None
            })

            if feedback["type"] == "Product":
                feedback.update({
                    "product_name": self.fake.catch_phrase(),
                    "brand_name": self.fake.company(),
                    "size": random.choice(["S", "M", "L", "XL", "One Size"]) if feedback["category"] in ["Clothing", "Toys"] else None,
                    "color": self.fake.color_name() if feedback["category"] in ["Clothing", "Furniture"] else None
                })

            feedbacks.append(feedback)

        return feedbacks

    def pretty_print_feedbacks(self, feedbacks):
        print("GENERATED FAKE FEEDBACKS:\n")
        for i, fb in enumerate(feedbacks, 1):
            print(f"Feedback #{i}")
            print(f"Customer: {fb['customer_name']} ({fb['customer_email']})")
            print(f"Type: {fb['type']} | Category: {fb['category']}")
            print(f"Rating: {'★' * fb['rating']} ({fb['rating']}/5)")
            print(f"Title: {fb['title']}")
            print(f"Comment: {fb['comment']}")

            if fb.get('product_name'):
                print(f"Product: {fb['product_name']} ({fb.get('brand', '')})")

            print(f"Date: {fb['fb_date']} | Verified: {'Yes' if fb['verified_purchase'] else 'No'}")
            print(f"Would recommend: {'Yes' if fb['would_recommend'] else 'No'}")

            if fb['company_response']:
                print(f"\nCompany Response ({fb['response_date']}):")
                print(fb['company_response'])

            print("\n" + "-"*100 + "\n")


if __name__ == "__main__":
    test = FkFeedback()
    print("Generating fake feedback data...")
    feedbacks = test.generate_fake_feedbacks(5)
    test.pretty_print_feedbacks(feedbacks)
    print("Fake feedback data generated successfully!")


    # Export to JSON (optional)
    with open('fake_feedbacks.json', 'w', encoding='utf-8') as f:
        json.dump(feedbacks, f, ensure_ascii=False, indent=2)
    print("Feedbacks exported to 'fake_feedbacks.json'")