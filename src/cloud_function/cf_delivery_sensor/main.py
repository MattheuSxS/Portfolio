import json
import time
import logging
from time import sleep
from flask import jsonify
from datetime import datetime
from modules.pub_sub import PubSub
from typing import Dict, Any, Union
from google.cloud import secretmanager
from modules.sensor import FakeWhSensorData


logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)


# def check_authorization(data_dict: dict) -> bool:
#     """
#     Retrieves the secret key from Google Cloud Secret Manager.

#     Args:
#         data_dict (dict): A dictionary containing the project ID and secret ID.

#     Returns:
#         bool: True if the secret key is successfully retrieved, False otherwise.

#     Raises:
#         Exception: If access to the secret key is denied.

#     """

#     client      = secretmanager.SecretManagerServiceClient()
#     secret_url  = {
#         "name": f"projects/{data_dict['project_id']}/secrets/{data_dict['secret_id']}/versions/latest"
#     }

#     try:
#         client.access_secret_version(secret_url)
#         return True

#     except google.api_core.exceptions.GoogleAPICallError as e:
#         raise f"Access denied! --> {e}"


# def main(request: dict) -> dict:
#     """
#     Entry point function for the Cloud Function.

#     Args:
#         request (dict): The request payload.

#     Returns:
#         dict: The response payload.
#     """

#     if type(request) != dict:
#         dt_request = request.get_json()
#     else:
#         dt_request = request

#     logging.info("Validating access, please wait...")
#     check_authorization(dt_request)

#     logging.info("Publishing fake data")
#     success, fail = 0, 0

#     # Define a duração máxima em segundos (3 minutos = 160 segundos)
#     max_duration = 330
#     start_time = time.time()

#     while True:
#         try:
#             fk = FakeWhSensorData()

#             pub = PubSub(
#                 dt_request["project_id"], dt_request["topic_id"],
#                 dt_request["subscriber"], dt_request["option"]
#             )

#             logging.info(f"Publishing data to topic: {dt_request['topic_id']}")
#             for _ in range(5):
#                 for data in fk.generate_sensor_data():
#                     pub.publisher(json.dumps(data))
#                     logging.info(f"Data published: {data}")

#             success += 1

#             if (time.time() - start_time) >= max_duration:
#                 break
#             else:
#                 sleep(5)

#         except Exception as e:
#             logging.error(f"Problem sending data \_O.o_/ ~~> {e}")
#             fail += 1
#             if fail >= 9:
#                 break

#     logging.info(f"All data submissions completed")

#     if fail >= 8:
#         status = 500
#     else:
#         status = 200

#     result = {
#         "status": status,
#         "body": \
#             {
#                 "success": success,
#                 "fail:": fail
#             }
#     }

#     return result

def _validate_and_parse_request(request: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
    """Validate and parse the incoming request."""
    if isinstance(request, dict):
        dt_request = request
    else:
        try:
            dt_request = request.get_json()
        except Exception as e:
            raise ValueError(f"Invalid request format: {str(e)}")

    required_fields = ["project_id", "topic_id", "subscriber", "option"]
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
        'start_time': datetime.timezone().isoformat()
    }

    try:
        # Validate and parse input
        dt_request = _validate_and_parse_request(request)
        logging.info("Request validation successful. Starting data publication...")

        # Initialize components
        faker = FakeWhSensorData()
        pubsub = PubSub(
            project_id  = dt_request["project_id"],
            topic_id    = dt_request["topic_id"],
            subscriber  = dt_request["subscriber"],
            option      = dt_request["option"]
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
    metrics['end_time'] = datetime.timezone().isoformat()
    metrics['duration_seconds'] = round(time.time() - start_time, 2)

    result = {
        "status": 200 if metrics['fail'] < retry_limit else 500,
        "body": metrics
    }

    logging.info(f"Processing completed. Result: {json.dumps(result, indent=2)}")
    return result





if __name__ == "__main__":
    data_dict = \
        dict(
            project_id  = "mts-default-portofolio",
            secret_id   = "access_authorization",
            topic_id    = "wh_sensor_topic",
            subscriber  = "wh_sensor_subs",
            option      = 1
        )
    main(data_dict)


