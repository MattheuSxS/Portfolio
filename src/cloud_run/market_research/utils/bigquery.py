import io
import json
import logging
import polars as pl
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig


class BigQuery:
    """
        BigQuery utility class for loading data into Google BigQuery tables.

            project (str): The Google Cloud project ID.

        Attributes:
            project (str): The Google Cloud project ID.
            client (bigquery.Client): The BigQuery client instance.

        Methods:
            batch_load_from_memory(data: list[dict], dataset: str, table: str) -> None:
                Loads a batch of data from memory into a specified BigQuery table using NDJSON format.
    """
    def __init__(self, project: str) -> None:
        self.project = project
        self.client = bigquery.Client(self.project)


    def batch_load_from_memory(self, data: list[dict], dataset: str, table: str) -> None:
        """
        Loads a batch of data from memory into a BigQuery table using NDJSON format.

        Args:
            data (list[dict]): A list of dictionaries representing the rows to be loaded.
            dataset (str): The name of the BigQuery dataset.
            table (str): The name of the BigQuery table.

        Raises:
            Exception: If there is an error converting data to NDJSON or loading data into BigQuery.

        Logs:
            - Info: When the batch load starts and completes successfully.
            - Error: If there is a failure during data conversion or loading.
        """
        table_id = f"{self.project}.{dataset}.{table}"

        logging.info(f"Starting batch load to {table_id}...")

        try:
            memory_file = io.BytesIO()
            for row in data:
                json_string = json.dumps(row) + '\n'
                memory_file.write(json_string.encode('utf-8'))

            memory_file.seek(0)

        except Exception as e:
            logging.error(f"Error converting data to NDJSON: {e}")
            raise

        job_config = \
            bigquery.LoadJobConfig(
                source_format       = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                write_disposition   = bigquery.WriteDisposition.WRITE_APPEND,
                create_disposition  = bigquery.CreateDisposition.CREATE_NEVER,
                autodetect          = False,
        )

        try:
            load_job = \
                self.client.load_table_from_file(
                    memory_file,
                    table_id,
                    job_config=job_config
            )

            load_job.result()

            logging.info(f"batch load was successful. {load_job.output_rows} rows loaded into {table_id}.")

        except Exception as e:
            logging.error(f"Failed to load data from memory: {e}")
            raise


    def get_query(self, query_name: str) -> str:
        """
        """
        query_scripts = \
            {
                "sql_feedback"        : f"""
                                            SELECT
                                                TFS.sentiment,
                                                TF.rating,
                                                FORMAT_TIMESTAMP('%Y-%m-%d', TF.fb_date) AS feedback_date
                                            FROM
                                                `mts-default-portfolio.ls_customers.tb_feedback_sentiment` AS TFS
                                            INNER JOIN
                                                `mts-default-portfolio.production.tb_feedback` AS TF
                                            USING
                                                (feedback_id)
                                            """,
                "sql_customer"        : f"""
                                            SELECT
                                                COUNT(associate_id) AS associate_count,
                                                TBAS.region,
                                                TBAS.state
                                            FROM
                                                `mts-default-portfolio.ls_customers.tb_customers` AS TBCS
                                            INNER JOIN
                                                `mts-default-portfolio.ls_customers.tb_address` AS TBAS
                                            ON
                                                TBCS.associate_id = TBAS.fk_associate_id
                                            GROUP BY
                                                TBAS.region,
                                                TBAS.state
                                            """,
                "sql_region_sales"    : f"""
                                            SELECT
                                                SUM(TBSS.discount_applied) AS discount_applied,
                                                SUM(TBSS.final_price) AS final_price,
                                                TBSS.region,
                                                TBAS.state,
                                                TBSS.order_status,
                                                FORMAT_TIMESTAMP('%Y-%m-%d', TBSS.purchase_date) AS purchase_date
                                            FROM
                                                `mts-default-portfolio.ls_customers.tb_sales` AS TBSS
                                            INNER JOIN
                                                `mts-default-portfolio.ls_customers.tb_address` AS TBAS
                                            ON
                                                TBSS.associate_id = TBAS.fk_associate_id
                                                AND TBSS.order_status = "completed"
                                            GROUP BY
                                                TBSS.region,
                                                TBAS.state,
                                                TBSS.order_status,
                                                TBSS.purchase_date;
                                            """,
                "sql_products_sales"  : f"""
                                            SELECT
                                                SUM(TBSS.discount_applied) AS discount_applied,
                                                SUM(TBSS.final_price) AS final_price,
                                                TBSS.region,
                                                TBSS.order_status,
                                                TBPS.category,
                                                REGEXP_REPLACE(TBPS.name, r'[0-9]', '') AS name,
                                                FORMAT_TIMESTAMP('%Y-%m-%d', TBSS.purchase_date) AS purchase_date
                                            FROM
                                                `mts-default-portfolio.ls_customers.tb_sales` AS TBSS
                                            INNER JOIN
                                                `mts-default-portfolio.ls_customers.tb_products` AS TBPS
                                            ON
                                                TBSS.product_id = TBPS.product_id
                                            WHERE
                                                TBSS.order_status IN ("completed", "processing")
                                                AND TBSS.purchase_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
                                            GROUP BY
                                                TBSS.region,
                                                TBSS.order_status,
                                                TBPS.category,
                                                REGEXP_REPLACE(TBPS.name, r'[0-9]', ''),
                                                TBSS.purchase_date
                                            """
            }

        return query_scripts[query_name]


    def read_bq(self, query: str, ) -> pl.DataFrame:
        """
            Execute a BigQuery SQL query and return the results as a list of rows.

            Parameters
            ----------
            query : str
                The SQL query to execute. Legacy SQL is disabled (standard SQL is used).

            Returns
            -------
            list[list]
                A list of rows, where each row is represented as a list of column values in the same
                order as the SELECT clause.

            Raises
            ------
            ValueError
                If the provided query is not a non-empty string.
            google.api_core.exceptions.GoogleAPICallError, google.api_core.exceptions.RetryError
                If the BigQuery request fails or the job cannot be completed.

            Notes
            -----
            This method submits the query using self.client, waits for the query job to finish
            (synchronous/blocking), and converts each returned Row to a plain list via list(row).
        """
        _query = self.get_query(query)

        if not isinstance(_query, str) or not _query.strip():
            raise ValueError("The 'query' parameter must be a non-empty string.")

        try:
            logging.info("Executing BigQuery query...")
            job_config = QueryJobConfig()
            job_config.use_legacy_sql = False

            query_job = self.client.query(_query, job_config=job_config)
            rows = query_job.to_arrow()
            logging.info("Query executed successfully.")

        except Exception as e:
            logging.error(f"Error executing query: {e}")
            raise

        return pl.from_arrow(rows)


if __name__ == '__main__':
    bq = BigQuery(project="mts-default-portfolio")
    result = bq.read_bq(
        query=bq.get_query('purchase_query')
    )
    print(result)