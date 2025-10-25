resource "google_artifact_registry_repository" "docker_repository" {
    provider      = google-beta
    project       = local.project
    location      = var.region
    repository_id = var.docker_repository
    description   = "Docker repository for Cloud Run images"
    format        = "DOCKER"
}


resource "null_resource" "push_sentiment_analysis_image" {
    depends_on = [google_artifact_registry_repository.docker_repository]

    triggers = {
        script_hash = md5(file("../../src/cloud_run/sentiment_analysis/Dockerfile"))
    }

    provisioner "local-exec" {
        command = <<EOT
            cd ../../src/cloud_run/sentiment_analysis && \
            docker build --platform linux/amd64 -t ${var.sentiment_analysis} . && \
            docker tag ${var.sentiment_analysis} ${local.artifact_registry_url}/${var.sentiment_analysis}:latest && \
            gcloud auth configure-docker ${var.region}-docker.pkg.dev --quiet && \
            docker push ${local.artifact_registry_url}/${var.sentiment_analysis}:latest
        EOT
    }
}

resource "null_resource" "push_logistream_solutions_report_image" {
    depends_on = [google_artifact_registry_repository.docker_repository]

    triggers = {
        script_hash = md5(file("../../src/cloud_run/market_research/Dockerfile"))
    }

    provisioner "local-exec" {
        command = <<EOT
            cd ../../src/cloud_run/market_research && \
            docker build --platform linux/amd64 -t ${var.logistream_solutions_report} . && \
            docker tag ${var.logistream_solutions_report} ${local.artifact_registry_url}/${var.logistream_solutions_report}:latest && \
            gcloud auth configure-docker ${var.region}-docker.pkg.dev --quiet && \
            docker push ${local.artifact_registry_url}/${var.logistream_solutions_report}:latest
        EOT
    }
}