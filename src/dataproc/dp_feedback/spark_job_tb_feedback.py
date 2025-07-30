#TODO: Finish the code tomorrow
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
    sql_query
)

#   ********************************************************************************************************   #
#                                                 Major Functions                                              #
#   ********************************************************************************************************   #
def main(args) -> None:
    spark = SparkSession.builder \
        .appName("BigQuery-ETL-Table-Sales") \
        .config("spark.jars.packages", "com.google.cloud.spark:spark-3.5-bigquery:0.42.2") \
        .getOrCreate()

    VAR_PROJECT_ID      = args.project_id
    VAR_DATASET_ID      = args.dataset_id
    VAR_NUM_FEEDBACKS   = args.num_feedbacks
    VAR_SQL_QUERY       = sql_query(VAR_PROJECT_ID, VAR_DATASET_ID)

    df_sales = spark.read.format("bigquery") \
        .option("query", VAR_SQL_QUERY["tb_sales"]) \
        .option("viewsEnabled", "true") \
        .load()

    df_sales.show()
    df_sales.printSchema()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate fake purchase data and write to BigQuery")

    parser.add_argument("--project_id", required=True, help="ID of the GCP project")
    parser.add_argument("--dataset_id", required=True, help="ID of the BigQuery dataset")
    parser.add_argument("--num_feedbacks", type=int, default=100000, help="Number of feedbacks to generate")
    parser.add_argument("--job_id", required=False, help="ID of the Dataproc job (optional)")

    args = parser.parse_args()

    main(args)