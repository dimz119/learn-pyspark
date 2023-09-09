from pyspark.sql import SparkSession
from pyspark.sql.types import  StructType, StructField, StringType
from pyspark.sql.functions import expr, from_json, col, lower

spark = SparkSession \
    .builder \
    .appName("StructuredWordCount") \
    .config("spark.streaming.stopGracefullyOnShutdown", "true") \
    .config("spark.sql.shuffle.partitions", "3") \
    .getOrCreate()

schema = StructType([
            StructField("city", StringType()),
            StructField("domain", StringType()),
            StructField("event", StringType())
        ])

events = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "raw") \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

# parse Kafka event
value_df = events.select(
                    col('key'),
                    from_json(
                        col("value").cast("string"), schema).alias("value"))

# select value
tf_df = value_df.selectExpr(
                    'value.city',
                    'value.domain',
                    'value.event as behavior')

concat_df = tf_df\
            .withColumn('lower_city', lower(col('city'))) \
            .withColumn('domain', expr('domain')) \
            .withColumn('behavior', expr('behavior'))\
            .drop('city')

output_df = concat_df.selectExpr(
                'null',
                "to_json(named_struct('lower_city', lower_city, 'domain', domain, 'behavior', behavior)) as value")

# important: chk/json and dataframe name
file_writer = concat_df \
                .writeStream \
                .queryName("transformed json") \
                .format("json") \
                .outputMode("append") \
                .option("path", "transformed") \
                .option("checkpointLocation", "chk/json") \
                .start()

# important: chk/kafka
kafka_writer = output_df \
                .writeStream \
                .queryName("transformed kafka") \
                .format("kafka") \
                .option("kafka.bootstrap.servers", "kafka:9092") \
                .option("checkpointLocation", "chk/kafka") \
                .option("topic", "transformed") \
                .outputMode("append") \
                .start()

# use awaitAnyTermination
spark.streams.awaitAnyTermination()
