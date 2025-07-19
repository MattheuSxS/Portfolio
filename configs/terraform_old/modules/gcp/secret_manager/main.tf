resource "google_secret_manager_secret" "create_secrets" {

    project     = var.project
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
    secret_data = jsonencode(var.bq_fb_access_authorization)
}

resource "google_secret_manager_secret_version" "bq_customers_access_authorization" {
    secret      = google_secret_manager_secret.create_secrets[2].id
    secret_data = jsonencode({
        "project_id"        = var.project
        "dataset_id"        = var.ls_customers_dataset
        "table_id"          = [var.tb_customers, var.tb_cards, var.tb_address]
        "number_customers"  = var.number_customers
    })
}