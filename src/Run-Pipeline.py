
#TODO: I must back here..
import subprocess
import shlex
import logging


# ******************************************************************************************************************** #
#                                              System Logging                                                          #
# ******************************************************************************************************************** #
logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)

# ******************************************************************************************************************** #
#                                               Main function                                                          #
def main(script_name, is_spark_job=False):
    try:
        logging.info(f"Executing script: {script_name}")
        # parse the script string into argv-style list so flags are passed correctly
        args = shlex.split(script_name)
        if is_spark_job:
            cmd = ['spark-submit'] + args
        else:
            cmd = ['python'] + args
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logging.info(f"Script {script_name} executed successfully.")
        logging.info(f"Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing script {script_name}.")
        logging.error(f"Error:\n{e.stderr or e.output or str(e)}")


scripts = [
    'src/cloud_function/cf_customers/main.py',
    'src/cloud_function/cf_products_inventory/main.py',
]

#spark-submit
spark_scripts = [
    'src/dataproc/dp_order/spark_job_tb_order.py --project_id mts-default-portofolio --dataset_id ls_customers --num_purchases 200000 --job_id job_23112741288',
]

for script in scripts:
    main(script)

for spark_script in spark_scripts:
    main(spark_script, is_spark_job=True)

logging.info("Pipeline executed successfully. \o.O/")
