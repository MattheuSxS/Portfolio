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