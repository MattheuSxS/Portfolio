resource "google_project_iam_member" "pubsub_bq_role" {
  project = var.project[terraform.workspace]
  count   = length(var.roles_sa_pub_sub)
  role    = var.roles_sa_pub_sub[count.index]
  member  = "serviceAccount:service-${var.project_id[terraform.workspace]}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_service_account" "creating_sa" {
  project     = var.project[terraform.workspace]
  count       = length(var.creating_sa)
  account_id  = var.creating_sa[count.index]
  description = "Creating Service Account to project ${var.project[terraform.workspace]}"

  lifecycle {
    prevent_destroy = false
  }
}


resource "google_project_iam_member" "roles_sa_composer" {
  project = var.project[terraform.workspace]
  count   = length(var.roles_sa_composer)
  role    = var.roles_sa_composer[count.index]
  member  = "serviceAccount:${local.sa_composer}"
}

resource "google_project_iam_member" "roles_sa_dataflow" {
  project = var.project[terraform.workspace]
  count   = length(var.roles_sa_dataflow)
  role    = var.roles_sa_dataflow[count.index]
  member  = "serviceAccount:${local.sa_dataflow}"
}

resource "google_project_iam_member" "roles_sa_cf_customers" {
  project = var.project[terraform.workspace]
  count   = length(var.roles_sa_cf_customers)
  role    = var.roles_sa_cf_customers[count.index]
  member  = "serviceAccount:${local.sa_cf_customers}"
}

resource "google_project_iam_member" "roles_sa_cf_wh_sensor" {
  project = var.project[terraform.workspace]
  count   = length(var.roles_sa_cf_wh_sensor)
  role    = var.roles_sa_cf_wh_sensor[count.index]
  member  = "serviceAccount:${local.sa_cf_wh_sensor}"
}

resource "google_project_iam_member" "roles_sa_cf_products_inventory" {
  project = var.project[terraform.workspace]
  count   = length(var.roles_sa_cf_products_inventory)
  role    = var.roles_sa_cf_products_inventory[count.index]
  member  = "serviceAccount:${local.sa_cf_products_inventory}"
}

resource "google_project_iam_member" "roles_sa_default_compute" {
  project = var.project[terraform.workspace]
  count   = length(var.roles_sa_default_compute)
  role    = var.roles_sa_default_compute[count.index]
  member  = "serviceAccount:${var.project_id[terraform.workspace]}-compute@developer.gserviceaccount.com"
}