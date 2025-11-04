-- This query finds the region with the highest enterprise gross margin for Q2 2024.

-- We select the region and calculate the gross margin.
-- Gross Margin = (Total Revenue - Total Cost) / Total Revenue
-- We multiply by 1.0 to ensure floating-point division for an accurate percentage.
SELECT
    region
    -- (SUM(revenue_usd - cost_usd) * 1.0 / SUM(revenue_usd)) AS gross_margin
FROM
    subscription_orders
WHERE
    -- Filter for Q2 (April, May, June)
    order_date >= '2024-04-01'
    AND order_date <= '2024-06-30'
    -- Filter for the 'Enterprise' segment
    AND segment = 'Enterprise'
GROUP BY
    region
ORDER BY
    (SUM(revenue_usd - cost_usd) * 1.0 / SUM(revenue_usd)) DESC -- Sort from highest margin to lowest
LIMIT 1; -- Select only the top one
