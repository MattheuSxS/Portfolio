import json
import logging
import google.api_core.exceptions
from typing import Dict, Any, Union
from modules.bigquery import BigQuery
from google.cloud import secretmanager
from modules.fk_products import FkCommerce


logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)


def check_authorization(data_dict: dict) -> bool:
    """
        Checks authorization by accessing a secret from Google Secret Manager.

        Args:
            data_dict (dict): A dictionary containing 'project_id' and 'secret_id' keys required to locate the secret.

        Returns:
            bool: The decoded secret value as a boolean.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If access to the secret fails.
    """

    client      = secretmanager.SecretManagerServiceClient()
    secret_url  = {
        "name": f"projects/{data_dict['project_id']}/secrets/{data_dict['secret_id']}/versions/latest"
    }

    try:
        result = client.access_secret_version(secret_url)
        return json.loads(result.payload.data.decode("UTF-8"))

    except google.api_core.exceptions.GoogleAPICallError as e:
        logging.error(f"Access to secret key denied")
        raise f"Access denied! --> {e}"


def _validate_and_parse_request(request: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
    """
        Validates and parses an incoming request for required fields and authorization.

        This function accepts a request object, which can be either a dictionary or an object
        with a `get_json()` method (such as a Flask request). It ensures the request contains
        the required fields and passes authorization checks.

        Args:
            request (Union[Dict[str, Any], Any]): The incoming request data, either as a dictionary
                or an object with a `get_json()` method.

        Returns:
            Dict[str, Any]: The validated and parsed request data as a dictionary.

        Raises:
            ValueError: If the request format is invalid, authorization fails, or any required
                field is missing.
    """
    if isinstance(request, dict):
        dt_request = request
    else:
        try:
            dt_request = request.get_json()
        except Exception as e:
            raise ValueError(f"Invalid request format: {str(e)}")

    dt_request = check_authorization(dt_request)
    logging.info("Request validation successful...")

    required_fields = ["project_id", "dataset_id", "table_id", "number_products"]
    for field in required_fields:
        if field not in dt_request:
            raise ValueError(f"Missing required field: {field}")

    return dt_request


def main(request: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
    try:
        logging.info("Checking request format and authorization...")
        dt_request = _validate_and_parse_request(request)
        logging.info("Request validation successful...")

        # Initialize components
        bigquery = BigQuery(
            project=dt_request["project_id"]
        )
        fk_products = FkCommerce()
        data_dict = fk_products.generate_complete_dataset(dt_request["number_products"])

        #Insert datas into BigQuery
        for table, data in data_dict.items():
            if not data:
                logging.warning(f"No data to insert into {table}. Skipping...")
                continue

            logging.info(f"Inserting {len(data)} rows into {table}...")
            bigquery.batch_load_from_memory(
                data    = data,
                dataset = dt_request["dataset_id"],
                table   = table
            )
            logging.info(f"Inserted {len(data)} rows into {table} successfully.")
        logging.info("All data inserted successfully into BigQuery.")

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return {
            "status": 500,
            "body": {
                "error": str(e)
            }
        }

    return {
        "status": 200,
        "body": {
            "message": "Products generated and inserted successfully."
        }
    }


if __name__ == "__main__":
    main({
        "project_id": "mts-default-portofolio",
        "secret_id" : "bq_products_access_authorization"
    })
