import logging
from typing import Dict, Any, Union
from utils.helpers import ForecastingHelper
from utils.secret_manager import get_request_data


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
    try:
        logging.info("Checking request format and authorization...")
        dt_request = get_request_data(request)
        logging.info("Request validation successful...")

        helper = ForecastingHelper(
            project = dt_request["project_id"],
            dataset = dt_request["dataset_id"],
            table   = dt_request["table_id"]
        )
        helper.run_all()

        logging.info("All processes completed successfully.")

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
        "project_id": "gcp-mts-pf",
        "secret_id" : "bq_sales_access_authorization"
    })
