from pyspark.sql import (
    functions as f,
    SparkSession,
    types as t
)

spark = SparkSession.builder.appName("partition_pruning").getOrCreate()

table_schema = t.StructType([
    t.StructField("date", t.StringType(), True),
    t.StructField("name", t.StringType(), True),
    t.StructField("price", t.IntegerType(), True)])

csv_file_path = "file:///home/jovyan/work/sample/ecommerce_order.csv"
df = spark.read.schema(table_schema).csv(csv_file_path)

df.write\
    .partitionBy("date")\
    .mode("overwrite")\
    .parquet("/home/jovyan/work/output/partition_pruning")
