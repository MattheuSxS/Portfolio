import logging
import argparse
import apache_beam as beam
from apache_beam.transforms import ParDo
from utils.bigquery import get_schema_from_bigquery
from apache_beam.options.pipeline_options import PipelineOptions
from utils.helpers import MessageParser, Kwargs, write_to_bigquery


# ******************************************************************************************************************** #
#                                              System Logging                                                          #
# ******************************************************************************************************************** #
logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)


# ******************************************************************************************************************** #
#                                              Dataflow Pipeline                                                       #
# ******************************************************************************************************************** #
def pipeline_run(exec_mode:str, region:str, job_name:str, bkt_dataflow:str, project:str, dataset:str,
                 table:str, topics:str) -> None:

    PROJECT_ID  = project
    DATASET_ID  = dataset
    TABLE_ID    = table
    TOPIC_ID    = f"projects/{project}/topics/{topics}"

    tb_anomalies   = get_schema_from_bigquery(
        PROJECT_ID, DATASET_ID, f"{TABLE_ID}_anomalies"
        )
    tb_normal_data = get_schema_from_bigquery(
        PROJECT_ID, DATASET_ID, TABLE_ID
        )

    options = \
        PipelineOptions(
            runner                      = exec_mode,
            project                     = PROJECT_ID,
            region                      = region,
            job_name                    = job_name,
            num_workers                 = 1,
            max_num_workers             = 2,
            machine_type                = 'n4-standard-2',
            worker_machine_type         = 'n4-standard-2',
            staging_location            = f"gs://{bkt_dataflow}/staging",
            temp_location               = f"gs://{bkt_dataflow}/temp",
            streaming                   = True,
            experiments                 = [
                                            'use_runner_v2',
                                            'max_batch_size=10000'
                                          ],
            save_main_session           = True
        )

    def is_anomaly(element):
        return (element['temperature'] > 30.0 or
                element['humidity'] < 30 or
                element['pressure'] < 1000.0)

    with beam.Pipeline(options=options) as p:
        get_messages = (
            p
            | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(
                topic           = TOPIC_ID,
                with_attributes = False
            )
            | 'Efficient Parse Message' >> ParDo(MessageParser())
        )

        anomalies, normal_data = (
            get_messages
            | 'Flatten' >> beam.ParDo(Kwargs())
            | 'Split by Anomaly' >> beam.Partition(
                lambda elem, num_partitions: 0 if is_anomaly(elem) else 1, 2
            )
        )

        _ = (
            anomalies
            | 'Write Anomalies' >> write_to_bigquery(
                PROJECT_ID, DATASET_ID, f"{TABLE_ID}_anomalies", tb_anomalies
            )
        )

        _ = (
            normal_data
            | 'Write Normal Data' >> write_to_bigquery(
                PROJECT_ID, DATASET_ID, TABLE_ID, tb_normal_data
            )
        )

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--runner",
        type=str,
        choices=['DataflowRunner', 'DirectRunner'],
        required=False,
        default='DirectRunner',
        help="Choose where apache-beam will run!"
    )
    parser.add_argument(
        "--project",
        type=str,
        required=True,
        help="What project will be used to get the schema!"
    )
    parser.add_argument(
        "--region",
        type=str,
        required=True,
        help="What region will stay the apache-beam!"
    )
    parser.add_argument(
        "--job_name",
        type=str,
        required=True,
        help="Name the job!"
    )
    parser.add_argument(
        "--bkt_dataflow",
        type=str,
        required=True,
        help="In which bucket will stay the files!"
    )

    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="What dataset will be used to get the schema!"
    )

    parser.add_argument(
        "--table",
        type=str,
        required=True,
        help="What table will be used to get the schema!"
    )

    parser.add_argument(
        "--topics",
        type=str,
        required=True,
        help="Choose which topics apache-beam will used!"
    )

    parser.add_argument(
        "--setup_file",
        type=str,
        required=False,
        help="Path to the setup.py file."
    )

    parser.add_argument(
        "--extra_package",
        type=str,
        required=False,
        help="Path to the extra package."
    )

    parser.add_argument(
        "--template_location",
        type=str,
        required=False,
        help="Path to the template location."
    )

    args = parser.parse_args()

    pipeline_run(
            exec_mode           = args.runner,
            project             = args.project,
            region              = args.region,
            job_name            = args.job_name,
            bkt_dataflow        = args.bkt_dataflow,
            dataset             = args.dataset,
            table               = args.table,
            topics              = args.topics
        )