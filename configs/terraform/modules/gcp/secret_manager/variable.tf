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
#                                             Secret Manager Variables                                          #
#   ********************************************************************************************************    #
variable "sm_create_secrets" {
    description = "All secrets to be created"
    type        = list(string)
}

variable "bq_fb_access_authorization" {
    description = "BigQuery Secret ID"
    type        = map(string)
}