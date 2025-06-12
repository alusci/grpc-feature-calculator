from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DoubleType
from datetime import datetime, timedelta
import random

# Start Spark
spark = SparkSession.builder.appName("CDRFeatureSample").getOrCreate()

# Define schema
schema = StructType([
    StructField("phone", StringType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("call_duration", DoubleType(), True),
    StructField("phone_range", StringType(), True),
    StructField("phone_prefix", StringType(), True),
])

# Generate sample data
base_date = datetime(2025, 4, 24)
phones = [f"+1-202-555-{str(i).zfill(4)}" for i in range(10)]
prefixes = ["+1-202", "+1-415", "+1-212"]

data = []
for _ in range(1000):
    phone = random.choice(phones)
    prefix = phone[:6]
    phone_range = random.choice(prefixes)
    days_ago = random.randint(0, 89)
    ts = base_date - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
    duration = round(random.uniform(0.5, 30.0), 2)
    data.append((phone, ts, duration, phone_range, prefix))

# Create DataFrame
cdr_sample_df = spark.createDataFrame(data, schema)

cdr_sample_df.show(10, truncate=False)

cdr_sample_df.write.mode("overwrite").parquet("cdr-data/cdr_sample/*.parquet")

