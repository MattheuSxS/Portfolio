import json
import logging
import google.api_core.exceptions
from google.cloud import secretmanager
from modules.bq_feedback import BigQueryFeedback
from modules.fake_data_feedback import FakeFeedbackData


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
        result = client.access_secret_version(secret_url)
        return json.loads(result.payload.data.decode("UTF-8"))

    except google.api_core.exceptions.GoogleAPICallError as e:
        raise f"Access denied! --> {e}"

#TODO: I need to try this function yet..
def main(request: dict) -> dict:
    """
    Entry point function for the Cloud Function.

    Args:
        request (dict): The request payload.

    Returns:
        dict: The response payload.
    """

    if type(request) != dict:
        dt_request = request.get_json()
    else:
        dt_request = request

    logging.info("Validating access, please wait...")
    credentials = check_authorization(dt_request)

    try:
        logging.info("Access granted!")
        logging.info("Generating fake feedback data...")
        fake_data   = FakeFeedbackData()
        df_fake     = fake_data.generate_fake_feedbacks(num_feedbacks=1000)
        logging.info("Fake feedback data generated successfully!")
        logging.info("Inserting data into BigQuery...")
        BigQueryFeedback(
            project = credentials["project"],
            dataset = credentials["dataset"],
            table   = credentials["table"]
        ).insert_data(df_fake)
        logging.info("Data inserted successfully!")
        return {
            "status": "success",
            "message": "Fake feedback data generated and inserted into BigQuery successfully!"
        }
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    data_dict = \
        dict(
            project_id  = "mts-default-projetct",
            secret_id   = "bq_fb_access_authorization"
        )
    main(data_dict)


