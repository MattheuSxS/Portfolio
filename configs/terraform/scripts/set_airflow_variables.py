import json
import logging
from pathlib import Path
from google.cloud import storage
from airflow.models import Variable


logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)


def read_json_files_from_gcs(bucket_name, prefix=""):
    """
    Read JSON files from a GCS bucket.

    Args:
        bucket_name (str): GCS bucket name.
        prefix (str): Prefix to filter files in the bucket.

    Returns:
        list: List of tuples with file name and JSON content.
    """
    json_data_dict = dict()

    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)

        for blob in blobs:
            if blob.name.endswith(".json"):
                logging.info(f"Reading file {blob.name}")
                json_data = blob.download_as_text()

                try:
                    json_data_dict.update(json.loads(json_data))

                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding JSON in file {blob.name} - {e}")

                except Exception as e:
                    logging.error(f"Unexpected error processing file {blob.name} - {e}")

    except Exception as e:
        logging.error(f"Error accessing GCS bucket {bucket_name} - {e}")

    return json_data_dict


def set_airflow_variables(bucket_name, prefix):
    """
        Reads JSON files from a Google Cloud Storage (GCS) bucket and sets Airflow variables.

        This function reads JSON files from the specified GCS bucket and prefix, and sets Airflow
        variables based on the contents of these files. Each key-value pair in the JSON files is
        set as an Airflow variable.

        Args:
        bucket_name (str): The name of the GCS bucket.
        prefix (str): The prefix path within the GCS bucket where the JSON files are located.

        Returns:
        None

        Logs:
        - An error if no JSON files are found or an error occurs while reading files.
        - An error if a file does not contain a valid JSON dictionary.
        - An error if there is an issue setting the Airflow variables.
        - An info message for each variable successfully created.
    """

    json_data = read_json_files_from_gcs(bucket_name, prefix)

    if not json_data:
        logging.error("No JSON files found or an error occurred while reading files.")
        return

    valid_data = {}

    for key, value in json_data.items():
        if isinstance(value, dict):
            valid_data[key] = value
        else:
            logging.error(f"File {key} does not contain a valid JSON dictionary.")
    try:
        for key, value in valid_data.items():
            Variable.set(key=key, value=json.dumps(value, indent=4))
            logging.info(f"Variable {key} created successfully")

    except Exception as e:
        logging.error(f"Error setting variables from file '{key}' - {e}")


bucket_name = "bkt-mts-composer"
prefix = "variables/"

set_airflow_variables(bucket_name, prefix)
