-- prefer per case filter > global where

SELECT
    DATE_TRUNC('month', order_ts)::date AS month,
    COUNT(*) FILTER (WHERE status = 'paid') AS paid_orders,
    COUNT(DISTINCT user_id) FILTER (WHERE status = 'paid') AS paid_users,
    COALESCE(SUM(total_usd) FILTER (WHERE status = 'paid'), 0)::numeric(12,2) AS paid_revenue_usd
FROM orders
GROUP BY 1
ORDER BY 1;