# Airflow

This module contains the Apache Airflow DAGs responsible for orchestrating the main data pipelines and analytical workflows running in Google Cloud Composer.

Apache Airflow acts as the **orchestration layer** of the platform. The DAGs coordinate the execution of Cloud Functions, Dataproc Spark jobs, Cloud Run services, Pub/Sub-based processes, and BigQuery operations.

The actual data processing is delegated to specialized GCP services, while Airflow manages execution order, dependencies, and workflow coordination.

---

## ☁️ Google Cloud Composer

The Airflow pipelines run inside **Google Cloud Composer**, Google Cloud's managed orchestration service for Apache Airflow.

Composer provides the environment where the DAGs are scheduled and executed.

The orchestration architecture can be represented as:

```text
                         ┌──────────────────────┐
                         │   Google Cloud       │
                         │      Composer        │
                         │                      │
                         │      Apache Airflow  │
                         └──────────┬───────────┘
                                    │
                                    │ Orchestration
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
      Cloud Functions           Dataproc               Cloud Run
             │                      │                      │
             ▼                      ▼                      ▼
          Pub/Sub                Spark                 Sentiment
                                                        Analysis
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                    ▼
                               ┌──────────┐
                               │ BigQuery │
                               └──────────┘
```

---

# 📁 Project Structure

```text
pipe/
├── dev_env/
│   ├── DAG_etl_ls.json
│   ├── DAG_sensor.json
│   └── DAG_sentiment_analysis.json
│
├── prd_env/
│   ├── DAG_sentiment_analysis.json
│   ├── pipe_etl.json
│   └── pipe_sensor.json
│
├── DAG_etl_ls.py
├── DAG_sensor.py
├── DAG_sentiment_analysis.py
└── delete.py
```

The module contains three main workflows:

* `DAG_etl_ls.py`
* `DAG_sensor.py`
* `DAG_sentiment_analysis.py`

---

# 🔄 DAG Workflows

## 1. `DAG_etl_ls.py`

The `DAG_etl_ls` workflow orchestrates the main ETL process.

This DAG coordinates multiple Cloud Functions, Dataproc Spark jobs, and BigQuery procedures.

### High-Level Workflow

```text
                         Start
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
      cf-customers              cf-products-inventory
             │                           │
             └─────────────┬─────────────┘
                           │
                           ▼
                  Create Dataproc Cluster
                           │
                           ▼
                    Spark Job: tb_order
                           │
                           ▼
                  cf-delivery-sensor
                           │
                           ▼
                 BigQuery: merge_delivery
                           │
                           ▼
                   Spark Job: tb_feedback
                           │
                           ▼
                  Delete Dataproc Cluster
                           │
                           ▼
                          End
```

The DAG also contains additional conditional and downstream processing.

---

### Customer and Product Processing

The workflow starts by executing two Cloud Functions in parallel:

```text
cf-customers
      │
      ├──────────────┐
      │              │
      ▼              ▼
Customer Data    Product Data
      │              │
      └──────┬───────┘
             ▼
```

The functions:

* `cf-customers`
* `cf-products-inventory`

prepare the required data before the Spark processing stage.

---

### Dataproc Processing

After the initial Cloud Functions complete, the DAG creates a Dataproc cluster.

```text
Cloud Functions
       │
       ▼
Create Dataproc Cluster
       │
       ▼
Spark Job: tb_order
```

The `tb_order` Spark job processes and enriches order-related data.

After the Spark job completes, the workflow continues to the delivery sensor processing.

---

### Delivery Sensor

The DAG then executes:

```text
cf-delivery-sensor
```

This Cloud Function processes delivery-related information and interacts with the Pub/Sub layer.

The resulting information is subsequently used by the ETL workflow.

---

### Delivery Merge

After the delivery sensor processing, the DAG executes the BigQuery procedure:

```text
merge_delivery
```

This step consolidates the delivery information into the appropriate BigQuery structures.

The flow is:

```text
cf-delivery-sensor
        │
        ▼
merge_delivery
        │
        ▼
   BigQuery
```

---

### Feedback Processing

After the delivery merge, another Spark job is executed:

```text
spark_submit_job("tb_feedback")
```

This job processes the feedback dataset using Apache Spark on Dataproc.

The general flow is:

```text
BigQuery
   │
   ▼
Dataproc
   │
   ▼
Spark: tb_feedback
   │
   ▼
Enriched Feedback Data
   │
   ▼
BigQuery
```

Once the processing is complete, the Dataproc cluster is deleted.

```text
Spark Job: tb_feedback
          │
          ▼
Delete Dataproc Cluster
```

This approach allows the Dataproc environment to exist only for the duration required by the ETL workload.

---

### Sales Forecast

The delivery sensor processing also triggers:

```text
cf-sales-forecast
```

The workflow is:

```text
cf-delivery-sensor
        │
        ▼
cf-sales-forecast
        │
        ▼
merge_delivery
```

This allows the sales forecast process to run after the delivery sensor stage has completed.

---

### Conditional Delivery Status Processing

The DAG also contains a time-based condition:

```python
if datetime.now().time() >= time(7, 0):
```

When the DAG runs after 07:00, the following BigQuery procedure is executed:

```text
delete_delivery_status
```

The result is then followed by:

```text
merge_delivery
```

Conceptually:

```text
Current Time >= 07:00
        │
        ▼
delete_delivery_status
        │
        ▼
merge_delivery
```

This conditional branch allows delivery status information to be cleaned or reset before the merge operation when the specified time condition is satisfied.

---

# 2. `DAG_sensor.py`

The `DAG_sensor` workflow is responsible for triggering the sensor-related Cloud Functions.

The DAG executes two Cloud Functions in parallel:

```text
                         Start
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
      cf-wh-sensor              cf-delivery-sensor
             │                           │
             │                           │
             └─────────────┬─────────────┘
                           │
                           ▼
                          End
```

The two functions are:

* `cf-wh-sensor`
* `cf-delivery-sensor`

These Cloud Functions process sensor information and publish data through **Google Cloud Pub/Sub**.

### Sensor Data Flow

```text
                    Airflow
                       │
                       ▼
                 DAG_sensor
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
       cf-wh-sensor      cf-delivery-sensor
              │                 │
              ▼                 ▼
           Pub/Sub            Pub/Sub
              │                 │
              └────────┬────────┘
                       ▼
                 Event Processing
```

The DAG itself does not perform the sensor data processing. Its responsibility is to trigger the appropriate Cloud Functions.

The Cloud Functions then handle the interaction with Pub/Sub.

---

# 3. `DAG_sentiment_analysis.py`

The `DAG_sentiment_analysis` workflow orchestrates the customer feedback sentiment analysis process.

The DAG contains a simple workflow:

```text
                         Start
                           │
                           ▼
              feedback_sentiment_analysis
                           │
                           ▼
                          End
```

The `feedback_sentiment_analysis()` task triggers the Cloud Run-based sentiment analysis application.

---

## 🧠 Sentiment Analysis Workflow

The sentiment analysis process analyzes customer feedback and writes the resulting sentiment information back to BigQuery.

The high-level flow is:

```text
                         Airflow
                            │
                            ▼
                DAG_sentiment_analysis
                            │
                            ▼
                       Cloud Run
                            │
                            ▼
                  Sentiment Analysis
                            │
                            ▼
                    Process Feedback
                            │
                            ▼
                        BigQuery
```

The Cloud Run application is responsible for the sentiment analysis processing.

Airflow is responsible for triggering the process and managing the workflow execution.

---

# 🔗 Complete Airflow Orchestration

The three DAGs cover different responsibilities within the platform.

```text
                         Google Composer
                              │
                         Apache Airflow
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
    DAG_etl_ls.py       DAG_sensor.py      DAG_sentiment_
                                               analysis.py
          │                   │                   │
          │                   │                   ▼
          │                   │               Cloud Run
          │                   │                   │
          │                   │                   ▼
          │                   │               BigQuery
          │                   │
          │                   ▼
          │              Cloud Functions
          │                   │
          │                   ▼
          │                Pub/Sub
          │
          ▼
   Cloud Functions
          │
          ▼
      Dataproc
          │
          ▼
      Apache Spark
          │
          ▼
      BigQuery
```

---

# 🧩 Services Orchestrated by Airflow

The Airflow layer coordinates several services within the platform.

| Service             | Role in the Workflow                       |
| ------------------- | ------------------------------------------ |
| **Cloud Composer**  | Managed Airflow environment                |
| **Apache Airflow**  | Workflow orchestration                     |
| **Cloud Functions** | Serverless processing and event generation |
| **Pub/Sub**         | Messaging and event distribution           |
| **Dataproc**        | Distributed Spark processing               |
| **Apache Spark**    | Data transformation and enrichment         |
| **Cloud Run**       | Sentiment analysis application             |
| **BigQuery**        | Analytical data storage and processing     |

---

# 🌎 Environments

The project maintains separate configurations for development and production.

## `dev_env/`

```text
dev_env/
├── DAG_etl_ls.json
├── DAG_sensor.json
└── DAG_sentiment_analysis.json
```

These files contain the configuration associated with the development environment.

---

## `prd_env/`

```text
prd_env/
├── DAG_sentiment_analysis.json
├── pipe_etl.json
└── pipe_sensor.json
```

These files contain the configuration associated with the production environment.

Maintaining separate configurations helps isolate development workflows from production workloads.

---

# 🗑️ `delete.py`

The `delete.py` script provides utility functionality for removing or cleaning up Airflow-related resources.

It is maintained separately from the DAG definitions so that administrative operations remain independent from the regular workflow orchestration logic.

---

# 🏗️ Design Principles

### Orchestration Over Processing

Airflow coordinates workloads but does not perform the heavy data-processing operations itself.

### Service-Based Processing

Each workload is delegated to the service best suited for the task:

* Cloud Functions for serverless processing
* Dataproc/Spark for distributed data processing
* Cloud Run for application-based processing
* BigQuery for analytical storage and SQL processing
* Pub/Sub for event communication

### Workflow Dependencies

Airflow explicitly defines dependencies between processing stages, ensuring that downstream tasks only execute after their required upstream tasks have completed.

### Parallel Execution

Independent tasks can execute in parallel when there are no dependencies between them.

For example:

```text
             Start
                │
       ┌────────┴────────┐
       │                 │
       ▼                 ▼
cf-customers      cf-products-inventory
       │                 │
       └────────┬────────┘
                ▼
        Dataproc Processing
```

### Environment Isolation

Development and production configurations are maintained separately.

### Resource Lifecycle

Dataproc clusters can be created when required by the workflow and deleted after processing is complete.

---

# 📊 Current Workflows

| DAG                         | Main Responsibility                   | Main Services                              |
| --------------------------- | ------------------------------------- | ------------------------------------------ |
| `DAG_etl_ls.py`             | Main ETL and data enrichment workflow | Cloud Functions, Dataproc, Spark, BigQuery |
| `DAG_sensor.py`             | Sensor event triggering               | Cloud Functions, Pub/Sub                   |
| `DAG_sentiment_analysis.py` | Customer feedback sentiment analysis  | Cloud Run, BigQuery                        |

---

# 📁 Summary Structure

```text
pipe/
│
├── dev_env/
│   ├── DAG_etl_ls.json
│   ├── DAG_sensor.json
│   └── DAG_sentiment_analysis.json
│
├── prd_env/
│   ├── DAG_sentiment_analysis.json
│   ├── pipe_etl.json
│   └── pipe_sensor.json
│
├── DAG_etl_ls.py
├── DAG_sensor.py
├── DAG_sentiment_analysis.py
└── delete.py
```

The `pipe` module therefore acts as the **central orchestration layer** of the data platform.

Running within Google Cloud Composer, Apache Airflow coordinates Cloud Functions, Pub/Sub, Dataproc, Spark, Cloud Run, and BigQuery to execute the platform's ETL, sensor, and sentiment-analysis workflows.
