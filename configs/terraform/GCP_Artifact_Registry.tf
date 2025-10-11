resource "google_artifact_registry_repository" "docker_repository" {
    provider      = google-beta
    project       = local.project
    location      = var.region
    repository_id = var.docker_repository
    description   = "Docker repository for Cloud Run images"
    format        = "DOCKER"
}



resource "null_resource" "push_docker_image" {
    depends_on = [google_artifact_registry_repository.docker_repository]

    provisioner "local-exec" {
        command = <<EOT
            cd ../../src/cloud_run/sentiment_analysis && \
            docker build --platform linux/amd64 -t sentiment-analysis . && \
            docker tag sentiment-analysis ${local.artifact_registry_url}/sentiment-analysis:latest && \
            gcloud auth configure-docker ${var.region}-docker.pkg.dev --quiet && \
            docker push ${local.artifact_registry_url}/sentiment-analysis:latest
        EOT
    }
}
