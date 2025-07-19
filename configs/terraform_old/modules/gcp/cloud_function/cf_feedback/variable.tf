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
variable "cf_name_feedback" {
    description = "name of cloud function"
    type        = string
}

variable "environment" {
    description = "Environment Development"
    type        = string
}

variable "bkt_mts_cf_feedback" {
    description = "path of the cloud function file"
    type        = string
}

variable "bkt_mts_cf_feedback_file_name" {
    description = "name of the cloud function file"
    type        = string
}

variable "sa_cf_feedback" {
    description = "service account of the cloud function"
    type        = string
}
