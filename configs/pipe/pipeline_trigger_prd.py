# ================================================================================================================================= --
# Object................: Portfolio                                                                                    .
# Creation Date.........: 2025/04/15                                                                                   |
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
from airflow.decorators import task
from datetime import timedelta, datetime
from google.protobuf.duration_pb2 import Duration
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
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
__artefact__    = "pipeline_trigger_prd"
__start_job__   = datetime.now() - timedelta(days=1)
__description__ = "Pipeline Trigger - GCP"


# ====================================================================================================================================
#                                           ~~~~> Variaveis Globais Airflow <~~~~                                                    #
# ====================================================================================================================================
__env_var__         = Variable.get(__artefact__, deserialize_json=True)


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
        task_id=name
    )


# ====================================================================================================================================
#                                                 ~~~~> Airflow Pipeline <~~~~                                                       #
# ====================================================================================================================================
with DAG(dag_id=__artefact__, start_date=default_args['start_date'], **dag_kwargs):

    dummy("Start") >> dummy("End")