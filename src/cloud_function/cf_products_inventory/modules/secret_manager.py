import json
import logging
import google.api_core.exceptions
from typing import Dict, Any, Union
from google.cloud import secretmanager


def _secret_manager(data_dict: dict) -> bool:
    """
        Retrieves and decodes a secret from Google Cloud Secret Manager.

        Args:
            data_dict (dict): Dictionary containing secret access parameters.
                Expected keys:
                    - 'project_id' (str): Google Cloud project ID
                    - 'secret_id' (str): Secret identifier/name

        Returns:
            dict: Parsed JSON content of the secret payload

        Raises:
            str: Formatted error message when access to the secret is denied

        Note:
            The function return type annotation indicates 'bool' but actually
            returns a dict (parsed JSON) or raises an exception.
    """
    client      = secretmanager.SecretManagerServiceClient()
    secret_url  = {
        "name": f"projects/{data_dict['project_id']}/secrets/{data_dict['secret_id']}/versions/latest"
    }

    try:
        result = client.access_secret_version(secret_url)
        return json.loads(result.payload.data.decode("UTF-8"))

    except google.api_core.exceptions.GoogleAPICallError as e:
        logging.error(f"It hasn't been possible to access the secret: {e}")
        raise f"Access denied! --> {e}"


def get_request_data(request: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
    """
        Extracts and validates request data from the incoming request.

        This function checks if the request is in the expected format and contains all
        required fields. It also handles authorization by accessing secrets from Google
        Secret Manager.

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

    dt_request = _secret_manager(dt_request)
    logging.info("Request validation successful...")

    required_fields = ["project_id", "topic_id"]
    for field in required_fields:
        if field not in dt_request:
            raise ValueError(f"Missing required field: {field}")

    return dt_request