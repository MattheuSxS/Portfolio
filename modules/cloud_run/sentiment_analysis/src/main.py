import time
import json
import logging
import argparse
from utils.bigquery import BigQuery
from utils.helpers import sentiment_analysis, df_columns_add


# ******************************************************************************************************************** #
#                                              System Logging                                                          #
# ******************************************************************************************************************** #
logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)


# ******************************************************************************************************************** #
#                                              Main Execution Function                                                 #
# ******************************************************************************************************************** #
def main(args=None) -> None:
    start_time = time.time()

    try:
        if args.comments.startswith('['):
            result = json.loads(args.comments)
        elif args.comments:
            with open(args.comments, 'r') as f:
                result = [json.loads(line)['comment'] for line in f]
        else:
            logging.warning("No comments provided. Exiting in comment analysis mode.")

        if args.batch_size <= 0:
            logging.error("❌ Batch size must be a positive integer.")
            raise ValueError("Invalid batch size.")

        if args.project:
            bq = BigQuery(project=args.project)
            df = bq.read_bq()

        comments = df['comment'].to_list()

        if comments:
            logging.info(f"Total comments fetched from BigQuery: {len(comments)}")

            response = sentiment_analysis(args, comments, start_time)
            df = df_columns_add(df, response)

            bq.batch_load(
                _df     = df,
                dataset = "ls_customers",
                table   = "tb_feedback_sentiment",
            )
        else:
            logging.info("No new comments to process.")

    except Exception as e:
        logging.error(f"❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sentiment Analysis on Comments")

    parser.add_argument(
        '--comments', type=str, default='[]',
        help='JSON string with comments array or path to JSON file'
    )
    parser.add_argument(
        '--batch-size', type=int, default=200,
        help='Batch size for processing'
    )
    parser.add_argument(
        '--output', type=str, default='results.json',
        help='Output file for results'
    )
    parser.add_argument(
        '--model', type=str, default='cardiffnlp/twitter-roberta-base-sentiment-latest',
        help='HuggingFace model for sentiment analysis'
    )

    parser.add_argument(
        '--project', type=str, default='gcp-default-portfolio',
        help='GCP project ID for BigQuery operations'
    )

    args = parser.parse_args()

    main(args)