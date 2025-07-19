#   ********************************************************************************************************    #
#                                                Global Variables                                               #
#   ********************************************************************************************************    #
variable "project" {
    description = "value of project"
    type        = string
}

variable "region" {
    description = "Region of bucket"
    type        = string
}

variable "environment" {
    description = "Environment Development"
    type        = string
}

#   ********************************************************************************************************    #
#                                                Dataflow Variables                                             #
#   ********************************************************************************************************    #
variable "dfl_wh_sensor_template" {
    description = "Dataflow template for sensor"
    type        = string
}

variable "dfl_wh_sensor_job_name" {
    description = "Dataflow job name for sensor"
    type        = string
}
variable "dfl_wh_sensor_script_path" {
    description = "Path to the Dataflow script"
    type        = string
}

variable "bkt_mts_dataflow" {
    description = "Bucket for Dataflow"
    type        = string
}

variable "sa_dataflow" {
    description = "Service account for Dataflow"
    type        = string
}

variable "pub_sub_wh_sensor_subscription" {
    description = "Pub/Sub Subscription for warehouse sensor"
    type        = string
}
variable "dataset_trusted" {
    description = "Dataset for trusted data"
    type        = string
}


# dfl_template    dfl_data_fake_nrt
# dfl_job_name    dfl-data-fake-nrt
# python_script_path  ../../src/gcp_dataflow