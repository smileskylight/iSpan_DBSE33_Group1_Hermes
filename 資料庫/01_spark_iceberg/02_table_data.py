import pyspark
from pyspark.sql import SparkSession

table_name = "tra_group_test"
data_input_path = "mydataset/tra_group/tag03comment1_ENG_v4.json"

conf = (
    pyspark.SparkConf()
    .setAppName("iceberg")
    .set(
        "spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.3_2.12-1.4.3"
    )
    .set(
        "spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    )
    .set("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
    .set("spark.sql.catalog.iceberg.type", "hadoop")
    .set("spark.sql.catalog.iceberg.warehouse", "iceberg-warehouse")
)
## Start Spark Session
spark = SparkSession.builder.config(conf=conf).getOrCreate()
# df = spark.read.json("mydataset/trip/彰化縣和美鎮.json")
df = spark.read.option("multiline", "true").json(f"{data_input_path}")
# df.show()
df.writeTo(f"iceberg.{table_name}").append()
