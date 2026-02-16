WITH baseline AS (
    SELECT COALESCE(SUM(total_usd), 0) AS baseline_rev_usd
    FROM orders
    WHERE status = 'paid'
),
joined AS (
  SELECT COALESCE(SUM(o.total_usd), 0) AS joined_rev_usd
  FROM orders o
  JOIN (
    -- pre-aggregate to order grain (one row per order_id)
    SELECT order_id
    FROM order_items
    GROUP BY order_id
  ) oi1 ON oi1.order_id = o.order_id
  WHERE o.status = 'paid'
)
SELECT
  joined.joined_rev_usd,
  baseline.baseline_rev_usd,
  (joined.joined_rev_usd - baseline.baseline_rev_usd) AS diff_usd
FROM joined, baseline
WHERE joined.joined_rev_usd <> baseline.baseline_rev_usd;