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
    project               = local.project
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
    project               = local.project
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
    project               = local.project
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
    project               = local.project
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

resource "google_bigquery_table" "tb_feedback_sentiment" {
    project               = local.project
    dataset_id            = local.bq_dataset_production
    table_id              = var.tb_feedback_sentiment
    schema                = file("${path.module}/schemas/${var.tb_feedback_sentiment}.json")
    deletion_protection   = false

    time_partitioning {
        type          = "DAY"
        field         = "created_at"
    }

    clustering = ["updated_at", "feedback_id"]
}
#   ********************************************************************************************************   #
#                                                   DataSet ls_customers                                       #
#   ********************************************************************************************************   #
resource "google_bigquery_table" "tb_customers" {
    project               = local.project
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
    project               = local.project
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
    project               = local.project
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
    project               = local.project
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
    project               = local.project
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
    project               = local.project
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
    project               = local.project
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
    project               = local.project
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
    project               = local.project
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


#   ********************************************************************************************************   #
#                                                 BigQuery  Connections                                        #
#   ********************************************************************************************************   #
resource "google_bigquery_connection" "cf_sentiment_analysis" {
    connection_id = var.cf_sentiment_analysis
    project       = local.project
    location      = "us-east1"
    description   =  "Connection for the Cloud Function to access BigQuery"
    friendly_name = "cf_sentiment_analysis_connection"
    cloud_resource {}
}


#   ********************************************************************************************************   #
#                                                 BigQuery Functions                                           #
#   ********************************************************************************************************   #
resource "google_bigquery_routine" "sentiment_analysis" {
    project      = local.project
    dataset_id   = local.bq_dataset_production
    routine_id   = "sentiment_analysis"
    routine_type = "SCALAR_FUNCTION"
    language     = "SQL"
    definition_body = ""

  arguments {
        name      = "text"
        data_type = "{\"typeKind\" :  \"STRING\"}"
  }

  return_type = "{\"typeKind\" :  \"JSON\"}"

  remote_function_options {
    connection          = google_bigquery_connection.cf_sentiment_analysis.id
    endpoint            = google_cloudfunctions2_function.cf_sentiment_analysis.service_config[0].uri
    max_batching_rows   = 2000
  }

  description = "Function to perform sentiment analysis using Cloud Function"
}


#   ********************************************************************************************************   #
#                                                 BigQuery  Procedures                                         #
#   ********************************************************************************************************   #
resource "google_bigquery_routine" "sp_merge_delivery_status" {
    project         = local.project
    dataset_id      = local.bq_dataset_ls_customers
    routine_id      = var.sp_merge_delivery_status
    routine_type    = "PROCEDURE"
    language        = "SQL"
    definition_body = <<-EOT
        BEGIN
            BEGIN TRANSACTION;

                CREATE TEMP TABLE AdditionalData AS (
                    SELECT
                        JSON_VALUE(attributes, '$.delivery_id') AS delivery_id,
                        CAST(JSON_VALUE(data, '$.remaining_distance_km') AS INT64) AS remaining_distance_km,
                        CAST(JSON_VALUE(data, '$.estimated_time_min') AS INT64) AS estimated_time_min,
                    FROM
                        `${local.project}.${local.bq_dataset_raw}.tb_raw_delivery_sensor`
                    WHERE
                        DATE(publish_time) = CURRENT_DATE()
                    QUALIFY
                        ROW_NUMBER() OVER (PARTITION BY delivery_id ORDER BY remaining_distance_km DESC) = 1
                );

                CREATE TEMP TABLE RecentData AS (
                    SELECT
                        TBDS.delivery_id,
                        TBDS.vehicle_id,
                        TBDS.purchase_id,
                        ADDA.remaining_distance_km,
                        ADDA.estimated_time_min,
                        TBDS.delivery_difficulty,
                        TBDS.status,
                        TBDS.created_at,
                        TBDS.updated_at,
                    FROM
                        `${local.project}.${local.bq_dataset_staging}.tb_delivery_status_stage` AS TBDS
                    LEFT JOIN
                        AdditionalData AS ADDA
                    ON
                        TBDS.delivery_id = ADDA.delivery_id
                );


                MERGE `${local.project}.${local.bq_dataset_ls_customers}.tb_delivery_status` AS T
                USING RecentData AS S
                ON T.delivery_id = S.delivery_id
                WHEN MATCHED THEN
                    UPDATE SET
                    T.remaining_distance_km     = COALESCE(S.remaining_distance_km, T.remaining_distance_km),
                    T.estimated_time_min        = COALESCE(S.estimated_time_min, T.estimated_time_min),
                    T.delivery_difficulty       = COALESCE(S.delivery_difficulty, T.delivery_difficulty),
                    T.status                    = COALESCE(S.status, T.status),
                    T.updated_at                = COALESCE(S.updated_at, T.updated_at)
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
            COMMIT TRANSACTION;
        END;
    EOT
}


resource "google_bigquery_routine" "sp_delete_delivery_status" {
    project         = local.project
    dataset_id      = local.bq_dataset_ls_customers
    routine_id      = var.sp_delete_delivery_status
    routine_type    = "PROCEDURE"
    language        = "SQL"
    definition_body = <<-EOT
        BEGIN
            BEGIN TRANSACTION;

                DELETE FROM
                    `${local.project}.${local.bq_dataset_staging}.tb_delivery_status_stage`
                WHERE
                    DATE(created_at) <= DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
                AND delivery_id IN (
                    SELECT
                        delivery_id
                    FROM
                        `${local.project}.${local.bq_dataset_ls_customers}.tb_delivery_status`
                    WHERE
                        DATE(created_at) <= DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
                );

            COMMIT TRANSACTION;
        END;
    EOT
}

resource "google_bigquery_routine" "sp_feedback_sentiment" {
    project         = local.project
    dataset_id      = local.bq_dataset_production
    routine_id      = var.sp_feedback_sentiment
    routine_type    = "PROCEDURE"
    language        = "SQL"
    definition_body = <<-EOT
        BEGIN
            INSERT INTO `${local.project}.${local.bq_dataset_production}.tb_feedback_sentiment` (
                feedback_id,
                feeling_score,
                feeling_magnitude,
                created_at,
                updated_at
            )
            WITH feedback_with_analysis AS (
                SELECT
                    f.feedback_id,
                    f.created_at,
                    sa.score AS feeling_score,
                    sa.magnitude AS feeling_magnitude,
                    -- Gera um ID para manter a ordem antes e depois da chamada da API
                    ROW_NUMBER() OVER (ORDER BY f.feedback_id) AS rn
                FROM
                    `${local.project}.${local.bq_dataset_production}.tb_feedback` AS f,
                    -- Chama a função UMA VEZ com um array de todos os comentários
                    UNNEST(
                        `${local.project}.${local.bq_dataset_production}.sentiment_analysis`(
                            (SELECT ARRAY_AGG(comment) FROM `${local.project}.${local.bq_dataset_production}.tb_feedback`)
                        )
                    ) WITH OFFSET AS sa_offset -- Pega o resultado da API e seu índice
                -- Junta o feedback original com o resultado da análise pelo índice
                WHERE
                    ROW_NUMBER() OVER (ORDER BY f.feedback_id) = sa_offset + 1
            )
            SELECT
                feedback_id,
                CAST(feeling_score AS FLOAT64),
                CAST(feeling_magnitude AS FLOAT64),
                created_at,
                CURRENT_TIMESTAMP() AS updated_at
            FROM
                feedback_with_analysis;
        END;
    EOT
}
