import json
import time
import logging
from time import sleep
from datetime import datetime
import google.api_core.exceptions
from modules.pub_sub import PubSub
from typing import Dict, Any, Union
from google.cloud import secretmanager
from modules.sensor import FakeWhSensorData


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
    """Validate and parse the incoming request."""
    if isinstance(request, dict):
        dt_request = request
    else:
        try:
            dt_request = request.get_json()
        except Exception as e:
            raise ValueError(f"Invalid request format: {str(e)}")

    dt_request = check_authorization(dt_request)
    logging.info("Request validation successful...")

    required_fields = ["project_id", "topic_id"]
    for field in required_fields:
        if field not in dt_request:
            raise ValueError(f"Missing required field: {field}")

    return dt_request


def _process_batch(faker: FakeWhSensorData, pubsub: PubSub, batch_size: int) -> int:
    """Process a single batch of messages."""
    messages_sent = 0
    for _ in range(batch_size):
        for data in faker.generate_sensor_data():
            try:
                message = json.dumps(data)
                pubsub.publisher(message)
                messages_sent += 1
                logging.debug(f"Message published: {message[:100]}...")  # Log truncated message
            except Exception as e:
                logging.warning(f"Failed to publish message: {str(e)}")
                raise  # Re-raise to trigger batch retry

    return messages_sent


def main(request: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
    """
    Entry point function for the Cloud Function that publishes fake sensor data to Pub/Sub.

    Args:
        request: The request payload which can be either a dict or a Flask request object.

    Returns:
        A dictionary containing:
        - status: HTTP status code (200 for success, 500 for critical failures)
        - body: Dictionary with success/failure counts and optional error messages

    Raises:
        ValueError: If the request format is invalid
    """

    # Initialize counters and metrics
    metrics = {
        'success': 0,
        'fail': 0,
        'total_messages_sent': 0,
        'start_time': datetime.now().isoformat()
    }

    try:
        # Validate and parse input
        dt_request = _validate_and_parse_request(request)
        logging.info("Request validation successful. Starting data publication...")

        # Initialize components
        faker = FakeWhSensorData()
        pubsub = PubSub(
            project_id  = dt_request["project_id"],
            topic_id    = dt_request["topic_id"]
        )

        # Main processing loop
        max_duration = 330  # 5.5 minutes in seconds
        batch_size = 5
        retry_limit = 9
        delay_between_batches = 5

        start_time = time.time()

        while (time.time() - start_time) < max_duration and metrics['fail'] < retry_limit:
            try:
                messages_sent = _process_batch(faker, pubsub, batch_size)
                metrics['total_messages_sent'] += messages_sent
                metrics['success'] += 1

                logging.info(f"Batch processed successfully. Total messages sent: {metrics['total_messages_sent']}")

                if (time.time() - start_time) < max_duration:
                    sleep(delay_between_batches)

            except Exception as batch_error:
                metrics['fail'] += 1
                logging.error(f"Batch processing failed (attempt {metrics['fail']}): {str(batch_error)}")

                if metrics['fail'] >= retry_limit:
                    logging.critical("Maximum retry limit reached. Stopping processing.")
                    break

    except Exception as main_error:
        logging.critical(f"Critical failure in main function: {str(main_error)}")
        return {
            "status": 500,
            "body": {
                "error": str(main_error),
                **metrics
            }
        }

    # Prepare final result
    metrics['end_time'] = datetime.now().isoformat()
    metrics['duration_seconds'] = round(time.time() - start_time, 2)

    result = {
        "status": 200 if metrics['fail'] < retry_limit else 500,
        "body": metrics
    }

    logging.info(f"Processing completed. Result: {json.dumps(result, indent=2)}")
    return result


if __name__ == "__main__":
    main({
        "project_id": "mts-default-portofolio",
        "secret_id" : "ps_wh_sensor_access_authorization"
    })


