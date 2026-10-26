FROM python:3.11-slim

LABEL maintainer="Matheus Dos S. Silva"
LABEL mail="mattheusxs@gmail.com"
LABEL description="This is a Docker image is running a Sentiment Analysis application."
LABEL version="2.0"
LABEL license="MIT"
LABEL name="mattheusxs/sentiment-analysis"

ENV TRANSFORMERS_CACHE=/app/model_cache
ENV HF_HOME=/app/model_cache

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean


RUN pip install --no-cache-dir torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/model_cache

RUN apt-get remove -y gcc g++ \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache/pip

CMD ["python", "main.py"]