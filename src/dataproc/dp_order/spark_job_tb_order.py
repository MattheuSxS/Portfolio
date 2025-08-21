import logging
import argparse
from pyspark.sql import SparkSession


#   ********************************************************************************************************   #
#                                                Logging Configuration                                         #
#   ********************************************************************************************************   #
logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)

#   ********************************************************************************************************   #
#                                                 Utility Functions                                            #
#   ********************************************************************************************************   #
from utils.helpers import (
    sql_query,
    generate_fake_purchases,
    generate_fake_orders,
)

#   ********************************************************************************************************   #
#                                                 Major Functions                                              #
#   ********************************************************************************************************   #
def main(args) -> None:
    spark = SparkSession.builder \
        .appName("BigQuery-ETL-TTable-Sales") \
        .config("spark.jars.packages", "com.google.cloud.spark:spark-3.5-bigquery:0.42.4") \
        .getOrCreate()

    # spark.sparkContext.setLogLevel("ERROR")

    VAR_PROJECT_ID      = args.project_id
    VAR_DATASET_ID      = args.dataset_id
    VAR_NUM_PURCHASES   = args.num_purchases
    VAR_SQL_QUERY       = sql_query(VAR_PROJECT_ID, VAR_DATASET_ID, VAR_NUM_PURCHASES)

    df_customers = spark.read.format("bigquery") \
        .option("query", VAR_SQL_QUERY["tb_customers"]) \
        .option("viewsEnabled", "true") \
        .load()

    df_products = spark.read.format("bigquery") \
        .option("query", VAR_SQL_QUERY["tb_products"]) \
        .option("viewsEnabled", "true") \
        .load()

    df_orders_fake = generate_fake_orders(
        generate_fake_purchases(df_customers, df_products, VAR_NUM_PURCHASES))

    df_orders_fake.write.format("bigquery") \
        .option("table", f"{VAR_PROJECT_ID}.{VAR_DATASET_ID}.tb_sales") \
        .option("writeMethod", "direct") \
        .option("partitionType", "DAY") \
        .option("partitionField", "purchase_date") \
        .mode("append") \
        .save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate fake purchase data and write to BigQuery")

    parser.add_argument("--project_id", required=True, help="ID of the GCP project")
    parser.add_argument("--dataset_id", required=True, help="ID of the BigQuery dataset")
    parser.add_argument("--num_purchases", type=int, default=100_000, help="NNumber of purchases to generate")
    parser.add_argument("--job_id", required=False, help="ID of the Dataproc job (optional)")

    args = parser.parse_args()

    main(args)