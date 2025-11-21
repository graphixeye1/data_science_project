from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql import functions as F
import sys

# Expected args: JOB_NAME, SOURCE_S3, TARGET_S3
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'SOURCE_S3', 'TARGET_S3'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

source = args['SOURCE_S3']
target = args['TARGET_S3']

print(f"Reading from {source}")
df = spark.read.option("header", "true").csv(source)

# Example transformations: trim strings and drop fully-empty rows
for c in df.columns:
    df = df.withColumn(c, F.trim(F.col(c)))

df = df.dropna(how='all')

print(f"Writing transformed data to {target} in parquet format")
df.write.mode('overwrite').parquet(target)

print("Job completed")
