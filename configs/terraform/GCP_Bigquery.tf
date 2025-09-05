#   ********************************************************************************************************   #
#                                                     DataSets                                                 #
#   ********************************************************************************************************   #
resource "google_bigquery_dataset" "bq_dataset" {
    project                     = local.project
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

resource "google_bigquery_table" "tb_delivery_status" {
    dataset_id            = local.bq_dataset_ls_customers
    table_id              = var.tb_delivery_status
    schema                = file("${path.module}/schemas/${var.tb_delivery_status}.json")
    deletion_protection   = false

    time_partitioning {
        type          = "DAY"
        field         = "created_at"
    }

    clustering = ["purchase_id", "delivery_id", "vehicle_id", "status"]
}

resource "google_bigquery_table" "tb_delivery_status_stage" {
    dataset_id            = local.bq_dataset_staging
    table_id              = "${var.tb_delivery_status}_stage"
    schema                = file("${path.module}/schemas/${var.tb_delivery_status}.json")
    deletion_protection   = false

    time_partitioning {
        type          = "DAY"
        field         = "created_at"
    }

    clustering = ["purchase_id", "delivery_id", "vehicle_id", "status"]
}


resource "google_bigquery_routine" "sp_merge_delivery_status" {
    project         = local.project
    dataset_id      = local.bq_dataset_ls_customers
    routine_id      = var.sp_merge_delivery_status
    routine_type    = "PROCEDURE"
    language        = "SQL"
    definition_body = <<-EOT
        BEGIN
            BEGIN TRANSACTION;

            CREATE TEMP TABLE RecentData AS (
                SELECT
                    *
                FROM
                    `${local.project}.${local.bq_dataset_staging}.${var.tb_delivery_status}_stage`
                WHERE
                    DATETIME(updated_at) >= TIMESTAMP_SUB(DATETIME(CURRENT_TIMESTAMP(), 'Europe/Dublin'), INTERVAL 45 MINUTE)
            );

            MERGE `${local.project}.${local.bq_dataset_ls_customers}.${var.tb_delivery_status}` AS T
            USING RecentData AS S
            ON T.delivery_id = S.delivery_id
            WHEN MATCHED THEN
                UPDATE SET
                T.remaining_distance_km = COALESCE(S.remaining_distance_km, T.remaining_distance_km),
                T.estimated_time_min = COALESCE(S.estimated_time_min, T.estimated_time_min),
                T.delivery_difficulty = COALESCE(S.delivery_difficulty, T.delivery_difficulty),
                T.status = COALESCE(S.status, T.status),
                T.updated_at = COALESCE(S.updated_at, T.updated_at)
            WHEN NOT MATCHED BY TARGET THEN
                INSERT (
                    delivery_id,
                    vehicle_id,
                    purchase_id,
                    remaining_distance_km,
                    estimated_time_min,
                    delivery_difficulty,
                    status,
                    created_at,
                    updated_at
                )
                VALUES (
                    S.delivery_id,
                    S.vehicle_id,
                    S.purchase_id,
                    S.remaining_distance_km,
                    S.estimated_time_min,
                    S.delivery_difficulty,
                    S.status,
                    COALESCE(S.created_at, CURRENT_TIMESTAMP()),
                    COALESCE(S.updated_at, CURRENT_TIMESTAMP())
                );

            DELETE FROM `${local.project}.${local.bq_dataset_staging}.${var.tb_delivery_status}_stage`
            WHERE delivery_id IN (SELECT delivery_id FROM RecentData);

            COMMIT TRANSACTION;
        END;
    EOT
}