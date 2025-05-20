import logging
from google.cloud import bigquery


logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)


class BigQueryFeedback:
    def __init__(self, project:str, dataset:str, table:str) -> None:
        self.project    = project
        self.dataset    = dataset
        self.table      = table

    def insert_data(self, data: list) -> None:
        """
        Inserts data into a BigQuery table.

        Args:
            data (list): List of dictionaries containing the data to be inserted.
        """
        client = bigquery.Client(project=self.project)
        errors = client.insert_rows_json(f"{self.project}.{self.dataset}.{self.table}", data)

        if errors:
            logging.error(f"Errors occurred while inserting data: {errors}")
            raise Exception(f"Errors ~~> {errors}")
        else:
            logging.info("Data inserted successfully.")
