import uuid
import random
from utils.fk_data import FkFeedback
from datetime import datetime, timedelta
from pyspark.sql.window import Window
from pyspark.sql.functions import expr, rand, udf, row_number, floor, when, udf, col, explode
from pyspark.sql.types import ArrayType, StructType, StructField, StringType, IntegerType, BooleanType, TimestampType




def sql_query(project_id:str, dataset_id:str, row_limit:int) -> dict:
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
            LIMIT {row_limit};
        """
    }


def feedback_schema() -> StructType:
    """
        Defines the schema for feedback data.

        Returns:
            StructType: A Spark SQL StructType defining the structure of feedback data.
    """
    return StructType([
        StructField("feedback_id", StringType(), True),
        StructField("purchase_id", StringType(), True),
        StructField("associate_id", StringType(), True),
        StructField("product_id", StringType(), True),
        StructField("type", StringType(), True),
        StructField("category", StringType(), True),
        StructField("customer_name", StringType(), True),
        StructField("customer_email", StringType(), True),
        StructField("rating", IntegerType(), True),
        StructField("title", StringType(), True),
        StructField("comment", StringType(), True),
        StructField("purchase_date", TimestampType(), True),
        StructField("verified_purchase", BooleanType(), True),
        StructField("would_recommend", BooleanType(), True),
        StructField("company_response", StringType(), True),
        StructField("fb_date", TimestampType(), True),
        StructField("response_date", TimestampType(), True),
        StructField("product_name", StringType(), True),
        StructField("brand_name", StringType(), True),
        StructField("size", StringType(), True),
        StructField("color", StringType(), True)
    ])


def _function_udf():
    """
        Creates a PySpark UDF that generates a single fake feedback entry for a given category.

        Returns:
            pyspark.sql.functions.udf: A user-defined function (UDF) that takes a category string as input
            and returns a dictionary representing a single fake feedback, conforming to the feedback schema.
    """
    fk = FkFeedback()

    def generate_single_feedback(category_str: str) -> dict:
        return fk.generate_fake_feedbacks(num_feedbacks=1, category=category_str)[0]

    return udf(generate_single_feedback, feedback_schema())


def generate_fake_feedbacks(df_sales) -> None:
    """
        Generates a DataFrame of fake feedbacks based on the provided sales DataFrame.

        This function applies a user-defined function (UDF) to the 'category' column of the input DataFrame to generate synthetic feedback data for each sale. The resulting DataFrame includes feedback-related fields along with relevant sales and customer information.

        Args:
            df_sales (DataFrame): Input Spark DataFrame containing sales data. Must include columns such as 'category', 'purchase_id', 'product_id', 'product_name', 'brand', 'customers_name', 'customers_email', and 'purchase_date'.

        Returns:
            DataFrame: A Spark DataFrame with generated feedback columns, including:
                - feedback_id
                - purchase_id
                - product_id
                - category
                - product_name
                - brand
                - size
                - color
                - type
                - customers_name
                - customers_email
                - rating
                - title
                - comment
                - purchase_date
                - verified_purchase
                - would_recommend
                - company_response
                - response_date
                - fb_date
    """

    generate_feedback_udf = _function_udf()
    df_feedbacks = df_sales \
        .withColumn("feedback", generate_feedback_udf(col("category"))) \
        .select(
            col("feedback.feedback_id"),
            col("purchase_id"),
            col("product_id"),
            col("category"),
            col("product_name"),
            col("brand"),
            col("feedback.size"),
            col("feedback.color"),
            col("feedback.type"),
            col("customers_name"),
            col("customers_email"),
            col("feedback.rating"),
            col("feedback.title"),
            col("feedback.comment"),
            col("purchase_date"),
            col("feedback.verified_purchase"),
            col("feedback.would_recommend"),
            col("feedback.company_response"),
            col("feedback.response_date"),
            col("feedback.fb_date"),
        )

    return df_feedbacks