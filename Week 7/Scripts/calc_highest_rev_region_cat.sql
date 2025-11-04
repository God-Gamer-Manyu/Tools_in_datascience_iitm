-- This query follows the workflow to find the highest-revenue
-- region-category pair from completed orders.

-- We calculate the total revenue (quantity * unit_price)
-- We filter for 'completed' orders
-- We group by region and category
-- We order by the total revenue to find the max
-- We limit to the top 1 result
SELECT
    region,
    category
    -- SUM(quantity * unit_price) AS total_revenue
FROM
    orders
WHERE
    status = 'completed'
GROUP BY
    region,
    category
ORDER BY
    SUM(quantity * unit_price) DESC
LIMIT 1;
