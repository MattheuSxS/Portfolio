# #  ********************************************************************************************************    #
# #                                            Dataflow Delivery Sensor                                          #
# #  ********************************************************************************************************    #
# resource "null_resource" "run_dataflow_job" {
#     provisioner "local-exec" {
#         command = <<EOT
#         python "${var.dfl_wh_sensor_script_path}/${var.dfl_wh_sensor_template}.py" \
#             --runner "DataflowRunner" \
#             --project_dataflow "${var.project_data_tools[terraform.workspace]}" \
#             --region "${var.region}" \
#             --job_name "${var.dfl_wh_sensor_job_name}" \
#             --bkt_dataflow "${google_storage_bucket.bucket[1].name}" \
#             --project "${var.project_data_tools[terraform.workspace]}" \
#             --dataset "${google_bigquery_dataset.bq_dataset[2].dataset_id}" \
#             --subscription "${var.pub_sub_wh_sensor_subs}" \
#             --setup_file ${var.dfl_wh_sensor_script_path}/setup.py \
#             --template_location "gs://${google_storage_bucket.bucket[1].name}/template/${var.dfl_wh_sensor_template}"
#         EOT
#     }
# }


# resource "google_dataflow_job" "dataflow_job" {

#     depends_on              = [
#                                 null_resource.run_dataflow_job,
#                                 google_project_iam_member.roles_sa_dataflow
#                             ]

#     name                    = var.dfl_wh_sensor_job_name
#     template_gcs_path       = "gs://${google_storage_bucket.bucket[1].name}/template/${var.dfl_wh_sensor_template}"
#     temp_gcs_location       = "gs://${google_storage_bucket.bucket[1].name}/tmp_dir"
#     enable_streaming_engine = true
#     service_account_email   = local.sa_dataflow

#     parameters = {
#         project_dataflow = var.project_data_tools[terraform.workspace]
#         region           = var.region
#         job_name         = var.dfl_wh_sensor_job_name
#         bkt_dataflow     = google_storage_bucket.bucket[1].name
#         project          = var.project_data_tools[terraform.workspace]
#         dataset          = google_bigquery_dataset.bq_dataset[2].dataset_id
#         subscription     = google_pubsub_subscription.pub_sub_wh_sensor_subs.name
#     }

#     on_delete = "cancel"

#     lifecycle {
#         prevent_destroy = false
#     }

#     labels = {
#         "created_by": "terraform",
#         "env": var.environment
#     }
# }
