#   ********************************************************************************************************    #
#                                             Cloud Function Sensor                                             #
#   ********************************************************************************************************    #
data "archive_file" "cf_path_feedback_files" {
  type        = "zip"
  source_dir  = "../../src/cloud_function/cf_feedbacks/"
  output_path = "../../src/cloud_function/cf_feedbacks/index.zip"
}


resource "google_cloudfunctions2_function" "function" {
  project       = var.project
  location      = var.region
  name          = var.cf_name_feedback
  description   = "It will be triggered via airflow and will send data to the BigQuery table"

  build_config {
    runtime     = "python311"
    entry_point = "main"
    source {
      storage_source {
        bucket = var.bkt_mts_cf_feedback
        object = var.bkt_mts_cf_feedback_file_name
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
    service_account_email = var.sa_cf_feedback
    ingress_settings      = "ALLOW_ALL"
  }

  lifecycle {
    ignore_changes = [
      build_config,
      service_config,
    ]
  }
}