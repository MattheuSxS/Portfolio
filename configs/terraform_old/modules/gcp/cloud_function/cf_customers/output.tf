output "cf_path_customers_files" {
    description = "Path of the cloud function file"
    value       = data.archive_file.cf_path_customers_files.output_path
}