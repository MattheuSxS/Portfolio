# ================================================================================================================================= --
# Object................: Sensor WareHouse | Delivery                                                                  .
# Creation Date.........: 2025/07/24                                                                                   |
# Version...............: 0.0.1                                                                                       < >
# Project...............: Technical challenge                                                                          |
# VS....................:                                                                  ______                    (^ ^)
# Department............: Arquitetura e Engenharia de Dados                      .-,__,-. |Eatons|                    `|`
# Owner.................: Gerencia: gd13 - Engenharia B2C                        | ]""[ | |""""""|       ,.,__         |
# Author................: Matheus Dos S. Silva | matheus.s@                      | |""| | |""""""|     /`.     ` ;     |
# maintainer............:                                                        | |""| | |""""""|   /`.  '.       ;   |
# Modification Date.....:                                                        | |""| | |""""""| /`.  '.  .       ; /^\
# Obs...................:                                    ---Toronto----------'-'--'-'-'------''---'---'--'-------'---'----ldb
# ================================================================================================================================= --

import json
import logging
import subprocess
from airflow import DAG
from airflow.models import Variable
from datetime import timedelta, datetime
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator


# ====================================================================================================================================
#                                                  ~~~~> Loggin Globais <~~~~                                                        #
# ====================================================================================================================================
logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)


# ====================================================================================================================================
#                                              ~~~~> Variaveis Globais <~~~~                                                         #
# ====================================================================================================================================
__artefact__    = "DAG_sensor"
__start_job__   = datetime.now() - timedelta(days=1)
__description__ = "This DAG is responsible for simulating the delivery of sensor data to a Pub/Sub topic."


# ====================================================================================================================================
#                                           ~~~~> Variaveis Globais Airflow <~~~~                                                    #
# ====================================================================================================================================
__env_var__         = Variable.get(__artefact__, deserialize_json=True)

VAR_PRJ_NAME        = __env_var__['project_vars']
VAR_PRJ_NUMBER      = __env_var__['project_number']
VAR_CLOUD_FUNCTION  = __env_var__['cloud_functions']


# ====================================================================================================================================
#                                           ~~~~> Propriedades da DAG <~~~~                                                          #
# ====================================================================================================================================
default_args = dict(
    owner           = "Matheus S. Silva",
    start_date      =  __start_job__,
    depends_on_past = False,
    retries         = 3,
    retry_delay     = timedelta(minutes=__env_var__['retry_delay']),
    dagrun_timeout  = timedelta(minutes=__env_var__['dagrun_timeout']),
)

dag_kwargs = dict(
    default_args        = default_args,
    description         = __description__,
    schedule_interval   = __env_var__['schedule_interval'],
    catchup             = False,
    concurrency         = 2,
    tags                = ["MTS - Pipeline"],
)


# ====================================================================================================================================
#                                                     ~~~~> Functions <~~~~                                                          #
# ====================================================================================================================================
def dummy(name:str) -> None:
    return EmptyOperator(
        task_id=name,
    )

def _call_cloud_function(data_dict:dict, cf_name:str) -> str:
    """
    Calls a Google Cloud Function using a POST request with curl.

    This function constructs a curl command to call a Google Cloud Function.
    It includes an authorization token and sends a JSON payload. The response
    from the cloud function is then parsed and checked for success.

    Returns:
        str: A string indicating the status and message from the cloud function response.

    Raises:
        Exception: If the cloud function response status is not "success", an exception is raised with the response message.
    """
    function_url = data_dict['cloud_function_url'].format(
        VAR_CF_NAME=cf_name,
        VAR_PRJ_NUMBER=VAR_PRJ_NUMBER
    )
    cmd = \
        f"""
            curl -X POST {function_url} \
                -H "Authorization: bearer $(gcloud auth print-identity-token)" \
                -H "Content-Type: application/json" \
                -d '{json.dumps(data_dict['cloud_function_dict'])}'
        """
    logging.info(f"Executando comando: {cmd}")

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    response = stdout.decode('utf-8').strip()

    result = json.loads(response)
    if result["status"] != 200:
        logging.error(f"Cloud Function call failed, please check the logs.....")
        raise Exception(result['body'])

    return f"Status: {result['status']} {result['body']}"


def call_cloud_function(cf_name:str) -> str:
    """
        Creates and returns a PythonOperator to call a specified Cloud Function.

        Args:
            cf_name (str): The name of the Cloud Function to be called. This is also used as the task_id for the operator.

        Returns:
            PythonOperator: An Airflow PythonOperator configured to call the specified Cloud Function with the appropriate arguments.

        Raises:
            KeyError: If the provided cf_name does not exist in VAR_CLOUD_FUNCTION.
    """

    return PythonOperator(
        python_callable=_call_cloud_function,
        task_id=cf_name,
        op_kwargs={
            'data_dict': VAR_CLOUD_FUNCTION[cf_name],
            'cf_name': cf_name
        }
    )

# ====================================================================================================================================
#                                                 ~~~~> Airflow Pipeline <~~~~                                                       #
# ====================================================================================================================================
with DAG(dag_id=__artefact__, start_date=default_args['start_date'], **dag_kwargs):

    # dummy("Start") >> [
    #     call_cloud_function("cf-wh-sensor"),
    #     call_cloud_function("cf-delivery-sensor")
    # ] >> dummy("End")

    dummy("Start") >> call_cloud_function("cf-wh-sensor") >> dummy("End")