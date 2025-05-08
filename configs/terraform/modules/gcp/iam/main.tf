resource "google_project_iam_member" "pubsub_bq_role" {
  project   = var.project
  count     = length(var.roles_sa_pub_sub)
  role      = var.roles_sa_pub_sub[count.index]
  member    = "serviceAccount:service-${var.project_id}@gcp-sa-pubsub.iam.gserviceaccount.com"
}
