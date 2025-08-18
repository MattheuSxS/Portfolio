#TODO: I must get back here tomorrow
import logging
from tqdm import tqdm
from typing import List, Dict
from modules.bigquery import BigQuery
from modules.fk_ids import FakeDataPerson
from modules.fk_address import FakeDataAddress
from modules.secret_manager import get_credentials
from modules.transformation import hide_data, add_columns, split_data



# logging.basicConfig(
#     format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
#             "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
#     level=logging.INFO
# )


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


def main(request: dict) -> dict:
    """
    Processes a request to generate, transform, and insert fake customer data into BigQuery tables.

    Args:
        request (dict): The request payload containing configuration parameters. If not a dict, attempts to parse JSON from the request object.

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

    disable_tqdm = logging.getLogger().level <= logging.INFO

    try:

        with tqdm(total=100, desc="🔄 Processing", disable=disable_tqdm) as pbar:
            if type(request) != dict:
                dt_request = request.get_json()
            else:
                dt_request = request
            pbar.update(5)

            logging.info("Validating access, please wait...")
            credentials = get_credentials(dt_request)
            pbar.update(10)  # 15%
            pbar.set_postfix_str("authorized access")

            logging.info("Generating fake data...")
            list_fake_data = generate_fake_data_bulk_cached(credentials['number_customers'])
            pbar.update(20)
            pbar.set_postfix_str("data generated")

            logging.info("Hiding sensitive data...")
            list_fake_data = hide_data(list_fake_data)
            pbar.update(10)

            logging.info("Adding columns to the data...")
            list_fake_data = add_columns(list_fake_data)
            pbar.update(10)
            pbar.set_postfix_str("columns added")

            logging.info("Splitting data into customers, cards, and address...")
            structured_data = split_data(list_fake_data)
            pbar.update(15)
            pbar.set_postfix_str("data split")
            logging.info("Data split successfully.")

            logging.info("Data structure ready for insertion into BigQuery.")
            logging.info("Inserting data into BigQuery...")
            bq_client = BigQuery(project=credentials['project_id'])
            tables = credentials['table_id']
            for i, table in enumerate(tables, 1):
                with tqdm(total=1, desc=f"📤 Inserindo {table}", leave=False, disable=disable_tqdm):
                    bq_client.batch_load_from_memory(
                        data=structured_data[table],
                        dataset=credentials['dataset_id'],
                        table=table
                    )
                pbar.update(30/len(tables))  # Progresso proporcional
                pbar.set_postfix_str(f"Tabela {i}/{len(tables)}")

            pbar.set_postfix_str("✅ Completo")
            pbar.update(100 - pbar.n)  # Garante 100%
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



