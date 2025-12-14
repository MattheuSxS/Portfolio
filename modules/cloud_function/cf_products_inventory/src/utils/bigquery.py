import io
import json
import time
import logging
from google.cloud import bigquery


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
        self.client = bigquery.Client(project=self.project)


    def batch_load_from_memory(self, data: list[dict], dataset: str, table: str) -> None:
        """
            Loads a list of dictionaries into a BigQuery table in a single batch.

            This method converts the provided data into a newline-delimited JSON (NDJSON)
            format, creates an in-memory file-like object, and then uses the BigQuery
            `load_table_from_file` method for an efficient batch insertion. The job is
            configured to append data to an existing table and will not create the table
            if it doesn't exist. It polls the job's status until completion and logs
            the outcome.

            Args:
                data (list[dict]): A list of dictionaries, where each dictionary
                    represents a row to be inserted into the BigQuery table.
                dataset (str): The ID of the BigQuery dataset.
                table (str): The ID of the BigQuery table to which data will be loaded.

            Raises:
                Exception: If there is an error converting the data to NDJSON format
                    or if the BigQuery load job fails for any reason.
        """
        table_id = f"{self.project}.{dataset}.{table}"
        logging.info(f"Starting optimized batch load to {table_id}...")

        
        try:
            
            ndjson_content = '\n'.join(json.dumps(row) for row in data)
            memory_file = io.BytesIO(ndjson_content.encode('utf-8'))

        except Exception as e:
            logging.error(f"Error converting data to NDJSON: {e}")
            raise


        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            create_disposition=bigquery.CreateDisposition.CREATE_NEVER,
            autodetect=False,
            max_bad_records=10,
        )

        try:

            load_job = self.client.load_table_from_file(
                memory_file,
                table_id,
                job_config=job_config,
                timeout=300
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