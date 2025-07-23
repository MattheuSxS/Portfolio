# #   ********************************************************************************************************    #
# #                                          Cloud Function WareHouse Sensor                                      #
# #   ********************************************************************************************************    #
resource "google_pubsub_topic" "pub_sub_topics" {
    project   = var.project[terraform.workspace]
    count     = length(var.pub_sub_topics)
    name      = var.pub_sub_topics[count.index]

    labels = {
        "created_by": "terraform",
        "env": var.environment
    }

    message_retention_duration = "86600s"

    lifecycle {
        prevent_destroy = false
    }

}

resource "google_pubsub_subscription" "pub_sub_wh_sensor_subs" {
    topic                 = google_pubsub_topic.pub_sub_topics[0].name
    name                  = var.pub_sub_wh_sensor_subs
    ack_deadline_seconds  = 30
    retain_acked_messages = true

    labels = {
        "created_by": "terraform",

        "env": var.environment
    }
}


resource "google_pubsub_subscription" "pub_sub_wh_sensor_subs_bq" {
    depends_on                  = [google_project_iam_member.pubsub_bq_role]
    project                     = var.project[terraform.workspace]
    name                        = var.pub_sub_wh_sensor_subs_bq
    topic                       = google_pubsub_topic.pub_sub_topics[0].name
    ack_deadline_seconds        = 30

    bigquery_config {
        table               = "${var.project[terraform.workspace]}.${google_bigquery_dataset.bq_dataset[0].dataset_id}.${google_bigquery_table.tb_raw_dw_messages.table_id}"
        write_metadata      = true
        use_topic_schema    = false
        drop_unknown_fields = false
    }

    labels = {
        "created_by": "terraform",
        "env": var.environment
    }
}