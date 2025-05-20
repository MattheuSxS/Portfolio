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
#                                                BigQuery Variables                                             #
#   ********************************************************************************************************    #
#   ~~~~~~~~~~~~~~~~~~~~~~~>>>> Dataset <<<<~~~~~~~~~~~~~~~~~~~~~~~
variable "bq_dataset" {
    description = "The name of the dataset"
    type        = list(string)
}

#   ~~~~~~~~~~~~~~~~~~~~~~~>>>> Table <<<<~~~~~~~~~~~~~~~~~~~~~~~
#   ~~~~~~~~~~~~~~~~~~~~~~>>>> Raw <<<<~~~~~~~~~~~~~~~~~~~~~~~
variable "tb_raw_hw_sensor" {
    description = "The name of the table"
    type        = string
}

#   ~~~~~~~~~~~~~~~~~~~~~~>>>> Trusted <<<<~~~~~~~~~~~~~~~~~~~~~~~
variable "tb_dw_messages" {
    description = "The name of the table"
    type        = string
}

variable "tb_feedback" {
    description = "The name of the table"
    type        = string
}