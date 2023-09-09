from pyspark.sql import SparkSession
from pyspark.sql.types import  StructType, StructField, StringType
from pyspark.sql.functions import from_json, col, to_timestamp

spark = SparkSession \
    .builder \
    .appName("StreamingJoin") \
    .config("spark.streaming.stopGracefullyOnShutdown", "true") \
    .config("spark.sql.shuffle.partitions", "3") \
    .getOrCreate()

impression_schema = StructType([
                        StructField("placement_id", StringType()),
                        StructField("uuid", StringType()),
                        StructField("create_date", StringType()),
                        StructField("campaign", StringType())
                    ])

click_schema = StructType([
                    StructField("placement_id", StringType()),
                    StructField("uuid", StringType()),
                    StructField("create_date", StringType())
                ])

impression_events = spark \
                    .readStream \
                    .format("kafka") \
                    .option("kafka.bootstrap.servers", "kafka:9092") \
                    .option("subscribe", "impression") \
                    .option("startingOffsets", "earliest") \
                    .option("failOnDataLoss", "false") \
                    .load()

timestamp_format = "yyyy-MM-dd HH:mm:ss"
impressions_df = impression_events.select(
                    col('key'),
                    from_json(
                        col("value").cast("string"), impression_schema).alias("value")) \
                    .select(
                        'value.*') \
                    .withColumn("create_date", to_timestamp("create_date", timestamp_format)) \
                    .withWatermark("create_date", "30 minutes")


click_events = spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", "kafka:9092") \
                .option("subscribe", "click") \
                .option("startingOffsets", "earliest") \
                .option("failOnDataLoss", "false") \
                .load()

timestamp_format = "yyyy-MM-dd HH:mm:ss"
clicks_df = click_events.select(
                    col('key'),
                    from_json(
                        col("value").cast("string"), click_schema).alias("value")) \
                    .select(
                        'value.*') \
                    .withColumn("create_date", to_timestamp("create_date", timestamp_format)) \
                    .withWatermark("create_date", "10 minutes")

join_df = impressions_df.join(
            clicks_df,
            impressions_df.uuid == clicks_df.uuid,
            "inner").drop(clicks_df.uuid).drop(clicks_df.placement_id)

# Start running the query that prints the running counts to the console
query = join_df \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .start()

query.awaitTermination()
