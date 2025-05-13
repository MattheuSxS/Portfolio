output "pubsub_bq_role" {
    description = "value of pubsub bq role"
    value       = "${google_project_iam_member.pubsub_bq_role.*.role}"
}

output "sa_composer" {
    description = "value of sa cf sensor"
    value       = "${google_service_account.creating_sa[0].email}"
}

output "sa_dataflow" {
    description = "value of sa cf sensor"
    value       = "${google_service_account.creating_sa[1].email}"
}

output "sa_dataproc" {
    description = "value of sa cf sensor"
    value       = "${google_service_account.creating_sa[2].email}"
}

output "sa_cf_hw_sensor" {
    description = "value of sa cf sensor"
    value       = "${google_service_account.creating_sa[3].email}"
}

output "sa_cf_order" {
    description = "value of sa cf sensor"
    value       = "${google_service_account.creating_sa[4].email}"
}

output "sa_pub_sub" {
    description = "value of sa cf sensor"
    value       = "${google_service_account.creating_sa[5].email}"
}