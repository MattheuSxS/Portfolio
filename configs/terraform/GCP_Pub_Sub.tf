#   ********************************************************************************************************    #
#                                                      Pub/Sub Sensor                                           #
#   ********************************************************************************************************    #
resource "google_pubsub_topic" "pub_sub_topics" {
    project   = local.project
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
    topic                 = local.pb_wh_sensor_topic
    name                  = var.pub_sub_wh_sensor_subs
    ack_deadline_seconds  = 30
    retain_acked_messages = true

    labels = {
        "created_by": "terraform",

        "env": var.environment
    }
}


resource "google_pubsub_subscription" "pub_sub_wh_sensor_subs_bq" {
    depends_on                  =   [
                                        google_project_iam_member.pubsub_bq_role,
                                        google_bigquery_table.tb_raw_wh_sensor
                                    ]
    project                     = local.project
    name                        = var.pub_sub_wh_sensor_subs_bq
    topic                       = local.pb_wh_sensor_topic
    ack_deadline_seconds        = 30

    bigquery_config {
        table               = "${local.project}.${local.bq_dataset_raw}.${var.tb_raw_wh_sensor}"
        write_metadata      = true
        use_topic_schema    = false
        drop_unknown_fields = false
    }

    labels = {
        "created_by": "terraform",
        "env": var.environment
    }
}

resource "google_pubsub_subscription" "pub_sub_delivery_sensor_subs" {
    topic                 = local.pb_delivery_sensor_topic
    name                  = var.pub_sub_delivery_sensor_subs
    ack_deadline_seconds  = 30
    retain_acked_messages = true

    labels = {
        "created_by": "terraform",

        "env": var.environment
    }
}


resource "google_pubsub_subscription" "pub_sub_delivery_sensor_subs_bq" {
    depends_on                  =   [
                                        google_project_iam_member.pubsub_bq_role,
                                        google_bigquery_table.tb_raw_delivery_sensor
                                    ]
    project                     = local.project
    name                        = var.pub_sub_delivery_sensor_subs_bq
    topic                       = local.pb_delivery_sensor_topic
    ack_deadline_seconds        = 30

    bigquery_config {
        table               = "${local.project}.${local.bq_dataset_raw}.${var.tb_raw_delivery_sensor}"
        write_metadata      = true
        use_topic_schema    = false
        drop_unknown_fields = false
    }

    labels = {
        "created_by": "terraform",
        "env": var.environment
    }
}
