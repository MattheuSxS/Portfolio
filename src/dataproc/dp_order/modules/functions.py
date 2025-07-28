import uuid
import random
from datetime import datetime, timedelta
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, FloatType, TimestampType
)



def sql_query(project_id, dataset_id) -> dict:
    return {
        "tb_customers": f"""
            SELECT
                TBCU.associate_id,
                TBCA.card_id,
                TBAD.address_id
            FROM
                `{project_id}.{dataset_id}.tb_customers` AS TBCU
            INNER JOIN
                `{project_id}.{dataset_id}.tb_cards` AS TBCA
            ON
                TBCU.associate_id = TBCA.fk_associate_id
            INNER JOIN
                `{project_id}.{dataset_id}.tb_address` AS TBAD
            ON
                TBCU.associate_id = TBAD.fk_associate_id
            ORDER BY
                RAND()
            LIMIT 50000;
        """,
        "tb_products": f"""
            SELECT
                TBIN.inventory_id,
                TBPR.product_id,
                TBPR.price,
                TBIN.location
            FROM
                `{project_id}.{dataset_id}.tb_products` AS TBPR
            INNER JOIN
                `{project_id}.{dataset_id}.tb_inventory` AS TBIN
            ON
                TBPR.product_id = TBIN.product_id;
        """
    }

def generate_order_id():
    return f"SALE##{str(uuid.uuid4())}"


def generate_random_date():
    days_ago = random.randint(0, 180)
    return datetime.now() - timedelta(days=days_ago)


def generate_peak_season_multiplier():
    return round(random.uniform(1.2, 2.5), 1)