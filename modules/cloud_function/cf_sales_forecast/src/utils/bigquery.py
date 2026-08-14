import logging
import pandas_gbq
import pandas as pd
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
        self.client = bigquery.Client(project=self.project)


    def batch_load_from_memory(self, data: pd.DataFrame, dataset: str, table: str) -> None:
        """
            Loads a batch of data from memory into a specified BigQuery table using pandas_gbq.

            Parameters
            ----------
            data : pd.DataFrame
                The data to load into BigQuery.
            dataset : str
                The ID of the BigQuery dataset.
            table : str
                The ID of the BigQuery table to which data will be loaded.

            Raises
            ------
            Exception
                If there is an error loading the data into BigQuery.
        """
        table_id = f"{self.project}.{dataset}.{table}"
        logging.info(f"Starting optimized batch load to {table_id}...")

        try:
            pandas_gbq.to_gbq(
                dataframe = data,
                destination_table = f"{self.project}.{dataset}.{table}",
                project_id = self.project,
                if_exists = "append"
            )
        except Exception as e:
            logging.error(f"Failed to load data: {e}")
            raise


    def get_data_from_bigquery(self, query: str) -> pd.DataFrame:
        """
        """
        job_config = QueryJobConfig()
        job_config.use_legacy_sql = False

        logging.info(f"Executing query on project {self.project}...")
        try:
            df = self.client.query(query, job_config=job_config).to_dataframe()
            logging.info(f"Query executed successfully. Retrieved {len(df)} rows.")

            return df

        except Exception as e:
            logging.error(f"Error executing query: {e}")
            raise


    def execute_ddl(self, query: str) -> None:
        """
            Executes a DDL command in BigQuery.

            Parameters
            ----------
            query : str
                The DDL command to execute.

            Raises
            ------
            Exception
                If there is an error executing the DDL command.
        """
        job_config = QueryJobConfig()
        job_config.use_legacy_sql = False

        logging.info(f"Executing DDL command on project {self.project}...")

        try:
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()

            logging.info(f"✅ DDL command executed successfully")

        except Exception as e:
            logging.error(f"❌ Error executing DDL: {e}")
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