#   ********************************************************************************************************    #
#                                             Cloud Function Sensor                                             #
#   ********************************************************************************************************    #
data "archive_file" "cf_path_sensor_files" {
    type        = "zip"
    source_dir  = "../../src/cloud_function/cf_sensor/"
    output_path = "../../src/cloud_function/cf_sensor/index.zip"
}


resource "google_cloudfunctions2_function" "function" {
  project       = var.project
  location      = var.region
  name          = var.function_name
  description   = "It will be triggered via airflow and will send data to the pub/sub"

  build_config {
    runtime     = "python311"
    entry_point = "main"
    source {
      storage_source {
        bucket = var.bkt_mts_cf_sensor
        object = var.bkt_mts_cf_sensor_file_name
      }
    }
  }

  labels = {
    "created_by": "terraform",
    "layer": "trusted",
    "env": "dev"
  }

  service_config {
    max_instance_count  = 1
    min_instance_count  = 1
    available_memory    = "512M"
    timeout_seconds     = 3000
  }

  lifecycle {
    ignore_changes = [
      build_config,
      service_config,
    ]
  }

}