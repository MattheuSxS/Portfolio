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

resource "google_secret_manager_secret_version" "ps_wh_sensor_access_authorization" {
    secret      = local.secret_wh_sensor_access_authorization
    secret_data = jsonencode({
        "project_id"    = var.project[terraform.workspace]
        "topic_id"      = local.pb_wh_sensor_topic
        "subscriber_id" = google_pubsub_subscription.pub_sub_wh_sensor_subs.name
    })
}

resource "google_secret_manager_secret_version" "bq_customers_access_authorization" {
    secret      = local.secret_bq_customers_access_authorization
    secret_data = jsonencode({
        "project_id"        = var.project[terraform.workspace]
        "dataset_id"        = local.bq_dataset_ls_customers
        "table_id"          = [var.tb_customers, var.tb_cards, var.tb_address]
        "number_customers"  = var.number_customers
    })
}

resource "google_secret_manager_secret_version" "bq_products_access_authorization" {
    secret      = local.secret_bq_products_access_authorization
    secret_data = jsonencode({
        "project_id"        = var.project[terraform.workspace]
        "dataset_id"        = local.bq_dataset_ls_customers
        "table_id"          = [var.tb_products, var.tb_inventory]
        "number_products"   = var.number_products
    })
}