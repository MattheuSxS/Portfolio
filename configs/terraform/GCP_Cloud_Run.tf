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
    name                = "sentiment-analysis-app"
    project             = local.project
    location            = var.region
    deletion_protection = false

    template {

        scaling {
            min_instance_count = 1
            max_instance_count = 5
        }

        max_instance_request_concurrency = 50
        containers {
            image = "${var.region}-docker.pkg.dev/${local.project}/${var.artifact_repo_name}/sentiment-api:latest"
            resources {
                limits = {
                cpu    = "1"
                memory = "512Mi"
                }
            }
        }
    }

    ingress = "INGRESS_TRAFFIC_ALL"

    traffic {
        type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
        percent = 100
    }
}