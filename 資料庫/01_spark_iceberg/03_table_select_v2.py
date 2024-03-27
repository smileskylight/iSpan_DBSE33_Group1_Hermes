import pyspark
from pyspark.sql import SparkSession

table_name = "tra_group_test"

conf = pyspark.SparkConf().setAppName("iceberg test")
## Start Spark Session
spark = SparkSession.builder.config(conf=conf).getOrCreate()
# df = spark.table("iceberg.tra")
df = spark.read.format("iceberg").load(f"iceberg-warehouse/{table_name}")
df.createOrReplaceTempView("tra2")

resultsDF = spark.sql("SELECT * FROM tra2")
resultsDF.show(2)
c = spark.sql("SELECT count(*) FROM tra2")
c.show()
