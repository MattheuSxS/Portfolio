import io
import json
import logging
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
                    comment,
                    fb_date AS created_at
                FROM
                    `{self.project}.production.tb_feedback`
                WHERE
                    feedback_id NOT IN (SELECT feedback_id FROM SelectData)
                ORDER BY
                    RAND()
                LIMIT 10000;
            """


    def read_bq(self, query: str) -> list[list]:
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
        if not isinstance(query, str) or not query.strip():
            raise ValueError("The 'query' parameter must be a non-empty string.")

        try:
            logging.info("Executing BigQuery query...")
            job_config = QueryJobConfig()
            job_config.use_legacy_sql = False

            query_job = self.client.query(query, job_config=job_config)
            rows = query_job.result()
            logging.info("Query executed successfully.")

        except Exception as e:
            logging.error(f"Error executing query: {e}")
            raise

        return [list(row) for row in rows]


if __name__ == '__main__':
    bq = BigQuery(project="mts-default-portfolio")
    result = bq.read_bq(
        query=bq.get_query('purchase_query')
    )

    # list_id         = list
    # list_comment    = list

    # list_id, list_comment = zip(*result[0:25])

    # print(list_id)
    # print(list_comment)]
    import polars as pl


    df = pl.DataFrame(result, schema=['feedback_id', 'comment'])
    print(df)