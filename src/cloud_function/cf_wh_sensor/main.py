import json
import time
import logging
from time import sleep
from datetime import datetime
from zoneinfo import ZoneInfo
from modules.pub_sub import PubSub
from typing import Dict, Any, Union
from modules.fk_sensor import FakeWhSensorData
from modules.secret_manager import get_request_data


# ******************************************************************************************************************** #
#                                              System Logging                                                          #
# ******************************************************************************************************************** #
logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)


# ******************************************************************************************************************** #
#                                               Auxiliary Function                                                     #
# ******************************************************************************************************************** #
def _process_batch(faker: FakeWhSensorData, pubsub: PubSub, batch_size: int) -> int:
    """
        Processes a batch of fake warehouse sensor data and publishes each data point using the provided
        PubSub publisher.

        Args:
            faker (FakeWhSensorData): An instance capable of generating fake warehouse sensor data.
            pubsub (PubSub): An object with a 'publisher' method for publishing messages.
            batch_size (int): The number of batches to process.

        Returns:
            int: The total number of messages successfully sent.

        Raises:
            Exception: Re-raises any exception encountered during message publishing to trigger a batch retry.
    """
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


# ******************************************************************************************************************** #
#                                               Main function                                                          #
# ******************************************************************************************************************** #
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

    metrics = {
        'success': 0,
        'fail': 0,
        'total_messages_sent': 0,
        'start_time': datetime.now(ZoneInfo('Europe/Dublin')).isoformat()
    }

    try:
        if type(request) != dict:
            dt_request = request.get_json()
        else:
            dt_request = request

        logging.info("Checking request format and authorization...")
        dt_request = get_request_data(dt_request)

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
    metrics['end_time'] = datetime.now(ZoneInfo('Europe/Dublin')).isoformat()
    metrics['duration_seconds'] = round(time.time() - start_time, 2)

    result = {
        "status": 200,
        "body": {
            "messages": "Processing completed successfully",
            **metrics
        }
    }

    logging.info(f"Processing completed. Result: {json.dumps(result, indent=2)}")
    return result


if __name__ == "__main__":
    main({
        "project_id": "mts-default-portofolio",
        "secret_id" : "ps_wh_sensor_access_authorization"
    })

