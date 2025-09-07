#TODO: I must conclude it
#  ********************************************************************************************************    #
#                                            Dataflow Warehouse Sensor                                         #
#  ********************************************************************************************************    #
# resource "null_resource" "run_dataflow_wh_job" {
#     provisioner "local-exec" {
#         command = <<EOT
#         python "${var.dfl_wh_sensor_script_path}/${var.dfl_wh_sensor_template}.py" \
#             --runner "DataflowRunner" \
#             --project_dataflow "${local.project}" \
#             --region "${var.region}" \
#             --job_name "${var.dfl_wh_sensor_job_name}" \
#             --bkt_dataflow "${local.bkt_dataflow}" \
#             --project "${local.project}" \
#             --dataset "${local.bq_dataset_production}" \
#             --subscription "${var.pub_sub_wh_sensor_subs}" \
#             --setup_file ${var.dfl_wh_sensor_script_path}/setup.py \
#             --template_location "gs://${local.bkt_dataflow}/template/${var.dfl_wh_sensor_template}"
#         EOT
#     }
# }


# resource "google_dataflow_job" "dataflow_wh_job" {

#     depends_on              = [
#                                 null_resource.run_dataflow_wh_job,
#                                 google_project_iam_member.roles_sa_dataflow
#                             ]

#     name                    = var.dfl_wh_sensor_job_name
#     template_gcs_path       = "gs://${local.bkt_dataflow}/template/${var.dfl_wh_sensor_template}"
#     temp_gcs_location       = "gs://${local.bkt_dataflow}/tmp_dir"
#     enable_streaming_engine = true
#     service_account_email   = local.sa_dataflow

#     parameters = {
#         project_dataflow = local.project
#         region           = var.region
#         job_name         = var.dfl_wh_sensor_job_name
#         bkt_dataflow     = local.bkt_dataflow
#         project          = local.project
#         dataset          = local.bq_dataset_production
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


#  ********************************************************************************************************    #
#                                            Dataflow Delivery Sensor                                          #
#  ********************************************************************************************************    #
resource "null_resource" "dfl_run_delivery_job" {
    provisioner "local-exec" {
        command = <<EOT
        python "${var.dfl_delivery_sensor_script_path}/${var.dfl_delivery_sensor_template}.py" \
            --runner "DataflowRunner" \
            --region "${var.region}" \
            --job_name "${var.dfl_delivery_sensor_job_name}" \
            --bkt_dataflow "${local.bkt_dataflow}" \
            --project "${local.project}" \
            --dataset "${local.bq_dataset_staging}" \
            --table "${var.tb_delivery_status}_stage" \
            --subscription "${var.pub_sub_wh_sensor_subs}" \
            --setup_file ${var.dfl_delivery_sensor_script_path}/setup.py \
            --template_location "gs://${local.bkt_dataflow}/template/${var.dfl_delivery_sensor_template}"
        EOT
    }
}


resource "google_dataflow_job" "dfl_delivery_job" {

    depends_on              = [
                                null_resource.dfl_run_delivery_job,
                                google_project_iam_member.roles_sa_dataflow
                            ]

    project                 = local.project
    region                  = var.region
    name                    = var.dfl_delivery_sensor_job_name
    template_gcs_path       = "gs://${local.bkt_dataflow}/template/${var.dfl_delivery_sensor_template}"
    temp_gcs_location       = "gs://${local.bkt_dataflow}/tmp_dir"
    enable_streaming_engine = true
    service_account_email   = local.sa_dataflow


    parameters = {
        project          = local.project
        region           = var.region
        job_name         = var.dfl_delivery_sensor_job_name
        bkt_dataflow     = local.bkt_dataflow
        dataset          = local.bq_dataset_staging
        table            = "${var.tb_delivery_status}_stage"
        subscription     = local.pb_sub_delivery_sensor
    }

    on_delete = "cancel"

    lifecycle {
        prevent_destroy = false
    }

    labels = {
        "created_by": "terraform",
        "env": var.environment
    }
}