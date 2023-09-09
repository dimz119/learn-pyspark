from pyspark.sql import SparkSession
from pyspark.sql.types import  StructType, StructField, StringType, IntegerType
from pyspark.sql.functions import from_json, col

spark = SparkSession \
    .builder \
    .appName("StatefulStreaming") \
    .config("spark.streaming.stopGracefullyOnShutdown", "true") \
    .config("spark.sql.shuffle.partitions", "3") \
    .getOrCreate()

schema = StructType([
            StructField("product_id", StringType()),
            StructField("amount", IntegerType())
        ])

events = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "pos") \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

value_df = events.select(
            col('key'),
            from_json(
                col("value").cast("string"), schema).alias("value"))

tf_df = value_df.selectExpr(
            'value.product_id',
            'value.amount')

total_df = tf_df.select("product_id", "amount")\
            .groupBy("product_id")\
            .sum("amount").withColumnRenamed("sum(amount)", "total_amount")

# Start running the query that prints the running counts to the console
query = total_df \
        .writeStream \
        .outputMode("complete") \
        .format("console") \
        .start()

query.awaitTermination()
