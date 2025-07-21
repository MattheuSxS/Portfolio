resource "google_storage_bucket" "bucket" {
  project                     = var.project[terraform.workspace]
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
    name            = "cf_wh_sensor/index.zip"
    bucket          = "${google_storage_bucket.bucket[0].name}"
    source          = data.archive_file.cf_path_wh_sensor_files.output_path
    content_type    = "application/zip"

    lifecycle {
        ignore_changes = [
        source_md5hash,
        ]
    }
}


resource "google_storage_bucket_object" "cf_feedback_files" {
    name            = "cf_feedback/index.zip"
    bucket          = "${google_storage_bucket.bucket[0].name}"
    source          = data.archive_file.cf_path_feedback_files.output_path
    content_type    = "application/zip"

    lifecycle {
        ignore_changes = [
        source_md5hash,
        ]
    }
}


resource "google_storage_bucket_object" "cf_customers_files" {
    name            = "cf_customers/index.zip"
    bucket          = "${google_storage_bucket.bucket[0].name}"
    source          = data.archive_file.cf_path_customers_files.output_path
    content_type    = "application/zip"

    lifecycle {
        ignore_changes = [
        source_md5hash,
        ]
    }
}