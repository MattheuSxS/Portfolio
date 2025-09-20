import json
import logging
from google.cloud import language_v1
from concurrent.futures import ThreadPoolExecutor, as_completed


def analyze_sentiment(request_json):

    try:
        client = language_v1.LanguageServiceClient()

        replies = [None] * len(request_json['calls'])  # placeholder

        def process_call(idx, call):
            text = call[0] if call else ""
            if not text:
                return idx, {"error": "Missing text"}

            document = language_v1.Document(
                content=text,
                type_=language_v1.Document.Type.PLAIN_TEXT
            )

            sentiment = client.analyze_sentiment(document=document)

            return idx, {
                "result": {
                    "score": sentiment.document_sentiment.score,
                    "magnitude": sentiment.document_sentiment.magnitude
                }
            }

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_call, i, call)
                        for i, call in enumerate(request_json['calls'])]
            for future in as_completed(futures):
                idx, reply = future.result()
                replies[idx] = reply

        return replies

    except Exception as e:
        logging.exception("Error processing request")
        return [{"error": str(e)}]
