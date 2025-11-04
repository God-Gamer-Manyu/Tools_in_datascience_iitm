/*
This query finds the maximum positive lift in daily activations for the EMEA region
compared to the average of the 7 previous days.
*/

-- Step 1: Create a Common Table Expression (CTE) to calculate the 7-day trailing average.
WITH TrailingData AS (
    SELECT
        metric_date,
        region,
        activations,
        
        -- This window function calculates the average 'activations'
        -- for the 7 rows (days) immediately before the current row,
        -- partitioned by each 'region'.
        AVG(activations) OVER (
            PARTITION BY region
            ORDER BY metric_date
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) AS prior_7_day_avg
    FROM
        daily_product_metrics
),

-- Step 2: Use the trailing average from Step 1 to calculate the lift for each day.
LiftCalculation AS (
    SELECT
        metric_date,
        region,
        activations,
        prior_7_day_avg,
        
        -- Calculate lift: (current_day - 7_day_avg) / 7_day_avg
        -- We multiply by 1.0 to ensure floating-point (decimal) division.
        -- NULLIF prevents division-by-zero errors if the average is 0.
        (activations * 1.0 - prior_7_day_avg) / NULLIF(prior_7_day_avg, 0) AS lift_vs_avg
    FROM
        TrailingData
    WHERE
        -- We can only calculate lift where a 7-day average actually exists
        -- (i.e., after the first 7 days of data for a region).
        prior_7_day_avg IS NOT NULL
)

-- Step 3: Filter for the 'EMEA' region and find the single largest positive lift.
SELECT
    MAX(lift_vs_avg) AS max_positive_lift
FROM
    LiftCalculation
WHERE
    region = 'EMEA'
    AND lift_vs_avg > 0; -- As requested, only find the max positive spike.
