from pyspark.sql import SparkSession
from pyspark.sql.types import  StructType, StructField, StringType, IntegerType
from pyspark.sql.functions import from_json, col, to_timestamp, window

spark = SparkSession \
    .builder \
    .appName("WaterMark") \
    .config("spark.streaming.stopGracefullyOnShutdown", "true") \
    .config("spark.sql.shuffle.partitions", "3") \
    .getOrCreate()

schema = StructType([
            StructField("create_date", StringType()),
            StructField("amount", IntegerType())
        ])

events = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "timeseries") \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

value_df = events.select(
            col('key'),
            from_json(
                col("value").cast("string"), schema).alias("value"))

timestamp_format = "yyyy-MM-dd HH:mm:ss"
tf_df = value_df.select("value.*") \
                .withColumn("create_date", to_timestamp("create_date", timestamp_format))

window_duration = "5 minutes"
# watermark boundary
# max(event time) - watermark = watermark boundary
# if the event comes after the watermark boundary, it will be ignored
window_agg_df = tf_df \
                .withWatermark("create_date", "10 minutes") \
                .groupBy(window(col("create_date"), window_duration)) \
                .sum("amount").withColumnRenamed("sum(amount)", "total_amount")

# Start running the query that prints the running counts to the console
query = window_agg_df \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .trigger(processingTime="5 seconds") \
        .start()

query.awaitTermination()
