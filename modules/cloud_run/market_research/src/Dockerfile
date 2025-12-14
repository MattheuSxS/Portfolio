FROM python:3.11-slim

LABEL maintainer="Matheus Dos S. Silva"
LABEL mail="mattheusxs@gmail.com"
LABEL description="This is a Docker image is running a Market Research Report application."
LABEL version="1.0"
LABEL license="MIT"
LABEL name="mattheusxs/logistream-solutions-report"

ENV TRANSFORMERS_CACHE=/app/report_cache
ENV HF_HOME=/app/report_cache

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip

RUN mkdir -p /app/report_cache


CMD streamlit run main.py --server.port $PORT