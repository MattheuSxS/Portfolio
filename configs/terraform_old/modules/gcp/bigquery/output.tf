output "raw_dataset" {
  value = "${google_bigquery_dataset.bq_dataset[0].dataset_id}"
}
output "staging_dataset" {
  value = "${google_bigquery_dataset.bq_dataset[1].dataset_id}"
}
output "production_dataset" {
  value = "${google_bigquery_dataset.bq_dataset[2].dataset_id}"
}

output "ls_customers_dataset" {
  value = "${google_bigquery_dataset.bq_dataset[3].dataset_id}"
}

output "tb_raw_dw_messages" {
  value = "${google_bigquery_table.tb_raw_dw_messages.table_id}"
}

output "tb_wh_sensor" {
  value = "${google_bigquery_table.tb_wh_sensor.table_id}"
}
output "tb_feedback" {
  value = "${google_bigquery_table.tb_feedback.table_id}"
}

output "tb_customers" {
  value = "${google_bigquery_table.tb_customers.table_id}"
}

output "tb_cards" {
  value = "${google_bigquery_table.tb_cards.table_id}"
}

output "tb_address" {
  value = "${google_bigquery_table.tb_address.table_id}"
}