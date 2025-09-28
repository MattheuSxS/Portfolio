import json
import logging
import requests
from typing import List, Any, Dict, Generator


# Configure seu endpoint e, se necessário, o token de autenticação
API_URL = "http://localhost:8080/classify"
# Se for Cloud Run, use o URL completo e implemente o token de autenticação
# API_URL = "https://sentiment-analysis-app-XYZ.a.run.app/classify"
# AUTH_TOKEN = "..." # Obtenha o token de serviço do GCP, se o serviço for privado


def call_cloud_run(data_dict: Dict[str, Any]) -> str:
    logging.info(f"Enviando dados para: {API_URL}")

    headers = {
        "Content-Type": "application/json",
        # Se AUTH_TOKEN for definido, descomente a linha abaixo para autenticar
        # "Authorization": f"Bearer {AUTH_TOKEN}"
    }

    try:
        response = requests.post(
            API_URL,
            json=data_dict,
            headers=headers,
            timeout=120
        )

        response.raise_for_status()
        result = response.json()

        if result.get("status") != 200:
            logging.error(f"API logic failed. Message: {result.get('message', 'N/A')}")
            raise Exception(f"Internal API failure: {result.get('message', 'Unknown error')}")

        return result

    except requests.exceptions.HTTPError as err:
        logging.error(f"❌ HTTP Error {response.status_code}: {err}")
        logging.error(f"Raw server response: {response.text[:200]}...")
        raise Exception(f"HTTP request failure: {err}")

    except json.JSONDecodeError as err:
        logging.error(f"❌ JSONDecodeError: {err}")
        logging.error(f"Server returned something non-JSON: {response.text[:200]}...")
        raise Exception(f"API response is not JSON: {err}")

    except requests.exceptions.RequestException as err:
        logging.error(f"❌ General Connection Error: {err}")
        raise Exception(f"Connection error with API: {err}")


def split_into_batches(data: List[Any], batch_size: int) -> Generator[List[Any], None, None]:
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]
