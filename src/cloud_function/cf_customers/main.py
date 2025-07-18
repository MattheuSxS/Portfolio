import json
import time
import logging
import google.api_core.exceptions
from modules.bigquery import BigQuery
from google.cloud import secretmanager
from modules.fk_ids import FakeDataPerson
from modules.fk_address import FakeDataAddress
from modules.transformation import hide_data, add_columns, split_data


logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)


def check_authorization(data_dict: dict) -> bool:
    """
    Retrieves the secret key from Google Cloud Secret Manager.

    Args:
        data_dict (dict): A dictionary containing the project ID and secret ID.

    Returns:
        bool: True if the secret key is successfully retrieved, False otherwise.

    Raises:
        Exception: If access to the secret key is denied.

    """

    client      = secretmanager.SecretManagerServiceClient()
    secret_url  = {
        "name": f"projects/{data_dict['project_id']}/secrets/{data_dict['secret_id']}/versions/latest"
    }

    try:
        client.access_secret_version(secret_url)
        return True

    except google.api_core.exceptions.GoogleAPICallError as e:
        raise f"Access denied! --> {e}"


def generate_fake_data() -> dict:
    """
    Generates fake customer and card data.

    Args:
        row_numbers (dict): A dictionary containing the number of customers and cards to generate.

    Returns:
        dict: A dictionary containing lists of fake customer and card data.
    """

    fk_person   = FakeDataPerson()
    fk_address  = FakeDataAddress()

    return \
        {
            "customers" : fk_person.dict_customers(),
            "cards"     : fk_person.dict_card(),
            "address"   : fk_address.get_random_address()
        }


def main(request: dict) -> dict:

    if type(request) != dict:
        dt_request = request.get_json()
    else:
        dt_request = request

    logging.info("Validating access, please wait...")
    check_authorization(dt_request)
    logging.info("Access granted, proceeding with data generation...")

    logging.info("Generating fake data...")
    list_fake_data = [generate_fake_data() for _ in range(dt_request['row_number'])]

    logging.info("Hiding sensitive data...")
    list_fake_data = hide_data(list_fake_data)


    logging.info("Adding columns to the data...")
    list_fake_data = add_columns(list_fake_data)
    logging.info("Columns added successfully.")

    logging.info("Splitting data into customers, cards, and address...")
    structured_data = split_data(list_fake_data)
    logging.info("Data split successfully.")

    logging.info("Data structure ready for insertion into BigQuery.")
    logging.info("Inserting data into BigQuery...")
    bq_client = BigQuery(project=dt_request['project_id'])
    for table in dt_request['table_id']:
        logging.info(f"Inserting data into {dt_request['dataset_id']}.{table}...")
        bq_client.batch_load_from_memory(
            data    = structured_data[table],
            dataset = dt_request['dataset_id'],
            table   = table
        )
        logging.info(f"Data inserted successfully into {dt_request['dataset_id']}.{table}.")

    return list_fake_data


if __name__ == "__main__":
    request_dict = \
        {
            "row_number"    : 100_000,
            'project_id'    : 'mts-default-portofolio',
            'dataset_id'    : 'ls_customers',
            'table_id'      : ['tb_customers', 'tb_cards', 'tb_address'],
            'secret_id'     : 'your_secret_id'
        }


    main(request_dict)
    # for _ in list_data:
    #     # print(f"--- Endereço {i+1} ---")
    #     for chave, valor in _.items():
    #         print(f"{chave}: {valor}")
    #     print("-" * 20 + "\n")
    #     # i+= 1
        # print(_)
