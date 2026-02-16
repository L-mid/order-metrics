-- grain sanity: paid_users > paid_orders

WITH m AS (
    SELECT
        DATE_TRUNC('month', order_ts)::date AS month,
        COUNT(*) FILTER (WHERE status = 'paid') AS paid_orders,
        COUNT(DISTINCT user_id) FILTER (WHERE status = 'paid') paid_users
    FROM orders
    GROUP BY 1
)
SELECT *
FROM m
WHERE paid_users > paid_orders      
-- if this returns any rows, data/logic violated the grain contract.


