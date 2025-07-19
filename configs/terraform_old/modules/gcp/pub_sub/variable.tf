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
#                                                Pub/Sub Variables                                              #
#   ********************************************************************************************************    #
variable "pub_sub_wh_sensor_topic" {
    description = "Pub/Sub Topic"
    type        = string
}

variable "pub_sub_wh_sensor_subscription" {
    description = "Pub/Sub Subscription"
    type        = string
}

variable "pub_sub_wh_sensor_subscription_bq" {
    description = "Pub/Sub Subscription BQ"
    type        = string
}

variable "tb_raw_dw_messages" {
    description = "Table Raw"
    type        = string
}

variable "pubsub_bq_role" {
    description = "Pub/Sub BQ Role"
    type        = list(string)
}