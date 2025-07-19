resource "google_secret_manager_secret" "create_secrets" {

    project     = var.project[terraform.workspace]
    count       = length(var.sm_create_secrets)
    secret_id   = var.sm_create_secrets[count.index]

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
    secret      = google_secret_manager_secret.create_secrets[0].id
    secret_data = jsonencode({validation = "ok"})
}

resource "google_secret_manager_secret_version" "bq_fb_access_authorization" {
    secret      = google_secret_manager_secret.create_secrets[1].id
    secret_data = jsonencode({
        "project"   = var.project[terraform.workspace]
        "dataset"   = google_bigquery_dataset.bq_dataset[2].dataset_id
        "table"     = var.tb_feedback
    })
}

resource "google_secret_manager_secret_version" "bq_customers_access_authorization" {
    secret      = google_secret_manager_secret.create_secrets[2].id
    secret_data = jsonencode({
        "project_id"        = var.project
        "dataset_id"        = google_bigquery_dataset.bq_dataset[3].dataset_id
        "table_id"          = [var.tb_customers, var.tb_cards, var.tb_address]
        "number_customers"  = var.number_customers
    })
}