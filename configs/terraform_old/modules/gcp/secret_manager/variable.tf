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

variable "ls_customers_dataset" {
    description = "Dataset for LS Customers"
    type        = string
}

variable "tb_customers" {
    description = "BigQuery Secret ID for Customers"
    type        = string
}

variable "tb_cards" {
    description = "BigQuery Secret ID for Cards"
    type        = string
}

variable "tb_address" {
    description = "BigQuery Secret ID for Address"
    type        = string
}

variable "number_customers" {
    description = "Number of rows to be inserted"
    type        = number
}