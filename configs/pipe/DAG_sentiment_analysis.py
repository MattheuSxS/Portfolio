# ================================================================================================================================= --
# Object................: Dags of execution of sentiment analysis job                                                  .
# Creation Date.........: 2025/11/30                                                                                   |
# Version...............: 0.1.0                                                                                       < >
# Project...............: Technical challenge                                                                          |
# VS....................:                                                                  ______                    (^ ^)
# Department............: Data Architecture and Engineering                      .-,__,-. |Eatons|                    `|`
# Owner.................: Management: gd13 - B2C Engineering                     | ]""[ | |""""""|       ,.,__         |
# Author................: Matheus Dos S. Silva | matheus.s@                      | |""| | |""""""|     /`.     ` ;     |
# maintainer............:                                                        | |""| | |""""""|   /`.  '.       ;   |
# Modification Date.....:                                                        | |""| | |""""""| /`.  '.  .       ; /^\
# Obs...................:                                    ---Toronto----------'-'--'-'-'------''---'---'--'-------'---'----ldb
# ================================================================================================================================= --


import logging
from airflow.sdk import DAG
from airflow.sdk import Variable
from datetime import timedelta, datetime
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.google.cloud.operators.cloud_run import CloudRunExecuteJobOperator


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
__artefact__    = "DAG_sentiment_analysis"
__start_job__   = datetime.now() - timedelta(days=1)
__description__ = "This DAG is responsible for extracting data from a feature source, processing \
                    it with PySpark/Cloud Dataflow/Cloud Function/Bigquery, and loading it into a destination."


# ====================================================================================================================================
#                                           ~~~~> Variaveis Globais Airflow <~~~~                                                    #
# ====================================================================================================================================
__env_var__         = Variable.get(__artefact__, deserialize_json=True)

VAR_PRJ_NAME        = __env_var__["project_vars"]
VAR_PRJ_NUMBER      = __env_var__["project_number"]

VAR_AR_PROJECT_ID   = __env_var__["Artifact_registry"]["project_id"]
VAR_AR_REGION       = __env_var__["Artifact_registry"]["region"]
VAR_AR_REPOSITORY   = __env_var__["Artifact_registry"]["repository"]
VAR_AR_IMAGE        = __env_var__["Artifact_registry"]["image"]



# ====================================================================================================================================
#                                           ~~~~> Propriedades da DAG <~~~~                                                          #
# ====================================================================================================================================
default_args = dict(
    owner           = "Matheus S. Silva",
    start_date      =  __start_job__,
    depends_on_past = False,
    retries         = 3,
    retry_delay     = timedelta(minutes=__env_var__["retry_delay"]),
    dagrun_timeout  = timedelta(minutes=__env_var__["dagrun_timeout"]),
)

dag_kwargs = dict(
    default_args        = default_args,
    description         = __description__,
    schedule            = __env_var__["schedule_interval"],
    catchup             = False,
    max_active_runs     = 2,
    tags                = ["MTS - Pipeline"],
)


# ====================================================================================================================================
#                                                     ~~~~> Functions <~~~~                                                          #
# ====================================================================================================================================
def dummy(name:str) -> EmptyOperator:
    return EmptyOperator(
        task_id=name
    )


# ====================================================================================================================================
#                                             ~~~~> Functions Cloud Kubernetes <~~~~                                                 #
# ====================================================================================================================================
def feedback_sentiment_analysis() -> CloudRunExecuteJobOperator:
    return CloudRunExecuteJobOperator(
        task_id                 = f"run_{VAR_AR_IMAGE}",
        job_name                = VAR_AR_IMAGE,
        project_id              = VAR_AR_PROJECT_ID,
        region                  = VAR_AR_REGION,
        overrides               = {},
        gcp_conn_id             = "google_cloud_default",
        polling_period_seconds  = 15,
    )


# ====================================================================================================================================
#                                                 ~~~~> Airflow Pipeline <~~~~                                                       #
# ====================================================================================================================================
with DAG(dag_id=__artefact__, start_date=default_args["start_date"], **dag_kwargs):

    dummy("Start") >> feedback_sentiment_analysis() >> dummy("End")