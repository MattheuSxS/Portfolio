resource "google_pubsub_topic" "pub_sub_wh_sensor_topic" {
    project   = var.project[terraform.workspace]
    name      = var.pub_sub_wh_sensor_topic

    labels = {
        "created_by": "terraform",
        "env": var.environment
    }

    message_retention_duration = "86600s"

    lifecycle {
        prevent_destroy = false
    }

}

resource "google_pubsub_subscription" "pub_sub_wh_sensor_subscription" {
    topic                 = google_pubsub_topic.pub_sub_wh_sensor_topic.name
    name                  = var.pub_sub_wh_sensor_subscription
    ack_deadline_seconds  = 30
    retain_acked_messages = true

    labels = {
        "created_by": "terraform",
        "env": var.environment
    }
}

#TODO: Fix this subscription to use BigQuery [  google_pubsub_subscription.pub_sub_wh_sensor_subscription_bq: Creating...]
# resource "google_pubsub_subscription" "pub_sub_wh_sensor_subscription_bq" {
#     depends_on                  = [google_project_iam_member.pubsub_bq_role]
#     project                     = var.project[terraform.workspace]
#     name                        = var.pub_sub_wh_sensor_subscription_bq
#     topic                       = google_pubsub_topic.pub_sub_wh_sensor_topic.name
#     message_retention_duration  = "250000s"

#     bigquery_config {
#         table               = "mts-default-projetct.raw.${google_bigquery_table.tb_raw_dw_messages.table_id}"
#         write_metadata      = true
#         use_topic_schema    = false
#         drop_unknown_fields = false
#     }

#     labels = {
#         "created_by": "terraform",
#         "env": var.environment
#     }
# }