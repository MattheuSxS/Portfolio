output "bkt_mts_airflow" {
  description = "Name of the bucket created for Airflow"
  value       = replace(replace(google_composer_environment.portfolio-composer.config[0].dag_gcs_prefix, "gs://", ""), "/dags", "")
}