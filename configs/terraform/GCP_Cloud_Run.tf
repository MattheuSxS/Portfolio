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