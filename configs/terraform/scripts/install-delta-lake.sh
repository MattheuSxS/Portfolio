#!/bin/bash
# Script para instalar o conector Delta Lake e configurar o Spark

# Variáveis (ajuste a versão do Scala/Spark e Delta Lake conforme necessário)
# Verifique a versão da imagem do Dataproc que você está usando para compatibilidade de Spark/Scala
# Por exemplo, se usa Dataproc 2.x, é provável que seja Spark 3.x com Scala 2.12
DELTA_LAKE_VERSION="3.2.1" # Use a versão mais recente do Delta Lake compatível com seu Spark
SCALA_VERSION="2.12"      # Verifique a versão do Scala do seu ambiente Spark no Dataproc

echo "Downloading Delta Lake Spark Connector ${DELTA_LAKE_VERSION} for Scala ${SCALA_VERSION}..."

# Use gsutil para copiar do bucket público do Spark/Delta
# Certifique-se de que a Service Account do seu cluster Dataproc tenha permissão para ler de gs://spark-lib
gsutil cp "gs://spark-lib/delta/delta-core_${SCALA_VERSION}-${DELTA_LAKE_VERSION}.jar" /usr/lib/spark/jars/
gsutil cp "gs://spark-lib/delta/delta-storage-${DELTA_LAKE_VERSION}.jar" /usr/lib/spark/jars/

# Opcional: Configurações Spark para usar o Delta Lake por padrão
# Adicione estas linhas se quiser que o Spark detecte tabelas Delta por padrão
cat <<EOF >> /etc/spark/conf/spark-defaults.conf
spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension
spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog
EOF

echo "Delta Lake connector and Spark configurations applied."