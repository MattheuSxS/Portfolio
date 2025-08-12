locals {
    bkt_cf_portfolio    = google_storage_bucket.bucket[0].name
    bkt_dataflow        = google_storage_bucket.data_tools_bucket[0].name
    bkt_dataproc        = google_storage_bucket.data_tools_bucket[1].name
    bkt_airflow         = replace(replace(google_composer_environment.portfolio-composer.config[0].dag_gcs_prefix, "gs://", ""), "/dags", "")

    sa_composer                 = google_service_account.creating_sa[0].email
    sa_pubsub                   = google_service_account.creating_sa[1].email
    sa_cf_customers             = google_service_account.creating_sa[2].email
    sa_cf_wh_sensor             = google_service_account.creating_sa[3].email
    sa_cf_delivery_sensor       = google_service_account.creating_sa[4].email
    sa_cf_products_inventory    = google_service_account.creating_sa[5].email
    sa_dataflow                 = google_service_account.data_tools_creating_sa[0].email

    bq_dataset_raw              = google_bigquery_dataset.bq_dataset[0].dataset_id
    bq_dataset_staging          = google_bigquery_dataset.bq_dataset[1].dataset_id
    bq_dataset_production       = google_bigquery_dataset.bq_dataset[2].dataset_id
    bq_dataset_ls_customers     = google_bigquery_dataset.bq_dataset[3].dataset_id

    pb_wh_sensor_topic          = google_pubsub_topic.pub_sub_topics[0].name
    pb_delivery_sensor_topic    = google_pubsub_topic.pub_sub_topics[1].name


    secret_wh_sensor_access_authorization       = google_secret_manager_secret.create_secrets[0].id
    secret_bq_feedback_access_authorization     = google_secret_manager_secret.create_secrets[1].id
    secret_bq_customers_access_authorization    = google_secret_manager_secret.create_secrets[2].id
    secret_bq_products_access_authorization     = google_secret_manager_secret.create_secrets[3].id
}