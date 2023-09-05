from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.functions import split

spark = SparkSession \
    .builder \
    .appName("StructuredWordCount") \
    .config("spark.streaming.stopGracefullyOnShutdown", "true") \
    .config("spark.sql.shuffle.partitions", "3") \
    .getOrCreate()

# Create DataFrame representing the stream of input lines from connection to localhost:9999
events = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "quickstart") \
    .option("startingOffsets", "earliest") \
    .load()

# # print schema
# events.printSchema()

# Split the lines into words
words = events.select(
   explode(
       split(events.value, " ")
   ).alias("word")
)

# Generate running word count
wordCounts = words.groupBy("word").count()

 # Start running the query that prints the running counts to the console
query = wordCounts \
    .writeStream \
    .option("checkpointLocation", "checkpoint") \
    .outputMode("complete") \
    .format("console") \
    .start()

query.awaitTermination()
