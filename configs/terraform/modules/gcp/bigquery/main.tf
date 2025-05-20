#   ********************************************************************************************************   #
#                                                     DataSets                                                 #
#   ********************************************************************************************************   #

resource "google_bigquery_dataset" "bq_dataset" {
    project                     = var.project
    location                    = var.region
    count                       = length(var.bq_dataset)
    dataset_id                  = var.bq_dataset[count.index]
    friendly_name               = var.bq_dataset[count.index]
    description                 = "Creating the dataset ${var.bq_dataset[count.index]}"
    delete_contents_on_destroy  = false

    labels = {
        "created_by": "terraform",
        "env": var.environment
    }
}

#   ********************************************************************************************************   #
#                                                    Table Raw                                                 #
#   ********************************************************************************************************   #
resource "google_bigquery_table" "tb_raw_dw_messages" {
    dataset_id            = google_bigquery_dataset.bq_dataset[0].dataset_id
    table_id              = var.tb_raw_hw_sensor
    schema                = file("${path.module}/schemas/tb_raw_dw_messages.json")
    deletion_protection   = false

    time_partitioning {
        type          = "DAY"
        field         = "publish_time"
        # expiration_ms = 7776000000
    }

    clustering = ["message_id"]
}

#   ********************************************************************************************************   #
#                                                 Table production                                             #
#   ********************************************************************************************************   #
resource "google_bigquery_table" "tb_dw_messages" {
    dataset_id            = google_bigquery_dataset.bq_dataset[2].dataset_id
    table_id              = var.tb_dw_messages
    schema                = file("${path.module}/schemas/tb_trusted_dw_messages.json")
    deletion_protection   = false

    time_partitioning {
        type          = "DAY"
        field         = "time_stamp"
        expiration_ms = 7776000000
    }

    clustering = ["warehouse_id", "message_id"]
}

resource "google_bigquery_table" "tb_feedback" {
    dataset_id            = google_bigquery_dataset.bq_dataset[2].dataset_id
    table_id              = var.tb_feedback
    schema                = file("${path.module}/schemas/tb_feedback.json")
    deletion_protection   = false

    time_partitioning {
        type          = "DAY"
        field         = "fb_date"
        expiration_ms = 7776000000
    }

    clustering = ["type", "category", "rating", "verified_purchase"]
}