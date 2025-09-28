resource "google_storage_bucket" "bucket" {
    project                     = local.project
    count                       = length(var.bkt_names)
    name                        = "bkt-mts-${var.bkt_names[count.index]}"
    location                    = var.region
    storage_class               = var.bkt_class_standard
    force_destroy               = true
    uniform_bucket_level_access = true

    versioning {
        enabled = true
    }

    lifecycle_rule {
        condition {
            age = 90
        }
        action {
            type = "SetStorageClass"
            storage_class = var.bkt_class_nearline
        }
    }

    lifecycle_rule {
        condition {
            age = 150
        }
        action {
            type = "SetStorageClass"
            storage_class = var.bkt_class_coldline
        }
    }

    lifecycle_rule {
        condition {
            age = 180
        }
        action {
            type = "SetStorageClass"
            storage_class = var.bkt_class_archive
        }
    }

    lifecycle_rule {
        condition {
            num_newer_versions = 3
        }
        action {
            type = "Delete"
        }
    }

    labels = {
        "created_by": "terraform",
        "env": var.environment
    }
}


resource "google_storage_bucket_object" "cf_wh_sensor_files" {
    name            = "${var.cf_wh_sensor}/index.zip"
    bucket          = "${local.bkt_cf_portfolio}"
    source          = data.archive_file.cf_path_wh_sensor_files.output_path
    content_type    = "application/zip"

    lifecycle {
        ignore_changes = [
        source_md5hash,
        ]
    }
}


resource "google_storage_bucket_object" "cf_delivery_sensor_files" {
    name            = "${var.cf_delivery_sensor}/index.zip"
    bucket          = "${local.bkt_cf_portfolio}"
    source          = data.archive_file.cf_path_cf_delivery_sensor_files.output_path
    content_type    = "application/zip"

    lifecycle {
        ignore_changes = [
        source_md5hash,
        ]
    }
}


resource "google_storage_bucket_object" "cf_customers_files" {
    name            = "${var.cf_customers}/index.zip"
    bucket          = "${local.bkt_cf_portfolio}"
    source          = data.archive_file.cf_path_customers_files.output_path
    content_type    = "application/zip"

    lifecycle {
        ignore_changes = [
        source_md5hash,
        ]
    }
}

resource "google_storage_bucket_object" "cf_products_inventory_files" {
    name            = "${var.cf_products_inventory}/index.zip"
    bucket          = "${local.bkt_cf_portfolio}"
    source          = data.archive_file.cf_path_products_inventory_files.output_path
    content_type    = "application/zip"

    lifecycle {
        ignore_changes = [
        source_md5hash,
        ]
    }
}


resource "google_storage_bucket_object" "cf_sentiment_analysis_files" {
    name            = "${var.cf_sentiment_analysis}/index.zip"
    bucket          = "${local.bkt_cf_portfolio}"
    source          = data.archive_file.cf_path_sentiment_analysis_files.output_path
    content_type    = "application/zip"

    lifecycle {
        ignore_changes = [
        source_md5hash,
        ]
    }
}


resource "google_storage_bucket_object" "airflow_dags" {
    for_each        = fileset("../pipe/", "**.py")
    name            = "dags/${each.value}"
    bucket          = local.bkt_airflow
    content_type    = "text/x-python"
    source          = "../pipe/${each.value}"
}


resource "google_storage_bucket_object" "airflow_variables" {
    for_each        = fileset("../pipe/${var.environment}_env", "**.json")
    name            = "variables/${each.value}"
    bucket          = local.bkt_airflow
    content_type    = "application/json"
    source          = "../pipe/${var.environment}_env/${each.value}"
}


resource "google_storage_bucket_object" "spark_job_tb_order" {

    name            = "${var.spark_job_tb_order}/${var.spark_job_tb_order}.py"
    bucket          = local.bkt_dataproc
    content_type    = "text/x-python"
    source          = "${var.dp_order_script_path}/${var.spark_job_tb_order}.py"
}


resource "google_storage_bucket_object" "spark_path_tb_order" {
    depends_on = [null_resource.spark_path_tb_order]
    name            = "${var.spark_job_tb_order}/utils.zip"
    bucket          = local.bkt_dataproc
    content_type    = "application/zip"
    source          = "${var.dp_order_script_path}/utils.zip"
}


resource "google_storage_bucket_object" "spark_job_tb_feedback" {
    name            = "${var.spark_job_tb_feedback}/${var.spark_job_tb_feedback}.py"
    bucket          = local.bkt_dataproc
    content_type    = "text/x-python"
    source          = "${var.dp_feedback_script_path}/${var.spark_job_tb_feedback}.py"
}


resource "google_storage_bucket_object" "spark_path_tb_feedback" {
    depends_on = [null_resource.spark_path_tb_feedback]
    name            = "${var.spark_job_tb_feedback}/utils.zip"
    bucket          = local.bkt_dataproc
    content_type    = "application/zip"
    source          = "${var.dp_feedback_script_path}/utils.zip"
}


# resource "null_resource" "bkt_compose_delete" {
#     triggers = {
#         bucket_name = local.bkt_airflow
#     }
#     depends_on = [null_resource.pause_all_dags]

#     provisioner "local-exec" {
#         when    = destroy
#         command = <<-EOT
#         sleep 30
#         echo "Deleting all objects in GCS bucket ${self.triggers.bucket_name}..."
#         gcloud storage rm -r --recursive gs://${self.triggers.bucket_name}
#         EOT
#     }
# }