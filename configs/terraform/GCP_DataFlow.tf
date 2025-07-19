#TODO: Conclude the DataFlow job configuration
# resource "null_resource" "run_dataflow_job" {
#     provisioner "local-exec" {
#         command = <<EOT
#         python "${var.dfl_script_path}/dfw_get_data_nrt.py" \
#             --runner "DataflowRunner" \
#             --project_dataflow "${var.project}" \
#             --region "${var.region}" \
#             --job_name "${var.dfl_sensor_job_name}" \
#             --bkt_dataflow "${var.bkt_mts_dataflow}" \
#             --project "${var.project}" \
#             --dataset "${var.dataset_trusted}" \
#             --subscription "${var.pub_sub_wh_sensor_subscription}" \
#             --setup_file ${var.dfl_script_path}/setup.py \
#             --template_location "gs://${var.bkt_mts_dataflow}/template/${var.dfl_sensor_template}"
#         EOT
#     }
# }


# resource "google_dataflow_job" "dataflow_job" {

#     # depends_on              = [
#     #                             null_resource.run_dataflow_job,
#     #                             google_pubsub_subscription.tp_pj_streaming_sub,
#     #                             google_project_iam_member.roles_dataflow
#     #                         ]

#     name                    = var.dfl_sensor_job_name
#     template_gcs_path       = "gs://${var.bkt_mts_dataflow}/template/${var.dfl_sensor_template}"
#     temp_gcs_location       = "gs://${var.bkt_mts_dataflow}/tmp_dir"
#     enable_streaming_engine = true
#     service_account_email   = var.sa_dataflow

#     parameters = {
#         project_dataflow = var.project
#         region           = var.region
#         job_name         = var.dfl_sensor_job_name
#         bkt_dataflow     = var.bkt_mts_dataflow
#         project          = var.project
#         dataset          = var.dataset_trusted
#         subscription     = var.pub_sub_wh_sensor_subscription
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
