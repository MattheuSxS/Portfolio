resource "google_composer_environment" "portfolio-composer" {
    depends_on  = [google_project_iam_member.roles_sa_composer]
    provider    = google-beta
    project     = local.project
    region      = var.region
    name        = var.composer_name

    config {
        environment_size = "ENVIRONMENT_SIZE_MEDIUM"

        software_config {
            image_version = var.composer_image_version
        }

        workloads_config {
            scheduler {
                cpu        = 1
                memory_gb  = 4
                storage_gb = 5
                count      = 2
            }
            triggerer {
                cpu        = 0.5
                memory_gb  = 2
                count      = 2
            }
            dag_processor {
                cpu        = 2
                memory_gb  = 7.5
                storage_gb = 5
                count      = 2
            }
            web_server {
                cpu        = 2
                memory_gb  = 7.5
                storage_gb = 5
            }
            worker {
                cpu        = 2
                memory_gb  = 7.5
                storage_gb = 20
                min_count  = 1
                max_count  = 2
            }
        }

        node_config {
            service_account = local.sa_composer
        }
    }

    storage_config {
        bucket = local.bkt_airflow
    }

    labels = {
        created_by = "terraform"
        env        = var.environment
    }
}


resource "local_file" "create_airflow_variable_script" {
    filename = "./scripts/set_airflow_variables.py"
    content  = <<-EOT
        import json
        import logging
        from pathlib import Path
        from google.cloud import storage
        from airflow.models import Variable


        logging.basicConfig(
            format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
                    "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
            level=logging.INFO
        )


        def read_json_files_from_gcs(bucket_name, prefix=""):
            """
            Read JSON files from a GCS bucket.

            Args:
                bucket_name (str): GCS bucket name.
                prefix (str): Prefix to filter files in the bucket.

            Returns:
                list: List of tuples with file name and JSON content.
            """
            json_data_dict = dict()

            try:
                client = storage.Client()
                bucket = client.bucket(bucket_name)
                blobs = bucket.list_blobs(prefix=prefix)

                for blob in blobs:
                    if blob.name.endswith(".json"):
                        logging.info(f"Reading file {blob.name}")
                        json_data = blob.download_as_text()

                        try:
                            json_data_dict.update(json.loads(json_data))

                        except json.JSONDecodeError as e:
                            logging.error(f"Error decoding JSON in file {blob.name} - {e}")

                        except Exception as e:
                            logging.error(f"Unexpected error processing file {blob.name} - {e}")

            except Exception as e:
                logging.error(f"Error accessing GCS bucket {bucket_name} - {e}")

            return json_data_dict


        def set_airflow_variables(bucket_name, prefix):
            """
                Reads JSON files from a Google Cloud Storage (GCS) bucket and sets Airflow variables.

                This function reads JSON files from the specified GCS bucket and prefix, and sets Airflow
                variables based on the contents of these files. Each key-value pair in the JSON files is
                set as an Airflow variable.

                Args:
                bucket_name (str): The name of the GCS bucket.
                prefix (str): The prefix path within the GCS bucket where the JSON files are located.

                Returns:
                None

                Logs:
                - An error if no JSON files are found or an error occurs while reading files.
                - An error if a file does not contain a valid JSON dictionary.
                - An error if there is an issue setting the Airflow variables.
                - An info message for each variable successfully created.
            """

            json_data = read_json_files_from_gcs(bucket_name, prefix)

            if not json_data:
                logging.error("No JSON files found or an error occurred while reading files.")
                return

            valid_data = {}

            for key, value in json_data.items():
                if isinstance(value, dict):
                    valid_data[key] = value
                else:
                    logging.error(f"File {key} does not contain a valid JSON dictionary.")
            try:
                for key, value in valid_data.items():
                    Variable.set(key=key, value=json.dumps(value, indent=4))
                    logging.info(f"Variable {key} created successfully")

            except Exception as e:
                logging.error(f"Error setting variables from file '{key}' - {e}")


        bucket_name = "${local.bkt_airflow}"
        prefix = "variables/"

        set_airflow_variables(bucket_name, prefix)
    EOT
}

# TODO: THIS FUNCTION ISNT WORKING, NEED TO FIGURE OUT HOW TO RUN THIS SCRIPT AFTER COMPOSER ENVIRONMENT IS CREATED
# resource "null_resource" "create_airflow_variable" {
#     provisioner "local-exec" {
#         command = <<EOT
#             echo "Waiting for Composer to be ready..."
#             sleep 30
#             gcloud composer environments storage plugins import \
#                 --environment ${var.composer_name} \
#                 --location ${var.region} \
#                 --source ${local_file.create_airflow_variable_script.filename}
#         EOT
#     }
# }

# resource "null_resource" "pause_all_dags" {
#     triggers = {
#         bucket_name     = local.bkt_airflow
#         composer_name   = var.composer_name
#         region_name     = var.region
#     }
#     provisioner "local-exec" {
#         when    = destroy
#         command = <<EOT
#             echo "Pausing all DAGs in Composer environment ${self.triggers.composer_name}..."
#             gcloud composer environments run ${self.triggers.composer_name} \
#                 --location ${self.triggers.region_name} \
#                 dags pause \
#                 -- \
#                 -y --treat-dag-id-as-regex ".*"
#         EOT
#     }
# }

