locals {
    project     = var.project[terraform.workspace]
    project_id  = var.project_id[terraform.workspace]

    # bkt_cf_portfolio    = google_storage_bucket.bucket[0].name
    # bkt_dataflow        = google_storage_bucket.bucket[1].name
    # bkt_dataproc        = google_storage_bucket.bucket[2].name
    # bkt_airflow         = google_storage_bucket.bucket[3].name

    # sa_composer                 = google_service_account.creating_sa[0].email
    # sa_pubsub                   = google_service_account.creating_sa[1].email
    # sa_dataflow                 = google_service_account.creating_sa[2].email
    # sa_cf_default               = google_service_account.creating_sa[3].email
    # sa_cf_pb_sensor             = google_service_account.creating_sa[4].email
    # sa_cloud_run                = google_service_account.creating_sa[5].email

    bq_dataset_raw              = google_bigquery_dataset.bq_dataset[0].dataset_id
    bq_dataset_staging          = google_bigquery_dataset.bq_dataset[1].dataset_id
    bq_dataset_production       = google_bigquery_dataset.bq_dataset[2].dataset_id
    bq_dataset_ls_customers     = google_bigquery_dataset.bq_dataset[3].dataset_id

    # pb_wh_sensor_topic          = google_pubsub_topic.pub_sub_topics[0].name
    # pb_delivery_sensor_topic    = google_pubsub_topic.pub_sub_topics[1].name

    # pb_sub_wh_sensor            = google_pubsub_subscription.pub_sub_wh_sensor_subs.name
    # pb_sub_delivery_sensor      = google_pubsub_subscription.pub_sub_delivery_sensor_subs.name

    # secret_ps_wh_sensor_access_authorization        = google_secret_manager_secret.create_secrets[0].id
    # secret_ps_delivery_sensor_access_authorization  = google_secret_manager_secret.create_secrets[1].id
    # secret_bq_feedback_access_authorization         = google_secret_manager_secret.create_secrets[2].id
    # secret_bq_customers_access_authorization        = google_secret_manager_secret.create_secrets[3].id
    # secret_bq_products_access_authorization         = google_secret_manager_secret.create_secrets[4].id
    # secret_bq_sales_access_authorization            = google_secret_manager_secret.create_secrets[5].id

    artifact_registry_url   = "${var.region}-docker.pkg.dev/${local.project}/${var.docker_repository}"
    # dfl_script_path         = "${path.cwd}/../../modules/dataflow"

    # sentiment_context_path = "${var.run_path_all_files}/${replace(var.sentiment_analysis, "-", "_")}/src"
    # sentiment_hash = sha256(join("", [
    #     for f in fileset(local.sentiment_context_path, "**") :
    #     filesha256("${local.sentiment_context_path}/${f}")
    # ]))
    # sentiment_image_tag = substr(local.sentiment_hash, 0, 12)

    # #TODO: I need to back here and solve the variable name
    logistream_solutions_report_context_path = "${var.run_path_all_files}/market_research/src"
    logistream_solutions_report_hash = sha256(join("", [
        for f in fileset(local.logistream_solutions_report_context_path, "**") :
        filesha256("${local.logistream_solutions_report_context_path}/${f}")
    ]))
    logistream_solutions_report_image_tag = substr(local.logistream_solutions_report_hash, 0, 12)

    sales_forecast_report_context_path = "${var.run_path_all_files}/sales_forecast/src"
    sales_forecast_report_hash = sha256(join("", [
        for f in fileset(local.sales_forecast_report_context_path, "**") :
        filesha256("${local.sales_forecast_report_context_path}/${f}")
    ]))
    sales_forecast_report_image_tag = substr(local.sales_forecast_report_hash, 0, 12)

}

# output "logistream_solutions_report_service_url" {
#     value = google_cloud_run_v2_service.logistream_solutions_report.uri
# }

# output "sales_forecast_report_service_url" {
#     value = google_cloud_run_v2_service.sales_forecast_report.uri
# }
