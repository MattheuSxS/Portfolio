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
variable "cf_name_wh_sensor" {
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

# variable "ready_sensor_files" {
#     description = "ready the cloud function file"
#     type        = string
# }
