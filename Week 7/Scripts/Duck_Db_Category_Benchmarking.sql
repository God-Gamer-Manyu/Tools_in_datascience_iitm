-- This query reads two CSVs directly from your computer,
-- joins them, filters by date, and calculates the highest gross margin.

WITH
-- Step 1: Join the two CSV files, filtering for the date
joined_data AS (
    SELECT
        s.units,
        s.unit_price,
        m.category,
        m.production_cost
    FROM
        -- ==========================================================
        -- IMPORTANT: Replace 'C:\path\to\your\file\' with the
        -- *full local path* where you saved the CSVs.
        read_csv_auto('D:\Rtamanyu\_IIt Madras\2nd year\sem 1\Tools in datascience\Week 7\q-duckdb-sku-benchmark-shipments.csv') AS s
        -- ==========================================================
    JOIN
        -- ==========================================================
        -- IMPORTANT: Use the full local path for this file as well.
        read_csv_auto('D:\Rtamanyu\_IIt Madras\2nd year\sem 1\Tools in datascience\Week 7\q-duckdb-sku-benchmark-sku_master.csv') AS m
        -- ==========================================================
    ON
        s.sku_id = m.sku_id
    WHERE
        -- Step 2: Filter for shipments on or after the launch date
        s.ship_date >= '2024-05-15'
),

-- Step 3: Aggregate by category to get total revenue and cost
category_metrics AS (
    SELECT
        category,
        SUM(units * unit_price) AS total_revenue,
        SUM(units * production_cost) AS total_cost
    FROM
        joined_data
    GROUP BY
        category
)

-- Step 4: Calculate gross margin and find the winner
SELECT
    category,
    -- (Revenue - Cost) / Revenue = Gross Margin Ratio
    (total_revenue - total_cost) / total_revenue AS gross_margin
FROM
    category_metrics
ORDER BY
    gross_margin DESC -- Find the highest margin
LIMIT 1; -- Show only the top one
