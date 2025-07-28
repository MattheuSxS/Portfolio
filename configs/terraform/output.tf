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
}


# resource "google_storage_bucket_object" "my_dags" {

#     for_each        = fileset("../pipe/", "**.py")
#     name            = "dags/${each.value}"
#     bucket          = local.bkt_airflow
#     content_type    = "text/x-python"
#     source          = "../pipe/${each.value}"
# }


# resource "google_storage_bucket_object" "variables" {

#     for_each        = fileset("../pipe/${var.environment}_env", "**.json")
#     name            = "variables/${each.value}"
#     bucket          = local.bkt_airflow
#     content_type    = "application/json"
#     source          = "../pipe/${each.value}"
# }


# resource "google_storage_bucket_object" "pyspark_files" {

#     name            = "job_tb_order/${var.spark_order_job}.py"
#     bucket          = local.bkt_dataproc
#     content_type    = "text/x-python"
#     source          = "${var.dp_order_script_path}/${var.spark_order_job}.py"
# }