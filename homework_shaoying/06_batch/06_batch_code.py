from pyspark.sql import SparkSession
import subprocess
from pyspark.sql.functions import col, unix_timestamp, max as spark_max

def create_spark_session():
    return SparkSession.builder \
        .master("local[*]") \
        .appName('test') \
        .getOrCreate()

def q1(spark: SparkSession):
    """
    Print the Spark version
    """
    print(f"Spark version: {spark.version}")
    
def load_and_repartition_yellow_data(
    spark: SparkSession,
    url: str,
    local_path: str,
    output_dir: str,
):
    subprocess.run(
        ["wget", url, "-O", local_path],
        check=True
    )
    
    df = spark.read.parquet(local_path)
    
    df.printSchema()
    
    df.repartition(4).write.mode("overwrite").parquet(output_dir)
    
    return df

def q2(
    spark: SparkSession,
    url: str = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet",
    local_path: str = "yellow_tripdata_2025-11.parquet",
    output_dir: str = "partitioned/",
):
    return load_and_repartition_yellow_data(spark, url, local_path, output_dir)
    
def q3(
    spark: SparkSession,
    date: str = "2025-11-15",
    parquet_dir: str = "partitioned/"
):
    """
    Get the taxi trips count for a given date (default 2025-11-15)
    """
    df = spark.read.parquet(parquet_dir)
    pickup_col = "tpep_pickup_datetime" if "tpep_pickup_datetime" in df.columns else "pickup_datetime"
    count = df.filter(df[pickup_col].startswith(date)).count()
    print(f"Taxi trips on {date}: {count}")
    return count

def q4(
    spark: SparkSession,
    parquet_dir: str = "partitioned/"
):
    """
    Get the longest trip time: tpep_dropoff_datetime - tpep_pickup_datetime
    """

    df = spark.read.parquet(parquet_dir)
    # Check column names
    pickup_col = "tpep_pickup_datetime" if "tpep_pickup_datetime" in df.columns else "pickup_datetime"
    dropoff_col = "tpep_dropoff_datetime" if "tpep_dropoff_datetime" in df.columns else "dropoff_datetime"

    # Compute duration in hours
    df_with_duration = df.withColumn(
        "duration_hours",
        (unix_timestamp(col(dropoff_col)) - unix_timestamp(col(pickup_col))) / 3600
    )

    result = df_with_duration.select(spark_max("duration_hours").alias("max_trip_hours")).collect()[0]["max_trip_hours"]
    print(f"Longest trip duration (hours): {result}")
    return result

def load_temp_lookup_zone(
    spark: SparkSession,
    url: str = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
):
    """
    Load the lookup zone csv file as a temp view in spark session
    """
    local_path = "taxi_zone_lookup.csv"
    subprocess.run(
        ["wget", url, "-O", local_path],
        check=True
    )
    df = spark.read.option("header", True).csv(local_path)
    df.createOrReplaceTempView("zones")
    return df

def q6(
    spark: SparkSession,
    parquet_dir: str = "partitioned/",
    zone_lookup_url: str = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
):
    """
    Find the least frequent pickup location Zone using the November 2025 yellow trip data and the taxi zone lookup,
    making use of the load_temp_lookup_zone function to create a temp view.
    """
    # Load trip data
    df = spark.read.parquet(parquet_dir)
    # Pickup location id column can be named "PULocationID" or "pickup_location_id"
    puloc_col = "PULocationID" if "PULocationID" in df.columns else "pickup_location_id"
    
    # Load zone lookup data as a temp view
    load_temp_lookup_zone(spark, zone_lookup_url)  # Registers "zones" temp view

    # Compute pickup location counts and register as a temp view
    pickup_counts = (
        df.groupBy(puloc_col)
        .count()
        .withColumnRenamed(puloc_col, "LocationID")
    )
    pickup_counts.createOrReplaceTempView("pickup_counts")
    
    # Now use Spark SQL to join and find min count
    joined_df = spark.sql("""
        SELECT pc.LocationID, pc.count, z.Zone
        FROM pickup_counts pc
        LEFT JOIN zones z
          ON pc.LocationID = cast(z.LocationID as int)
    """)
    min_count = joined_df.agg({"count": "min"}).collect()[0][0]
    least_zones = joined_df.filter(joined_df["count"] == min_count).select("Zone", "count")
    results = [row["Zone"] for row in least_zones.collect()]

    print(f"Least frequent pickup location zone(s): {results}")
    return results



if __name__ == "__main__":
    spark = create_spark_session()
    try:
        # print("Answer for question 1")
        # q1(spark)
        # q2(spark)
        # q3(spark)
        # q4(spark)
        q6(spark)
    finally:
        # Optional (only matters if you used cache/persist):
        spark.catalog.clearCache()
        spark.stop()