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
#                                               Composer Variables                                              #
#   ********************************************************************************************************    #
variable "composer_name" {
    description = "Name of the Composer environment"
    type        = string
}

variable "composer_image_version" {
    description = "Image version of the Composer environment"
    type        = string
}

variable "sa_airflow" {
    description = "Service account for Airflow"
    type        = string
}