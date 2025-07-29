import uuid
import random
from datetime import datetime, timedelta
from pyspark.sql.window import Window
from pyspark.sql.types import StringType, FloatType, TimestampType
from pyspark.sql.functions import expr, rand, udf, row_number, floor, when



def sql_query(project_id, dataset_id) -> dict:
    """
        Generates SQL query strings for retrieving customer and product data from specified BigQuery datasets.

        Args:
            project_id (str): The Google Cloud project ID.
            dataset_id (str): The BigQuery dataset ID.

        Returns:
            dict: A dictionary containing two SQL query strings:
                - "tb_customers": SQL query to select associate, card, and address IDs from customers, cards, and address tables, limited to 50,000 random records.
                - "tb_products": SQL query to select inventory and product details by joining products and inventory tables.
    """
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


def _generate_order_id() -> str:
    """
        Generates a unique order ID string.

        Returns:
            str: A unique order ID in the format 'SALE##<UUID>'.
    """
    return f"SALE##{str(uuid.uuid4())}"


def _generate_random_date() -> datetime:
    """
        Generates a random datetime within the past 180 days from the current date.

        Returns:
            datetime: A randomly generated datetime object between now and 180 days ago.
    """
    days_ago = random.randint(0, 180)
    return datetime.now() - timedelta(days=days_ago)


def _generate_peak_season_multiplier() -> float:
    """
        Generates a random peak season multiplier.

        Returns:
            float: A random float value between 1.2 and 2.5 (inclusive), rounded to one decimal place.
    """
    return round(random.uniform(1.2, 2.5), 1)


def _udf_functions() -> list:
    """
        Registers UDFs (User Defined Functions) for generating random dates, peak season multipliers, and order IDs.

        Returns:
            tuple: A tuple containing three UDFs:
                - generate_random_date_udf: UDF for generating random dates.
                - generate_peak_season_multiplier_udf: UDF for generating peak season multipliers.
                - generate_order_id_udf: UDF for generating order IDs.
    """
    generate_random_date_udf = udf(_generate_random_date, TimestampType())
    generate_peak_season_multiplier_udf = udf(_generate_peak_season_multiplier, FloatType())
    generate_order_id_udf = udf(_generate_order_id, StringType())

    return generate_random_date_udf, generate_peak_season_multiplier_udf, generate_order_id_udf


def generate_fake_purchases(spark, df_customers, df_products, VAR_NUM_PURCHASES):
    """
        Generates a DataFrame of fake purchase records by randomly pairing customers and products.

        Args:
            spark (pyspark.sql.SparkSession): The active Spark session.
            df_customers (pyspark.sql.DataFrame): DataFrame containing customer data.
            df_products (pyspark.sql.DataFrame): DataFrame containing product data.
            VAR_NUM_PURCHASES (int): The number of fake purchase records to generate.

        Returns:
            pyspark.sql.DataFrame: A DataFrame representing fake purchases, with each row containing randomly selected customer and product information.
    """

    w1 = Window.orderBy(rand())
    w2 = Window.orderBy(rand())

    df_customers_indexed = df_customers.withColumn("cust_idx", row_number().over(w1) - 1)
    df_products_indexed = df_products.withColumn("prod_idx", row_number().over(w2) - 1)

    total_customers = df_customers_indexed.count()
    total_products = df_products_indexed.count()

    df_base = spark.range(VAR_NUM_PURCHASES) \
        .withColumn("cust_idx", floor(rand() * total_customers)) \
        .withColumn("prod_idx", floor(rand() * total_products))

    return df_base \
        .join(df_customers_indexed, on="cust_idx", how="inner") \
        .join(df_products_indexed, on="prod_idx", how="inner") \
        .drop("cust_idx", "prod_idx")


def generate_fake_orders(df_base):
    """
        Generates a DataFrame of fake orders by adding purchase IDs, random dates, and peak season multipliers.

        Args:
            df_base (pyspark.sql.DataFrame): DataFrame containing fake purchase records.

        Returns:
            pyspark.sql.DataFrame: A DataFrame representing fake orders, with additional columns for purchase ID, purchase date, and peak season multiplier.
    """
    generate_random_date_udf, generate_peak_season_multiplier_udf, generate_order_id_udf = _udf_functions()

    df_base.withColumn("purchase_id", generate_order_id_udf()) \
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
    

    return df_base.select(
        "purchase_id",
        "associate_id",
        "card_id",
        "address_id",
        "product_id",
        "inventory_id",
        "location",
        "quantity",
        "price",
        "discount_applied",
        "final_price"
        "order_status",
        "purchase_date",
        "normal_processing_time",
        "expedited_processing_time",
        "peak_season_multiplier",
    )