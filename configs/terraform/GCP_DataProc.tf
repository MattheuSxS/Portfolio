resource "null_resource" "spark_path_tb_order1" {
  provisioner "local-exec" {
    command = <<EOT
      cd ../../src/dataproc/dp_order/
      zip -r utils.zip utils
    EOT
  }
}

resource "null_resource" "spark_path_tb_feedback" {
  provisioner "local-exec" {
    command = <<EOT
      cd ../../src/dataproc/dp_feedback/
      zip -r utils.zip utils
    EOT
  }
}