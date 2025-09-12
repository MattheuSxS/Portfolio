#TODO: I must finish it later [0]
import logging
import argparse
import apache_beam as beam
from apache_beam.transforms import ParDo
from modules.bigquery import get_schema_from_bigquery
from modules.helpers import MessageParser, SelectFields
from apache_beam.options.pipeline_options import PipelineOptions


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
def pipeline_run(exec_mode:str, region:str, job_name:str,
                    bkt_dataflow:str, project:str, dataset:str,
                        table:str, subscription:str) -> None:

    PROJECT_ID      = project
    DATASET_ID      = dataset
    TABLES_ID       = table
    SUBSCRIPTION_ID = f"projects/{PROJECT_ID}/subscriptions/{subscription}"
    BQ_SCHEMA       = get_schema_from_bigquery(PROJECT_ID, DATASET_ID, TABLES_ID)

    options = \
        PipelineOptions(
            runner                      = exec_mode,
            project                     = project,
            region                      = region,
            job_name                    = job_name,
            num_workers                 = 1,
            max_num_workers             = 2,
            machine_type                = 'n2-standard-4',
            worker_machine_type         = 'n2-standard-4',
            staging_location            = f"gs://{bkt_dataflow}/staging",
            temp_location               = f"gs://{bkt_dataflow}/temp",
            streaming                   = True
        )


    with beam.Pipeline(options=options) as p:
        get_messages = (
            p
            | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(
                subscription    = SUBSCRIPTION_ID,
                with_attributes = False
            )
            | 'Efficient Parse Message' >> ParDo(MessageParser())
        )

        treat_the_data = (
            get_messages
            | 'Select the fields' >> ParDo(SelectFields())
            | 'Filter the datas' >> beam.Filter(lambda x: x['status'] != 'in_route')
        )

        whitelisted = (
            treat_the_data
                | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
                    table                   = f"{PROJECT_ID}.{DATASET_ID}.{TABLES_ID}",
                    schema                  = BQ_SCHEMA,
                    create_disposition      = beam.io.BigQueryDisposition.CREATE_NEVER,
                    write_disposition       = beam.io.BigQueryDisposition.WRITE_APPEND,
                    method                  = beam.io.WriteToBigQuery.Method.STREAMING_INSERTS
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
        "--subscription",
        type=str,
        required=True,
        help="Choose which subscription apache-beam will used!"
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
            subscription        = args.subscription
        )
