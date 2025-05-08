resource "google_secret_manager_secret" "access_authorization" {

    project = var.project
    secret_id = var.access_authorization

    labels = {
        "created_by": "terraform",
        "env": var.environment
    }

    replication {
        auto {}
    }

    lifecycle {
        prevent_destroy = false
    }

}

resource "google_secret_manager_secret_version" "access_authorization" {
    secret      = google_secret_manager_secret.access_authorization.id
    secret_data = jsonencode({
        validation = "ok"
    })
}