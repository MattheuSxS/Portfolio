#   ********************************************************************************************************    #
#                                                    Cloud Project                                              #
#   ********************************************************************************************************    #
variable "project" {
    description = "Project name"
    type        = map(string)
}

variable "project_id" {
    description = "What is the project id number"
    type    = map(string)
}

variable "project_data_tools" {
    description = "Project name for data tools"
    type        = map(string)
}

variable "project_data_tools_id" {
    description = "Project id number for data tools"
    type    = map(string)
}

variable "region" {
    description = "where the resources will be created"
    type        = string
}

variable "environment" {
    description = "What is the environment"
    type        = string
    default     = "development"
}


#   ********************************************************************************************************    #
#                                             Google Cloud Storage                                              #
#   ********************************************************************************************************    #
variable "bkt_names" {
    description = "The name of the buckets"
    type        = list(string)
}

variable "bkt_data_tools_names" {
    description = "The names of the data tools buckets"
    type        = list(string)
}

variable "bkt_class_standard" {
    description = "The class of the bucket"
    type        = string
}

variable "bkt_class_nearline" {
    description = "The class of the bucket"
    type        = string
}

variable "bkt_class_coldline" {
    description = "The class of the bucket"
    type        = string
}


variable "bkt_class_archive" {
    description = "The class of the bucket"
    type        = string
}

#   ********************************************************************************************************    #
#                                                Google Cloud Sql                                               #
#   ********************************************************************************************************    #
variable "postgres_instance_name" {
    description = "The name of the Cloud SQL instance"
    type        = string
}

variable "postgres_db_name" {
    description = "The name of the database to create"
    type        = string
}

variable "postgres_schema" {
    description = "The name of the schema to create"
    type        = string
}

variable "postgres_username" {
    description = "the username for the user"
    type        = string
}

variable "postgres_password" {
    description = "The password for the user"
    type        = string
}

#   ********************************************************************************************************    #
#                                          IAM Members Permissions                                              #
#   ********************************************************************************************************    #

variable "members" {
    description = "The members that will have access to the buckets"
    type        = list(string)
}

variable "creating_sa" {
    description = "The service account to create"
    type        = list(string)
}

variable "data_tools_creating_sa" {
    description = "The service account to create for data tools"
    type        = list(string)
}

variable "roles_sa_dataflow" {
    description = "The roles to assign to the service account"
    type        = list(string)
}
variable "roles_sa_pub_sub" {
    description = "The roles to assign to the service account"
    type        = list(string)
}
# variable "roles_sa_dataproc" {
#     description = "The roles to assign to the service account"
#     type        = list(string)
# }

variable "roles_sa_cf_customers" {
    description = "The roles to assign to the service account"
    type        = list(string)
}

variable "roles_sa_cf_pb_sensor" {
    description = "The roles to assign to the service account"
    type        = list(string)
}

variable "roles_sa_cf_feedback" {
    description = "The roles to assign to the service account"
    type        = list(string)
}

variable "roles_sa_composer" {
    description = "The roles to assign to the service account"
    type        = list(string)
}

variable "roles_sa_cf_products_inventory" {
    description = "The roles to assign to the service account for products inventory"
    type        = list(string)
}

variable "roles_sa_default_compute" {
    description = "The roles to assign to the default compute service account"
    type        = list(string)
}
#   ********************************************************************************************************    #
#                                              Google Cloud Function                                            #
#   ********************************************************************************************************    #
variable "cf_wh_sensor" {
    description = "name of the function"
    type        = string
}

variable "cf_feedback" {
    description = "name of the function"
    type        = string
}

variable "cf_customers" {
    description = "name of cloud function"
    type        = string
}

variable "cf_products_inventory" {
    description = "name of cloud function for products inventory"
    type        = string
}

variable "cf_delivery_sensor" {
    description = "name of the function for delivery sensor"
    type        = string
}

#   ********************************************************************************************************    #
#                                                   Secret Manager                                              #
#   ********************************************************************************************************    #
variable "sm_create_secrets" {
    description = "All secrets to be created"
    type        = list(string)
}

variable "number_customers" {
    description = "Number of rows to be inserted"
    type        = number
}

variable "number_products" {
    description = "Number of products to be inserted"
    type        = number
}
#   ********************************************************************************************************    #
#                                               Cloud Composer                                                  #
#   ********************************************************************************************************    #
variable "composer_name" {
    description = "The name of the Composer environment"
    type        = string
}

variable "composer_image_version" {
    description = "The version of the Composer environment"
    type        = string
}

#   ********************************************************************************************************    #
#                                                   BigQuery                                                    #
#   ********************************************************************************************************    #
#                           ~~~~~~~~~~~~~~~~~~~~~~~>>>> Dataset <<<<~~~~~~~~~~~~~~~~~~~~~~~                     #
#   ********************************************************************************************************    #
variable "bq_dataset" {
    description = "The name of the dataset"
    type        = list(string)
}

#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    #
#                         | ~~~~~~~~~~~~~~~~~~~~~~~>>>> Table <<<<~~~~~~~~~~~~~~~~~~~~~~~ |                     #
#                         | ~~~~~~~~~~~~~~~~~~~~~~~>>>>  Raw  <<<<~~~~~~~~~~~~~~~~~~~~~~~ |                     #
#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    #
variable "tb_raw_wh_sensor" {
    description = "The name of the table"
    type        = string
}

variable "tb_raw_delivery_sensor" {
    description = "The name of the table"
    type        = string
}

#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    #
#                         |  ~~~~~~~~~~~~~~~~~~~~~~~>>>> Table <<<<~~~~~~~~~~~~~~~~~~~~~~~  |                   #
#                         |  ~~~~~~~~~~~~~~~~~~~~~~>>>> Trusted <<<<~~~~~~~~~~~~~~~~~~~~~~  |                   #
#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    #
variable "tb_wh_sensor" {
    description = "Table with warehouse sensor information"
    type        = string
}

variable "tb_feedback" {
    description = "Table with feedback information of customers"
    type        = string
}

variable "tb_customers" {
    description = "Table with customer information"
    type        = string
}

variable "tb_cards" {
    description = "Table with card information of customers"
    type        = string
}

variable "tb_address" {
    description = "Table with address information of customers"
    type        = string
}

variable "tb_products" {
    description = "Table with product information"
    type        = string
}

variable "tb_inventory" {
    description = "Table with inventory information"
    type        = string
}

variable "tb_sales" {
    description = "Table with sales information"
    type        = string
}

variable "tb_vehicles" {
    description = "Table with vehicle information"
    type        = string
}

variable "tb_processing_times" {
    description = "The name of the table"
    type        = string
}


#   ********************************************************************************************************    #
#                                                   Pub/Sub                                                     #
#   ********************************************************************************************************    #
variable "pub_sub_topics" {
    description = "The names of the Pub/Sub topics"
    type        = list(string)
}

variable "pub_sub_wh_sensor_subs" {
    description = "The name of the Pub/Sub subscription"
    type        = string
}

variable "pub_sub_wh_sensor_subs_bq" {
    description = "The name of the Pub/Sub subscription"
    type        = string
}

variable "pub_sub_delivery_sensor_subs" {
    description = "The name of the Pub/Sub subscription for delivery sensor"
    type        = string
}

variable "pub_sub_delivery_sensor_subs_bq" {
    description = "The name of the Pub/Sub subscription for delivery sensor in BigQuery"
    type        = string
}

#   ********************************************************************************************************    #
#                                                   Dataflow                                                    #
#   ********************************************************************************************************    #
variable "dfl_wh_sensor_job_name" {
    description = "The name of the Dataflow job"
    type        = string
}

variable "dfl_wh_sensor_template" {
    description = "The name of the Dataflow template"
    type        = string
}
variable "dfl_wh_sensor_script_path" {
    description = "The path to the Python script"
    type        = string
}

variable "dfl_delivery_sensor_template" {
    description = "The name of the Dataflow template for delivery sensor"
    type        = string
}

variable "dfl_delivery_sensor_job_name" {
    description = "The name of the Dataflow job for delivery sensor"
    type        = string
}

variable "dfl_delivery_sensor_script_path" {
    description = "The path to the Python script for delivery sensor"
    type        = string
}

#   ********************************************************************************************************    #
#                                               Google Cloud Dataproc                                           #
#   ********************************************************************************************************    #
variable "spark_job_tb_order" {
    description = "The name of the Spark job"
    type        = string
}

variable "spark_job_tb_feedback" {
    description = "The name of the Spark job"
    type        = string
}

variable "dp_order_script_path" {
    description = "The path to the Spark job script"
    type        = string
}

variable "dp_feedback_script_path" {
    description = "The path to the Spark job script for feedback"
    type        = string
}

#   ********************************************************************************************************    #
#                                                  Enable Api                                                   #
#   ********************************************************************************************************    #
variable "api_enabled" {
    description = "Enable API"
    type        = list(string)
}