from pyspark.sql import functions as F
from pyspark.sql import SparkSession
from datetime import datetime
from functools import reduce

# Start Spark
spark = SparkSession.builder.appName("CDRFeatureSample").getOrCreate()

# Load data
cdr_sample_df = spark.read.parquet("cdr-data/cdr_sample.parquet")

# Assume `cdr_sample_df` is your input DataFrame
cdr_sample_df = cdr_sample_df.withColumn("date", F.to_date("timestamp"))

# Get latest date in dataset
base_date = cdr_sample_df.agg(F.max("date")).collect()[0][0]

# Time windows to evaluate
windows = [1, 7, 30, 90]

# Store output DataFrames
agg_list = []
prefix_agg_list = []
range_agg_list = []

for d in windows:
    window_start = F.date_sub(F.lit(base_date), d - 1)
    df_filtered = cdr_sample_df.filter(F.col("date").between(window_start, F.lit(base_date)))
    
    # PHONE-level features
    agg = df_filtered.groupBy("phone").agg(
        F.count("*").alias(f"count_phone_{d}d"),
        F.countDistinct("date").alias(f"acount_phone_active_{d}d")
    ).withColumn(f"velocity_phone_{d}d", F.round(F.col(f"count_phone_{d}d") / F.lit(d), 2))
    agg_list.append(agg)

    # PREFIX-level features
    prefix_agg = df_filtered.groupBy("phone_prefix").agg(
        F.count("*").alias(f"count_phone_prefix_{d}d")
    ).withColumn(f"velocity_phone_prefix_{d}d", F.round(F.col(f"count_phone_prefix_{d}d") / F.lit(d), 2))
    prefix_agg_list.append(prefix_agg)

    # RANGE-level features
    range_agg = df_filtered.groupBy("phone_range").agg(
        F.count("*").alias(f"count_phone_range_{d}d")
    ).withColumn(f"velocity_phone_range_{d}d", F.round(F.col(f"count_phone_range_{d}d") / F.lit(d), 2))
    range_agg_list.append(range_agg)

# Merge features
phone_features = reduce(lambda df1, df2: df1.join(df2, on="phone", how="outer"), agg_list)
prefix_features = reduce(lambda df1, df2: df1.join(df2, on="phone_prefix", how="outer"), prefix_agg_list)
range_features = reduce(lambda df1, df2: df1.join(df2, on="phone_range", how="outer"), range_agg_list)

# Show results
phone_features.show(5, truncate=False)

# Save results
phone_features.write.mode("overwrite").parquet("features/phone_features.parquet")
