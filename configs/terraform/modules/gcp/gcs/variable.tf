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
variable "environment" {
    description = "Environment Development"
    type        = string
}


#   ********************************************************************************************************    #
#                                                   Cloud Storagem                                              #
#   ********************************************************************************************************    #
variable "bkt_names" {
    description = "List of bucket names"
    type        = list(string)
}
variable "bkt_class_standard" {
    description = "Standard storage class"
    type        = string
}
variable "bkt_class_nearline" {
    description = "Nearline storage class"
    type        = string
}
variable "bkt_class_coldline" {
    description = "Coldline storage class"
    type        = string
}
variable "bkt_class_archive" {
    description = "Archive storage class"
    type        = string
}

variable "cf_path_wh_sensor_files" {
    description = "path of the cloud function file"
    type        = string
}