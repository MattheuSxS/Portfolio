# output "pubsub_bq_role" {
#     description = "value of pubsub bq role"
#     value       = "${google_project_iam_member.pubsub_bq_role.*.role}"
# }

# output "sa_composer" {
#     description = "value of sa composer"
#     value       = "${google_service_account.creating_sa[0].email}"
# }

# output "sa_dataflow" {
#     description = "value of sa dataflow"
#     value       = "${google_service_account.creating_sa[1].email}"
# }

# output "sa_dataproc" {
#     description = "value of sa dataproc"
#     value       = "${google_service_account.creating_sa[2].email}"
# }

# output "sa_cf_wh_sensor" {
#     description = "value of sa cf sensor"
#     value       = "${google_service_account.creating_sa[3].email}"
# }

# output "sa_cf_order" {
#     description = "value of sa cf order"
#     value       = "${google_service_account.creating_sa[4].email}"
# }

# output "sa_pub_sub" {
#     description = "value of sa pub sub"
#     value       = "${google_service_account.creating_sa[5].email}"
# }

# output "sa_cf_feedback" {
#     description = "value of sa cf feedback"
#     value       = "${google_service_account.creating_sa[6].email}"
# }


# output "bkt_mts_cf_wh_sensor" {
#     description = "Cloud Function Sensor"
#     value       = google_storage_bucket.bucket[0].name
# }

# output "bkt_mts_cf_ai_api" {
#     description = "Cloud Function AI API"
#     value       = google_storage_bucket.bucket[1].name
# }

# output "bkt_mts_cf_feedback" {
#     description = "Cloud Function Feedback"
#     value       = google_storage_bucket.bucket[2].name
# }

# output "bkt_mts_cf_order" {
#     description = "Cloud Function Order"
#     value       = google_storage_bucket.bucket[3].name
# }

# output "bkt_mts_dataflow" {
#     description = "Dataflow"
#     value       = google_storage_bucket.bucket[4].name
# }

# output "bkt_mts_dataproc" {
#     description = "Dataproc"
#     value       = google_storage_bucket.bucket[5].name
# }

# # output "bkt_mts_cf_wh_sensor_file_name" {
# #     description = "Ready sensor files"
# #     value       = google_storage_bucket_object.cf_wh_sensor_files.name
# # }

# output "bkt_mts_cf_feedback_file_name" {
#     description = "Ready sensor files"
#     value       = replace(replace(google_composer_environment.portfolio-composer.config[0].dag_gcs_prefix, "gs://", ""), "/dags", "")
# }


locals {
    bkt_cf_portfolio    = google_storage_bucket.bucket[0].name
    bkt_dataflow        = google_storage_bucket.bucket[1].name
    bkt_dataproc        = google_storage_bucket.bucket[2].name
    bkt_airflow         = replace(replace(google_composer_environment.portfolio-composer.config[0].dag_gcs_prefix, "gs://", ""), "/dags", "")
}
