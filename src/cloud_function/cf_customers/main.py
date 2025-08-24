#TODO: I must get back here tomorrow
import logging
from typing import List, Dict
from modules.bigquery import BigQuery
from modules.fk_ids import FakeDataPerson
from modules.fk_address import FakeDataAddress
from modules.secret_manager import get_request_data
from modules.transformation import hide_data, add_columns, split_data


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
def generate_fake_data_bulk_cached(num_records: int) -> List[Dict]:
    """
        Generates a list of fake customer data records using cached faker instances.

        Args:
            num_records (int): The number of fake data records to generate.

        Returns:
            List[Dict]: A list of dictionaries, each containing fake customer, card, and address data.
    """
    fakers = {
        'person': FakeDataPerson(),
        'address': FakeDataAddress()
    }

    results = []
    for _ in range(num_records):
        results.append({
            "customers": fakers['person'].dict_customers(),
            "cards": fakers['person'].dict_card(),
            "address": fakers['address'].get_random_address()
        })
    return results


# ******************************************************************************************************************** #
#                                               Main function                                                          #
# ******************************************************************************************************************** #
def main(request: dict) -> dict:
    """
    Processes a request to generate, transform, and insert fake customer data into BigQuery tables.

    Args:
        request (dict): The request payload containing configuration parameters. If not a dict,
        attempts to parse JSON from the request object.

    Returns:
        list: A list of generated fake data records after processing.

    Raises:
        AuthorizationError: If the request fails authorization.
        KeyError: If required keys ('number_customers', 'project_id', 'table_id', 'dataset_id') are missing in the request.
        Exception: For errors during data generation, transformation, or insertion into BigQuery.

    Workflow:
        1. Validates and parses the request.
        2. Checks authorization.
        3. Generates fake data records.
        4. Hides sensitive data.
        5. Adds additional columns to the data.
        6. Splits data into structured components (customers, cards, address).
        7. Inserts structured data into specified BigQuery tables.
    """

    try:

        if type(request) != dict:
            dt_request = request.get_json()
        else:
            dt_request = request

        logging.info("Validating access, please wait...")
        credentials = get_request_data(dt_request)

        logging.info("Generating fake data...")
        list_fake_data = generate_fake_data_bulk_cached(credentials['number_customers'])

        logging.info("Hiding sensitive data...")
        list_fake_data = hide_data(list_fake_data)

        logging.info("Adding columns to the data...")
        list_fake_data = add_columns(list_fake_data)

        logging.info("Splitting data into customers, cards, and address...")
        structured_data = split_data(list_fake_data)
        logging.info("Data split successfully.")

        logging.info("Data structure ready for insertion into BigQuery.")
        logging.info("Inserting data into BigQuery...")
        bq_client = BigQuery(project=credentials['project_id'])
        tables = credentials['table_id']
        for _, table in enumerate(tables, 1):
            bq_client.batch_load_from_memory(
                data=structured_data[table],
                dataset=credentials['dataset_id'],
                table=table
            )

        logging.info("All data inserted successfully into BigQuery tables.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {
            "status": 500,
            "body": {
                "error": str(e)
            }
        }

    return {
            "status": 200,
            "body": {
                "message": f"Whole process completed successfully! {credentials['number_customers'] * 3} records processed."
            }
        }


if __name__ == "__main__":
    # request_dict = \
    #     {
    #         "number_customers"    : 200_000,
    #         'project_id'    : 'mts-default-portofolio',
    #         'dataset_id'    : 'ls_customers',
    #         'table_id'      : ['tb_customers', 'tb_cards', 'tb_address'],
    #         'secret_id'     : 'bq_customers_access_authorization'
    #     }

    # main(request_dict)
    main({
            "project_id": "mts-default-portofolio",
            "secret_id": "bq_customers_access_authorization"
        })



