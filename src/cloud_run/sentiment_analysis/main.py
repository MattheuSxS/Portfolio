import time
import json
import logging
import argparse
from utils.helpers import sentiment_analysis


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
def main(args=None):
    start_time = time.time()

    try:
        if args.comments.startswith('['):
            comments = json.loads(args.comments)
        else:
            with open(args.comments, 'r') as f:
                comments = [json.loads(line)['comment'] for line in f]

        if not comments:
            logging.error("❌ The comments list is empty.")
            return

        if args.batch_size <= 0:
            logging.error("❌ Batch size must be a positive integer.")
            return

        #TODO: Get data on bigquery!
        response = sentiment_analysis(args, comments, start_time)

        # with open(args.output, 'w') as f:
        #     json.dump(response.model_dump(), f, indent=2, default=str)

        # logging.info(f"✅ Results saved to {args.output}")
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

    args = parser.parse_args()

    main(args)