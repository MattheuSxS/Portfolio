#   ********************************************************************************************************    #
#                                           Google Cloud Storage                                                #
#   ********************************************************************************************************    #
module "GCP_Buckets" {
    source                  = "./modules/gcp/gcs"
    project                 = var.project[terraform.workspace]
    region                  = var.region
    environment             = var.environment
    bkt_names               = var.bkt_names
    bkt_class_standard      = var.bkt_class_standard
    bkt_class_nearline      = var.bkt_class_nearline
    bkt_class_coldline      = var.bkt_class_coldline
    bkt_class_archive       = var.bkt_class_archive
    cf_path_wh_sensor_files = module.GCP_Cloud_function_wh_sensor.cf_path_wh_sensor_files
    cf_path_feedback_files  = module.GCP_Cloud_function_feedback.cf_path_feedback_files
}

#   ********************************************************************************************************    #
#                                            Google Cloud Sql                                                   #
#   ********************************************************************************************************    #


#   ********************************************************************************************************    #
#                                                  BigQuery                                                     #
#   ********************************************************************************************************    #
module "GCP_BigQuery" {
    source                  = "./modules/gcp/bigquery"
    project                 = var.project[terraform.workspace]
    region                  = var.region
    environment             = var.environment
    bq_dataset              = var.bq_dataset
    tb_raw_hw_sensor        = var.tb_raw_hw_sensor
    tb_dw_messages          = var.tb_dw_messages
    tb_feedback             = var.tb_feedback
}

#   ********************************************************************************************************    #
#                                           Google Cloud Function                                               #
#   ********************************************************************************************************    #
module "GCP_Cloud_function_wh_sensor" {
    source                          = "./modules/gcp/cloud_function/cf_wh_sensor"
    project                         = var.project[terraform.workspace]
    region                          = var.region
    environment                     = var.environment
    cf_name_wh_sensor                   = var.cf_name_wh_sensor
    bkt_mts_cf_wh_sensor            = module.GCP_Buckets.bkt_mts_cf_wh_sensor
    bkt_mts_cf_wh_sensor_file_name  = module.GCP_Buckets.bkt_mts_cf_wh_sensor_file_name
    sa_cf_hw_sensor                 = module.GCP_Iam.sa_cf_hw_sensor
}

# module "GCP_Cloud_function_delivery_sensor" {
#     source                      = "./modules/gcp/cloud_function/cf_delivery_sensor"
#     project                     = var.project[terraform.workspace]
#     region                      = var.region
#     environment                 = var.environment
# }

module "GCP_Cloud_function_feedback" {
    source                          = "./modules/gcp/cloud_function/cf_feedback"
    project                         = var.project[terraform.workspace]
    region                          = var.region
    environment                     = var.environment
    cf_name_feedback                = var.cf_name_feedback
    bkt_mts_cf_feedback             = module.GCP_Buckets.bkt_mts_cf_feedback
    bkt_mts_cf_feedback_file_name   = module.GCP_Buckets.bkt_mts_cf_feedback_file_name
    sa_cf_feedback                  = module.GCP_Iam.sa_cf_feedback
}

#   ********************************************************************************************************    #
#                                          IAM Members Permissions                                              #
#   ********************************************************************************************************    #
module "GCP_Iam" {
    source                  = "./modules/gcp/iam"
    project                 = var.project[terraform.workspace]
    project_id              = var.project_id[terraform.workspace]
    region                  = var.region
    environment             = var.environment
    creating_sa             = var.creating_sa
    roles_sa_pub_sub        = var.roles_sa_pub_sub
    roles_sa_cf_hw_sensor   = var.roles_sa_cf_hw_sensor
    roles_sa_cf_feedback    = var.roles_sa_cf_feedback
    # members                 = var.members
    # service_accounts        = var.service_accounts
    # roles_sa_dataflow       = var.roles_sa_dataflow
    # # roles_sa_dataproc      = var.roles_sa_dataproc
    # roles_sa_composer       = var.roles_sa_composer
}

#   ********************************************************************************************************    #
#                                               Secret Manager                                                  #
#   ********************************************************************************************************    #
module "GCP_Secret_manager" {
    source                      = "./modules/gcp/secret_manager"
    project                     = var.project[terraform.workspace]
    region                      = var.region
    environment                 = var.environment
    sm_create_secrets    = var.sm_create_secrets
    bq_fb_access_authorization  = {
                                    "project"   = var.project[terraform.workspace]
                                    "dataset"   = module.GCP_BigQuery.production_dataset
                                    "table"     = module.GCP_BigQuery.tb_feedback
                                  }

}

#   ********************************************************************************************************    #
#                                               Cloud Composer                                                  #
#   ********************************************************************************************************    #


#   ********************************************************************************************************    #
#                                                 Pub / Sub                                                     #
#   ********************************************************************************************************    #
module "GCP_Pub_sub" {
    source                              = "./modules/gcp/pub_sub"
    project                             = var.project[terraform.workspace]
    region                              = var.region
    environment                         = var.environment
    pub_sub_wh_sensor_topic             = var.pub_sub_wh_sensor_topic
    pub_sub_wh_sensor_subscription      = var.pub_sub_wh_sensor_subscription
    pub_sub_wh_sensor_subscription_bq   = var.pub_sub_wh_sensor_subscription_bq
    tb_raw_dw_messages                  = module.GCP_BigQuery.tb_raw_dw_messages
    pubsub_bq_role                      = module.GCP_Iam.pubsub_bq_role
}

#   ********************************************************************************************************    #
#                                                 Dataflow                                                      #
#   ********************************************************************************************************    #
# module "GCP_Dataflow_hw_sensor" {
#     source                          = "./modules/gcp/dataflow/wh_sensor"
#     project                         = var.project[terraform.workspace]
#     region                          = var.region
#     environment                     = var.environment
#     dfl_wh_sensor_template          = var.dfl_wh_sensor_template
#     dfl_wh_sensor_job_name          = var.dfl_wh_sensor_job_name
#     dfl_wh_sensor_script_path       = var.dfl_wh_sensor_script_path
#     bkt_mts_dataflow                = module.GCP_Buckets.bkt_mts_dataflow
#     sa_dataflow                     = module.GCP_Iam.sa_dataflow
#     pub_sub_wh_sensor_subscription  = var.pub_sub_wh_sensor_subscription
#     dataset_trusted                 = var.dataset_trusted
# }