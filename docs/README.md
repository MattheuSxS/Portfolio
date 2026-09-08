# 🚧 IN PROGRESING ..... 🚧

# 🚛 LogiStream Solutions — Data Platform

A cloud-native data platform designed to integrate, process, enrich, and analyze data from multiple sources across the LogiStream Solutions supply chain.

The platform was designed as a practical final project to solve a real-world business problem involving **demand forecasting, logistics optimization, customer feedback analysis, and real-time sensor data processing**.

The solution uses Google Cloud Platform (GCP) as the primary cloud environment and combines batch processing, real-time processing, serverless applications, orchestration, analytics, and Infrastructure as Code.

---

# 📋 Project Overview

## Business Scenario

**LogiStream Solutions** is an online retail company looking to optimize its supply chain in order to:

* Improve delivery efficiency
* Reduce operational costs
* Improve customer experience
* Predict future product demand
* Monitor warehouse and delivery operations
* Better understand logistics performance
* Process data from multiple sources in different formats and volumes

The company has several independent data sources that need to be integrated into a unified data platform.

The main business objective is to transform these distributed data sources into reliable and actionable information for **demand forecasting and logistics optimization**.

---

# 🎯 Project Objective

The main objective of this project is to design and implement a scalable cloud data platform capable of integrating the company's data sources and supporting analytical and predictive workloads.

The platform must support both:

* **Batch data processing**
* **Near real-time data processing**

The solution should also be capable of enriching raw information before making it available for analytics and machine learning workloads.

---

# 📊 Available Data

The company provides several types of data.

### 🛒 Order Data

Order information includes:

* Products
* Quantities
* Customer information
* Delivery locations
* Processing times
* Sales information

### 🚚 Logistics Data

Logistics information includes:

* Delivery routes
* Transportation costs
* Delivery deadlines
* Delivery status
* Vehicle information
* Processing times

### 💬 Customer Feedback

Customer feedback includes:

* Customer comments
* Product ratings
* Delivery experience
* Customer satisfaction information

### 🌡️ Warehouse Sensors

Real-time warehouse sensor information includes:

* Temperature
* Humidity
* Warehouse sensor readings
* Sensor events

### 📍 Delivery Vehicle Sensors

Real-time vehicle sensor information includes:

* GPS location
* Vehicle sensor readings
* Delivery-related events

---

# 🧠 Business Challenges

The company needs to transform these different data sources into useful business information.

The main challenges are:

```text
Multiple Data Sources
        │
        ▼
Different Data Formats
        │
        ▼
Different Data Volumes
        │
        ▼
Batch + Real-Time Processing
        │
        ▼
Data Integration
        │
        ▼
Data Enrichment
        │
        ├───────────────┐
        ▼               ▼
Demand Forecasting   Logistics Analysis
        │               │
        └───────┬───────┘
                ▼
        Business Decisions
```

The platform therefore needs to address:

* Scalability
* Data integration
* Data quality
* Near real-time processing
* Batch processing
* Data enrichment
* Forecasting
* Sentiment analysis
* Operational monitoring
* Infrastructure automation

---

# 🏗️ Proposed Solution

The proposed solution is a **cloud-native data platform built on Google Cloud Platform**.

The architecture separates the platform into different layers:

```text
┌─────────────────────────────────────────────────────────────┐
│                       DATA SOURCES                          │
│                                                             │
│ Orders │ Logistics │ Feedback │ Warehouse │ Vehicles       │
│                               Sensors      Sensors          │
└───────────────────────────────┬─────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                       INGESTION                             │
│                                                             │
│              Cloud Functions │ Pub/Sub                      │
└───────────────────────────────┬─────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
             Batch Processing       Near Real-Time
                    │                       │
                    ▼                       ▼
                Dataproc                 Dataflow
                 Spark                 Apache Beam
                    │                       │
                    └───────────┬───────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                         BIGQUERY                            │
│                                                             │
│     Integrated │ Enriched │ Analytical │ Predictive Data   │
└───────────────────────────────┬─────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
             Sales Forecasting       Sentiment Analysis
                    │                       │
                    ▼                       ▼
               Cloud Run              Cloud Run
                    │                       │
                    └───────────┬───────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                     ANALYTICS & BI                          │
│                                                             │
│            Market Research │ Sales Forecast                 │
└─────────────────────────────────────────────────────────────┘

                 ▲
                 │
          Apache Airflow
          Google Composer
                 │
                 │ Orchestration
                 │
        ┌────────┴─────────┐
        │                  │
     Batch              Streaming
```

---

# 🖼️ Architecture

The complete architecture diagram is available in the project documentation.

If the architecture image is stored in the same directory as this README:

```markdown
![LogiStream Solutions Architecture](./images/architecture.png)
```

If the image is stored inside a documentation directory:

```markdown
![LogiStream Solutions Architecture](./docs/architecture.png)
```

---

# ☁️ Google Cloud Platform

Google Cloud Platform was selected as the primary cloud provider because the solution requires scalable data processing, managed orchestration, serverless computing, event-driven architecture, and analytical storage.

The main GCP services used by the platform are:

| GCP Service           | Purpose                                  |
| --------------------- | ---------------------------------------- |
| **BigQuery**          | Central analytical data warehouse        |
| **Cloud Functions**   | Serverless data processing and ingestion |
| **Cloud Run**         | Containerized analytical applications    |
| **Dataflow**          | Near real-time data processing           |
| **Dataproc**          | Apache Spark batch processing            |
| **Cloud Composer**    | Apache Airflow orchestration             |
| **Pub/Sub**           | Event-driven messaging                   |
| **Cloud Storage**     | Object and artifact storage              |
| **Cloud SQL**         | Relational database workloads            |
| **Secret Manager**    | Secure secret management                 |
| **Artifact Registry** | Container image storage                  |
| **Cloud Build**       | Build and deployment automation          |
| **VPC**               | Network infrastructure                   |
| **IAM**               | Identity and access management           |

---

# 🧩 Project Modules

The repository is organized into independent modules based on their responsibility within the platform.

```text
.
├── cloud_function/
├── cloud_run/
├── dataflow/
├── dataproc/
├── pipe/
├── terraform/
└── README.md
```

Each module represents a specific layer of the architecture.

---

# ⚡ Cloud Functions

The `cloud_function/` module contains the serverless functions responsible for lightweight processing, data preparation, event handling, and communication with other GCP services.

```text
cloud_function/
├── cf_customers/
├── cf_delivery_sensor/
├── cf_products_inventory/
├── cf_sales_forecast/
└── cf_wh_sensor/
```

The Cloud Functions are responsible for workloads such as:

* Customer data processing
* Product and inventory processing
* Delivery sensor processing
* Warehouse sensor processing
* Sales forecasting triggers

Some functions also interact with **Pub/Sub** and **BigQuery**.

---

# 🌊 Dataflow

The `dataflow/` module contains the Apache Beam pipelines executed using Google Cloud Dataflow.

```text
dataflow/
├── dfl_delivery_sensor/
└── dfl_wh_sensor/
```

These pipelines are designed for **near real-time processing** of sensor-related data.

The general architecture is:

```text
Pub/Sub
   │
   ▼
Dataflow
   │
   ▼
Apache Beam
   │
   ▼
Data Transformation
   │
   ▼
BigQuery
```

Dataflow provides scalable distributed processing for high-volume streaming workloads.

---

# ⚡ Dataproc

The `dataproc/` module contains Apache Spark workloads executed on Google Cloud Dataproc.

```text
dataproc/
├── dp_feedback/
└── dp_order/
```

These jobs retrieve information from BigQuery, perform transformations and enrichments, and write the resulting data back to BigQuery.

```text
BigQuery
   │
   │ Read existing data
   ▼
Dataproc
   │
   ▼
Apache Spark
   │
   │ Transform + Enrich
   ▼
Enriched Dataset
   │
   ▼
BigQuery
```

This approach allows existing data to be combined with additional information before being returned to the analytical layer.

---

# 🚀 Cloud Run

The `cloud_run/` module contains containerized applications deployed to Google Cloud Run.

```text
cloud_run/
├── market_research/
├── sales_forecast/
└── sentiment_analysis/
```

These applications provide analytical and predictive capabilities.

### Market Research

Provides analytical views of:

* Customers
* Sales
* Products
* Regions
* Customer feedback

### Sales Forecast

Provides sales forecasting and visualization capabilities.

### Sentiment Analysis

Processes customer feedback and analyzes customer sentiment.

The resulting sentiment information is written back to BigQuery.

---

# 🎼 Airflow / Cloud Composer

The `pipe/` module contains the Apache Airflow DAGs executed inside Google Cloud Composer.

```text
pipe/
├── dev_env/
├── prd_env/
├── DAG_etl_ls.py
├── DAG_sensor.py
├── DAG_sentiment_analysis.py
└── delete.py
```

Airflow acts as the **central orchestration layer**.

The main workflows are:

### `DAG_etl_ls.py`

Coordinates:

```text
Cloud Functions
      │
      ▼
Dataproc
      │
      ▼
Spark
      │
      ▼
Cloud Functions
      │
      ▼
BigQuery
      │
      ▼
Spark
      │
      ▼
BigQuery
```

### `DAG_sensor.py`

Triggers:

```text
Cloud Functions
      │
      ▼
Pub/Sub
      │
      ▼
Sensor Processing
```

### `DAG_sentiment_analysis.py`

Triggers:

```text
Airflow
   │
   ▼
Cloud Run
   │
   ▼
Sentiment Analysis
   │
   ▼
BigQuery
```

---

# 🏗️ Terraform

The `terraform/` module contains the Infrastructure as Code configuration for the complete GCP environment.

```text
terraform/
├── schemas/
├── scripts/
├── sql_scripts/
├── GCP_Apis.tf
├── GCP_Bigquery.tf
├── GCP_Cloud_Function.tf
├── GCP_Cloud_Run.tf
├── GCP_Composer.tf
├── GCP_DataFlow.tf
├── GCP_DataProc.tf
├── GCP_GCS.tf
├── GCP_IAM.tf
├── GCP_Pub_Sub.tf
├── GCP_Secret_Manager.tf
├── GCP_VPC_Networks.tf
├── variable.tf
├── output.tf
└── terraform.tfvars.example
```

Terraform manages the infrastructure required by the entire platform.

This includes:

* BigQuery
* Cloud Functions
* Cloud Run
* Dataflow
* Dataproc
* Cloud Composer
* Cloud Storage
* Pub/Sub
* Cloud SQL
* Secret Manager
* Artifact Registry
* Cloud Build
* IAM
* VPC networking

---

# 🚀 Deploy the Infrastructure

One of the main advantages of the project is that the infrastructure can be provisioned using Terraform.

After configuring the required variables, the complete GCP environment can be created with:

```bash
terraform init
terraform apply -auto-approve
```

The command:

```bash
terraform apply -auto-approve
```

allows Terraform to automatically approve the execution plan and provision the configured infrastructure without requiring interactive confirmation.

This makes the environment **reproducible and deployable using a small number of commands**.

---

# 🔐 Sensitive Configuration

The actual `terraform.tfvars` file contains environment-specific and potentially sensitive configuration.

For security reasons:

```text
terraform.tfvars
        │
        ▼
   NOT committed
        │
        ▼
      GitHub
```

Instead, the repository contains a template/mockup:

```text
terraform.tfvars.example
```

with the required fields left blank.

Example:

```hcl
project_id      = ""
region          = ""
environment     = ""
service_account = ""
```

Developers can create their own local `terraform.tfvars` based on the example file.

Sensitive credentials and environment-specific configuration should never be committed to the repository.

---

# 🔄 End-to-End Data Flow

The complete platform combines batch, streaming, serverless, analytical, and orchestration workloads.

```text
                        DATA SOURCES
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
       Orders            Logistics          Feedback
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                             ▼
                      Cloud Functions
                             │
                             ▼
                          BigQuery
                             │
                             │
       ┌─────────────────────┼─────────────────────┐
       │                     │                     │
       ▼                     ▼                     ▼
    Dataproc              Dataflow             Cloud Run
     Spark                Beam                 Analytics
       │                     │                     │
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                             ▼
                         BigQuery
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
        Demand Forecasting          Sentiment Analysis
                │                         │
                └────────────┬────────────┘
                             ▼
                    Business Analytics
```

---

# 📈 Demand Forecasting

Demand forecasting is one of the primary business objectives of the platform.

The platform combines historical sales information with other business dimensions to generate forecasts.

```text
Historical Sales
      │
      ▼
BigQuery
      │
      ▼
Data Preparation
      │
      ▼
Forecasting Models
      │
      ├── Holt-Winters
      └── Prophet
      │
      ▼
Sales Forecast
      │
      ▼
BigQuery
      │
      ▼
Cloud Run
      │
      ▼
Business Analytics
```

Forecasting information can support decisions related to:

* Inventory planning
* Product availability
* Distribution
* Logistics capacity
* Sales planning
* Operational resources

---

# 💬 Customer Sentiment Analysis

Customer feedback is processed to extract additional information from unstructured customer comments.

```text
Customer Feedback
       │
       ▼
Cloud Run
       │
       ▼
Sentiment Analysis
       │
       ▼
Sentiment Classification
       │
       ▼
BigQuery
       │
       ▼
Analytics
```

This allows the company to combine traditional structured data with customer sentiment information.

For example:

```text
Sales Data
     +
Delivery Performance
     +
Customer Feedback
     +
Sentiment
     =
Customer Experience Analysis
```

---

# 📡 Real-Time Sensor Processing

Warehouse and delivery vehicle sensors generate data continuously.

The platform uses event-driven processing to handle this information.

```text
Warehouse Sensors
       │
       ▼
Cloud Function
       │
       ▼
Pub/Sub
       │
       ▼
Dataflow
       │
       ▼
BigQuery
```

A similar flow is used for delivery vehicle sensor information.

This architecture allows the platform to process incoming sensor events without requiring all data to be processed as a single batch.

---

# 🧪 Testing

Each processing module contains its own tests where applicable.

Example:

```text
cloud_function/
└── cf_customers/
    └── test/
        ├── test_bigquery.py
        ├── test_fk_address.py
        ├── test_fk_ids.py
        ├── test_main.py
        ├── test_secret_manager.py
        └── test_transformation.py
```

Tests are implemented primarily using Python testing frameworks and are organized close to the corresponding application module.

---

# 📦 Technology Stack

| Category               | Technology                      |
| ---------------------- | ------------------------------- |
| Cloud Platform         | Google Cloud Platform           |
| Infrastructure as Code | Terraform                       |
| Data Warehouse         | BigQuery                        |
| Object Storage         | Google Cloud Storage            |
| Orchestration          | Apache Airflow / Cloud Composer |
| Batch Processing       | Apache Spark / Dataproc         |
| Streaming Processing   | Apache Beam / Dataflow          |
| Messaging              | Pub/Sub                         |
| Serverless             | Cloud Functions                 |
| Containers             | Cloud Run                       |
| Container Registry     | Artifact Registry               |
| CI/CD Support          | Cloud Build                     |
| Relational Database    | Cloud SQL                       |
| Secrets                | Secret Manager                  |
| Networking             | VPC                             |
| Access Management      | IAM                             |
| Programming Language   | Python                          |
| Query Language         | SQL                             |
| Forecasting            | Prophet / Holt-Winters          |
| Application UI         | Streamlit                       |

---

# 🎯 Expected Business Benefits

The proposed architecture provides several potential benefits.

### Scalability

Cloud-native services allow processing capacity to scale according to workload requirements.

### Real-Time Processing

Pub/Sub and Dataflow enable near real-time processing of sensor and operational events.

### Centralized Analytics

BigQuery provides a centralized analytical layer for integrated business data.

### Demand Forecasting

Historical and enriched sales data can be used to generate demand forecasts.

### Customer Experience Analysis

Sentiment analysis provides additional insight into customer feedback.

### Operational Efficiency

Integrated logistics and sensor information can help identify operational inefficiencies.

### Infrastructure Reproducibility

Terraform allows the infrastructure to be recreated consistently.

### Automated Orchestration

Cloud Composer and Airflow coordinate dependencies between the different processing services.

---

# ⚠️ Challenges

The implementation also introduces several technical challenges.

### Data Quality

Multiple sources can contain inconsistent, incomplete, or duplicated information.

### Data Volume

Sensor and operational systems can generate large amounts of data.

### Real-Time Processing

Streaming workloads require careful management of latency, failures, retries, and duplicate events.

### Infrastructure Complexity

The architecture contains several interconnected GCP services that require appropriate IAM and networking configuration.

### Cost Management

Services such as BigQuery, Dataproc, Dataflow, and Cloud Composer require appropriate resource and workload management.

### Security

Sensitive configuration and credentials must be protected through IAM and Secret Manager.

### Model Accuracy

Demand forecasting models require continuous monitoring and validation against actual results.

---

# ⏱️ Implementation Considerations

A production implementation would normally be divided into several stages:

```text
1. Infrastructure
       │
       ▼
2. Data Ingestion
       │
       ▼
3. Data Processing
       │
       ▼
4. Data Warehouse
       │
       ▼
5. Orchestration
       │
       ▼
6. Analytics
       │
       ▼
7. Forecasting
       │
       ▼
8. Monitoring & Optimization
```

Each stage can be developed and validated independently before being integrated into the complete platform.

---

# 📚 Project Structure

The final repository is organized as follows:

```text
.
├── cloud_function/
│   ├── cf_customers/
│   ├── cf_delivery_sensor/
│   ├── cf_products_inventory/
│   ├── cf_sales_forecast/
│   └── cf_wh_sensor/
│
├── cloud_run/
│   ├── market_research/
│   ├── sales_forecast/
│   └── sentiment_analysis/
│
├── dataflow/
│   ├── dfl_delivery_sensor/
│   └── dfl_wh_sensor/
│
├── dataproc/
│   ├── dp_feedback/
│   └── dp_order/
│
├── pipe/
│   ├── dev_env/
│   ├── prd_env/
│   ├── DAG_etl_ls.py
│   ├── DAG_sensor.py
│   └── DAG_sentiment_analysis.py
│
├── terraform/
│   ├── schemas/
│   ├── scripts/
│   ├── sql_scripts/
│   ├── GCP_*.tf
│   ├── variable.tf
│   └── output.tf
│
└── README.md
```

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```
# 🧪 Testing

The project includes automated tests across the different application modules.

All tests can be executed from the **root directory of the project**, without needing to navigate into each individual module.

The project root is:

```text
portfolio/
├── cloud_function/
├── cloud_run/
├── dataflow/
├── dataproc/
├── pipe/
├── terraform/
├── Makefile
└── README.md
```

## Run the Test Suite

From the root `portfolio/` directory, run:

```bash
make test
```

This command executes the automated test suite across the entire project.

```text
portfolio/
    │
    └── make test
            │
            ▼
      Run all tests
            │
      ┌─────┼─────┐
      ▼     ▼     ▼
    Cloud  Data   Data
   Function Flow  Proc
      │     │      │
      └─────┼──────┘
            ▼
        Cloud Run
            │
            ▼
       Test Results
```

## Test Coverage

To execute the tests and generate a coverage report, run:

```bash
make coverage
```

This command runs the complete test suite and generates a **test coverage report**, allowing the developer to identify which parts of the codebase are covered by automated tests.

Depending on the project configuration, the coverage report can be inspected through the generated terminal output and/or the HTML coverage report.

### Quick Reference

| Command         | Description                                    |
| --------------- | ---------------------------------------------- |
| `make test`     | Run the complete project test suite            |
| `make coverage` | Run all tests and generate the coverage report |

> **Note:** Both commands should be executed from the root `portfolio/` directory. There is no need to manually enter each individual project folder.

Example:

```bash
cd portfolio

make test
```

or:

```bash
cd portfolio

make coverage
```

This provides a single entry point for validating the entire project and makes the testing process easier to reproduce locally and in CI/CD environments.

## 2. Configure Terraform

Navigate to the Terraform directory:

```bash
cd terraform
```

Initialize Terraform:

```bash
terraform init
```

Create your local variables file based on the provided example:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Fill in the required environment-specific values.

---

## 3. Validate the configuration

```bash
terraform validate
```

Review the infrastructure changes:

```bash
terraform plan
```

---

## 4. Deploy the GCP Infrastructure

To provision the complete environment:

```bash
terraform apply -auto-approve
```

Terraform will create and configure the resources defined in the infrastructure layer.

---

# 🧹 Infrastructure Removal

When the environment is no longer required, Terraform can be used to remove the infrastructure:

```bash
terraform destroy
```

> ⚠️ Use this command carefully. It can remove infrastructure and data resources managed by the Terraform configuration.

---

# 📌 Original Project Instructions

This project was developed as a practical final project focused on proposing a solution to a business problem.

The original requirements were:

```text
1. The practical final project should be completed after the theoretical exam.

2. The practical final project consists of proposing a solution
   to a business problem.

3. Carefully analyze the business scenario presented.

4. Create a solution proposal for the business problem.

5. Justify the proposed solution.

6. Identify the tools and platforms that could be used.

7. Estimate the average implementation time.

8. Present the benefits and challenges of the proposed solution.

9. Develop the solution and answer the corresponding learning questions.
```

The project was designed to simulate a real-world environment where not all required information is necessarily available in advance.

Therefore, architectural decisions, technology choices, assumptions, and implementation strategies should be justified based on the business requirements.

---

# 🧭 Final Architecture Concept

The complete solution can be summarized as:

```text
                    LOGISTREAM SOLUTIONS
                           │
                           ▼
                    Business Problems
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
       Demand          Logistics        Customer
      Forecasting      Optimization     Experience
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                    DATA PLATFORM
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
    Ingestion          Processing          Analytics
       │                   │                   │
 Cloud Functions      Dataproc/Spark       BigQuery
 Pub/Sub              Dataflow/Beam        Cloud Run
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
                    Airflow / Composer
                           │
                           ▼
                  Workflow Orchestration
                           │
                           ▼
                     Terraform
                           │
                           ▼
              Infrastructure as Code
                           │
                           ▼
                    Google Cloud
```

---

# 🏁 Conclusion

The LogiStream Solutions platform provides a cloud-native architecture capable of integrating multiple data sources and supporting both batch and near real-time workloads.

The architecture combines:

**Cloud Functions + Pub/Sub + Dataflow + Dataproc + Spark + BigQuery + Cloud Run + Cloud Composer + Airflow + Terraform**

to create an integrated data platform capable of supporting operational analytics, customer sentiment analysis, sensor monitoring, and demand forecasting.

The use of Terraform further allows the infrastructure to be provisioned consistently and reproducibly, including the ability to deploy the complete cloud environment using:

```bash
terraform apply -auto-approve
```

This approach transforms the original business requirements into a scalable and automated cloud data platform.


## Document Version

| Versão Do Document |        Editor      |    Data    |  Percentage Complete  |
|        :---:       |        :---:       |    :---:   |         :---:         |
|        1.0.0       | Matheus S. Silva   | 2026-09-08 |          85%          |