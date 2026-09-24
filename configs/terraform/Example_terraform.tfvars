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

region      = ""
environment = ""


#   ********************************************************************************************************    #
#                                             Google Cloud Storage                                              #
#   ********************************************************************************************************    #
bkt_names               = []
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
cf_path_all_files       = ""
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

creating_sa  = []
roles_sa_dataflow = []

roles_sa_composer = []

#TODO: Check out whole rules of Service Accounts
roles_sa_cf_pb_sensor = []
roles_sa_cf_default = []
roles_sa_pub_sub = []
roles_sa_default_compute = []
roles_sa_cloud_run = []

#   ********************************************************************************************************    #
#                                                   Secret Manager                                              #
#   ********************************************************************************************************    #
sm_create_secrets = []

embedding_model     = ""
groq_api_key        = ""
number_customers    = 200000
number_products     = 3000

#   ********************************************************************************************************    #
#                                                   Cloud Composer                                              #
#   ********************************************************************************************************    #
composer_name = ""
composer_image_version = ""

#   ********************************************************************************************************    #
#                                                 Cloud Pub/sub                                                 #
#   ********************************************************************************************************    #
pub_sub_topics                  = []
pub_sub_wh_sensor_subs          = ""
pub_sub_wh_sensor_subs_bq       = ""

pub_sub_delivery_sensor_subs    = ""
pub_sub_delivery_sensor_subs_bq = ""


#   ********************************************************************************************************    #
#                                                   BigQuery                                                    #
#   ********************************************************************************************************    #
#                           ~~~~~~~~~~~~~~~~~~~~~~~>>>> Dataset <<<<~~~~~~~~~~~~~~~~~~~~~~~                     #
#   ********************************************************************************************************    #
bq_dataset = []


#| ~~~~~~~~~~~~~~~~~~~~~~~~>>>> Table <<<<~~~~~~~~~~~~~~~~~~~~~~~~ |
#| ~~~~~~~~~~~~~~~~~~~~~~~~>>>>  Raw  <<<<~~~~~~~~~~~~~~~~~~~~~~~~ |
tb_raw_wh_sensor        = ""
tb_raw_delivery_sensor  = ""


#|  ~~~~~~~~~~~~~~~~~~~~~~~>>>> Table <<<<~~~~~~~~~~~~~~~~~~~~~~~  |
#|  ~~~~~~~~~~~~~~~~~~~~~~>>> Production <<<<~~~~~~~~~~~~~~~~~~~~  |
tb_wh_sensor            = ""
tb_wh_sensor_anomalies  = ""
tb_feedback             = ""
tb_feedback_sentiment   = ""
tb_sales_forecast       = ""

#|  ~~~~~~~~~~~~~~~~~~~~~~~>>>> Table <<<<~~~~~~~~~~~~~~~~~~~~~~~  |
#|  ~~~~~~~~~~~~~~~~~~~>>>> ls_customers <<<<~~~~~~~~~~~~~~~~~~~~  |
tb_customers            = ""
tb_cards                = ""
tb_address              = ""
tb_products             = ""
tb_inventory            = ""
tb_sales                = ""
tb_vehicles             = ""
tb_delivery_status      = ""


#|  ~~~~~~~~~~~~~~~~~~~~~>>>> Procedure <<<<~~~~~~~~~~~~~~~~~~~~~  |
#|  ~~~~~~~~~~~~~~~~~~~>>>> ls_customers <<<<~~~~~~~~~~~~~~~~~~~~  |
sp_merge_delivery_status    = ""
sp_delete_delivery_status   = ""
sp_feedback_sentiment       = ""

#   ********************************************************************************************************    #
#                                                     Dataflow                                                  #
#   ********************************************************************************************************    #
dfl_wh_sensor_template    = ""
dfl_wh_sensor_job_name    = ""
dfl_script_path           = "/../../modules/dataflow"

dfl_delivery_sensor_template    = ""
dfl_delivery_sensor_job_name    = ""

#   ********************************************************************************************************    #
#                                               Google Cloud Dataproc                                           #
#   ********************************************************************************************************    #
spark_job_tb_order = ""
spark_job_tb_feedback = ""


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
