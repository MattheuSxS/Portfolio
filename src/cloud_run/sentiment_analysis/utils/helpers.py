import time
import logging
from typing import List
from pydantic import BaseModel
from transformers import pipeline


# ******************************************************************************************************************** #
#                                              Data Models                                                             #
# ******************************************************************************************************************** #
class ClassificationResult(BaseModel):
    sentiment: str
    confidence: float
    is_positive: bool
    is_neutral: bool

class BatchResponse(BaseModel):
    status: int = 200
    message: str = None
    predictions: List[ClassificationResult]
    processing_time: float
    total_processed: int


# ******************************************************************************************************************** #
#                                              Batch Processing Function                                               #
# ******************************************************************************************************************** #
def process_batch(classifier, comments_batch) -> List[ClassificationResult]:
    results = classifier(comments_batch)

    predictions = []
    for comment, result_list in zip(comments_batch, results):
        result = result_list[0] if result_list else None
        if not result:
            predictions.append(ClassificationResult(
                sentiment="UNKNOWN",
                confidence=0.0,
                is_positive=False,
                is_neutral=False
            ))
            continue

        original_label = result['label']

        sentiment = original_label.upper() if isinstance(original_label, str) else original_label

        is_positive = sentiment in ['POSITIVE', 'POSITIVO', 'LABEL_2', 2]
        is_neutral = sentiment in ['NEUTRAL', 'NEUTRO', 'LABEL_1', 1]

        predictions.append(ClassificationResult(
            sentiment=sentiment,
            confidence=round(result['score'], 4),
            is_positive=is_positive,
            is_neutral=is_neutral
        ))

    return predictions


# ******************************************************************************************************************** #
#                                              Main Execution Function                                                 #
# ******************************************************************************************************************** #
def sentiment_analysis(args, comments, start_time) -> BatchResponse:
        logging.info(f"Loading model: {args.model}")

        classifier = pipeline(
            task        = "text-classification",
            model       = args.model,
            tokenizer   = args.model,
            top_k       = 1,
            device      = -1
        )
        logging.info("Model loaded successfully!")

        all_predictions = []
        total_comments = len(comments)

        logging.info(f"Processing {total_comments} comments...")

        for i in range(0, total_comments, args.batch_size):
            batch = comments[i:i + args.batch_size]
            batch_predictions = process_batch(classifier, batch)
            all_predictions.extend(batch_predictions)

            logging.info(f"Processed batch {i//args.batch_size + 1}")

        processing_time = round(time.time() - start_time, 2)

        response = BatchResponse(
            status          = 200,
            predictions     = all_predictions,
            processing_time = processing_time,
            total_processed = total_comments
        )

        positive_count = sum(1 for p in all_predictions if p.is_positive)
        neutral_count  = sum(1 for p in all_predictions if p.is_neutral)
        negative_count = total_comments - positive_count - neutral_count

        logging.info(f" -- ---------------------------- --")
        logging.info(f" |       📊 DETAILED SUMMARY:     |")
        logging.info(f" -- ---------------------------- --")
        logging.info(f" 📈 Total comments  ~~> {total_comments}")
        logging.info(f" ✅ POSITIVE        ~~> {positive_count} ({positive_count/total_comments*100:.1f}%)")
        logging.info(f" ➖ NEUTRAL         ~~> {neutral_count} ({neutral_count/total_comments*100:.1f}%)")
        logging.info(f" ❌ NEGATIVE        ~~> {negative_count} ({negative_count/total_comments*100:.1f}%)")
        logging.info(f" ⏱️ Processing time  ~~> {response.processing_time}s")
        logging.info(f" -- ---------------------------- --")

        return response