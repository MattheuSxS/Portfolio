#   ********************************************************************************************************    #
#                                             Cloud Function Sensor                                             #
#   ********************************************************************************************************    #
data "archive_file" "cf_path_customers_files" {
    type        = "zip"
    source_dir  = "../../src/cloud_function/cf_customers/"
    output_path = "../../src/cloud_function/cf_customers/index.zip"
}


resource "google_cloudfunctions2_function" "function" {
  project       = var.project
  location      = var.region
  name          = var.cf_name_customers
  description   = "Cloud Function for processing customer data"

  build_config {
    runtime     = "python311"
    entry_point = "main"
    source {
      storage_source {
        bucket = var.bkt_mts_cf_customers
        object = var.bkt_mts_cf_customers_file_name
      }
    }
  }

  labels = {
    "created_by": "terraform",
    "layer": "trusted",
    "env": "dev"
  }

  service_config {
    max_instance_count    = 1
    min_instance_count    = 1
    available_memory      = "1G"
    timeout_seconds       = 3000
    service_account_email = var.sa_cf_customers
    ingress_settings      = "ALLOW_ALL"
  }

  lifecycle {
    ignore_changes = [
      build_config,
      service_config,
    ]
  }
}