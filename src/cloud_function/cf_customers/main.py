import os
import json
import time
import logging
from time import sleep
from google.cloud import secretmanager
import google.api_core.exceptions


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
    check_authorization(dt_request)

    logging.info("Publishing fake data")
    success, fail = 0, 0

    # Define a duração máxima em segundos (3 minutos = 160 segundos)
    max_duration = 330
    start_time = time.time()

    while True:
        try:
            fk = FakeWhSensorData()

            pub = PubSub(
                dt_request["project_id"], dt_request["topic_id"],
                dt_request["subscriber"], dt_request["option"]
            )

            logging.info(f"Publishing data to topic: {dt_request['topic_id']}")
            for _ in range(5):
                for data in fk.generate_sensor_data():
                    pub.publisher(json.dumps(data))
                    logging.info(f"Data published: {data}")

            success += 1

            if (time.time() - start_time) >= max_duration:
                break
            else:
                sleep(5)

        except Exception as e:
            logging.error(f"Problem sending data \_O.o_/ ~~> {e}")
            fail += 1
            if fail >= 9:
                break

    logging.info(f"All data submissions completed")

    if fail >= 8:
        status = 401
    else:
        status = 200

    result = {
        "status": status,
        "body": \
            {
                "success": success,
                "fail:": fail
            }
    }

    return result


if __name__ == "__main__":
    data_dict = \
        dict(
            project_id  = "mts-default-projetct",
            secret_id   = "access_authorization",
            topic_id    = "portfolio-topic",
            subscriber  = "portfolio-subscription",
            option      = 1
        )
    main(data_dict)


