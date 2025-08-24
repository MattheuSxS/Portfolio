import logging
from typing import Dict, Any, Union
from modules.bigquery import BigQuery
from modules.fk_products import FkCommerce
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
    try:
        logging.info("Checking request format and authorization...")
        dt_request = get_request_data(request)
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
