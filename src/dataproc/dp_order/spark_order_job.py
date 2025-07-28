

import uuid
import random
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.types import StringType, FloatType, TimestampType
from pyspark.sql.functions import expr, rand, udf, row_number, floor, when


#   ********************************************************************************************************   #
#                                                 Utility Functions                                            #
#   ********************************************************************************************************   #
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


#   ********************************************************************************************************   #
#                                                 Major Functions                                              #
#   ********************************************************************************************************   #
def main():
    spark = SparkSession.builder \
        .appName("BigQuery-ETL-Job") \
        .config("spark.jars.packages", "com.google.cloud.spark:spark-3.5-bigquery:0.42.2") \
        .getOrCreate()

    project_id = "mts-default-portofolio"
    dataset_id = "ls_customers"

    _sql_query = sql_query(project_id, dataset_id)
    df_customers = spark.read.format("bigquery") \
        .option("query", _sql_query["tb_customers"]) \
        .option("viewsEnabled", "true") \
        .load()

    df_products = spark.read.format("bigquery") \
        .option("query", _sql_query["tb_products"]) \
        .option("viewsEnabled", "true") \
        .load()


    generate_random_date_udf = udf(generate_random_date, TimestampType())
    generate_peak_season_multiplier_udf = udf(generate_peak_season_multiplier, FloatType())
    generate_order_id_udf = udf(generate_order_id, StringType())

    w1 = Window.orderBy(rand())
    w2 = Window.orderBy(rand())

    df_customers_indexed = df_customers.withColumn("cust_idx", row_number().over(w1) - 1)
    df_products_indexed = df_products.withColumn("prod_idx", row_number().over(w2) - 1)

    total_customers = df_customers_indexed.count()
    total_products = df_products_indexed.count()

    df_base = spark.range(200_000) \
        .withColumn("cust_idx", floor(rand() * total_customers)) \
        .withColumn("prod_idx", floor(rand() * total_products))

    df_fake = df_base \
        .join(df_customers_indexed, on="cust_idx", how="inner") \
        .join(df_products_indexed, on="prod_idx", how="inner") \
        .drop("cust_idx", "prod_idx")

    df_fake = df_fake \
        .withColumn("purchase_id", generate_order_id_udf()) \
        .withColumn("purchase_date", generate_random_date_udf()) \
        .withColumn("quantity", expr("CAST(FLOOR(RAND() * 10 + 1) AS INT)")) \
        .withColumn("normal_processing_time", expr("CAST(FLOOR(RAND() * 10 + 1) AS INT)")) \
        .withColumn("expedited_processing_time", expr("CAST(FLOOR(RAND() * 5 + 1) AS INT)")) \
        .withColumn("peak_season_multiplier", generate_peak_season_multiplier_udf()) \
        .withColumn(
        "order_status",
            when(rand() < 0.80, "completed")
            .when(rand() < 0.90, "processing")
            .otherwise("cancelled")) \
        .withColumn("discount_applied", expr("ROUND(RAND() * 20, 2)")) \
        .withColumn("final_price", expr("ROUND((price * quantity) - discount_applied, 2)"))


    df_purchases_fake = df_fake.select(
        "purchase_id",
        "associate_id",
        "card_id",
        "address_id",
        "product_id",
        "inventory_id",
        "location",
        "price",
        "quantity",
        "purchase_date",
        "normal_processing_time",
        "expedited_processing_time",
        "peak_season_multiplier",
        "order_status",
        "discount_applied",
        "final_price"
    )

    df_purchases_fake.write.format("bigquery") \
        .option("table", f"{project_id}.{dataset_id}.tb_sales") \
        .option("writeMethod", "direct") \
        .option("partitionType", "DAY") \
        .option("partitionField", "purchase_date") \
        .mode("append") \
        .save()


if __name__ == "__main__":
    main()