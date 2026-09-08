# Cloud Run

This module contains the containerized applications deployed on Google Cloud Run.

The services in this module provide analytical interfaces and applications focused on market research, sales forecasting, and sentiment analysis.

Each application is independently structured, containerized using Docker, and designed to be deployed as an isolated Cloud Run service.

## 📁 Project Structure

```text
cloud_run/
├── market_research/
├── sales_forecast/
└── sentiment_analysis/
```

Each directory represents an independent Cloud Run application with its own source code, dependencies, Docker configuration, and test suite.

---

## 🧩 Cloud Run Applications

### `market_research`

The `market_research` application provides an analytical interface for exploring market and customer-related information.

```text
market_research/
├── src/
│   ├── .streamlit/
│   │   └── config.toml
│   ├── utils/
│   │   ├── bigquery.py
│   │   ├── brazil_map.py
│   │   ├── customer.py
│   │   ├── feedback.py
│   │   ├── helpers.py
│   │   ├── products_sales.py
│   │   └── region_sales.py
│   ├── Dockerfile
│   ├── dockerignore
│   ├── main.py
│   └── requirements.txt
└── test/
```

The application provides functionality related to:

* Customer analysis
* Customer feedback
* Product sales
* Regional sales
* Geographic visualization
* Brazilian state and region analysis
* BigQuery data retrieval

The application uses **Streamlit** to provide the analytical user interface.

---

### `sales_forecast`

The `sales_forecast` application provides an analytical interface for exploring sales forecast information and related business metrics.

```text
sales_forecast/
├── src/
│   ├── .streamlit/
│   │   └── config.toml
│   ├── utils/
│   │   ├── bigquery.py
│   │   ├── br_general.py
│   │   ├── brazil_map.py
│   │   ├── helpers.py
│   │   └── mockup.py
│   ├── Dockerfile
│   ├── dockerignore
│   ├── main.py
│   └── requirements.txt
└── test/
```

The application includes functionality for:

* Sales data retrieval
* Forecast visualization
* Brazilian geographic analysis
* General business metrics
* Data preparation and helper functions
* Mock data for application development and testing

The Streamlit configuration is maintained under `.streamlit/config.toml`.

---

### `sentiment_analysis`

The `sentiment_analysis` application provides functionality for analyzing customer or business feedback and presenting sentiment-related insights.

```text
sentiment_analysis/
├── src/
│   ├── utils/
│   │   ├── bigquery.py
│   │   └── helpers.py
│   ├── Dockerfile
│   ├── dockerignore
│   ├── main.py
│   └── requirements.txt
└── test/
```

The application is structured around:

* BigQuery data retrieval
* Sentiment analysis processing
* Supporting helper functions
* A containerized application entry point

---

## 🏗️ Common Structure

The Cloud Run applications follow a consistent structure:

```text
<application>/
├── src/
│   ├── utils/
│   ├── Dockerfile
│   ├── dockerignore
│   ├── main.py
│   └── requirements.txt
└── test/
```

This structure keeps application logic, infrastructure configuration, dependencies, and tests separated.

---

## 📦 `src/`

The `src/` directory contains the application's production source code.

It includes the main application entry point, supporting utilities, configuration, and Docker-related files.

---

## 🚀 `main.py`

The `main.py` file is the main entry point of each Cloud Run application.

For the Streamlit-based applications, it is responsible for initializing and running the application's user interface and coordinating the required data-processing components.

---

## 🛠️ `utils/`

The `utils/` directory contains application-specific modules that support the main application.

Depending on the service, these modules provide functionality for:

* BigQuery integration
* Data preparation
* Business logic
* Geographic visualization
* Customer analysis
* Feedback processing
* Sales analysis
* Forecast-related calculations
* Helper functions

Keeping these responsibilities outside `main.py` helps maintain a modular and maintainable codebase.

---

## 🎨 Streamlit Configuration

The `market_research` and `sales_forecast` applications contain a `.streamlit` configuration directory:

```text
.streamlit/
└── config.toml
```

The `config.toml` file contains Streamlit-specific configuration used by the application.

This allows the visual and runtime behavior of the Streamlit interface to be configured independently from the Python application code.

---

## 🐳 Docker

Each Cloud Run application contains its own Docker configuration:

```text
src/
├── Dockerfile
├── dockerignore
├── main.py
└── requirements.txt
```

### `Dockerfile`

Defines how the application container is built, including:

* Base Python environment
* Application dependencies
* Source code
* Runtime configuration
* Application startup command

The resulting container image can be deployed independently to Google Cloud Run.

### `dockerignore`

Defines files and directories that should not be included in the Docker build context.

This helps reduce the container build context and prevents unnecessary files from being copied into the image.

### `requirements.txt`

Contains the Python dependencies required by the application.

Dependencies are maintained independently for each Cloud Run service, allowing applications to evolve without unnecessarily coupling their runtime environments.

---

## 🧪 Testing

Each application has a dedicated `test/` directory:

```text
<application>/
└── test/
```

This provides a dedicated location for unit and application-level tests.

For example:

```text
market_research/
└── test/

sales_forecast/
└── test/

sentiment_analysis/
└── test/
```

Tests are kept separate from the production source code to maintain a clear separation between application implementation and validation.

---

## ☁️ Google Cloud Integration

The applications are designed to run as containerized services on **Google Cloud Run**.

Depending on the application, Cloud Run services interact with other components of the data platform.

| Service       | Purpose                                              |
| ------------- | ---------------------------------------------------- |
| **Cloud Run** | Hosts and runs containerized applications            |
| **BigQuery**  | Provides analytical and business data                |
| **Docker**    | Packages each application into an isolated container |
| **Streamlit** | Provides interactive analytical interfaces           |

---

## 🔄 Application Architecture

The general architecture follows this pattern:

```text
                         ┌──────────────────────┐
                         │     Google Cloud     │
                         │        Run           │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
     ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
     │ Market Research │   │ Sales Forecast  │   │    Sentiment    │
     │                 │   │                 │   │    Analysis     │
     └────────┬────────┘   └────────┬────────┘   └────────┬────────┘
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │    BigQuery     │
                           │                 │
                           │ Analytical Data │
                           └─────────────────┘
```

Each application is deployed as an independent Cloud Run service while consuming data from the shared analytical platform.

---

## 🔐 Application Isolation

Each application maintains its own:

* Source code
* Python dependencies
* Docker image configuration
* Runtime configuration
* Tests
* Utility modules

This approach allows services to be developed, tested, built, and deployed independently.

For example:

```text
market_research
       │
       ├── Docker image
       └── Cloud Run service


sales_forecast
       │
       ├── Docker image
       └── Cloud Run service


sentiment_analysis
       │
       ├── Docker image
       └── Cloud Run service
```

This isolation reduces dependencies between applications and makes individual services easier to maintain and scale.

---

## 📊 Application Responsibilities

| Application          | Main Responsibility          | Key Components                                                           |
| -------------------- | ---------------------------- | ------------------------------------------------------------------------ |
| `market_research`    | Market and customer analysis | BigQuery, Streamlit, customer data, feedback, sales, geographic analysis |
| `sales_forecast`     | Sales forecast visualization | BigQuery, Streamlit, forecasting data, geographic analysis               |
| `sentiment_analysis` | Sentiment analysis           | BigQuery, sentiment processing, helper functions                         |

---

## 📌 Design Principles

The Cloud Run module follows several architectural principles.

### Separation of Responsibilities

Each Cloud Run service has a specific business or analytical responsibility.

### Containerization

Applications are packaged as Docker containers, providing consistent and reproducible runtime environments.

### Independent Deployment

Each service can be built and deployed independently without requiring changes to the other Cloud Run applications.

### Modular Code

Application logic is separated into dedicated utility modules rather than being concentrated entirely in `main.py`.

### Dependency Isolation

Each application maintains its own `requirements.txt`, allowing dependencies to be managed independently.

### Scalability

Cloud Run allows each containerized application to scale independently according to demand.

---

## 📁 Summary Structure

The overall organization can be summarized as:

```text
cloud_run/
│
├── market_research/
│   ├── src/
│   │   ├── .streamlit/
│   │   ├── utils/
│   │   ├── Dockerfile
│   │   ├── dockerignore
│   │   ├── main.py
│   │   └── requirements.txt
│   └── test/
│
├── sales_forecast/
│   ├── src/
│   │   ├── .streamlit/
│   │   ├── utils/
│   │   ├── Dockerfile
│   │   ├── dockerignore
│   │   ├── main.py
│   │   └── requirements.txt
│   └── test/
│
└── sentiment_analysis/
    ├── src/
    │   ├── utils/
    │   ├── Dockerfile
    │   ├── dockerignore
    │   ├── main.py
    │   └── requirements.txt
    └── test/
```

The `cloud_run` module therefore acts as the **application and visualization layer** of the platform, providing containerized services that expose analytical capabilities on top of the underlying data infrastructure.
