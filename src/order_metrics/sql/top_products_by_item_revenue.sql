-- best practice join here: compute revenue 
-- at the order_items grain (cannot inflate from joins)

SELECT
    oi.product_sku,
    SUM(oi.qty) AS units_sold,
    COALESCE(SUM(oi.qty * oi.unit_price_usd), 0)::numeric(12,2) AS item_revenue_usd
FROM order_items oi
JOIN orders o
    ON o.order_id = oi.order_id
WHERE o.status = 'paid'
GROUP BY 1
ORDER BY item_revenue_usd DESC
LIMIT 20;