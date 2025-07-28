#TODO: I must get back to this file and make the necessary changes to adapt it to the new project structure.
# ================================================================================================================================= --
# Object................: Dags of datase Ls                                                                            .
# Creation Date.........: 2025/04/25                                                                                   |
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
from google.protobuf.duration_pb2 import Duration
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocSubmitJobOperator,
    DataprocDeleteClusterOperator,
)


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
__artefact__    = "Dag_etl_ls"
__start_job__   = datetime.now() - timedelta(days=1)
__description__ = "This DAG is responsible for extracting data from a source, processing \
                    it with PySpark, and loading it into a destination."


# ====================================================================================================================================
#                                           ~~~~> Variaveis Globais Airflow <~~~~                                                    #
# ====================================================================================================================================
__env_var__         = Variable.get(__artefact__, deserialize_json=True)

VAR_PRJ_NAME        = __env_var__['project_vars']
VAR_PRJ_NUMBER      = __env_var__['project_number']
VAR_CLOUD_FUNCTION  = __env_var__['cloud_functions']

VAR_DP_PROJECT_ID   = __env_var__['dataproc_config']['project_id']
VAR_DP_PRJ_REGION   = __env_var__['dataproc_config']['region']
VAR_DP_BUCKET       = __env_var__['dataproc_config']['cluster_config']['config_bucket']
VAR_DP_CLUSTER_NAME = __env_var__['dataproc_config']['cluster_name']
VAR_DP_SECRET_ID    = __env_var__['dataproc_config']['secret_id']


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
def dummy(name:str) -> EmptyOperator:
    return EmptyOperator(
        task_id=name
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


def call_cloud_function(cf_name:str) -> PythonOperator:
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
#                                                       ~~~~> Funções Utils <~~~~                                                    #
# ====================================================================================================================================
def get_pyspark_job_config(cfg, task_id) -> dict:
    """
        Generates and injects a unique job ID into the provided configuration dictionary for a PySpark job.

        The job ID is constructed by truncating the given `task_id` to 78 characters, appending an underscore,
        and then adding the current timestamp in the format "%Y%m%d%H%M%S%f". This job ID is set in
        `cfg["reference"]["job_id"]` and also appended to `cfg["pyspark_job"]["args"]`.

        Args:
            cfg (dict): The configuration dictionary to be updated with the job ID.
            task_id (str): The task identifier used as the base for the job ID.

        Returns:
            dict: The updated configuration dictionary with the new job ID.
    """
    job_id = task_id[0:78] + "_" + datetime.now().strftime("%Y%m%d%H%M%S%f")
    cfg["reference"]["job_id"] = job_id
    cfg["pyspark_job"]["args"].append(job_id)

    return cfg


# ====================================================================================================================================
#                                                    ~~~~> Variaveis DataProc <~~~~                                                  #
# ====================================================================================================================================
def select_dataproc_job(job_name: str) -> dict:
    """
        Selects and returns the necessary variables for configuring a Dataproc cluster and job.

        This function retrieves the project ID, region, cluster name, and secret ID from the global environment variables
        defined in __env_var__. It returns these variables in a dictionary format.

        Returns:
            dict: A dictionary containing:
                - "project_id" (str): The GCP project ID.
                - "region" (str): The region where the Dataproc cluster will be created.
                - "cluster_name" (str): The name of the Dataproc cluster.
                - "secret_id" (str): The secret ID for accessing sensitive data.
    """

    select_var = {
        "tb_order":\
            {
                "main_python_file_uri": f"gs://{VAR_DP_BUCKET}/job_tb_order/app_spark.py",
                "args": ["--output_path", f"gs://{VAR_DP_BUCKET}/job_tb_order/output", "--mode", "overwrite", "--data_secret", \
                        json.dumps({"project_id": VAR_DP_PROJECT_ID, "secret_id": VAR_DP_SECRET_ID})],
                "jar_file_uris": None,
            },

        "tb_feedback": {
            "main_python_file_uri": f"gs://{VAR_DP_BUCKET}/job_tb_feedback/app_spark.py",
            "args": ["--output_path", f"gs://{VAR_DP_BUCKET}/job_tb_feedback/output", "--mode", "overwrite", "--data_secret", \
                     json.dumps({"project_id": VAR_DP_PROJECT_ID, "secret_id": VAR_DP_SECRET_ID})],
            "jar_file_uris": None,
        }
    }


    return select_var[job_name]


def cluster_config(job_name: str = None) -> dict:
    """
        Configures and returns the Dataproc cluster and PySpark job settings.

        This function prepares the configuration for a Dataproc cluster and a PySpark job,
        including cluster name, cluster configuration, and job details. It sets specific
        lifecycle parameters such as idle and auto-delete time-to-live, software image version,
        and job arguments.

        Returns:
            dict: A dictionary containing:
                - "cluster_name" (str): The name of the Dataproc cluster.
                - "cluster_config" (dict): The configuration dictionary for the Dataproc cluster,
                including lifecycle and software settings.
                - "pyspark_job" (dict): The configuration for the PySpark job, including file URIs,
                arguments, and dependencies.

        Raises:
            KeyError: If required environment variables are missing from __env_var__.
    """
    durationIdle = Duration()
    durationIdle.seconds = 3600

    durationAuto = Duration()
    durationAuto.seconds = 3600 * (12 * 2 + 1)

    CLUSTER_NAME = __env_var__['dataproc_config']['cluster_name']
    CLUSTER_CONFIG = __env_var__['dataproc_config']['cluster_config']
    CLUSTER_CONFIG["gce_cluster_config"]["zone_uri"] = f"https://www.googleapis.com/compute/v1/projects/{VAR_DP_PROJECT_ID}/zones/us-east1-c" # In creating...
    # CLUSTER_CONFIG["gce_cluster_config"]["subnetwork_uri"] = "projects/shared-services-268518/regions/us-east1/subnetworks/shared" # In creating...
    # CLUSTER_CONFIG["gce_cluster_config"]["tags"] = CLUSTER_CONFIG["gce_cluster_config"]["tags"].extend('Test') # In creating...
    CLUSTER_CONFIG["software_config"]["image_version"] = "2.3-debian12"
    CLUSTER_CONFIG["lifecycle_config"]["idle_delete_ttl"] = durationIdle
    CLUSTER_CONFIG["lifecycle_config"]["auto_delete_ttl"] = durationAuto

    if job_name is not None:
        _pyspark_job = select_dataproc_job(job_name)
    else:
        _pyspark_job = {}

    PYSPARK_JOB = {
        "reference": {"project_id": VAR_PRJ_NAME},
        "placement": {"cluster_name": CLUSTER_NAME},
        "pyspark_job": _pyspark_job
    }

    return {
        "cluster_name": CLUSTER_NAME,
        "cluster_config": CLUSTER_CONFIG,
        "pyspark_job": PYSPARK_JOB
    }


# ====================================================================================================================================
#                                               ~~~~> Functions Cloud DataProc <~~~~                                                 #
# ====================================================================================================================================
def create_dataproc_cluster() -> DataprocCreateClusterOperator:
    """
        Creates and returns a DataprocCreateClusterOperator for provisioning a Dataproc cluster.

        Returns:
            DataprocCreateClusterOperator: An Airflow operator configured to create a Dataproc cluster
            with specified project, cluster name, labels, configuration, region, and error handling options.

        Raises:
            KeyError: If required keys are missing from the cluster configuration dictionary.
    """

    return \
        DataprocCreateClusterOperator(
            task_id             = f"create_dataproc_cluster",
            project_id          = VAR_DP_PROJECT_ID,
            cluster_name        = VAR_DP_CLUSTER_NAME,
            labels              = {"projeto": "vd", "vsname": "vendadireta"},
            cluster_config      = cluster_config()["cluster_config"],
            region              = VAR_DP_PRJ_REGION,
            delete_on_error     = True,
            use_if_exists       = True,
            retries             = 1,
            trigger_rule        = TriggerRule.ALL_DONE,
        )


def spark_submit_job(job_name: str) -> DataprocSubmitJobOperator:
    """
        Creates and returns a DataprocSubmitJobOperator for submitting a PySpark job to a Dataproc cluster.

        Returns:
            DataprocSubmitJobOperator: An Airflow operator configured to submit a PySpark job to Google Cloud Dataproc.

        Raises:
            KeyError: If required keys are missing in the cluster configuration dictionary.

        Notes:
            - The job configuration is retrieved using `get_pyspark_job_config` with parameters from `cluster_config`.
            - The operator is set to retry once and has an execution timeout of 30 minutes.
            - Uses global variables `VAR_DP_PRJ_REGION` and `VAR_DP_PROJECT_ID` for region and project ID.
    """

    # data_dict = cluster_config()
    return \
        DataprocSubmitJobOperator(
            task_id             = f"spark_submit_{job_name}_job",
            job                 = get_pyspark_job_config(cluster_config(job_name)["pyspark_job"], "get_data_cloud_sql"),
            region              = VAR_DP_PRJ_REGION,
            project_id          = VAR_DP_PROJECT_ID,
            retries             = 1,
            execution_timeout   = timedelta(minutes=30),
        )


def delete_dataproc_cluster() -> DataprocDeleteClusterOperator:
    """
        Creates a DataprocDeleteClusterOperator task to delete a Dataproc cluster.

        Returns:
            DataprocDeleteClusterOperator: An Airflow operator configured to delete the specified Dataproc cluster
            with the provided project ID, cluster name, region, trigger rule, and retry settings.

        Raises:
            AirflowException: If the operator fails to delete the cluster after the specified number of retries.

        Note:
            The function relies on the following variables being defined in the global scope:
                - VAR_DP_PROJECT_ID: GCP project ID where the Dataproc cluster resides.
                - VAR_DP_CLUSTER_NAME: Name of the Dataproc cluster to delete.
                - VAR_DP_PRJ_REGION: Region of the Dataproc cluster.
    """
    return \
        DataprocDeleteClusterOperator(
            task_id         = f"delete_dataproc_cluster",
            project_id      = VAR_DP_PROJECT_ID,
            cluster_name    = VAR_DP_CLUSTER_NAME,
            region          = VAR_DP_PRJ_REGION,
            trigger_rule    = TriggerRule.ALL_DONE,
            retries         = 2
        )


# ====================================================================================================================================
#                                                 ~~~~> Airflow Pipeline <~~~~                                                       #
# ====================================================================================================================================
with DAG(dag_id=__artefact__, start_date=default_args['start_date'], **dag_kwargs):

    dummy("Start") >> [
        call_cloud_function("cf-customers"),
        call_cloud_function("cf-products-inventory")
            ] >> create_dataproc_cluster() >> spark_submit_job("tb_order") \
                >> spark_submit_job("tb_feedback") >> delete_dataproc_cluster() >> dummy("End")