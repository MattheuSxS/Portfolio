output "pubsub_bq_role" {
    description = "value of pubsub bq role"
    value       = "${google_project_iam_member.pubsub_bq_role.*.role}"
}