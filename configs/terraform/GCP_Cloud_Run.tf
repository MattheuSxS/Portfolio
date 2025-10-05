# TODO: Implement Cloud Run services

# resource "google_cloud_run_v2_service" "streamlit_app" {
#   name     = "meu-app-streamlit"
#   location = "us-central1"

#   template {
#     containers {
#       image = "us-central1-docker.pkg.dev/seu-projeto-gcp/meu-repositorio/minha-imagem-streamlit:latest"
#       ports {
#         container_port = 8501 # A porta padrão do Streamlit
#       }
#     }
#   }
# }


resource "google_cloud_run_v2_service" "sentiment-analysis" {
    depends_on = [null_resource.push_docker_image]

    name                  = var.sentiment_analysis
    project               = local.project
    location              = var.region
    description           = "Sentiment Analysis API using DistilBERT"
    deletion_protection   = false

    template {
        scaling {
        min_instance_count = 0
        max_instance_count = 3
        }

        timeout = "1800s"
        max_instance_request_concurrency = 50

        containers {
        image = "${var.region}-docker.pkg.dev/${local.project}/${var.artifact_repo_name}/${var.sentiment_analysis}:latest"

        resources {
            limits = {
            cpu    = "4"
            memory = "8Gi"
            }
        }

        startup_probe {
            initial_delay_seconds = 10
            timeout_seconds       = 300
            period_seconds        = 10
            failure_threshold     = 10

            tcp_socket {
                port = 8080
            }
        }

        env {
            name  = "TRANSFORMERS_CACHE"
            value = "/tmp/model_cache"
        }
        env {
            name  = "HF_HOME"
            value = "/tmp/model_cache"
        }
        env {
            name  = "PYTHONUNBUFFERED"
            value = "1"
        }
        }


    }

    build_config {
        environment_variables = {
            "project" = local.project,
            "dataset" = local.bq_dataset_ls_customers,
            "table"   = var.tb_feedback_sentiment
        }
        service_account = local.sa_cloud_run
    }

    traffic {
        type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
        percent = 100
    }

    ingress = "INGRESS_TRAFFIC_ALL"
}