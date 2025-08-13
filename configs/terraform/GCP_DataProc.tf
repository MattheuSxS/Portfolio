# # data "archive_file" "spark_path_tb_order" {
# #     type        = "zip"
# #     source_dir  = "../../src/dataproc/dp_order/"
# #     output_path = "../../src/dataproc/dp_order/utils.zip"

# #   excludes = [
# #     "**.py",  # exclui arquivos .py fora da pasta utils/
# #     ".DS_Store",
# #     "!utils/**"
# #   ]
# # }

# resource "null_resource" "spark_path_tb_order1" {
#   provisioner "local-exec" {
#     command = <<EOT
#       cd ../../src/dataproc/dp_order/
#       zip -r utils.zip utils
#     EOT
#   }
# }

# resource "null_resource" "spark_path_tb_feedback" {
#   provisioner "local-exec" {
#     command = <<EOT
#       cd ../../src/dataproc/dp_feedback/
#       zip -r utils.zip utils
#     EOT
#   }
# }