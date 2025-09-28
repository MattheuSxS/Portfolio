import json
import logging
from flask import jsonify
import functions_framework
from utils.secret_manager import get_request_data
from utils.cloud_run import call_cloud_run, split_into_batches


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
# ******************************************************************************************************************** #
@functions_framework.http
def main(request):
    FILE_PATH = ""
    BATCH_SIZE = 1500
    try:
        request_json = request.get_json(silent=True)
        if not request_json or "file_path" not in request_json:
            raise ValueError('Request must contain "file_path".')

        FILE_PATH = request_json.get("file_path", "")
        BATCH_SIZE = request_json.get("batch_size", 1500)

        if not FILE_PATH:
            raise ValueError('"file_path" cannot be empty.')

        logging.info(f"Received request to process file: {FILE_PATH} with batch size: {BATCH_SIZE}")

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 400
    logging.info(f"Reading data from file: {FILE_PATH}")

    try:
        with open(FILE_PATH, "r") as f:

            all_comments = [json.loads(line)['comment'] for line in f]

    except FileNotFoundError:
        logging.error(f"File not found at path: {FILE_PATH}")
        all_comments = []

    if not all_comments:
        logging.warning("No comments loaded. Exiting.")
    else:
        logging.info(f"Total of {len(all_comments)} comments loaded.")

        logging.info(f"First comment: {all_comments[0]}")
        logging.info(f"Last comment: {all_comments[-1]}")

        comment_batches_generator = split_into_batches(all_comments, BATCH_SIZE)

        num_batches = len(list(split_into_batches(all_comments, BATCH_SIZE)))
        logging.info(f"\nData divided into {num_batches} batches of {BATCH_SIZE} items.")


        response = list()
        for i, batch in enumerate(comment_batches_generator):
            logging.info(f"Processing batch {i+1} - Size: {len(batch)} items")

            data_dict = {"texts": batch}
            response.extend(call_cloud_run(data_dict)['results'])

            logging.info(f"Batch {i+1} processed. Total results so far: {len(response)}")

        #TODO: Save results to a file or database as needed


# @functions_framework.http
# def main(request):
#     try:
#         if not isinstance(request, dict):
#             request_json = request.get_json(silent=True)
#         else:
#             request_json = request

#         if not request_json or "calls" not in request_json:
#             raise ValueError('Request must contain "calls".')

#         logging.info(f"Received request with {len(request_json['calls'])} calls")

#         calls = request_json.get("calls", [])
#         feedbacks = [call[0] for call in calls if call]

#         replies = analyze_sentiment_vertex(feedbacks)


#     except Exception as e:
#         logging.error("Error processing request")
#         return jsonify({"replies": [{"error": str(e)}]}), 500

#     return jsonify(replies)


if __name__ == "__main__":

    test_req = {"calls": [["I love it so much!"], ["I hate this product!"]]}
    print(main(test_req))