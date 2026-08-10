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
        context_hash = local.sentiment_hash
    }

    provisioner "local-exec" {
        command = <<EOT
        set -e
        IMAGE="${local.artifact_registry_url}/${var.sentiment_analysis}:${local.sentiment_image_tag}"
        echo "Building image: $IMAGE"
        cd ${local.sentiment_context_path}
        docker build --platform linux/amd64 -t $IMAGE .
        gcloud auth configure-docker ${var.region}-docker.pkg.dev --quiet
        docker push $IMAGE
        echo "Image pushed: $IMAGE"
        EOT
    }
}

resource "null_resource" "push_logistream_solutions_report_image" {
    depends_on = [google_artifact_registry_repository.docker_repository]

    triggers = {
        context_hash = local.logistream_solutions_report_hash
    }

    provisioner "local-exec" {
        command = <<EOT
        set -e
        IMAGE="${local.artifact_registry_url}/${var.logistream_solutions_report}:${local.logistream_solutions_report_image_tag}"
        echo "Building image: $IMAGE"
        cd ${local.logistream_solutions_report_context_path}
        docker build --platform linux/amd64 -t $IMAGE .
        gcloud auth configure-docker ${var.region}-docker.pkg.dev --quiet
        docker push $IMAGE
        echo "Image pushed: $IMAGE"
        EOT
    }
}