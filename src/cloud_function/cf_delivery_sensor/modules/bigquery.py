import io
import json
import logging
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig


class BigQuery:
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

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            create_disposition=bigquery.CreateDisposition.CREATE_NEVER,
            autodetect=False,
        )

        try:
            load_job = self.client.load_table_from_file(
                memory_file, table_id, job_config=job_config
            )

            load_job.result()

            logging.info(f"batch load was successful. {load_job.output_rows} rows loaded into {table_id}.")

        except Exception as e:
            logging.error(f"Failed to load data from memory: {e}")
            raise


    def read_bigquery_with_params(self, dataset_id, table_id, columns=None, filters=None, limit=None) -> list[dict]:

        table_ref = f"{self.project}.{dataset_id}.{table_id}"

        where_clause = ""
        if filters:
            conditions = [f"{k} = '{v}'" if isinstance(v, str) else f"{k} = {v}"
                        for k, v in filters.items()]
            where_clause = "WHERE \n" + " AND ".join(conditions)
        if columns:
            columns_list = ", ".join(columns)
        else:
            columns_list = ""

        query = \
            f"""
                SELECT
                    TBSA.purchase_id,
                    TBIN.location,
                    TBIN.coordinates.latitude,
                    TBIN.coordinates.longitude,
                    TBSA.associate_id,
                    CONCAT(TBCU.name, " ", TBCU.last_name) AS customer_name,
                    CONCAT(TBAD.address, ", ", TBAD.city, " - ", TBAD.state) AS address,
                    TBAD.latitude,
                    TBAD.longitude,
                    {columns_list}
                FROM
                    `{self.project}.ls_customers.tb_sales` AS TBSA
                INNER JOIN
                    `{self.project}.ls_customers.tb_inventory` AS TBIN
                ON
                    TBSA.inventory_id = TBIN.inventory_id
                INNER JOIN
                    `{self.project}.ls_customers.tb_customers` AS TBCU
                ON
                    TBSA.associate_id = TBCU.associate_id
                INNER JOIN
                    `{self.project}.ls_customers.tb_address` AS TBAD
                ON
                    TBSA.associate_id = TBAD.fk_associate_id
                {where_clause}
                {'LIMIT ' + str(limit) if limit else ''}
            """

        job_config = QueryJobConfig()
        job_config.use_legacy_sql = False

        query_job = self.client.query(query, job_config=job_config)

        return [[col for col in row[0:9]] for row in query_job]

# Exemplo de uso:
# results = read_bigquery_with_params(
#     project_id="seu-projeto-gcp",
#     dataset_id="dataset_exemplo",
#     table_id="tabela_clientes",
#     filters={"status": "ativo", "idade": 30},
#     limit=100
# )
if __name__ == '__main__':
    bq = BigQuery(project="mts-default-portofolio")
    result = bq.read_bigquery_with_params(
        dataset_id="ls_customers",
        table_id="tb_sales",
        columns=None,
        filters=None,
        limit=5
    )
    print(result[0])  # Exibe os primeiros 5 resultados