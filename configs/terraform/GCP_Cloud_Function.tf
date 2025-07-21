#   ********************************************************************************************************    #
#                                             Cloud Function Customers                                          #
#   ********************************************************************************************************    #
data "archive_file" "cf_path_customers_files" {
    type        = "zip"
    source_dir  = "../../src/cloud_function/cf_customers/"
    output_path = "../../src/cloud_function/cf_customers/index.zip"
}


resource "google_cloudfunctions2_function" "cf_customers" {
    project       = var.project[terraform.workspace]
    location      = var.region
    name          = var.cf_name_customers
    description   = "Cloud Function for processing customer data"

    build_config {
        runtime     = "python311"
        entry_point = "main"
        source {
            storage_source {
            bucket = google_storage_bucket.bucket[0].name
            object = google_storage_bucket_object.cf_customers_files.name
            }
        }
    }

  labels = {
    "created_by": "terraform",
    "layer": "trusted",
    "env": "dev"
  }

    service_config {
        max_instance_count              = 2
        min_instance_count              = 1
        available_memory                = "4Gi"
        available_cpu                   = 4
        timeout_seconds                 = 3000
        service_account_email           = google_service_account.creating_sa[4].email
        ingress_settings                = "ALLOW_ALL"
        all_traffic_on_latest_revision  = true
    }

    lifecycle {
        ignore_changes = [
        build_config,
        service_config,
        ]
    }
}


#   ********************************************************************************************************    #
#                                           Cloud Function Feedback Sensor                                      #
#   ********************************************************************************************************    #
data "archive_file" "cf_path_feedback_files" {
    type        = "zip"
    source_dir  = "../../src/cloud_function/cf_feedbacks/"
    output_path = "../../src/cloud_function/cf_feedbacks/index.zip"
}


resource "google_cloudfunctions2_function" "cf_feedback" {
    project       = var.project[terraform.workspace]
    location      = var.region
    name          = var.cf_name_feedback
    description   = "It will be triggered via airflow and will send data to the BigQuery table"

    build_config {
        runtime     = "python311"
        entry_point = "main"
        source {
            storage_source {
                bucket = google_storage_bucket.bucket[0].name
                object = google_storage_bucket_object.cf_feedback_files.name
            }
        }
    }

    labels = {
        "created_by": "terraform",
        "env": var.environment
    }

    service_config {
        max_instance_count    = 1
        min_instance_count    = 1
        available_memory      = "256M"
        timeout_seconds       = 3000
        service_account_email = google_service_account.creating_sa[6].email
        ingress_settings      = "ALLOW_ALL"
    }

    lifecycle {
        ignore_changes = [
        build_config,
        service_config,
        ]
    }
}


#   ********************************************************************************************************    #
#                                          Cloud Function WareHouse Sensor                                      #
#   ********************************************************************************************************    #
data "archive_file" "cf_path_wh_sensor_files" {
  type        = "zip"
  source_dir  = "../../src/cloud_function/cf_wh_sensor/"
  output_path = "../../src/cloud_function/cf_wh_sensor/index.zip"
}


resource "google_cloudfunctions2_function" "cf_wh_sensor" {
  project       = var.project[terraform.workspace]
  location      = var.region
  name          = var.cf_name_wh_sensor
  description   = "It will be triggered via airflow and will send data to the pub/sub"

  build_config {
    runtime     = "python311"
    entry_point = "main"
    source {
      storage_source {
        bucket = google_storage_bucket.bucket[0].name
        object = google_storage_bucket_object.cf_feedback_files.name
      }
    }
  }

  labels = {
    "created_by": "terraform",
    "env": var.environment
  }

  service_config {
    max_instance_count    = 1
    min_instance_count    = 1
    available_memory      = "256M"
    timeout_seconds       = 3000
    service_account_email = google_service_account.creating_sa[3].email
    ingress_settings      = "ALLOW_ALL"
  }

  lifecycle {
    ignore_changes = [
      build_config,
      service_config,
    ]
  }
}