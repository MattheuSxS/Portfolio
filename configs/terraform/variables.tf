
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

variable "service_accounts" {
    description = "The service accounts that will have access to the buckets"
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
# variable "roles_sa_cloud_function" {
#     description = "The roles to assign to the service account"
#     type        = list(string)
# }
variable "roles_sa_composer" {
    description = "The roles to assign to the service account"
    type        = list(string)
}

#   ********************************************************************************************************    #
#                                              Google Cloud Function                                            #
#   ********************************************************************************************************    #
variable "function_name" {
    description = "name of the function"
    type        = string
}

variable "sa_cloud_function" {
    description = "The service account to grant the roles"
    type        = string
}

#   ********************************************************************************************************    #
#                                                   Secret Manager                                              #
#   ********************************************************************************************************    #
variable "access_authorization" {
    description = "Secret ID"
    type        = string
}

# variable "database_credentials" {
#     description = "Password for database"
#     type        = string
# }

#   ********************************************************************************************************    #
#                                               Cloud Composer                                                  #
#   ********************************************************************************************************    #
variable "airflow_name" {
    description = "The name of the Composer environment"
    type        = string
}

variable "image_version" {
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
variable "tb_raw_backup_sensor" {
    description = "The name of the table"
    type        = string
}

#   ~~~~~~~~~~~~~~~~~~~~~~>>>> Trusted <<<<~~~~~~~~~~~~~~~~~~~~~~~
variable "tb_dw_messages" {
    description = "The name of the table"
    type        = string
}

#   ********************************************************************************************************    #
#                                                   Pub/Sub                                                     #
#   ********************************************************************************************************    #
variable "pub_sub_topic" {
    description = "The name of the Pub/Sub topic"
    type        = string
}

variable "pub_sub_subscription" {
    description = "The name of the Pub/Sub subscription"
    type        = string
}

variable "pub_sub_subscription_bq" {
    description = "The name of the Pub/Sub subscription"
    type        = string
}


#   ********************************************************************************************************    #
#                                                   Dataflow                                                    #
#   ********************************************************************************************************    #
variable "dfl_job_name" {
    description = "The name of the Dataflow job"
    type        = string
}

variable "dfl_template" {
    description = "The name of the Dataflow template"
    type        = string
}
variable "python_script_path" {
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