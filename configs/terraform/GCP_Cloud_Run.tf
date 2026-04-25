# resource "google_cloud_run_v2_service" "logistream_dashboard" {
#     depends_on          = [
#                             null_resource.push_logistream_solutions_report_image,
#                             google_project_iam_member.roles_sa_cloud_run
#                             ]

#     name                = var.logistream_solutions_report
#     project             = local.project
#     location            = var.region
#     description         = "LogiStream Solutions Report Dashboard"
#     deletion_protection = false

#   template {

#         timeout = "3600s"
#         max_instance_request_concurrency = 50

#         containers {
#             image = "${var.region}-docker.pkg.dev/${local.project}/${var.docker_repository}/${var.logistream_solutions_report}:latest"

#             resources {
#                 limits = {
#                 cpu    = "1"
#                 memory = "4Gi"
#                 }
#             }

#             startup_probe {
#                         initial_delay_seconds = 10
#                         timeout_seconds       = 10
#                         period_seconds        = 10
#                         failure_threshold     = 60

#                         tcp_socket {}
#                     }
#             env {
#                     name  = "TRANSFORMERS_CACHE"
#                     value = "/app/report_cache"
#                 }
#             env {
#                     name  = "HF_HOME"
#                     value = "/app/report_cache"
#                 }
#         }


#     }

#     scaling {
#         min_instance_count = 1
#         max_instance_count = 2
#     }

#     build_config {
#         environment_variables = {}
#         service_account = "projects/${local.project}/serviceAccounts/${local.sa_cloud_run}"
#     }

#     traffic {
#         type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
#         percent = 100
#     }

#     ingress = "INGRESS_TRAFFIC_ALL"
# }

resource "google_cloud_run_v2_job" "sentiment_analysis_job" {
    depends_on          = [
                            null_resource.push_sentiment_analysis_image,
                            google_project_iam_member.roles_sa_cloud_run
                        ]

    name                = var.sentiment_analysis
    project             = local.project
    location            = var.region
    deletion_protection = false

    template {
        template {

            containers {
                image = "${var.region}-docker.pkg.dev/${local.project}/${var.docker_repository}/${var.sentiment_analysis}:latest"

                resources {
                    limits = {
                        cpu    = "4"
                        memory = "8Gi"
                    }
                }

                env {
                    name  = "TRANSFORMERS_CACHE"
                    value = "/tmp/model_cache"
                }
                env {
                    name  = "HF_HOME"
                    value = "/tmp/model_cache"
                }
                env {
                    name  = "PYTHONUNBUFFERED"
                    value = "1"
                }
                env {
                    name  = "PROJECT"
                    value = local.project
                }
                env {
                    name  = "DATASET"
                    value = local.bq_dataset_ls_customers
                }
                env {
                    name  = "TABLE"
                    value = var.tb_feedback_sentiment
                }
            }
            timeout         = "3600s"
            max_retries     = 2
            service_account = "${local.sa_cloud_run}"
        }
    }

    lifecycle {
        ignore_changes = [labels]
    }
}
