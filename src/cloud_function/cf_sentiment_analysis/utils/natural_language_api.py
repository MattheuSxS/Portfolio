import logging
import time
from google.cloud import language_v1


client = language_v1.LanguageServiceClient()


def analyze_sentiment(request_json) -> dict:
    replies = []
    texts = [call[0] for call in request_json.get('calls', []) if call and call[0]]

    if not texts:
        return {"replies": [{"error": "Missing texts"}]}

    try:
        for text in texts:
            document = language_v1.Document(
                content=text,
                type_=language_v1.Document.Type.PLAIN_TEXT,
                language='en'
            )

            sentiment = client.analyze_sentiment(
                document=document,
            )

            replies.append({
                "score": sentiment.document_sentiment.score,
                "magnitude": sentiment.document_sentiment.magnitude
            })

            time.sleep(0.11)

        return {"replies": replies}

    except Exception as e:
        logging.error(f"Error processing batch request: {e}")
        raise e