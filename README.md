# 🚧 IN PROGRESING ..... 🚧


## General Summary


## Code structure


## Referências

- Github:
    - [Document Github](https://docs.github.com/en)
    - [Documemt Github Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)
    - [Document Github CI/CD](docs.github.com/en/actions)

- Terraform:
    - [Document Terraform](https://developer.hashicorp.com/terraform/intro)
    - [Document Terraform Google](registry.terraform.io/providers/hashicorp/google/7.1.0)

- Python:
    - [Document Python](https://docs.python.org/3.11/)
    - [Document Polars](https://pola-rs.github.io/polars/py-polars/html/index.html)
    - [Book Polars](https://pola-rs.github.io/polars-book/)
    - [Document Pytest](https://docs.pytest.org/en/8.3.x/contents.html)
    - [Document Coverage](https://coverage.readthedocs.io/en/7.6.12/)

- Apache-Spark
    - [Document API-SPARK](https://spark.apache.org/docs/3.5.6/index.html)
    - [Document PySpark Auxiliary](https://sparkbyexamples.com/pyspark)

- Airflow:
    - [Document Airflow](https://airflow.apache.org/docs/apache-airflow/2.10.5/index.html)

- Google Cloud (Google Cloud Platform):
    - [Document Composer](https://cloud.google.com/composer/docs/composer-3/composer-overview)
    - [Document Cloud Storage](https://cloud.google.com/storage/docs)
    - [Document Cloud Sql](https://cloud.google.com/sql/docs)
    - [Document DataProc](https://cloud.google.com/dataproc/docs)
    - [Document Dataflow](https://cloud.google.com/dataflow/docs/)
    - [Document APIs](https://cloud.google.com/apis/docs)
    - [Document Secret Manager](https://cloud.google.com/secret-manager/docs)
    - [Document BigQuery](https://cloud.google.com/bigquery/docs)
    - [Document IAM](https://cloud.google.com/iam/docs)
    - [Document Cloud Run Functions](https://cloud.google.com/functions/docs)
    - [Document Pub/Sub](https://cloud.google.com/pubsub/docs)
    - [Document Cloud Run](https://cloud.google.com/run/docs)
    - [Document Artifact Registry](https://cloud.google.com/artifact-registry/docs)

- Docker:
    - [Document Docker](https://docs.docker.com)
    - [Docker Airflow](https://hub.docker.com/r/apache/airflow)

- Makefile
    - [Document Makefile](https://www.gnu.org/software/make/manual/make.html)
    - [Document Tutorial Makefile](https://makefiletutorial.com)


## Document Version

| Versão Do Document |        Editor      |    Data    |  Percentage Complete  |
|        :---:       |        :---:       |    :---:   |         :---:         |
|        0.1.0       | Matheus S. Silva   | 2024-04-15 |          10%           |



Portfolio/
├─ .github/
│  └─ workflows/
│     └─ blank.yml
├─ configs/
│  ├─ pipe/
│  │  ├─ dev_env/
│  │  │  ├─ DAG_etl_ls.json
│  │  │  ├─ DAG_sensor.json
│  │  │  └─ DAG_sentiment_analysis.json
│  │  ├─ prd_env/
│  │  │  ├─ pipe_etl.json
│  │  │  └─ pipe_sensor.json
│  │  ├─ DAG_etl_ls.py
│  │  ├─ DAG_sensor.py
│  │  ├─ DAG_sentiment_analysis.py
│  │  └─ delete.py
│  └─ terraform/
│     ├─ .terraform/
│     │  ├─ providers/
│     │  ├─ environment
│     │  └─ terraform.tfstate
│     ├─ schemas/
│     │  ├─ tb_address.json
│     │  ├─ tb_cards.json
│     │  ├─ tb_customers.json
│     │  ├─ tb_delivery_status.json
│     │  ├─ tb_feedback_sentiment.json
│     │  ├─ tb_feedback.json
│     │  ├─ tb_inventory.json
│     │  ├─ tb_processing_times.json
│     │  ├─ tb_products.json
│     │  ├─ tb_raw_delivery_sensor.json
│     │  ├─ tb_raw_wh_sensor.json
│     │  ├─ tb_sales.json
│     │  ├─ tb_trusted_dw_messages.json
│     │  ├─ tb_vehicles.json
│     │  └─ tb_wh_sensor.json
│     ├─ scripts/
│     │  └─ install-delta-lake.sh
│     ├─ sql_scripts/
│     │  └─ delivery_merger.sql
│     ├─ .terraform.lock.hcl
│     ├─ config.tf
│     ├─ errored.tfstate
│     ├─ GCP_Apis.tf
│     ├─ GCP_Artifact_Registry.tf
│     ├─ GCP_Bigquery.tf
│     ├─ GCP_Cloud_Build.tf
│     ├─ GCP_Cloud_Function.tf
│     ├─ GCP_Cloud_Run.tf
│     ├─ GCP_Cloud_Sql.tf
│     ├─ GCP_Composer.tf
│     ├─ GCP_DataFlow.tf
│     ├─ GCP_DataProc.tf
│     ├─ GCP_GCS.tf
│     ├─ GCP_IAM.tf
│     ├─ GCP_Pub_Sub.tf
│     ├─ GCP_Secret_Manager.tf
│     ├─ GCP_VPC_Networks.tf
│     ├─ output.tf
│     ├─ terraform.tfvars
│     └─ variable.tf
├─ dist/
│  └─ reports/
│     └─ html/
│        ├─ assets/
│        │  └─ style.css
│        ├─ coverage_html/
│        │  ├─ .gitignore
│        │  └─ z_c640eeb397196e3e_fk_sensor_py.html
│        └─ tests-result.html
├─ Docker/
│  └─ Dockerfile
├─ docs/
│  ├─ README_en.md
│  ├─ README_pt.md
│  └─ Solve.md
├─ modules/
│  ├─ cloud_function/
│  │  ├─ cf_customers/
│  │  │  ├─ src/
│  │  │  │  ├─ src/
│  │  │  │  │  └─ index.zip
│  │  │  │  ├─ utils/
│  │  │  │  │  ├─ __init__.py
│  │  │  │  │  ├─ bigquery.py
│  │  │  │  │  ├─ fk_address.py
│  │  │  │  │  ├─ fk_ids.py
│  │  │  │  │  ├─ secret_manager.py
│  │  │  │  │  └─ transformation.py
│  │  │  │  ├─ index.zip
│  │  │  │  ├─ main.py
│  │  │  │  └─ requirements.txt
│  │  │  └─ test/
│  │  │     ├─ __init__.py
│  │  │     ├─ test_bigquery.py
│  │  │     ├─ test_fk_address.py
│  │  │     ├─ test_fk_ids.py
│  │  │     ├─ test_main.py
│  │  │     ├─ test_secret_manager.py
│  │  │     └─ test_transformation.py
│  │  ├─ cf_delivery_sensor/
│  │  │  ├─ src/
│  │  │  │  ├─ utils/
│  │  │  │  │  ├─ __init__.py
│  │  │  │  │  ├─ bigquery.py
│  │  │  │  │  ├─ delivery_sensor.py
│  │  │  │  │  ├─ pub_sub.py
│  │  │  │  │  └─ secret_manager.py
│  │  │  │  ├─ index.zip
│  │  │  │  ├─ main.py
│  │  │  │  └─ requirements.txt
│  │  │  └─ test/
│  │  │     ├─ test_bigquery.py
│  │  │     ├─ test_delivery_sensor.py
│  │  │     ├─ test_pub_sub.py
│  │  │     └─ test_secret_manager.py
│  │  ├─ cf_products_inventory/
│  │  │  ├─ src/
│  │  │  │  ├─ utils/
│  │  │  │  │  ├─ __init__.py
│  │  │  │  │  ├─ bigquery.py
│  │  │  │  │  ├─ fk_dates.py
│  │  │  │  │  ├─ fk_products.py
│  │  │  │  │  ├─ fk_vehicle.py
│  │  │  │  │  └─ secret_manager.py
│  │  │  │  ├─ index.zip
│  │  │  │  ├─ main.py
│  │  │  │  └─ requirements.txt
│  │  │  └─ test/
│  │  │     ├─ test_fk_dates.py
│  │  │     ├─ test_fk_products.py
│  │  │     └─ test_fk_vehicle.py
│  │  └─ cf_wh_sensor/
│  │     ├─ src/
│  │     │  ├─ utils/
│  │     │  │  ├─ __init__.py
│  │     │  │  ├─ fk_sensor.py
│  │     │  │  ├─ pub_sub.py
│  │     │  │  └─ secret_manager.py
│  │     │  ├─ index.zip
│  │     │  ├─ main.py
│  │     │  └─ requirements.txt
│  │     └─ test/
│  │        └─ test_fk_sensor.py
│  ├─ cloud_run/
│  │  ├─ market_research/
│  │  │  ├─ src/
│  │  │  │  ├─ utils/
│  │  │  │  │  ├─ __init__.py
│  │  │  │  │  ├─ bigquery.py
│  │  │  │  │  ├─ brazil_map.py
│  │  │  │  │  ├─ customer.py
│  │  │  │  │  ├─ feedback.py
│  │  │  │  │  ├─ helpers.py
│  │  │  │  │  ├─ products_sales.py
│  │  │  │  │  └─ region_sales.py
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ Dockerfile
│  │  │  │  ├─ dockerignore
│  │  │  │  ├─ main.py
│  │  │  │  └─ requirements.txt
│  │  │  └─ test/
│  │  ├─ sales_forecast/
│  │  │  ├─ src/
│  │  │  │  ├─ models/
│  │  │  │  │  └─ prophet_models.pkl
│  │  │  │  ├─ utils/
│  │  │  │  │  ├─ __init__.py
│  │  │  │  │  ├─ bigquery.py
│  │  │  │  │  ├─ brazil_map.py
│  │  │  │  │  ├─ customer.py
│  │  │  │  │  ├─ helpers.py
│  │  │  │  │  ├─ region_sales.py
│  │  │  │  │  └─ retrain.py
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ Dockerfile
│  │  │  │  ├─ dockerignore
│  │  │  │  ├─ main.py
│  │  │  │  ├─ requirements.txt
│  │  │  │  ├─ streamlit_app.py
│  │  │  │  └─ test.py
│  │  │  └─ test/
│  │  └─ sentiment_analysis/
│  │     ├─ src/
│  │     │  ├─ utils/
│  │     │  │  ├─ __init__.py
│  │     │  │  ├─ bigquery.py
│  │     │  │  └─ helpers.py
│  │     │  ├─ Dockerfile
│  │     │  ├─ dockerignore
│  │     │  ├─ main.py
│  │     │  └─ requirements.txt
│  │     └─ test/
│  ├─ dataflow/
│  │  ├─ dfl_delivery_sensor/
│  │  │  ├─ src/
│  │  │  │  ├─ utils/
│  │  │  │  │  ├─ __init__.py
│  │  │  │  │  ├─ bigquery.py
│  │  │  │  │  └─ helpers.py
│  │  │  │  ├─ dfl_delivery_sensor_nrt.py
│  │  │  │  ├─ requirements.txt
│  │  │  │  └─ setup.py
│  │  │  └─ test/
│  │  └─ dfl_wh_sensor/
│  │     ├─ src/
│  │     │  ├─ utils/
│  │     │  │  ├─ __init__.py
│  │     │  │  ├─ bigquery.py
│  │     │  │  └─ helpers.py
│  │     │  ├─ dfl_wh_sensor_nrt.py
│  │     │  ├─ requirements.txt
│  │     │  └─ setup.py
│  │     └─ test/
│  ├─ dataproc/
│  │  ├─ dp_feedback/
│  │  │  ├─ src/
│  │  │  │  ├─ utils/
│  │  │  │  │  ├─ fk_data.py
│  │  │  │  │  └─ helpers.py
│  │  │  │  ├─ spark_job_tb_feedback.py
│  │  │  │  └─ utils.zip
│  │  │  └─ test/
│  │  │     └─ test_fk_data.py
│  │  └─ dp_order/
│  │     ├─ src/
│  │     │  ├─ utils/
│  │     │  │  └─ helpers.py
│  │     │  ├─ spark_job_tb_order.py
│  │     │  └─ utils.zip
│  │     └─ test/
│  ├─ requirements-dev.txt
│  └─ requirements.txt
├─ .coverage
├─ .gitignore
├─ .python-version
├─ coverage.xml
├─ Makefile
├─ mts-default-portfolio.json
├─ README.md
└─ tests-result.xml
