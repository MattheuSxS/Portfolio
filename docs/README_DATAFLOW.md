# Dataflow

This module contains the Apache Beam pipelines designed to run on Google Cloud Dataflow.

The pipelines are responsible for processing sensor-related data in near real-time (NRT), with dedicated pipelines for delivery and warehouse sensor events.

The module follows a modular structure where each Dataflow pipeline is isolated into its own directory, with dedicated pipeline code, utilities, dependencies, packaging configuration, and tests.

## 📁 Project Structure

```text
dataflow/
├── dfl_delivery_sensor/
└── dfl_wh_sensor/
```

Each directory represents an independent Apache Beam pipeline that can be deployed and executed as a Dataflow job.

---

## 🧩 Dataflow Pipelines

### `dfl_delivery_sensor`

The `dfl_delivery_sensor` pipeline processes delivery sensor data in a near real-time environment.

```text
dfl_delivery_sensor/
├── src/
│   ├── dfl_delivery_sensor.egg-info/
│   ├── utils/
│   │   ├── bigquery.py
│   │   └── helpers.py
│   ├── dfl_delivery_sensor_nrt.py
│   ├── requirements.txt
│   └── setup.py
└── test/
```

The pipeline contains components responsible for:

* Apache Beam pipeline execution
* Near real-time sensor processing
* BigQuery integration
* Data transformation and helper functions
* Pipeline packaging and dependency management

The main pipeline implementation is located in:

```text
src/dfl_delivery_sensor_nrt.py
```

---

### `dfl_wh_sensor`

The `dfl_wh_sensor` pipeline processes warehouse sensor data in a near real-time environment.

```text
dfl_wh_sensor/
├── .vscode/
│   └── settings.json
├── src/
│   ├── dfl_wh_sensor_nrt.egg-info/
│   ├── utils/
│   │   ├── bigquery.py
│   │   └── helpers.py
│   ├── dfl_wh_sensor_nrt.py
│   ├── requirements.txt
│   └── setup.py
└── test/
```

The pipeline provides functionality for:

* Warehouse sensor processing
* Near real-time data ingestion
* BigQuery integration
* Data transformation
* Reusable helper functions
* Apache Beam pipeline execution

The main pipeline implementation is located in:

```text
src/dfl_wh_sensor_nrt.py
```

---

## 🔄 Near Real-Time Processing

Both pipelines are designed around near real-time processing.

```text
                  ┌──────────────────────┐
                  │     Sensor Events    │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │    Apache Beam       │
                  │      Pipeline        │
                  └──────────┬───────────┘
                             │
                    Near Real-Time
                       Processing
                             │
                             ▼
                  ┌──────────────────────┐
                  │   Transformations    │
                  │   & Data Processing  │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │      BigQuery        │
                  └──────────────────────┘
```

The Apache Beam pipelines can be executed locally during development or submitted to Google Cloud Dataflow for distributed processing.

---

## 🏗️ Common Structure

The Dataflow pipelines follow a consistent internal organization:

```text
<pipeline>/
├── src/
│   ├── utils/
│   ├── <pipeline>_nrt.py
│   ├── requirements.txt
│   └── setup.py
└── test/
```

This structure separates pipeline orchestration, reusable functionality, dependencies, packaging, and testing.

---

## ⚙️ Pipeline Entry Point

The main pipeline file follows the naming convention:

```text
<pipeline_name>_nrt.py
```

For example:

```text
dfl_delivery_sensor_nrt.py
dfl_wh_sensor_nrt.py
```

These files contain the Apache Beam pipeline definition and represent the primary entry points for Dataflow execution.

The pipelines can be configured with Apache Beam `PipelineOptions` to support different execution environments and Dataflow configurations.

---

## 🛠️ `utils/`

The `utils/` directory contains reusable components used by the pipelines.

Common modules include:

### `bigquery.py`

Provides functionality related to Google BigQuery operations, such as reading from or writing to analytical tables.

### `helpers.py`

Contains reusable helper functions used during pipeline processing and data transformations.

This separation keeps the main Beam pipeline focused on orchestration while allowing individual processing components to be tested and maintained independently.

---

## 📦 Dependencies

Each Dataflow pipeline maintains its own dependency configuration:

```text
requirements.txt
```

This file contains the Python packages required to execute the pipeline.

Dependencies may include Apache Beam and Google Cloud libraries required for Dataflow and BigQuery integration.

---

## 🏗️ Package Configuration

Each pipeline contains a `setup.py` file:

```text
setup.py
```

The setup configuration allows the pipeline and its supporting modules to be packaged and distributed to the Dataflow workers.

This is particularly important when executing Apache Beam pipelines using the Dataflow runner, as worker instances need access to the project's Python modules and dependencies.

---

## 📦 `*.egg-info/`

The following directories:

```text
dfl_delivery_sensor.egg-info/
dfl_wh_sensor_nrt.egg-info/
```

are generated Python package metadata directories.

They contain information generated during the package build/install process, such as:

* Package metadata
* Dependencies
* Source file information
* Top-level package information

These files are not part of the core pipeline business logic.

For source-control management, generated package metadata should generally be excluded from the repository when it is reproducible from the project configuration.

---

## 🧪 Testing

Each Dataflow pipeline has its own dedicated test directory:

```text
dfl_delivery_sensor/
└── test/

dfl_wh_sensor/
└── test/
```

The test directories are intended to contain unit and pipeline-level tests.

Testing individual utility functions and transformation logic independently helps reduce the complexity of validating the complete distributed pipeline.

---

## ☁️ Google Cloud Integration

The Dataflow pipelines integrate primarily with Google Cloud services.

| Service                   | Purpose                                                |
| ------------------------- | ------------------------------------------------------ |
| **Google Cloud Dataflow** | Distributed execution of Apache Beam pipelines         |
| **Apache Beam**           | Pipeline definition and data processing framework      |
| **BigQuery**              | Data storage and analytical processing                 |
| **Cloud Storage**         | Supporting Dataflow artifacts and deployment resources |

---

## 🚀 Execution Model

The pipelines can be executed using different Apache Beam runners depending on the environment.

### Local Development

During development, pipelines can be executed locally using the Direct Runner.

```text
Developer
    │
    ▼
Apache Beam
    │
    ▼
Direct Runner
    │
    ▼
Local Environment
```

This approach is useful for:

* Development
* Debugging
* Unit testing
* Pipeline validation

### Google Cloud Dataflow

For distributed execution, the pipeline can be submitted using the Dataflow runner.

```text
Developer / CI/CD
       │
       ▼
Apache Beam Pipeline
       │
       ▼
Dataflow Runner
       │
       ▼
Google Cloud Dataflow
       │
       ├──────────────┐
       ▼              ▼
   Worker 1        Worker N
       │              │
       └──────┬───────┘
              ▼
          BigQuery
```

Dataflow provides the infrastructure required to execute the Beam pipeline across distributed workers.

---

## 📊 Pipeline Responsibilities

| Pipeline              | Responsibility              | Main Integration              |
| --------------------- | --------------------------- | ----------------------------- |
| `dfl_delivery_sensor` | Delivery sensor processing  | Pub/Sub + Dataflow + BigQuery |
| `dfl_wh_sensor`       | Warehouse sensor processing | Pub/Sub + Dataflow + BigQuery |

Both pipelines follow the same general architectural approach while processing different sensor domains.

---

## 📌 Design Principles

### Separation of Responsibilities

Each pipeline is responsible for a specific sensor-processing domain.

### Near Real-Time Processing

The pipelines are designed to process incoming sensor data with low processing latency.

### Modular Processing

Reusable functionality is separated into utility modules instead of being implemented entirely inside the main pipeline.

### Distributed Execution

Apache Beam provides the processing model while Google Cloud Dataflow provides the distributed execution infrastructure.

### Independent Pipelines

Each pipeline maintains its own dependencies and packaging configuration, allowing them to be developed and deployed independently.

### Testability

Pipeline utilities and processing logic are organized into modules that can be tested independently.

---

## 📁 Summary Structure

The overall organization can be summarized as:

```text
dataflow/
│
├── dfl_delivery_sensor/
│   ├── src/
│   │   ├── utils/
│   │   │   ├── bigquery.py
│   │   │   └── helpers.py
│   │   ├── dfl_delivery_sensor_nrt.py
│   │   ├── requirements.txt
│   │   └── setup.py
│   └── test/
│
└── dfl_wh_sensor/
    ├── src/
    │   ├── utils/
    │   │   ├── bigquery.py
    │   │   └── helpers.py
    │   ├── dfl_wh_sensor_nrt.py
    │   ├── requirements.txt
    │   └── setup.py
    └── test/
```

The `dataflow` module therefore acts as the **distributed data-processing layer** of the platform, using Apache Beam and Google Cloud Dataflow to process sensor data in near real time and integrate the resulting data with BigQuery.
