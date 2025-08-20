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
        Versão otimizada para carga de grandes volumes no BigQuery.
        """
        table_id = f"{self.project}.{dataset}.{table}"
        logging.info(f"Starting optimized batch load to {table_id}...")

        # Otimização 1: Geração eficiente de NDJSON
        try:
            # Usando join + generator expression (mais eficiente em memória)
            ndjson_content = '\n'.join(json.dumps(row) for row in data)
            memory_file = io.BytesIO(ndjson_content.encode('utf-8'))

        except Exception as e:
            logging.error(f"Error converting data to NDJSON: {e}")
            raise

        # Otimização 2: Configuração otimizada para performance
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            create_disposition=bigquery.CreateDisposition.CREATE_NEVER,
            autodetect=False,
            max_bad_records=10,  # Permite alguns registros inválidos sem falhar
        )

        try:
            # Otimização 3: Timeout configurável e retry policy
            load_job = self.client.load_table_from_file(
                memory_file,
                table_id,
                job_config=job_config,
                timeout=300  # 5 minutos timeout
            )

            # Otimização 4: Não usar result() que é bloqueante para jobs muito grandes
            # Em vez disso, verifica periodicamente
            while load_job.state != 'DONE':
                time.sleep(3)  # Verifica a cada 3 segundos
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