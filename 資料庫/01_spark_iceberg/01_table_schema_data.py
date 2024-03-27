import pyspark
from pyspark.sql import SparkSession

table_name = "tra_group_test"
partition = "City"
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
table_ddl = f"""create table iceberg.{table_name}
          (Attractions                             string,
          Address                           string,
          City                              string,
          District                          string,
          Google_comment_web                string,
          Star_counts                       string,
          Opentime                          string,
          Comment_count                     string,
          NS                                string,
          WE                                string,
          Tag                               string,
          5star                             bigint,
          4star                             bigint,
          3star                             bigint,
          2star                             bigint,
          1star                             bigint,
          Mon_open                          string,
          Mon_close                         string,
          Tue_open                          string,
          Tue_close                         string,
          Wed_open                          string,
          Wed_close                         string,
          Thu_open                          string,
          Thu_close                         string,
          Fri_open                          string,
          Fri_close                         string,
          Sat_open                          string,
          Sat_close                         string,
          Sun_open                          string,
          Sun_close                         string,
          Comment                           string,
          Group                             string
          )
          USING iceberg
          PARTITIONED BY ({partition})"""
# 建table
spark.sql(table_ddl)

## Start Spark Session
# spark = SparkSession.builder.config(conf=conf).getOrCreate()
# df = spark1.read.json(f"{data_input_path}")
df = spark.read.option("multiline", "true").json(f"{data_input_path}")
df.printSchema()
# df.show()
df.writeTo(f"iceberg.{table_name}").append()
