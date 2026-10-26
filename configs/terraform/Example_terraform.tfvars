#   ********************************************************************************************************    #
#                                                Default variables                                              #
#   ********************************************************************************************************    #
project     = {
    dev = ""
    prd = ""
    }

project_id  = {
    dev = ""
    prd = ""
    }

region      = "us-east1"
environment = "dev"


#   ********************************************************************************************************    #
#                                             Google Cloud Storage                                              #
#   ********************************************************************************************************    #
bkt_names               = ["", "", "", ""]
bkt_class_standard      = "STANDARD"
bkt_class_nearline      = "NEARLINE"
bkt_class_coldline      = "COLDLINE"
bkt_class_archive       = "ARCHIVE"


#   ********************************************************************************************************    #
#                                                Google Cloud Sql                                               #
#   ********************************************************************************************************    #
postgres_instance_name  = ""
postgres_db_name        = ""
postgres_schema         = ""
postgres_username       = ""
postgres_password       = ""

#   ********************************************************************************************************    #
#                                              Google Cloud Function                                            #
#   ********************************************************************************************************    #
cf_path_all_files       = "../../modules/cloud_function/"
cf_wh_sensor            = ""
cf_feedback             = ""
cf_customers            = ""
cf_products_inventory   = ""
cf_delivery_sensor      = ""
cf_sentiment_analysis   = ""
cf_sales_forecast       = ""


#TODO: Check out whole rules of Service Accounts
#   ********************************************************************************************************    #
#                                             IAM Members Permissions                                           #
#   ********************************************************************************************************    #
members = [
    "serviceAccount:",
    "user:"
    ]

creating_sa  = [
    "",
    "",
    "",
    "",
    "",
    ""
    ]


roles_sa_dataflow = [
    "roles/dataflow.admin",
    "roles/dataflow.worker",
    "roles/storage.objectAdmin",
    "roles/bigquery.jobUser",
    "roles/bigquery.dataEditor",
    "roles/bigquery.metadataViewer",
    "roles/pubsub.editor",
    "roles/iam.serviceAccountUser"
    ]

roles_sa_composer = [
    "roles/composer.worker",
    "roles/composer.serviceAgent",
    "roles/storage.admin",
    "roles/storage.objectAdmin",
    "roles/bigquery.dataEditor",
    "roles/bigquery.metadataViewer",
    "roles/cloudfunctions.serviceAgent",
    "roles/run.invoker",
    "roles/secretmanager.secretAccessor",
    "roles/dataproc.editor",
    "roles/compute.viewer",
    "roles/bigquery.jobUser",
    "roles/cloudfunctions.invoker",
    "roles/artifactregistry.reader"
    ]

roles_sa_cf_pb_sensor = [
    "roles/cloudfunctions.serviceAgent",
    "roles/storage.objectAdmin",
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/run.invoker",
    "roles/secretmanager.secretAccessor",
    "roles/bigquery.dataViewer",
    "roles/bigquery.jobUser"
    ]

roles_sa_cf_default = [
    "roles/cloudfunctions.serviceAgent",
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser",
    "roles/storage.objectAdmin",
    "roles/run.invoker",
    "roles/secretmanager.secretAccessor",
    "roles/bigquery.connectionUser",
    "roles/cloudfunctions.invoker",
    "roles/aiplatform.user"
    ]


roles_sa_pub_sub = [
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser",
    "roles/bigquery.metadataViewer",
    "roles/pubsub.admin",
    "roles/run.invoker"
    ]

roles_sa_default_compute = [
    "roles/storage.admin",
    "roles/bigquery.dataEditor"
    ]

roles_sa_cloud_run = [
    "roles/run.admin",
    "roles/storage.objectViewer",
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser"
    ]
#   ********************************************************************************************************    #
#                                                   Secret Manager                                              #
#   ********************************************************************************************************    #
sm_create_secrets = [
    "",
    "",
    "",
    "",
    "",
    "",
    ""
    ]

embedding_model     = ""
groq_api_key        = ""
number_customers    = 200000
number_products     = 3000

#   ********************************************************************************************************    #
#                                                   Cloud Composer                                              #
#   ********************************************************************************************************    #
composer_name = ""
composer_image_version = "composer-3-airflow-3.1.8-build.0"

#   ********************************************************************************************************    #
#                                                 Cloud Pub/sub                                                 #
#   ********************************************************************************************************    #
pub_sub_topics                  = ["", ""]
pub_sub_wh_sensor_subs          = ""
pub_sub_wh_sensor_subs_bq       = ""

pub_sub_delivery_sensor_subs    = ""
pub_sub_delivery_sensor_subs_bq = ""


#   ********************************************************************************************************    #
#                                                   BigQuery                                                    #
#   ********************************************************************************************************    #
#                           ~~~~~~~~~~~~~~~~~~~~~~~>>>> Dataset <<<<~~~~~~~~~~~~~~~~~~~~~~~                     #
#   ********************************************************************************************************    #
bq_dataset = ["raw", "staging", "production", "ls_customers"]


#| ~~~~~~~~~~~~~~~~~~~~~~~~>>>> Table <<<<~~~~~~~~~~~~~~~~~~~~~~~~ |
#| ~~~~~~~~~~~~~~~~~~~~~~~~>>>>  Raw  <<<<~~~~~~~~~~~~~~~~~~~~~~~~ |
tb_raw_wh_sensor        = "tb_raw_wh_sensor"
tb_raw_delivery_sensor  = "tb_raw_delivery_sensor"


#|  ~~~~~~~~~~~~~~~~~~~~~~~>>>> Table <<<<~~~~~~~~~~~~~~~~~~~~~~~  |
#|  ~~~~~~~~~~~~~~~~~~~~~~>>> Production <<<<~~~~~~~~~~~~~~~~~~~~  |
tb_wh_sensor            = "tb_wh_sensor"
tb_wh_sensor_anomalies  = "tb_wh_sensor_anomalies"
tb_feedback             = "tb_feedback"
tb_feedback_sentiment   = "tb_feedback_sentiment"
tb_sales_forecast       = "tb_sales_forecast"

#|  ~~~~~~~~~~~~~~~~~~~~~~~>>>> Table <<<<~~~~~~~~~~~~~~~~~~~~~~~  |
#|  ~~~~~~~~~~~~~~~~~~~>>>> ls_customers <<<<~~~~~~~~~~~~~~~~~~~~  |
tb_customers            = "tb_customers"
tb_cards                = "tb_cards"
tb_address              = "tb_address"
tb_products             = "tb_products"
tb_inventory            = "tb_inventory"
tb_sales                = "tb_sales"
tb_vehicles             = "tb_vehicles"
tb_delivery_status      = "tb_delivery_status"


#|  ~~~~~~~~~~~~~~~~~~~~~>>>> Procedure <<<<~~~~~~~~~~~~~~~~~~~~~  |
#|  ~~~~~~~~~~~~~~~~~~~>>>> ls_customers <<<<~~~~~~~~~~~~~~~~~~~~  |
sp_merge_delivery_status    = "sp_merge_delivery_status"
sp_delete_delivery_status   = "sp_delete_delivery_status"
sp_feedback_sentiment       = "sp_feedback_sentiment"

#   ********************************************************************************************************    #
#                                                     Dataflow                                                  #
#   ********************************************************************************************************    #
dfl_wh_sensor_template    = "dfl_wh_sensor_nrt"
dfl_wh_sensor_job_name    = "dfl-wh-sensor-nrt"
dfl_script_path           = "/../../modules/dataflow"

dfl_delivery_sensor_template    = "dfl_delivery_sensor_nrt"
dfl_delivery_sensor_job_name    = "dfl-delivery-sensor-nrt"

#   ********************************************************************************************************    #
#                                               Google Cloud Dataproc                                           #
#   ********************************************************************************************************    #
spark_job_tb_order = "spark_job_tb_order"
spark_job_tb_feedback = "spark_job_tb_feedback"


dp_order_script_path = "../../modules/dataproc/dp_order/src"
dp_feedback_script_path = "../../modules/dataproc/dp_feedback/src"


#   ********************************************************************************************************    #
#                                                  Enable Api                                                   #
#   ********************************************************************************************************    #
api_enabled = [
    "cloudresourcemanager.googleapis.com",
    "compute.googleapis.com",
    "cloudfunctions.googleapis.com",
    "run.googleapis.com",
    "eventarc.googleapis.com",
    "pubsub.googleapis.com",
    "cloudbuild.googleapis.com",
    "bigquery.googleapis.com",
    "composer.googleapis.com",
    "dataproc.googleapis.com",
    "dataflow.googleapis.com",
    "cloudbuild.googleapis.com",
    "language.googleapis.com",
    "notebooks.googleapis.com",
    "visionai.googleapis.com",
    "storage-component.googleapis.com",
    "artifactregistry.googleapis.com",
    "dataplex.googleapis.com",
    "dataform.googleapis.com",
    "secretmanager.googleapis.com",
    "serviceusage.googleapis.com",
    ]

#   ********************************************************************************************************    #
#                                                  Artifact Registry                                            #
#   ********************************************************************************************************    #
docker_repository           = ""
sentiment_analysis          = ""
logistream_solutions_report = ""
sales_forecast_report       = ""


#   ********************************************************************************************************    #
#                                                   Cloud Run                                                   #
#   ********************************************************************************************************    #
run_path_all_files = "../../modules/cloud_run"
