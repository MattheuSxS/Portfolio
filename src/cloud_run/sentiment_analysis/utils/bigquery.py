import io
import time
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

    def batch_load(self, _df: pl.DataFrame, dataset: str, table: str) -> None:
    # def batch_load_from_memory(self, data: list[dict], dataset: str, table: str) -> None:
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
            with io.BytesIO() as stream:
                _df.write_parquet(stream)
                stream.seek(0)
                parquet_options = bigquery.ParquetOptions()
                parquet_options.enable_list_inference = True
                load_job = self.client.load_table_from_file(
                    file_obj    = stream,
                    destination = table_id,
                    project     = self.project,
                    job_config  = bigquery.LoadJobConfig(
                        source_format   = bigquery.SourceFormat.PARQUET,
                        parquet_options = parquet_options,
                    ),
                )

                while load_job.state != 'DONE':
                    time.sleep(3)
                    load_job.reload()

                    if load_job.errors:
                        logging.warning(f"Job warnings: {load_job.errors}")

                logging.info(f"Batch load completed. {load_job.output_rows} rows loaded into {table_id}.")

        except Exception as e:
            logging.error(f"Failed to load data: {e}")
            raise


    def get_query(self) -> str:
        """
        """

        return \
            f"""
                WITH SelectData AS (
                    SELECT feedback_id FROM `{self.project}.ls_customers.tb_feedback_sentiment`
                )

                SELECT
                    feedback_id,
                    CONCAT(comment, ' I give it a rating of ', rating) AS comment,
                    fb_date AS created_at
                FROM
                    `{self.project}.production.tb_feedback`
                WHERE
                    feedback_id NOT IN (SELECT feedback_id FROM SelectData)
                ORDER BY
                    RAND()
                LIMIT 400;
            """


    def read_bq(self) -> pl.DataFrame:
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
        _query = self.get_query()

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
    result = bq.read_bq()

    print(result)