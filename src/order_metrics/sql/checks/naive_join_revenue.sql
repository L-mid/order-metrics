-- bad join example

SELECT
  COALESCE(SUM(o.total_usd), 0) AS joined_rev_usd
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status = 'paid';