output "cf_path_sensor_files" {
    description = "Path of the cloud function file"
    value       = data.archive_file.cf_path_sensor_files.output_path
}