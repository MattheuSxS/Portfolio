
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

variable "roles_sa_cf_wh_sensor" {
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


#   ********************************************************************************************************    #
#                                              Google Cloud Function                                            #
#   ********************************************************************************************************    #
variable "cf_name_wh_sensor" {
    description = "name of the function"
    type        = string
}

variable "cf_name_feedback" {
    description = "name of the function"
    type        = string
}

#   ********************************************************************************************************    #
#                                                   Secret Manager                                              #
#   ********************************************************************************************************    #
variable "sm_create_secrets" {
    description = "All secret ids"
    type        = list(string)
}

# variable "database_credentials" {
#     description = "Password for database"
#     type        = string
# }

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
#   ~~~~~~~~~~~~~~~~~~~~~~~>>>> Dataset <<<<~~~~~~~~~~~~~~~~~~~~~~~
variable "bq_dataset" {
    description = "The name of the dataset"
    type        = list(string)
}

#   ~~~~~~~~~~~~~~~~~~~~~~~>>>> Table <<<<~~~~~~~~~~~~~~~~~~~~~~~
#   ~~~~~~~~~~~~~~~~~~~~~~>>>> Raw <<<<~~~~~~~~~~~~~~~~~~~~~~~
variable "tb_raw_hw_sensor" {
    description = "The name of the table"
    type        = string
}

#   ~~~~~~~~~~~~~~~~~~~~~~>>>> Trusted <<<<~~~~~~~~~~~~~~~~~~~~~~~
variable "tb_dw_messages" {
    description = "The name of the table"
    type        = string
}

variable "tb_feedback" {
    description = "The name of the table"
    type        = string
}



variable "tb_customers" {
    description = "The name of the table"
    type        = string
}

variable "tb_cards" {
    description = "The name of the table"
    type        = string
}

variable "tb_address" {
    description = "The name of the table"
    type        = string
}
#   ********************************************************************************************************    #
#                                                   Pub/Sub                                                     #
#   ********************************************************************************************************    #
variable "pub_sub_wh_sensor_topic" {
    description = "The name of the Pub/Sub topic"
    type        = string
}

variable "pub_sub_wh_sensor_subscription" {
    description = "The name of the Pub/Sub subscription"
    type        = string
}

variable "pub_sub_wh_sensor_subscription_bq" {
    description = "The name of the Pub/Sub subscription"
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


#   ********************************************************************************************************    #
#                                                  Enable Api                                                   #
#   ********************************************************************************************************    #
variable "api_enabled" {
    description = "Enable API"
    type        = list(string)
}