import logging
from datetime import datetime
from typing import Dict, Any, Union
from modules.bigquery import BigQuery
from modules.delivery_sensor import DeliverySystem
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
        dt_request = get_request_data(dt_request)

        logging.info("Checking BigQuery access...")
        bq = BigQuery(
            project = dt_request["project_id"]
            )

        data_dict = {}
        for query in ['purchase_query', 'delivery_query']:
            logging.info(f"Executing BigQuery for {query}...")
            result = bq.read_bq(
                query=bq.get_query(query)
            )

            data_dict[query] = result

        logging.info("Initializing DeliverySystem...")
        delivery_system = DeliverySystem(
            project_id      = dt_request["project_id"],
            topic_id        = dt_request["topic_id"],
            client_list     = data_dict['purchase_query'],
            vehicle_list    = data_dict['delivery_query']
        )

        logging.info("Creating deliveries...")
        for client in delivery_system.clients:
            delivery_system.create_delivery(client.id)

        logging.info("Monitoring deliveries...")
        metrics = delivery_system.monitor_deliveries()

        return {
            "status": 200,
            "body": {
                "message": "Whole message has been processed successfully.",
                **metrics
            }
        }

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
    data_dict = {
            "project_id": "mts-default-portofolio",
            "secret_id": "ps_delivery_sensor_access_authorization",
        }
    print(main(data_dict))