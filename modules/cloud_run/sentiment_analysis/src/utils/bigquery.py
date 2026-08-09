import io
import time
import google
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
        """
            Load a Polars DataFrame into a BigQuery table using Parquet format.

            This method performs a batch load operation, converting a Polars DataFrame
            to Parquet format and uploading it to a specified BigQuery table. The load
            operation appends data to the existing table without creating or overwriting it.

            Args:
                _df (pl.DataFrame): The Polars DataFrame to be loaded into BigQuery.
                dataset (str): The BigQuery dataset name where the table resides.
                table (str): The BigQuery table name where data will be loaded.

            Returns:
                None

            Raises:
                - pl.ComputeError: If there is an error in processing the Polars DataFrame.
                - google.api_core.exceptions.BadRequest: If the BigQuery load job fails due to a bad request.
                - Exception: For any other unexpected errors during the load process.

            Notes:
                - Uses Parquet format with Snappy compression for efficient data transfer.
                - Enables list inference in Parquet options for better nested type handling.
                - Respects the existing BigQuery table schema (autodetect=False).
                - Write disposition is set to WRITE_APPEND (inserts data).
                - Create disposition is set to CREATE_NEVER (table must exist).
                - Operations timeout after 300 seconds.
                - Logs detailed information about shape, columns, and schema before loading.
                - Logs the number of rows successfully loaded upon completion.
        """

        table_id = f"{self.project}.{dataset}.{table}"

        logging.info(f"🚀 Iniciando batch load para {table_id}...")
        logging.info(f"📊 Shape: {_df.shape}, Colunas: {_df.columns}")
        logging.info(f"📋 Tipos: {_df.schema}")

        try:

            table_ref   = self.client.dataset(dataset).table(table)
            bq_table    = self.client.get_table(table_ref)

            with io.BytesIO() as stream:
                _df.write_parquet(stream, compression='snappy')
                stream.seek(0)

                parquet_options = bigquery.ParquetOptions()
                parquet_options.enable_list_inference = True

                job_config = bigquery.LoadJobConfig(
                    source_format       = bigquery.SourceFormat.PARQUET,
                    parquet_options     = parquet_options,
                    schema              = bq_table.schema,
                    write_disposition   = bigquery.WriteDisposition.WRITE_APPEND,
                    create_disposition  = bigquery.CreateDisposition.CREATE_NEVER,
                    autodetect          = False,
                )

                load_job = self.client.load_table_from_file(
                    file_obj    = stream,
                    destination = table_id,
                    project     = self.project,
                    job_config  = job_config,
                    timeout     = 300
                )

                load_job.result(timeout=300)
                logging.info(f"✅ {load_job.output_rows} Rows have been loaded successfully into {table_id}.")

        except pl.ComputeError as e:
            logging.error(f"❌ Error in Polars DataFrame: {e}")
            raise
        except google.api_core.exceptions.BadRequest as e:
            logging.error(f"❌ Error in BigQuery (BadRequest): {e}")
            if hasattr(e, 'errors') and e.errors:
                for err in e.errors:
                    logging.error(f"  - {err.get('reason')}: {err.get('message')}")
            raise
        except Exception as e:
            logging.error(f"❌ Unexpected error: {type(e).__name__}: {e}")
            raise


    def get_query(self) -> str:
        """
            Generates a BigQuery SQL query to retrieve feedback records for sentiment analysis.

            This method constructs a query that:
            - Identifies feedback records that have already been processed for sentiment analysis
            - Selects unprocessed feedback from the production feedback table
            - Combines the comment text with the rating information
            - Returns results in random order with a limit of 400 records

            The query uses a CTE (Common Table Expression) named 'SelectData' to identify
            feedback IDs that already exist in the sentiment analysis table, then excludes
            those records from the result set using a NOT IN clause.

            Returns:
                str: A formatted SQL query string for BigQuery that retrieves up to 400
                    unprocessed feedback records with their combined comment and rating,
                    and creation date, ordered randomly.
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
    bq = BigQuery(project="gcp-mts-pf")
    result = bq.read_bq()

    print(result)