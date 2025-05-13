#   ********************************************************************************************************    #
#                                                Global Variables                                               #
#   ********************************************************************************************************    #
variable "project" {
    description = " Project ID"
    type = string
}

variable "region" {
    description = "Region of bucket"
    type        = string
}


#   ********************************************************************************************************    #
#                                                Global Variables                                               #
#   ********************************************************************************************************    #
variable "function_name" {
    description = "name of cloud function"
    type        = string
}

variable "environment" {
    description = "Environment Development"
    type        = string
}

variable "bkt_mts_cf_wh_sensor" {
    description = "path of the cloud function file"
    type        = string
}

variable "bkt_mts_cf_wh_sensor_file_name" {
    description = "name of the cloud function file"
    type        = string
}

variable "sa_cf_hw_sensor" {
    description = "service account of the cloud function"
    type        = string
}
