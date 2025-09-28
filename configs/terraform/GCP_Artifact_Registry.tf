resource "google_artifact_registry_repository" "repo" {
    provider      = google-beta
    project       = local.project
    location      = var.region
    repository_id = var.artifact_repo_name
    description   = "Docker repository for Cloud Run images"
    format        = "DOCKER"
}



resource "null_resource" "push_docker_image" {
    depends_on = [google_artifact_registry_repository.repo]

    provisioner "local-exec" {
        command = <<EOT
            cd ../../src/cloud_run && \
            docker build -t sentiment-api . && \
            docker tag sentiment-api ${local.artifact_registry_url}/sentiment-api:latest && \
            gcloud auth configure-docker ${var.region}-docker.pkg.dev --quiet && \
            docker push ${local.artifact_registry_url}/sentiment-api:latest
        EOT
    }
}
