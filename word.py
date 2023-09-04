from pyspark.sql import (
    Row,
    SparkSession)
from pyspark.sql.functions import col, asc, desc

def parse_line(line: str):
    fields = line.split('|') # |
    return Row(
        name=str(fields[0]),
        country=str(fields[1]),
        email=str(fields[2]),
        compensation=int(fields[3]))


spark = SparkSession.builder.appName("SparkSQL").getOrCreate()
lines = spark.sparkContext.textFile("file:///opt/bitnami/spark/work/sample/income.txt")
income_data = lines.map(parse_line)

# Creates a DataFrame from an RDD, a list or a pandas.DataFrame.
# SparkSession.createDataFrame(data, schema=None, samplingRatio=None, verifySchema=True)[source]
schema_income = spark.createDataFrame(data=income_data).cache()

# Creates or replaces a local temporary view with this DataFrame.
schema_income.createOrReplaceTempView("income")

# returns the dataframe
medium_income_df = spark.sql(
    "SELECT * FROM income WHERE compensation >= 70000 AND compensation <= 100000")
# medium_income_df.show()
medium_income_df.write.csv("medium_income_df")

# for income_data in medium_income_df.collect():
#     # print(income_data)
#     print(income_data.name)

# # use function instead of sql function
# schema_income.groupBy("country").count().orderBy(col("count").desc()).show()