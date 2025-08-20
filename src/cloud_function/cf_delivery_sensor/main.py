import json
from os import system
import time
import logging
from time import sleep
from datetime import datetime
from modules.pub_sub import PubSub
from typing import Dict, Any, Union
from modules.bigquery import BigQuery
from modules.delivery_sensor import DeliverySystem
from modules.secret_manager import get_credentials


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
# def _process_batch(faker: FakeWhSensorData, pubsub: PubSub, batch_size: int) -> int:
#     """Process a single batch of messages."""
#     messages_sent = 0
#     for _ in range(batch_size):
#         for data in faker.generate_sensor_data():
#             try:
#                 message = json.dumps(data)
#                 pubsub.publisher(message)
#                 messages_sent += 1
#                 logging.debug(f"Message published: {message[:100]}...")  # Log truncated message
#             except Exception as e:
#                 logging.warning(f"Failed to publish message: {str(e)}")
#                 raise  # Re-raise to trigger batch retry

#     return messages_sent


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
        'start_time': datetime.now().isoformat()
    }


    try:
        if type(request) != dict:
            dt_request = request.get_json()
        else:
            dt_request = request

        logging.info("Checking request format and authorization...")
        dt_request = get_credentials(dt_request)

        # bq = BigQuery(project=dt_request["project_id"])

        # data_dict = {}
        # for query in ['purchase_query', 'delivery_query']:
        #     result = bq.read_bq(
        #         query=bq.get_query(query)
        #     )

        #     data_dict[query] = result

        # delivery_system = DeliverySystem(
        #     client_list=data_dict['purchase_query'],
        #     vehicle_list=data_dict['delivery_query']
        # )

        # for client in delivery_system.clients:
        #     delivery_system.create_delivery(client.id)

        # delivery_system.monitor_deliveries(project_id=dt_request["project_id"], topic_id=dt_request["topic_id"])

    except Exception as main_error:
        logging.critical(f"Critical failure in main function: {str(main_error)}")
        return {
            "status": 500,
            "body": {
                "error": str(main_error),
                **metrics
            }
        }


if __name__ == "__main__":
    data_dict = \
        dict(
            project_id  = "mts-default-portofolio",
            topic_id    = "delivery_sensor_topic",
        )
    main(data_dict)


