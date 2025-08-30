import time
import logging
import apache_beam as beam
from google.cloud import bigquery
from apache_beam.io.gcp.bigquery import WriteToBigQuery


# ******************************************************************************************************************** #
#                                              System Logging                                                          #
# ******************************************************************************************************************** #
logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)


class BigQueryConn:
    """
        Class to handle BigQuery operations such as retrieving table schemas
        and writing data to BigQuery.
    """

    def __init__(self, project: str) -> None:
        self.project = project

    def setup(self):
        from google.cloud import bigquery
        self.client = bigquery.Client(project=self.project)


class BigQueryWriter(beam.DoFn):

    def __init__(self, project_id, dataset_id, table_id):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id   = table_id
        self.client     = None
        self.schema     = None


    def setup(self):
        from google.cloud import bigquery
        self.client = bigquery.Client(project=self.project_id)


    def _get_schema_bigquery(self) -> str:

        try:
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            table = self.client.get_table(table_ref)

            # Convert schema to the format expected by WriteToBigQuery
            schema_fields = []
            for field in table.schema:
                schema_fields.append({
                    'name': field.name,
                    'type': field.field_type,
                    'mode': field.mode if field.mode else 'NULLABLE'
                })

            return schema_fields

        except Exception as e:
            logging.error(f"Error getting BigQuery schema: {e}")
            # # Fallback to a default schema if table doesn't exist yet
            # return self._get_default_schema()
            field_types = [f"{field.name}:{field.field_type}" for field in table_ref.schema]
            str_schema = ", ".join(field_types)

            return str_schema


    def process(self, element) -> None:
        """
            Processes an element by writing it to BigQuery.

            This method takes an Apache Beam element and writes it to a BigQuery table
            in the staging dataset. The data is streamed using the STREAMING_INSERTS method
            and will be appended to the existing table or create a new table if it doesn't exist.

            Args:
                element: The Apache Beam element to be processed and written to BigQuery.
                        This should contain the data that matches the expected schema.

            Returns:
                None: This method doesn't return any value as it performs a side effect
                    of writing data to BigQuery.

            Note:
                - Uses streaming inserts for real-time data ingestion
                - Creates table automatically if it doesn't exist
                - Appends data to existing table without overwriting
                - Schema is determined by the _get_schema_bigquery() method
        """
        element | WriteToBigQuery(
            table               = f"{self.project}.staging.tb_delivery_status_stage",
            schema              = self._get_schema_bigquery(),
            create_disposition  = beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition   = beam.io.BigQueryDisposition.WRITE_APPEND,
            method              = "STORAGE_WRITE_API"  # Using Storage Write API for better performance
        )





class BigQueryMerger(beam.DoFn):
    def __init__(self, project_id, dataset_id, table_id, interval=180):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id   = table_id
        self.client     = None
        self.interval   = interval
        self.last_run   = 0


    def setup(self):
        from google.cloud import bigquery
        self.client = bigquery.Client(project=self.project_id)


    def _clear_staging_table(self, sql_query):
        try:
            self.client.query(sql_query).result()
        except Exception as e:
            logging.warning(f"Error clearing staging table: {e}")


    def process(self, element) -> None:
        current_time = time.time()
        sql_query = {
            "insert":
                f"""
                    MERGE `{self.project}.ls_customers.tb_delivery_status` AS T
                    USING `{self.project}.staging.tb_delivery_status_stage` AS S
                    ON T.delivery_id = S.delivery_id
                    WHEN MATCHED THEN
                    UPDATE SET
                        T.remaining_distance_km = COALESCE(S.remaining_distance_km, T.remaining_distance_km),
                        T.estimated_time_min = COALESCE(S.estimated_time_min, T.estimated_time_min),
                        T.delivery_difficulty = COALESCE(S.delivery_difficulty, T.delivery_difficulty),
                        T.status = COALESCE(S.status, T.status),
                        T.updated_at = COALESCE(S.updated_at, T.updated_at)
                    WHEN NOT MATCHED THEN
                    INSERT (
                        delivery_id,
                        vehicle_id,
                        purchase_id,
                        remaining_distance_km,
                        estimated_time_min,
                        delivery_difficulty,
                        status,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        S.delivery_id,
                        S.vehicle_id,
                        S.purchase_id,
                        S.remaining_distance_km,
                        S.estimated_time_min,
                        S.delivery_difficulty,
                        S.status,
                        COALESCE(S.created_at, CURRENT_TIMESTAMP()),
                        COALESCE(S.updated_at, CURRENT_TIMESTAMP())
                    );""",
            "delete":
                f"""
                    TRUNCATE TABLE `{self.project}.staging.tb_delivery_status_stage`;
                """
        }

        if current_time - self.last_run >= self.interval:
            try:

                self.client.query(sql_query["insert"]).result()
                self._clear_staging_table(sql_query["delete"])
                self.last_run = current_time

            except Exception as e:
                logging.warning(f"Error executing BigQuery merge: {e}")
