# #   ********************************************************************************************************    #
# #                                             Cloud Function Customers                                          #
# #   ********************************************************************************************************    #
# data "archive_file" "cf_path_customers_files" {
#     type        = "zip"
#     source_dir  = "../../src/cloud_function/cf_customers/"
#     output_path = "../../src/cloud_function/cf_customers/index.zip"
# }


# resource "google_cloudfunctions2_function" "cf_customers" {
#     project       = var.project[terraform.workspace]
#     location      = var.region
#     name          = var.cf_customers
#     description   = "It will be triggered via airflow and will send data to the bigquery table"
#     build_config {
#         runtime     = "python311"
#         entry_point = "main"
#         source {
#             storage_source {
#             bucket = google_storage_bucket.bucket[0].name
#             object = google_storage_bucket_object.cf_customers_files.name
#             }
#         }
#     }

#   labels = {
#     "created_by": "terraform",
#     "layer": "trusted",
#     "env": "dev"
#   }

#     service_config {
#         max_instance_count              = 1
#         min_instance_count              = 1
#         available_memory                = "2Gi"
#         available_cpu                   = 4
#         timeout_seconds                 = 3000
#         service_account_email           = local.sa_cf_customers
#         ingress_settings                = "ALLOW_ALL"
#         all_traffic_on_latest_revision  = true
#     }

#     lifecycle {
#         ignore_changes = [
#         build_config,
#         service_config,
#         ]
#     }
# }


# #   ********************************************************************************************************    #
# #                                          Cloud Function WareHouse Sensor                                      #
# #   ********************************************************************************************************    #
# data "archive_file" "cf_path_wh_sensor_files" {
#   type        = "zip"
#   source_dir  = "../../src/cloud_function/cf_wh_sensor/"
#   output_path = "../../src/cloud_function/cf_wh_sensor/index.zip"
# }


# resource "google_cloudfunctions2_function" "cf_wh_sensor" {
#   project       = var.project[terraform.workspace]
#   location      = var.region
#   name          = var.cf_wh_sensor
#   description   = "It will be triggered via airflow and will send data to the pub/sub"

#   build_config {
#     runtime     = "python311"
#     entry_point = "main"
#     source {
#       storage_source {
#         bucket = google_storage_bucket.bucket[0].name
#         object = google_storage_bucket_object.cf_wh_sensor_files.name
#       }
#     }
#   }

#   labels = {
#     "created_by": "terraform",
#     "env": var.environment
#   }

#   service_config {
#     max_instance_count    = 1
#     min_instance_count    = 1
#     available_memory      = "512M"
#     timeout_seconds       = 3000
#     service_account_email = local.sa_cf_wh_sensor
#     ingress_settings      = "ALLOW_ALL"
#   }

#   lifecycle {
#     ignore_changes = [
#       build_config,
#       service_config,
#     ]
#   }
# }

# #   ********************************************************************************************************    #
# #                                           Cloud Function Delivery Sensor                                      #
# #   ********************************************************************************************************    #
# # data "archive_file" "cf_path_delivery_files" {
# #     type        = "zip"
# #     source_dir  = "../../src/cloud_function/cf_delivery/"
# #     output_path = "../../src/cloud_function/cf_delivery/index.zip"
# # }

# #TODO: transfer to Dataproc Bucket
# # #   ********************************************************************************************************    #
# # #                                           Cloud Function Feedback Sensor                                      #
# # #   ********************************************************************************************************    #
# # data "archive_file" "cf_path_feedback_files" {
# #     type        = "zip"
# #     source_dir  = "../../src/cloud_function/cf_feedbacks/"
# #     output_path = "../../src/cloud_function/cf_feedbacks/index.zip"
# # }


# # resource "google_cloudfunctions2_function" "cf_feedback" {
# #     project       = var.project[terraform.workspace]
# #     location      = var.region
# #     name          = var.cf_feedback
# #     description   = "It will be triggered via airflow and will send data to the BigQuery table"

# #     build_config {
# #         runtime     = "python311"
# #         entry_point = "main"
# #         source {
# #             storage_source {
# #                 bucket = google_storage_bucket.bucket[0].name
# #                 object = google_storage_bucket_object.cf_feedback_files.name
# #             }
# #         }
# #     }

# #     labels = {
# #         "created_by": "terraform",
# #         "env": var.environment
# #     }

# #     service_config {
# #         max_instance_count    = 1
# #         min_instance_count    = 1
# #         available_memory      = "512M"
# #         timeout_seconds       = 3000
# #         service_account_email = google_service_account.creating_sa[7].email
# #         ingress_settings      = "ALLOW_ALL"
# #     }

# #     lifecycle {
# #         ignore_changes = [
# #         build_config,
# #         service_config,
# #         ]
# #     }
# # }





# #   ********************************************************************************************************    #
# #                                          Cloud Function Products/Inventory                                    #
# #   ********************************************************************************************************    #
# data "archive_file" "cf_path_products_inventory_files" {
#   type        = "zip"
#   source_dir  = "../../src/cloud_function/cf_products_inventory/"
#   output_path = "../../src/cloud_function/cf_products_inventory/index.zip"
# }


# resource "google_cloudfunctions2_function" "cf_products_inventory" {
#   project       = var.project[terraform.workspace]
#   location      = var.region
#   name          = var.cf_products_inventory
#   description   = "It will be triggered via airflow and will send data to the bigquery table"

#   build_config {
#     runtime     = "python311"
#     entry_point = "main"
#     source {
#       storage_source {
#         bucket = google_storage_bucket.bucket[0].name
#         object = google_storage_bucket_object.cf_products_inventory_files.name
#       }
#     }
#   }

#   labels = {
#     "created_by": "terraform",
#     "env": var.environment
#   }

#   service_config {
#     max_instance_count    = 1
#     min_instance_count    = 1
#     available_memory      = "512M"
#     timeout_seconds       = 3000
#     service_account_email = local.sa_cf_products_inventory
#     ingress_settings      = "ALLOW_ALL"
#   }

#   lifecycle {
#     ignore_changes = [
#       build_config,
#       service_config,
#     ]
#   }
# }