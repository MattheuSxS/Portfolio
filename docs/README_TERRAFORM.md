# Terraform

This module contains the Infrastructure as Code (IaC) configuration used to provision and manage the Google Cloud Platform infrastructure required by the data platform.

Terraform is responsible for defining the infrastructure in a declarative and reproducible way, including data storage, data processing, orchestration, networking, security, serverless applications, and supporting GCP services.

The infrastructure is organized into dedicated Terraform files according to the Google Cloud service being managed.

---

# 🏗️ Infrastructure as Code

The Terraform module acts as the **infrastructure layer** of the platform.

Instead of creating and configuring GCP resources manually through the Google Cloud Console, the infrastructure is defined as code.

```text
                     Terraform
                         │
                         │ Infrastructure as Code
                         ▼
              ┌──────────────────────┐
              │      Google Cloud    │
              │                      │
              │  Infrastructure      │
              └──────────┬───────────┘
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
   Compute           Data Platform      Networking
       │                 │                 │
       ▼                 ▼                 ▼
Cloud Run          BigQuery            VPC
Cloud Functions    Dataflow            IAM
Dataproc           Cloud SQL           APIs
Composer           GCS                 Secrets
```

Terraform provides a consistent way to create, update, and manage these resources.

---

# 📁 Project Structure

```text
terraform/
├── schemas/
├── scripts/
├── sql_scripts/
│   └── delivery_merger.sql
│
├── config.tf
├── GCP_Apis.tf
├── GCP_Artifact_Registry.tf
├── GCP_Bigquery.tf
├── GCP_Cloud_Build.tf
├── GCP_Cloud_Function.tf
├── GCP_Cloud_Run.tf
├── GCP_Cloud_Sql.tf
├── GCP_Composer.tf
├── GCP_DataFlow.tf
├── GCP_DataProc.tf
├── GCP_GCS.tf
├── GCP_IAM.tf
├── GCP_Pub_Sub.tf
├── GCP_Secret_Manager.tf
├── GCP_VPC_Networks.tf
├── output.tf
├── terraform.tfvars
└── variable.tf
```

The infrastructure is separated into multiple Terraform files, with each file responsible for a specific area of the GCP architecture.

---

# ☁️ Google Cloud Resources

The Terraform configuration provisions and manages several Google Cloud services.

## APIs

### `GCP_Apis.tf`

Responsible for enabling and configuring the Google Cloud APIs required by the platform.

This ensures that the services required by the infrastructure are available before dependent resources are created.

---

## Artifact Registry

### `GCP_Artifact_Registry.tf`

Defines Artifact Registry resources used to store container images and other deployment artifacts.

These artifacts can be consumed by services such as Cloud Run and Cloud Build.

---

## BigQuery

### `GCP_Bigquery.tf`

Defines the BigQuery infrastructure used by the data platform.

The BigQuery configuration includes the datasets and tables required to store:

* Customer data
* Address information
* Card information
* Product data
* Inventory data
* Sales data
* Delivery status
* Feedback
* Sensor data
* Sales forecasts
* Sentiment analysis results
* Processing metrics

The table schemas are maintained separately under the `schemas/` directory.

---

# 📐 BigQuery Schemas

The `schemas/` directory contains JSON schema definitions for the BigQuery tables.

```text
schemas/
├── tb_address.json
├── tb_cards.json
├── tb_customers.json
├── tb_delivery_status.json
├── tb_feedback_sentiment.json
├── tb_feedback.json
├── tb_inventory.json
├── tb_processing_times.json
├── tb_products.json
├── tb_raw_delivery_sensor.json
├── tb_raw_wh_sensor.json
├── tb_sales_forecast.json
├── tb_sales.json
├── tb_trusted_dw_messages.json
├── tb_vehicles.json
├── tb_wh_sensor_anomalies.json
└── tb_wh_sensor.json
```

Separating schemas from the Terraform resource definitions keeps table structures easier to maintain and reuse.

The schema files define the structure of the corresponding BigQuery tables, while Terraform is responsible for provisioning the infrastructure.

---

# 🏃 Cloud Functions

### `GCP_Cloud_Function.tf`

Defines the infrastructure required to deploy and manage the project's Google Cloud Functions.

These resources support the serverless processing components documented in the `cloud_function` module.

Terraform can manage aspects such as:

* Function deployment
* Runtime configuration
* Source artifacts
* Service accounts
* Environment configuration
* IAM permissions
* Trigger configuration

---

# 🚀 Cloud Run

### `GCP_Cloud_Run.tf`

Defines the infrastructure required to deploy the containerized applications documented in the `cloud_run` module.

The Cloud Run services include applications such as:

* Market research
* Sales forecast
* Sentiment analysis

Terraform provides the infrastructure configuration required to run these containerized applications on Google Cloud.

---

# 🗄️ Cloud SQL

### `GCP_Cloud_Sql.tf`

Defines the Cloud SQL infrastructure used by the platform.

The configuration can include the database instance, networking, database configuration, and associated access controls.

Cloud SQL provides relational database capabilities for workloads that require a transactional database environment.

---

# 🎼 Cloud Composer

### `GCP_Composer.tf`

Defines the Google Cloud Composer environment used to run the Apache Airflow workflows.

The Composer environment provides the managed orchestration layer used by the `pipe` module.

```text
Terraform
    │
    ▼
Cloud Composer
    │
    ▼
Apache Airflow
    │
    ├── ETL DAG
    ├── Sensor DAG
    └── Sentiment Analysis DAG
```

---

# 🌊 Dataflow

### `GCP_DataFlow.tf`

Defines the Google Cloud Dataflow infrastructure used by the Apache Beam pipelines.

The Dataflow resources support the near real-time processing workloads documented in the `dataflow` module.

```text
Terraform
    │
    ▼
Google Cloud Dataflow
    │
    ▼
Apache Beam
    │
    ├── Delivery Sensor
    └── Warehouse Sensor
```

---

# ⚡ Dataproc

### `GCP_DataProc.tf`

Defines the Dataproc infrastructure required to execute Apache Spark workloads.

Dataproc is used by the `dataproc` module for distributed data processing and enrichment.

The general architecture is:

```text
BigQuery
    │
    │ Read
    ▼
Dataproc
    │
    ▼
Apache Spark
    │
    │ Transform / Enrich
    ▼
BigQuery
```

Terraform manages the infrastructure required to create and configure the Dataproc environment.

---

# 🪣 Google Cloud Storage

### `GCP_GCS.tf`

Defines Google Cloud Storage resources used by the platform.

Cloud Storage can be used for:

* Data files
* Deployment artifacts
* Pipeline resources
* Temporary processing files
* Cloud Function packages
* Dataflow and Dataproc resources

---

# 🔐 IAM

### `GCP_IAM.tf`

Defines Identity and Access Management resources and permissions required by the platform.

IAM configuration controls which users, service accounts, and GCP services can access specific resources.

This is particularly important for interactions between:

* Airflow
* Cloud Functions
* Dataflow
* Dataproc
* Cloud Run
* BigQuery
* Pub/Sub
* Secret Manager
* Cloud Storage

---

# 📨 Pub/Sub

### `GCP_Pub_Sub.tf`

Defines Google Cloud Pub/Sub resources used for event-driven communication.

Pub/Sub is used by the sensor-related workloads to publish and distribute messages.

The general architecture is:

```text
Sensor Processing
       │
       ▼
    Pub/Sub
       │
       ├── Subscription
       │
       ▼
Downstream Processing
```

---

# 🔑 Secret Manager

### `GCP_Secret_Manager.tf`

Defines the Secret Manager infrastructure used to securely manage sensitive configuration and credentials.

Secrets can be consumed by workloads such as:

* Cloud Functions
* Cloud Run
* Dataflow
* Dataproc
* Cloud Composer

Secret Manager helps prevent sensitive values from being hardcoded directly into application source code.

---

# 🌐 VPC Networks

### `GCP_VPC_Networks.tf`

Defines the networking infrastructure required for communication between GCP resources.

This can include:

* VPC networks
* Subnets
* Firewall rules
* Private connectivity
* Network configuration

The networking layer provides the foundation required for secure communication between services.

---

# 🔨 Cloud Build

### `GCP_Cloud_Build.tf`

Defines Cloud Build resources used to automate application build and deployment processes.

Cloud Build can be integrated with containerized workloads and other deployment processes within the platform.

A typical container deployment flow can be represented as:

```text
Source Code
     │
     ▼
Cloud Build
     │
     ▼
Build Container Image
     │
     ▼
Artifact Registry
     │
     ▼
Cloud Run
```

---

# 🧾 Terraform Configuration

## `config.tf`

Contains the core Terraform configuration for the project.

This file is typically responsible for defining configuration such as:

* Terraform settings
* Required providers
* Provider configuration
* Project-level configuration

---

## `variable.tf`

Defines variables used throughout the Terraform configuration.

Variables allow infrastructure configuration to remain reusable across different environments.

Examples of configurable values may include:

* GCP project
* Region
* Zone
* Resource names
* Environment
* Network configuration

---

## `terraform.tfvars`

The `terraform.tfvars` file contains the environment-specific values used by the Terraform configuration.

Some of these variables may contain **sensitive information**, such as project-specific configuration, credentials, identifiers, or other values that should not be publicly exposed.

For security reasons, the actual `terraform.tfvars` file is **not committed to the GitHub repository**.

Instead, the repository contains a **mockup/template version** of the file with the variable fields left blank. This allows developers to understand which variables are required without exposing sensitive project information.

Example:

```hcl
project_id        = ""
region            = ""
zone              = ""
environment       = ""
service_account   = ""
```

The developer or deployment environment must provide the appropriate values locally before running Terraform.

### Security Considerations

```text
Actual terraform.tfvars
        │
        │ Contains sensitive values
        ▼
     NOT pushed
        │
        ▼
      GitHub

Mockup terraform.tfvars
        │
        │ Contains empty fields
        ▼
      Pushed
        │
        ▼
      GitHub
```

This approach prevents sensitive infrastructure configuration from being exposed in version control while still documenting the variables required to deploy the infrastructure.


---

## `output.tf`

Defines Terraform outputs that expose useful information after infrastructure deployment.

Outputs can provide values such as:

* Resource identifiers
* Service names
* URLs
* Network information
* Dataset information

These outputs can also be consumed by other Terraform configurations or deployment processes.

---

# 🗃️ SQL Scripts

The `sql_scripts/` directory contains SQL scripts used by the infrastructure configuration.

```text
sql_scripts/
└── delivery_merger.sql
```

### `delivery_merger.sql`

Contains SQL logic associated with the delivery data merge process.

Separating SQL logic from Terraform resource definitions keeps infrastructure configuration and data-processing SQL easier to maintain.

---

# 📜 Scripts

The `scripts/` directory contains supporting scripts used by the Terraform infrastructure or deployment workflow.

Scripts can be used for auxiliary tasks that complement the Terraform configuration.

---

# 🔒 Terraform State

Terraform maintains state information to track the resources it manages.

The local Terraform working directory contains:

```text
.terraform/
```

and may contain:

```text
terraform.tfstate
```

The `.terraform/` directory contains downloaded provider binaries and Terraform working files.

The Terraform state contains information about managed infrastructure and should be treated as sensitive infrastructure metadata.

For collaborative or production environments, Terraform state should preferably be stored using a secure remote backend with appropriate access controls and state locking.

---

# 🔌 Terraform Providers

The project uses HashiCorp Terraform providers to interact with external services.

The current configuration includes providers such as:

```text
hashicorp/google
hashicorp/google-beta
hashicorp/archive
hashicorp/local
hashicorp/null
```

The provider versions are locked through:

```text
.terraform.lock.hcl
```

This helps ensure consistent provider versions across Terraform executions.

---

# 🔄 Infrastructure Lifecycle

The general Terraform workflow is:

```text
Terraform Configuration
          │
          ▼
    terraform init
          │
          ▼
    terraform validate
          │
          ▼
     terraform plan
          │
          ▼
     terraform apply
          │
          ▼
    Google Cloud
          │
          ▼
   Provisioned Resources
```

When infrastructure changes are required, Terraform compares the desired configuration with the current state and determines which resources need to be created, updated, or removed.

---

# 🧪 Terraform Validation

Before applying infrastructure changes, the configuration should be validated.

Typical commands include:

```bash
terraform init
terraform validate
terraform plan
```

After reviewing the generated execution plan:

```bash
terraform apply
```

To remove infrastructure managed by the current Terraform configuration:

```bash
terraform destroy
```

> `terraform destroy` should be used carefully, especially when managing production infrastructure.

---

# 🏗️ Infrastructure Architecture

The Terraform configuration provisions the infrastructure supporting the complete data platform.

```text
                           Terraform
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Google Cloud     │
                    │    Infrastructure   │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
   Orchestration           Processing              Storage
        │                      │                      │
   Cloud Composer          Dataflow                BigQuery
   Apache Airflow          Dataproc                Cloud SQL
                           Cloud Functions          GCS
                           Cloud Run
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                               ▼
                       Supporting Services
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
            IAM             Pub/Sub        Secret Manager
             │                 │                 │
             └─────────────────┼─────────────────┘
                               │
                               ▼
                         VPC Networks
```

---

# 📊 Managed Resources

| Terraform File             | GCP Component     | Main Responsibility                  |
| -------------------------- | ----------------- | ------------------------------------ |
| `GCP_Apis.tf`              | Google Cloud APIs | Enable required APIs                 |
| `GCP_Artifact_Registry.tf` | Artifact Registry | Store deployment/container artifacts |
| `GCP_Bigquery.tf`          | BigQuery          | Analytical data storage              |
| `GCP_Cloud_Build.tf`       | Cloud Build       | Build and deployment automation      |
| `GCP_Cloud_Function.tf`    | Cloud Functions   | Serverless workloads                 |
| `GCP_Cloud_Run.tf`         | Cloud Run         | Containerized applications           |
| `GCP_Cloud_Sql.tf`         | Cloud SQL         | Relational database                  |
| `GCP_Composer.tf`          | Cloud Composer    | Airflow orchestration                |
| `GCP_DataFlow.tf`          | Dataflow          | Distributed Beam processing          |
| `GCP_DataProc.tf`          | Dataproc          | Distributed Spark processing         |
| `GCP_GCS.tf`               | Cloud Storage     | Object and artifact storage          |
| `GCP_IAM.tf`               | IAM               | Access control                       |
| `GCP_Pub_Sub.tf`           | Pub/Sub           | Event messaging                      |
| `GCP_Secret_Manager.tf`    | Secret Manager    | Secrets management                   |
| `GCP_VPC_Networks.tf`      | VPC               | Network infrastructure               |

---

# 📌 Design Principles

### Infrastructure as Code

Infrastructure is defined as code instead of being manually configured through the Google Cloud Console.

### Reproducibility

The same Terraform configuration can be used to reproduce the required infrastructure consistently.

### Modularity

Infrastructure resources are separated by GCP service, making the configuration easier to navigate and maintain.

### Environment Configuration

Variables and environment-specific values are separated from the infrastructure definitions.

### Security

IAM, Secret Manager, and VPC configuration are managed as part of the infrastructure layer.

### Dependency Management

Terraform manages dependencies between GCP resources and ensures that resources are created in the appropriate order.

### Version Control

Infrastructure configuration can be version-controlled alongside the application code, providing traceability for infrastructure changes.

---

# ⚠️ Generated and Local Terraform Files

The following directories and files are generated or managed locally by Terraform:

```text
.terraform/
terraform.tfstate
.terraform.lock.hcl
```

The `.terraform/` directory and local state files should generally not be treated as application source code.

For production and collaborative environments, remote Terraform state is recommended.

The `.terraform.lock.hcl` file, however, should normally be committed to version control because it locks provider versions and helps ensure reproducible Terraform executions.

---

# 📁 Summary Structure

```text
terraform/
│
├── schemas/
│   ├── BigQuery table schemas
│   └── ...
│
├── scripts/
│
├── sql_scripts/
│   └── delivery_merger.sql
│
├── config.tf
├── GCP_Apis.tf
├── GCP_Artifact_Registry.tf
├── GCP_Bigquery.tf
├── GCP_Cloud_Build.tf
├── GCP_Cloud_Function.tf
├── GCP_Cloud_Run.tf
├── GCP_Cloud_Sql.tf
├── GCP_Composer.tf
├── GCP_DataFlow.tf
├── GCP_DataProc.tf
├── GCP_GCS.tf
├── GCP_IAM.tf
├── GCP_Pub_Sub.tf
├── GCP_Secret_Manager.tf
├── GCP_VPC_Networks.tf
├── output.tf
├── terraform.tfvars
└── variable.tf
```

The `terraform` module therefore acts as the **Infrastructure as Code layer** of the platform, provisioning and managing the Google Cloud resources required by the orchestration, processing, storage, messaging, analytics, and application layers.

It provides the infrastructure foundation on which the `cloud_function`, `dataflow`, `dataproc`, `pipe`, and `cloud_run` modules operate.
