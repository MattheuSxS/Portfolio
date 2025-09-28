import torch
import logging
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification


# ******************************************************************************************************************** #
#                                              System Logging                                                          #
# ******************************************************************************************************************** #
logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)


app = FastAPI(
    title="Sentiment Analysis API",
    description="An API for classifying the sentiment of text using DistilBERT.",
    version="1.0.0"
)


tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model.eval()

class FeedbackBatch(BaseModel):
    texts: List[str]

@app.post("/classify")
def classify(feedback_batch: FeedbackBatch, batch_size: int = 32):
    results = []

    for i in range(0, len(feedback_batch.texts), batch_size):
        batch_texts = feedback_batch.texts[i:i+batch_size]
        inputs = tokenizer(batch_texts, padding=True, truncation=True, return_tensors="pt")

        with torch.no_grad():
            logits = model(**inputs).logits
            probs = torch.softmax(logits, dim=1)
            predicted_ids = torch.argmax(probs, dim=1)

            for idx, pred_id in enumerate(predicted_ids):
                results.append({
                    "label": model.config.id2label[pred_id.item()],
                    "score": round(probs[idx][pred_id].item(), 4)
                })

    return {
        "status": 200,
        "results": results
    }
