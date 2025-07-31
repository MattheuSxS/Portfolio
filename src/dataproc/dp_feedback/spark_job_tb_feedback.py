#TODO: Finish the code tomorrow
import logging
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col


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
    generate_fake_feedbacks
)

#   ********************************************************************************************************   #
#                                                 Major Functions                                              #
#   ********************************************************************************************************   #
def main(args) -> None:
    spark = SparkSession.builder \
        .appName("BigQuery-ETL-Table-FeedBack") \
        .config("spark.jars.packages", "com.google.cloud.spark:spark-3.5-bigquery:0.42.2") \
        .getOrCreate()

    VAR_PROJECT_ID          = args.project_id
    VAR_DATASET_ID          = args.dataset_id
    VAR_DATASET_WRITE_ID    = args.dataset_write_id
    VAR_NUM_FEEDBACKS       = args.num_feedbacks
    VAR_SQL_QUERY           = sql_query(VAR_PROJECT_ID, VAR_DATASET_ID, VAR_NUM_FEEDBACKS)


    df_sales = spark.read.format("bigquery") \
        .option("query", VAR_SQL_QUERY["tb_sales"]) \
        .option("viewsEnabled", "true") \
        .load()


    df_feedbacks = generate_fake_feedbacks(df_sales)
    df_feedbacks.write.format("bigquery") \
        .option("table", f"{VAR_PROJECT_ID}.{VAR_DATASET_WRITE_ID}.tb_feedback") \
        .option("writeMethod", "direct") \
        .option("partitionType", "DAY") \
        .option("partitionField", "fb_date") \
        .mode("append") \
        .save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate fake purchase data and write to BigQuery")

    parser.add_argument("--project_id", required=True, help="ID of the GCP project")
    parser.add_argument("--dataset_id", required=True, help="ID of the BigQuery dataset")
    parser.add_argument("--dataset_write_id", required=True, help="ID of the BigQuery dataset to write feedbacks")
    parser.add_argument("--num_feedbacks", type=int, default=50_000, help="Number of feedbacks to generate")
    parser.add_argument("--job_id", required=False, help="ID of the Dataproc job (optional)")

    args = parser.parse_args()

    main(args)