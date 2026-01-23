# Week 1

## Question 1. Understanding Docker images

Run docker with the `python:3.13` image. Use an entrypoint `bash` to interact with the container.

What's the version of `pip` in the image?

- 25.3
- 24.3.1
- 24.2.1
- 23.3.1

### Solution 1:

Code to run:

```bash
docker run -it --entrypoint=bash python:3.13
```

Then inside the container, run:

```bash
pip -V
```
Output:

```
pip 25.3 from /usr/local/lib/python3.13/site-packages/pip (python 3.13)
```

## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that pgadmin should use to connect to the postgres database?

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'  # Host port 5433 maps to container port 5432
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```

- postgres:5433
- localhost:5432
- db:5433
- postgres:5432
- db:5432

If multiple answers are correct, select any 

### Solution 2:
The correct answer is: **db:5432**


## Prepare the Data

Download the green taxi trips data for November 2025:

```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet
```

You will also need the dataset with zones:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

## Question 3. Counting short trips

For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a `trip_distance` of less than or equal to 1 mile?

- 7,853
- 8,007
- 8,254
- 8,421

### Solution 3:

```sql
SELECT
	count(1)
FROM
	green_taxi_trips
WHERE
	trip_distance <= 1
AND
	lpep_pickup_datetime >= '2025-11-01'
AND
	lpep_pickup_datetime < '2025-12-01'
;
```
The correct answer is: **8,007**

## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance? Only consider trips with `trip_distance` less than 100 miles (to exclude data errors).

Use the pick up time for your calculations.

- 2025-11-14
- 2025-11-20
- 2025-11-23
- 2025-11-25

### Solution 4:
Since the question didn't clarify whether is asking for the day with the single longest trip or the day with the highest total trip distance, here are both solutions:

1. Day with the single longest trip:
```sql
SELECT
  CAST(lpep_pickup_datetime AS DATE) AS pickup_day,
  MAX(trip_distance) AS max_trip_distance
FROM
  green_taxi_trips
WHERE
  trip_distance < 100
GROUP BY
  CAST(lpep_pickup_datetime AS DATE)
ORDER BY
  max_trip_distance DESC
LIMIT 1;
```
The correct answer is: **2025-11-14**, with a max trip distance of 88.03 miles.

2. Day with the highest total trip distance:
```sql
SELECT
  CAST(lpep_pickup_datetime AS DATE) AS pickup_day,
  SUM(trip_distance) AS total_trip_distance
FROM
  green_taxi_trips
WHERE
  trip_distance < 100
GROUP BY
  CAST(lpep_pickup_datetime AS DATE)
ORDER BY
  total_trip_distance DESC
LIMIT 1;
```
The correct answer is: **2025-11-20**, with a total trip distance of 6377 miles.

## Question 5. Biggest pickup zone

Which was the pickup zone with the largest `total_amount` (sum of all trips) on November 18th, 2025?

- East Harlem North
- East Harlem South
- Morningside Heights
- Forest Hills

### Solution 5:

```sql
SELECT
	z."Zone",
	SUM(g."total_amount") AS zone_total_amount
FROM
	zones z
JOIN
	green_taxi_trips g ON z."LocationID" = g."PULocationID"
WHERE
	CAST(g."lpep_pickup_datetime" AS DATE) = '2025-11-18'
GROUP BY
	z."Zone"
ORDER BY
	zone_total_amount DESC
LIMIT 1;
```
The correct answer is: **East Harlem North**


## Question 6. Largest tip

For the passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip?

Note: it's `tip` , not `trip`. We need the name of the zone, not the ID.

- JFK Airport
- Yorkville West
- East Harlem North
- LaGuardia Airport

### Solution 6:
Again, two possible interpretations of the question:

1. Drop off zone with the single largest tip:

```sql
SELECT
  z_do."Zone" AS dropoff_zone,
  g."tip_amount"
FROM
  green_taxi_trips g
JOIN
  zones z_pu ON g."PULocationID" = z_pu."LocationID"
JOIN
  zones z_do ON g."DOLocationID" = z_do."LocationID"
WHERE
  z_pu."Zone" = 'East Harlem North'
ORDER BY
  g."tip_amount" DESC
LIMIT 1;
```
The correct answer is: **Yorkville West**, with a tip amount of $81.89.

2. Drop off zone with the highest total tips:

```sql
SELECT
  z_do."Zone" AS dropoff_zone,
  SUM(g."tip_amount") AS total_tips
FROM
  green_taxi_trips g
JOIN
  zones z_pu ON g."PULocationID" = z_pu."LocationID"
JOIN
  zones z_do ON g."DOLocationID" = z_do."LocationID"
WHERE
  z_pu."Zone" = 'East Harlem North'
GROUP BY
  z_do."Zone"
ORDER BY
  total_tips DESC
LIMIT 1;
```
The correct answer is: **Upper East Side North**, with total tips of $4242.

## Terraform

In this section homework we'll prepare the environment by creating resources in GCP with Terraform.

In your VM on GCP/Laptop/GitHub Codespace install Terraform.
Copy the files from the course repo
[here](../../../01-docker-terraform/terraform/terraform) to your VM/Laptop/GitHub Codespace.

Modify the files as necessary to create a GCP Bucket and Big Query Dataset.


## Question 7. Terraform Workflow

Which of the following sequences, respectively, describes the workflow for:
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform`

Answers:
- terraform import, terraform apply -y, terraform destroy
- teraform init, terraform plan -auto-apply, terraform rm
- terraform init, terraform run -auto-approve, terraform destroy
- terraform init, terraform apply -auto-approve, terraform destroy
- terraform import, terraform apply -y, terraform rm