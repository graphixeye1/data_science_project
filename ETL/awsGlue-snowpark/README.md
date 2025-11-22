# AWS Glue & Snowpark End-to-End ELT Pipeline

![Architecture](./images/Architecture.png)

## 📌 Project Overview

This project automates the extraction, loading, transformation, and aggregation of multi-country sales data using AWS Glue, Amazon S3, and Snowflake Snowpark.
The pipeline standardizes different file formats, consolidates them, and prepares curated datasets for analytics and reporting.

## 🎯 Objective

Build a fully automated ELT workflow that:

Extracts sales files from GitHub

Loads structured data into Snowflake

Applies transformations with Snowpark

Produces curated analytics-ready datasets

## 📂 Data Sources

Sales order files are stored in a GitHub repository with different formats per country:

Country	File Format
India	CSV
USA	Parquet
France	JSON

## 🏗️ ELT Workflow
1️⃣ Data Extraction & Storage (AWS Glue + S3)

An AWS Glue Python script connects to the GitHub repository.

It downloads all sales files (CSV, Parquet, JSON).

Files are stored in an Amazon S3 bucket inside country-specific folders.

This forms the landing zone for the pipeline.

2️⃣ Load Data Into Snowflake (Snowpark + STAGING Schema)

Snowpark is used to connect to Snowflake and process multi-format files.

Data is ingested from S3 into STAGING tables using the Snowflake COPY INTO command.

Basic validation occurs in Staging.

Valid records are then moved into the RAW schema.

3️⃣ Transform & Standardize Data (Snowpark + RAW → TRANSFORMED)

Once the three datasets are in RAW, transformation logic is applied:

Column renaming and standardization

Rearrangement of column order

Addition of new computed fields

Splitting complex fields into multiple columns

Unifying all three datasets through a UNION operation

The final standardized dataset is stored inside the TRANSFORMED schema.

4️⃣ Aggregations & Final Curated Layer (Snowpark + CURATED Schema)

Snowpark is used to compute business-level metrics such as:

`Total sales`

`Country-based summaries`

`Product-level analysis`


These final analytical datasets are written into the CURATED schema, optimized for dashboards and reporting tools.

✅ Outcome

This pipeline delivers:

Automated ingestion from GitHub

Consistent file processing across three formats

Clean, unified datasets in Snowflake

Aggregated analytics-ready tables

A scalable ELT architecture across AWS and Snowflake

This enables accurate reporting, faster insights, and easier downstream integration.

📦 Repository Structure
/project
│── glue_scripts/
│     └── extract_github_data.py
│── snowpark_jobs/
│     └── transformations.py
│── sql/
│     ├── staging_tables.sql
│     ├── raw_tables.sql
│     └── curated_views.sql
│── images/
│     └── Architecture.png
│── README.md


```

import snowflake.snowpark as snowpark
from snowflake.snowpark.functions import col, sum, year, quarter, to_date, concat, lit

def main(session: snowpark.Session): 
    # setting current database
    session.sql('USE  SCHEMA SNOWPARK_DB.TRANSFORMED').collect()

    # global sales order delivered
    df_global_sales_order_delivered = session.table("SNOWPARK_DB.TRANSFORMED.GLOBAL_SALES_ORDER").\
        filter(col("SHIPPING_STATUS") == 'Delivered')

    # load the data into the table
    df_global_sales_order_delivered.write.mode("overwrite").save_as_table("SNOWPARK_DB.AGGREGATED.GLOBAL_SALES_ORDER_DELIVERD")

    # aggregating sales base on mobile brand

    df_global_sales_order_brand = session.table("SNOWPARK_DB.TRANSFORMED.GLOBAL_SALES_ORDER").\
        groupBy(col("MOBILE_BRAND"), col("MOBILE_MODEL")).\
        agg(sum(col("TOTAL_PRICE")).alias("TOTAL_SALES_AMOUNT"))

    df_global_sales_order_brand.write.mode("overwrite").save_as_table("SNOWPARK_DB.AGGREGATED.GLOBAL_SALES_ORDER_BRAND")

    # global sales order by country

    df_global_sales_order_country = session.table("SNOWPARK_DB.TRANSFORMED.GLOBAL_SALES_ORDER").\
        groupBy(col("COUNTRY"),
                year(to_date(col("ORDER_DATE"))).alias("YEAR"),
                concat(lit("Q"), quarter(to_date(col("ORDER_DATE")))).alias("QUARTER")).\
                    agg(sum(col("QUANTITY")).alias("TOTAL_SALES_VOLUME"), sum(col("TOTAL_PRICE")).alias("TOTAL_SALES_AMOUNT"))

    # load data to table

    df_global_sales_order_country.write.mode("overwrite").save_as_table("SNOWPARK_DB.AGGREGATED.GLOBAL_SALES_ORDER_COUNTRY")

    
    
    
    return df_global_sales_order_brand`
    ```