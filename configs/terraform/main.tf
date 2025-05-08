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
    cf_path_sensor_files    = module.GCP_Cloud_function_sensor.cf_path_sensor_files
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
    tb_raw_backup_sensor    = var.tb_raw_backup_sensor
    tb_dw_messages          = var.tb_dw_messages

}

#   ********************************************************************************************************    #
#                                           Google Cloud Function                                               #
#   ********************************************************************************************************    #
module "GCP_Cloud_function_sensor" {
    source                      = "./modules/gcp/cloud_function/cf_sensor"
    project                     = var.project[terraform.workspace]
    region                      = var.region
    environment                 = var.environment
    function_name               = var.function_name
    bkt_mts_cf_sensor           = module.GCP_Buckets.bkt_mts_cf_sensor
    bkt_mts_cf_sensor_file_name = module.GCP_Buckets.bkt_mts_cf_sensor_file_name
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
    roles_sa_pub_sub        = var.roles_sa_pub_sub
#     members                 = var.members
#     service_accounts        = var.service_accounts
#     roles_sa_dataflow       = var.roles_sa_dataflow
#     # roles_sa_dataproc      = var.roles_sa_dataproc
#     roles_sa_composer       = var.roles_sa_composer
}

#   ********************************************************************************************************    #
#                                               Secret Manager                                                  #
#   ********************************************************************************************************    #
module "GCP_Secret_manager" {
    source                  = "./modules/gcp/secret_manager"
    project                 = var.project[terraform.workspace]
    region                  = var.region
    environment             = var.environment
    access_authorization    = var.access_authorization
}

#   ********************************************************************************************************    #
#                                               Cloud Composer                                                  #
#   ********************************************************************************************************    #


#   ********************************************************************************************************    #
#                                                 Pub / Sub                                                     #
#   ********************************************************************************************************    #
module "GCP_Pub_sub" {
    source                  = "./modules/gcp/pub_sub"
    project                 = var.project[terraform.workspace]
    region                  = var.region
    environment             = var.environment
    pub_sub_topic           = var.pub_sub_topic
    pub_sub_subscription    = var.pub_sub_subscription
    pub_sub_subscription_bq = var.pub_sub_subscription_bq
    tb_raw_dw_messages      = module.GCP_BigQuery.tb_raw_dw_messages
    pubsub_bq_role          = module.GCP_Iam.pubsub_bq_role
}

#   ********************************************************************************************************    #
#                                                 Dataflow                                                      #
#   ********************************************************************************************************    #