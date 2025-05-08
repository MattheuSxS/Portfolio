output "bkt_mts_cf_sensor" {
    description = "Cloud Function Sensor"
    value       = google_storage_bucket.bucket[0].name
}

output "bkt_mts_cf_ai_api" {
    description = "Cloud Function AI API"
    value       = google_storage_bucket.bucket[1].name
}

output "bkt_mts_cf_feedback" {
    description = "Cloud Function Feedback"
    value       = google_storage_bucket.bucket[2].name
}

output "bkt_mts_cf_order" {
    description = "Cloud Function Order"
    value       = google_storage_bucket.bucket[3].name
}

output "bkt_mts_dataflow" {
    description = "Dataflow"
    value       = google_storage_bucket.bucket[4].name
}

output "bkt_mts_dataproc" {
    description = "Dataproc"
    value       = google_storage_bucket.bucket[5].name
}

output "bkt_mts_airflow" {
    description = "Airflow"
    value       = google_storage_bucket.bucket[6].name
}

output "bkt_mts_cf_sensor_file_name" {
    description = "Ready sensor files"
    value       = google_storage_bucket_object.archive.name
}