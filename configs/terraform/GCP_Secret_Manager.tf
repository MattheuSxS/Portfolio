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

# resource "google_secret_manager_secret_version" "bq_wh_sensor_access_authorization" {
#     secret      = google_secret_manager_secret.create_secrets[0].id
#     secret_data = jsonencode({
#         "project_id"    = var.project[terraform.workspace]
#         "topic_id"      = google_pubsub_topic.pub_sub_topics[0].name
#         "subscriber_id" = google_pubsub_subscription.pub_sub_wh_sensor_subs.name
#     })
# }

resource "google_secret_manager_secret_version" "bq_feedback_access_authorization" {
    secret      = google_secret_manager_secret.create_secrets[1].id
    secret_data = jsonencode({
        "project_id"   = var.project[terraform.workspace]
        "dataset_id"   = google_bigquery_dataset.bq_dataset[2].dataset_id
        "table_id"     = var.tb_feedback
    })
}

resource "google_secret_manager_secret_version" "bq_customers_access_authorization" {
    secret      = google_secret_manager_secret.create_secrets[2].id
    secret_data = jsonencode({
        "project_id"        = var.project[terraform.workspace]
        "dataset_id"        = google_bigquery_dataset.bq_dataset[3].dataset_id
        "table_id"          = [var.tb_customers, var.tb_cards, var.tb_address]
        "number_customers"  = var.number_customers
    })
}

resource "google_secret_manager_secret_version" "bq_products_access_authorization" {
    secret      = google_secret_manager_secret.create_secrets[3].id
    secret_data = jsonencode({
        "project_id"        = var.project[terraform.workspace]
        "dataset_id"        = google_bigquery_dataset.bq_dataset[3].dataset_id
        "table_id"          = [var.tb_products, var.tb_inventory]
        "number_products"   = var.number_products
    })
}