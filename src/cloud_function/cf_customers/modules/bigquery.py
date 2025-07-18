import io
import json
import logging
from google.cloud import bigquery


class BigQuery:
    def __init__(self, project: str) -> None:
        self.project = project
        self.client = bigquery.Client(project=self.project)

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

# --- Exemplo de Uso ---
if __name__ == '__main__':
    # Substitua com suas informações
    PROJECT_ID = "seu-projeto-gcp"
    DATASET_ID = "seu_dataset"
    TABLE_ID = "sua_tabela"

    bq_feedback = BigQuery(project=PROJECT_ID)

    # Dados que estão na memória RAM da sua aplicação
    dados_em_memoria = [
        {"id": 1, "produto": "laptop", "valor": 7500.50},
        {"id": 2, "produto": "mouse", "valor": 150.75},
        {"id": 3, "produto": "teclado", "valor": 300.00},
        {"id": 4, "produto": "monitor", "valor": 2200.00}
    ]

    try:
        print("\n--- Testando Batch Load da Memória RAM ---")
        bq_feedback.batch_load_from_memory(dados_em_memoria, DATASET_ID, TABLE_ID)
    except Exception as e:
        print(f"Erro no teste de batch load da memória: {e}")