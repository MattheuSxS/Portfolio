import logging
from flask import jsonify
import functions_framework
from utils.secret_manager import get_request_data
from utils.natural_language_api import analyze_sentiment


# ******************************************************************************************************************** #
#                                              System Logging                                                          #
# ******************************************************************************************************************** #
logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)


# ******************************************************************************************************************** #
#                                               Auxiliary Function                                                     #
# ******************************************************************************************************************** #


# ******************************************************************************************************************** #
#                                               Main function                                                          #
# ******************************************************************************************************************** #
@functions_framework.http
def main(request: dict) -> dict:

    try:

        if type(request) != dict:
            request_json = request.get_json(silent=True)
        else:
            request_json = request

        if not request_json or 'calls' not in request_json:
            raise ValueError('Request must contain "calls".')

        logging.info(f"Received request with {len(request_json['calls'])} calls")

        replies = analyze_sentiment(request_json)


    except Exception as e:
        logging.exception("Error processing request")
        return jsonify( { "errorMessage": str(e) } ), 400

    return jsonify( { "replies" :  replies } )


if __name__ == "__main__":

    print(
        main({"calls": [["I love it so much!"], ["I hate this product!"]]})
    )
