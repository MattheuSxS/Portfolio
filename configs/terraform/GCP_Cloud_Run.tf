resource "google_cloud_run_v2_service" "logistream_dashboard" {
    depends_on          = [null_resource.push_logistream_solutions_report_image]

    name                = var.logistream_solutions_report
    project             = local.project
    location            = var.region
    description         = "LogiStream Solutions Report Dashboard"
    deletion_protection = false

  template {
        scaling {
            min_instance_count = 1
            max_instance_count = 2
        }

        timeout = "3600s"
        max_instance_request_concurrency = 50

        containers {
            image = "${var.region}-docker.pkg.dev/${local.project}/${var.docker_repository}/${var.logistream_solutions_report}:latest"

        resources {
            limits = {
            cpu    = "1"
            memory = "4Gi"
            }
        }

        startup_probe {
                    initial_delay_seconds = 10
                    timeout_seconds       = 10
                    period_seconds        = 10
                    failure_threshold     = 60

                    tcp_socket {}
                }
        env {
                name  = "TRANSFORMERS_CACHE"
                value = "/app/report_cache"
            }
        env {
                name  = "HF_HOME"
                value = "/app/report_cache"
            }
        }


    }

    build_config {
        environment_variables = {}
        service_account = "projects/${local.project}/serviceAccounts/${local.sa_cloud_run}"
    }

    traffic {
        type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
        percent = 100
    }

    ingress = "INGRESS_TRAFFIC_ALL"
}

resource "google_cloud_run_v2_service" "sentiment_analysis" {
    depends_on          = [null_resource.push_logistream_solutions_report_image]

    name                  = var.sentiment_analysis
    project               = local.project
    location              = var.region
    description           = "Sentiment Analysis API using DistilBERT"
    deletion_protection   = false

    template {
        scaling {
        min_instance_count = 0
        max_instance_count = 3
        }

        timeout = "1800s"
        max_instance_request_concurrency = 50

        containers {
        image = "${var.region}-docker.pkg.dev/${local.project}/${var.docker_repository}/${var.sentiment_analysis}:latest"

        resources {
            limits = {
            cpu    = "4"
            memory = "8Gi"
            }
        }

        startup_probe {
            initial_delay_seconds = 10
            timeout_seconds       = 300
            period_seconds        = 10
            failure_threshold     = 10

            tcp_socket {
                port = 8080
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
        }


    }

    build_config {
        environment_variables = {
            "PROJECT" = local.project,
            "DATASET" = local.bq_dataset_ls_customers,
            "TABLE"   = var.tb_feedback_sentiment
        }
        service_account = "projects/${local.project}/serviceAccounts/${local.sa_cloud_run}"
    }

    traffic {
        type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
        percent = 100
    }

    ingress = "INGRESS_TRAFFIC_ALL"
}