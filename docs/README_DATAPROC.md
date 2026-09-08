# Dataproc

This module contains Apache Spark jobs designed to run on Google Cloud Dataproc.

The Dataproc workloads are responsible for enriching data stored in BigQuery. The jobs read existing datasets from BigQuery, apply transformations and enrichment logic using Spark, and write the enriched data back to BigQuery.

The module currently contains dedicated Spark jobs for feedback and order data processing.

## 📁 Project Structure

```text id="k4s3qz"
dataproc/
├── dp_feedback/
└── dp_order/
```

Each directory represents an independent Spark job with its own source code, utility modules, packaged dependencies, and tests.

---

## 🧩 Dataproc Jobs

### `dp_feedback`

The `dp_feedback` job is responsible for processing and enriching feedback data.

```text id="h1e7tx"
dp_feedback/
├── src/
│   ├── utils/
│   │   ├── fk_data.py
│   │   └── helpers.py
│   ├── spark_job_tb_feedback.py
│   └── utils.zip
└── test/
    └── test_fk_data.py
```

The job uses Apache Spark to process feedback data retrieved from BigQuery.

The processing layer can enrich the existing records with additional information before writing the resulting dataset back to BigQuery.

The main Spark job is:

```text id="a0kz9n"
src/spark_job_tb_feedback.py
```

---

### `dp_order`

The `dp_order` job is responsible for processing and enriching order data.

```text id="9j1r5a"
dp_order/
├── src/
│   ├── utils/
│   │   └── helpers.py
│   ├── spark_job_tb_order.py
│   └── utils.zip
└── test/
```

The job reads order-related data from BigQuery, applies Spark-based processing and enrichment, and writes the resulting dataset back to BigQuery.

The main Spark job is:

```text id="0z1m5x"
src/spark_job_tb_order.py
```

---

## 🔄 Data Enrichment Workflow

The main responsibility of the Dataproc module is to transform existing BigQuery data into richer datasets.

The general workflow is:

```text id="x6b8r4p"
                    ┌─────────────────┐
                    │    BigQuery     │
                    │                 │
                    │ Existing Data   │
                    └────────┬────────┘
                             │
                             │ Read
                             ▼
                    ┌─────────────────┐
                    │    Dataproc     │
                    │                 │
                    │ Apache Spark    │
                    └────────┬────────┘
                             │
                    Transformations
                    & Enrichment
                             │
                             ▼
                    ┌─────────────────┐
                    │ Enriched Data   │
                    │                 │
                    │ New Information │
                    └────────┬────────┘
                             │
                             │ Write
                             ▼
                    ┌─────────────────┐
                    │    BigQuery     │
                    │                 │
                    │ Enriched Dataset│
                    └─────────────────┘
```

In other words:

**BigQuery → Dataproc/Spark → Enrichment → BigQuery**

The objective is not simply to move the data, but to **add new information to existing records**, producing a more complete and useful dataset for downstream analytical workloads.

---

## ⚙️ Apache Spark

The processing logic is implemented using Apache Spark.

Spark provides the distributed processing framework required to handle data transformations efficiently.

The main Spark jobs are:

```text id="8g0v7m"
spark_job_tb_feedback.py
spark_job_tb_order.py
```

These files define the main processing workflows executed by the Dataproc environment.

---

## 🛠️ `utils/`

Each Spark job contains a `utils/` directory with reusable processing components.

### `fk_data.py`

Used by the `dp_feedback` job to support data-related enrichment and foreign-key processing.

### `helpers.py`

Contains reusable helper functions used by the Spark jobs.

Separating these functions from the main Spark job helps keep the pipeline logic organized and easier to test.

---

## 📦 `utils.zip`

The `utils.zip` files contain utility modules that can be distributed to the Spark execution environment.

This allows the Dataproc workers to access the project's custom Python modules when the Spark job is executed in the distributed environment.

The package is associated with the corresponding Spark job and its utility dependencies.

---

## 🧪 Testing

The Dataproc module maintains tests alongside each individual Spark job.

For example:

```text id="g3h9yd"
dp_feedback/
└── test/
    └── test_fk_data.py
```

The tests validate individual components of the data-processing logic.

Keeping tests separate from the Spark job implementation allows individual transformation and enrichment functions to be validated without requiring the complete distributed processing environment.

---

## ☁️ Google Cloud Integration

The Dataproc module primarily integrates with the following Google Cloud services:

| Service                   | Purpose                                             |
| ------------------------- | --------------------------------------------------- |
| **Google Cloud Dataproc** | Provides the managed Spark processing environment   |
| **Apache Spark**          | Performs distributed data processing and enrichment |
| **BigQuery**              | Source and destination for the datasets             |
| **Cloud Storage**         | Supports artifacts and distributed job resources    |

---

## 📊 Data Processing Pattern

The Dataproc jobs follow a common **read → transform → enrich → write** pattern.

```text id="3x6v3r"
┌──────────────┐
│   BigQuery   │
│              │
│ Source Data  │
└──────┬───────┘
       │
       │ 1. Read
       ▼
┌──────────────┐
│    Spark     │
│              │
│ DataFrame    │
└──────┬───────┘
       │
       │ 2. Transform
       ▼
┌──────────────┐
│ Enrichment   │
│              │
│ New Fields   │
│ / Attributes │
└──────┬───────┘
       │
       │ 3. Write
       ▼
┌──────────────┐
│   BigQuery   │
│              │
│ Enriched Data│
└──────────────┘
```

This pattern allows existing datasets to be enhanced without moving the primary data-processing responsibility into the analytical layer itself.

---

## 🔗 Foreign-Key Enrichment

Some of the processing logic is focused on generating or enriching foreign-key-related information.

For example, the feedback job contains:

```text id="6h9j2s"
fk_data.py
```

This type of processing allows existing records to be associated with additional entities or reference information.

The resulting data can then be consumed by downstream analytical processes with richer relationships between datasets.

---

## 📁 Common Structure

The Dataproc jobs follow a lightweight structure:

```text id="z5c8r1"
<dataproc_job>/
├── src/
│   ├── utils/
│   ├── spark_job_<table>.py
│   └── utils.zip
└── test/
```

The structure separates:

* Spark job orchestration
* Reusable processing functions
* Distributed utility packages
* Unit tests

---

## 📌 Design Principles

### Data Enrichment

The primary objective is to enrich existing BigQuery datasets with additional information.

### Distributed Processing

Apache Spark is used to perform transformations in a distributed processing environment.

### Separation of Responsibilities

The Spark job is responsible for orchestrating the processing workflow, while reusable functionality is maintained inside `utils/`.

### BigQuery Integration

BigQuery acts as both the source and destination for the processed datasets.

### Independent Jobs

Feedback and order processing are maintained as separate Dataproc jobs, allowing them to be executed and maintained independently.

### Testability

Individual processing components can be tested independently from the complete Spark execution environment.

---

## 📊 Current Jobs

| Job           | Source Data | Processing                         | Destination |
| ------------- | ----------- | ---------------------------------- | ----------- |
| `dp_feedback` | BigQuery    | Spark transformations & enrichment | BigQuery    |
| `dp_order`    | BigQuery    | Spark transformations & enrichment | BigQuery    |

Both jobs follow the same high-level architecture while addressing different business datasets.

---

## 📁 Summary Structure

```text id="q2v6ps"
dataproc/
│
├── dp_feedback/
│   ├── src/
│   │   ├── utils/
│   │   │   ├── fk_data.py
│   │   │   └── helpers.py
│   │   ├── spark_job_tb_feedback.py
│   │   └── utils.zip
│   └── test/
│       └── test_fk_data.py
│
└── dp_order/
    ├── src/
    │   ├── utils/
    │   │   └── helpers.py
    │   ├── spark_job_tb_order.py
    │   └── utils.zip
    └── test/
```

The `dataproc` module therefore acts as the **data enrichment and distributed processing layer** of the platform.

It uses Apache Spark running on Google Cloud Dataproc to retrieve existing data from BigQuery, apply transformations and enrichment logic, and return richer datasets to BigQuery for downstream analytical and data-processing workloads.
