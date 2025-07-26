locals {
    bkt_cf_portfolio    = google_storage_bucket.bucket[0].name
    bkt_dataflow        = google_storage_bucket.bucket[1].name
    bkt_dataproc        = google_storage_bucket.bucket[2].name
    bkt_airflow         = replace(replace(google_composer_environment.portfolio-composer.config[0].dag_gcs_prefix, "gs://", ""), "/dags", "")

    sa_composer                 = google_service_account.creating_sa[0].email
    sa_dataflow                 = google_service_account.creating_sa[1].email
    sa_pubsub                   = google_service_account.creating_sa[2].email
    sa_cf_customers             = google_service_account.creating_sa[3].email
    sa_cf_wh_sensor             = google_service_account.creating_sa[4].email
    sa_cf_delivery_sensor       = google_service_account.creating_sa[5].email
    sa_cf_products_inventory    = google_service_account.creating_sa[6].email
}
