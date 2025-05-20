output "raw_dataset" {
  value = "${google_bigquery_dataset.bq_dataset[0].dataset_id}"
}
output "staging_dataset" {
  value = "${google_bigquery_dataset.bq_dataset[1].dataset_id}"
}
output "production_dataset" {
  value = "${google_bigquery_dataset.bq_dataset[2].dataset_id}"
}
output "tb_raw_dw_messages" {
  value = "${google_bigquery_table.tb_raw_dw_messages.table_id}"
}

output "tb_dw_messages" {
  value = "${google_bigquery_table.tb_dw_messages.table_id}"
}
output "tb_feedback" {
  value = "${google_bigquery_table.tb_feedback.table_id}"
}