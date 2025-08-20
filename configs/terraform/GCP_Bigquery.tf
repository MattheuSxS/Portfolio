#   ********************************************************************************************************   #
#                                                     DataSets                                                 #
#   ********************************************************************************************************   #
resource "google_bigquery_dataset" "bq_dataset" {
    project                     = var.project[terraform.workspace]
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
resource "google_bigquery_table" "tb_raw_wh_sensor" {
    dataset_id            = local.bq_dataset_raw
    table_id              = var.tb_raw_wh_sensor
    schema                = file("${path.module}/schemas/${var.tb_raw_wh_sensor}.json")
    deletion_protection   = false

    time_partitioning {
        type          = "DAY"
        field         = "publish_time"
        # expiration_ms = 7776000000
    }

    clustering = ["message_id"]
}

resource "google_bigquery_table" "tb_raw_delivery_sensor" {
    dataset_id            = local.bq_dataset_raw
    table_id              = var.tb_raw_delivery_sensor
    schema                = file("${path.module}/schemas/${var.tb_raw_delivery_sensor}.json")
    deletion_protection   = false

    time_partitioning {
        type          = "DAY"
        field         = "publish_time"
        # expiration_ms = 7776000000
    }

    clustering = ["message_id"]
}


#   ********************************************************************************************************   #
#                                             DataSet production |  Table production                           #
#   ********************************************************************************************************   #
resource "google_bigquery_table" "tb_wh_sensor" {
    dataset_id            = local.bq_dataset_production
    table_id              = var.tb_wh_sensor
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
    dataset_id            = local.bq_dataset_production
    table_id              = var.tb_feedback
    schema                = file("${path.module}/schemas/${var.tb_feedback}.json")
    deletion_protection   = false

    time_partitioning {
        type          = "DAY"
        field         = "fb_date"
    }

    clustering = ["feedback_id", "category", "brand", "rating"]
}


#   ********************************************************************************************************   #
#                                                   DataSet ls_customers                                       #
#   ********************************************************************************************************   #
resource "google_bigquery_table" "tb_customers" {
    dataset_id            = local.bq_dataset_ls_customers
    table_id              = var.tb_customers
    schema                = file("${path.module}/schemas/${var.tb_customers}.json")
    deletion_protection   = false

    time_partitioning {
        type          = "DAY"
        field         = "created_at"
    }

    clustering = ["associate_id", "name", "last_name", "cpf"]
}

resource "google_bigquery_table" "tb_cards" {
    dataset_id            = local.bq_dataset_ls_customers
    table_id              = var.tb_cards
    schema                = file("${path.module}/schemas/${var.tb_cards}.json")
    deletion_protection   = false

    time_partitioning {
        type          = "DAY"
        field         = "created_at"
    }

    clustering = ["card_id", "fk_associate_id", "card_flag", "Enabled"]
}

resource "google_bigquery_table" "tb_address" {
    dataset_id            = local.bq_dataset_ls_customers
    table_id              = var.tb_address
    schema                = file("${path.module}/schemas/${var.tb_address}.json")
    deletion_protection   = false

    time_partitioning {
        type          = "DAY"
        field         = "created_at"
    }

    clustering = ["address_id", "neighborhood", "city", "state"]
}

resource "google_bigquery_table" "tb_products" {
    dataset_id            = local.bq_dataset_ls_customers
    table_id              = var.tb_products
    schema                = file("${path.module}/schemas/${var.tb_products}.json")
    deletion_protection   = false

    time_partitioning {
        type          = "DAY"
        field         = "created_at"
    }

    clustering = ["product_id", "name", "category", "condition"]
}

resource "google_bigquery_table" "tb_inventory" {
    dataset_id            = local.bq_dataset_ls_customers
    table_id              = var.tb_inventory
    schema                = file("${path.module}/schemas/${var.tb_inventory}.json")
    deletion_protection   = false

    time_partitioning {
        type          = "DAY"
        field         = "created_at"
    }

    clustering = ["location", "inventory_id", "product_id", "last_restock"]
}

resource "google_bigquery_table" "tb_sales" {
    dataset_id            = local.bq_dataset_ls_customers
    table_id              = var.tb_sales
    schema                = file("${path.module}/schemas/${var.tb_sales}.json")
    deletion_protection   = false

    time_partitioning {
        type          = "DAY"
        field         = "purchase_date"
    }

    clustering = ["purchase_id", "associate_id", "product_id", "inventory_id"]
}

resource "google_bigquery_table" "tb_vehicles" {
    dataset_id            = local.bq_dataset_ls_customers
    table_id              = var.tb_vehicles
    schema                = file("${path.module}/schemas/${var.tb_vehicles}.json")
    deletion_protection   = false

    time_partitioning {
        type          = "DAY"
        field         = "created_at"
    }

    clustering = ["vehicle_id", "location", "year", "type"]
}

# resource "google_bigquery_table" "tb_delivery_locations" {
#     dataset_id            = local.bq_dataset_ls_customers
#     table_id              = var.tb_delivery_locations
#     schema                = file("${path.module}/schemas/tb_delivery_locations.json")
#     deletion_protection   = false

#     time_partitioning {
#         type          = "DAY"
#         field         = "created_at"
#     }

#     clustering = ["location_id", "state", "city", "neighborhood"]
# }

# resource "google_bigquery_table" "tb_processing_times" {
#     dataset_id            = local.bq_dataset_ls_customers
#     table_id              = var.tb_processing_times
#     schema                = file("${path.module}/schemas/tb_processing_times.json")
#     deletion_protection   = false

#     time_partitioning {
#         type          = "DAY"
#         field         = "created_at"
#     }

#     clustering = ["processing_id", "product_id", "location_id", "last_updated"]
# }