import argparse
import apache_beam as beam
from apache_beam.transforms import window
from apache_beam.options.pipeline_options import PipelineOptions
from modules.functions import (
    parse_pubsub_message, split_dict, ConvertToTableRowFn, \
                                    get_schema, write_to_bigquery
)

#TODO: Redoing whole file, because had plan changes.
def pipeline_run(exec_mode:str, project_dataflow:str, region:str, job_name:str,
                 bkt_dataflow:str, project:str, dataset:str, subscription:str) -> None:

    project_id      = project
    dataset_id      = dataset
    subscription_id = f"projects/{project_id}/subscriptions/{subscription}"


    options = \
        PipelineOptions(
            runner                      = exec_mode,
            project                     = project_id,
            region                      = region,
            job_name                    = job_name,
            num_workers                 = 1,
            max_num_workers             = 2,
            machine_type                = 'n2-standard-2',
            worker_machine_type         = 'n2-standard-2',
            staging_location            = f"gs://{bkt_dataflow}/staging",
            temp_location               = f"gs://{bkt_dataflow}/temp",
            streaming                   = True
        )

    with beam.Pipeline(options=options) as p:
        messages = (
            p
            | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(
                subscription    = subscription_id,
                with_attributes = False
            )
            # | 'Decode messages' >> beam.Map(parse_pubsub_message)
            | 'Print messages' >> beam.Map(print)
        )

        transformed_messages = (
            # messages
            # | 'Split dictionaries' >> beam.FlatMap(split_dict)
            # | 'Flatten dictionaries' >> beam.ParDo(ConvertToTableRowFn())
            # | 'Extract Key' >> beam.Map(lambda x: (next(iter(x)), x))
        )

        # group_messages = (
        #     transformed_messages
        #     | 'Window into fixed intervals' >> beam.WindowInto(window.FixedWindows(2 * 30),
        #                       trigger=beam.transforms.trigger.AfterWatermark(),
        #                       accumulation_mode=beam.transforms.trigger.AccumulationMode.DISCARDING)
        #     | 'Group by key' >> beam.GroupByKey()
        # )

        # group_messages | 'Write to BigQuery' >> beam.Map(
        #         lambda element: write_to_bigquery(element, dict_schema, project_id, dataset_id)
        # )


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
        "--project_dataflow",
        type=str,
        required=True,
        help="Choose which project apache-beam will run!"
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
        "--project",
        type=str,
        required=True,
        help="What project will be used to get the schema!"
    )

    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="What dataset will be used to get the schema!"
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
            project_dataflow    = args.project_dataflow,
            region              = args.region,
            job_name            = args.job_name,
            bkt_dataflow        = args.bkt_dataflow,
            project             = args.project,
            dataset             = args.dataset,
            subscription        = args.subscription
        )
