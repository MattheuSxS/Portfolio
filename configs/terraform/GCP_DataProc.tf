resource "null_resource" "spark_path_tb_order" {
  provisioner "local-exec" {
    command = <<EOT
      cd ${var.dp_order_script_path}
      zip -r utils.zip utils
    EOT
  }
}

resource "null_resource" "spark_path_tb_feedback" {
  provisioner "local-exec" {
    command = <<EOT
      cd ${var.dp_feedback_script_path}
      zip -r utils.zip utils
    EOT
  }
}