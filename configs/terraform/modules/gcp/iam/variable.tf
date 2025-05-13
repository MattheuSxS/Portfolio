#   ********************************************************************************************************    #
#                                                Global Variables                                               #
#   ********************************************************************************************************    #
variable "project" {
    description = "value of project"
    type        = string
}

variable "project_id" {
    description = "What is the project id number"
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
#                                          IAM Members Permissions                                              #
#   ********************************************************************************************************    #
variable "creating_sa" {
    description = "The service account to create"
    type        = list(string)
}

variable "roles_sa_pub_sub" {
    description = "The roles to assign to the service account"
    type        = list(string)
}

variable "roles_sa_cf_hw_sensor" {
    description = "The roles to assign to the service account"
    type        = list(string)
}