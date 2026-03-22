import logging
from airflow import DAG
from airflow.sdk import Variable
from datetime import timedelta, datetime
from airflow.providers.standard.operators.python import PythonOperator

# Configure o logger para ver as mensagens no log do Airflow
log = logging.getLogger(__name__)
__start_job__   = datetime.now() - timedelta(days=1)


def delete_airflow_variable(variable_name):
    """Deleta uma variável do Airflow."""
    try:
        Variable.delete(variable_name)
        log.info(f"Variável '{variable_name}' deletada com sucesso.")
    except Exception as e:
        log.error(f"Erro ao deletar a variável '{variable_name}': {e}")
        raise # Re-levanta a exceção para que a tarefa falhe se houver um problema

with DAG(
    dag_id='delete_composer_variable_dag',
    start_date=__start_job__,
    schedule=None,
    catchup=False,
    tags=['admin', 'variables'],
) as dag:
    delete_dag_etl_ls_variable = PythonOperator(
        task_id='delete_dag_etl_ls',
        python_callable=delete_airflow_variable,
        op_kwargs={'variable_name': 'Dag_etl_ls'},
    )