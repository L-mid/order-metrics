from __future__ import annotations

from order_metrics.read_sql import read_sql


def _scalar(mock_connect, sql: str) -> float:
    """Return float of executed row."""
    with mock_connect.cursor() as cur:
        cur.execute(sql)
        (v,) = cur.fetchone()   # Unpack a 1-element tuple into v.
        return float(v)


def test_naive_join_inflates_when_order_has_multiple_items(mock_connect):
    """
    Shows a naive join can inflate revenue.
    If you sum an order-level metric after joining to a lower-grain table, you can inflate it.
    - picks a paid order
    - row = cur.fetchone() returns something like order_id = 42.
    - create a fanout on purpose.
    - If order 42 already had 1 item, it now has 2 items.
    - So joining orders -> order_items will produce 2 rows for that one order.
    """
    # Force a fanout: add a second item to any paid order.
    with mock_connect.cursor() as cur:
        cur.execute("SELECT order_id FROM orders WHERE status='paid' ORDER BY order_id LIMIT 1;")
        row = cur.fetchone()
        assert row is not None, "Need at least one paid order in seed data"
        (order_id,) = row

        # Insert a second line item
        cur.execute(
            """
            INSERT INTO order_items (order_id, product_sku, qty, unit_price_usd)
            VALUES (%s, %s, %s, %s);
            """,
            (order_id, "FANOUT_TEST_SKU", 1, 1.00),
        )

    # When joining this to order_items, each order repeats once per item.
    naive = read_sql("checks/naive_join_revenue.sql")
    # reads from orders only, orders is one row per order
    baseline_sql = "SELECT COALESCE(SUM(total_usd),0) FROM orders WHERE status='paid';"

    joined_rev = _scalar(mock_connect, naive)
    baseline_rev = _scalar(mock_connect, baseline_sql)

    # Assert inflation happened
    assert joined_rev > baseline_rev, (joined_rev, baseline_rev)


def test_guardrail_query_detects_no_fanout(mock_connect):
    """A query on the correct grain does not cause fanout."""
    # Same forced fanout insert
    with mock_connect.cursor() as cur:
        cur.execute("SELECT order_id FROM orders WHERE status='paid' ORDER BY order_id LIMIT 1;")
        (order_id,) = cur.fetchone()
        cur.execute(
            """
            INSERT INTO order_items (order_id, product_sku, qty, unit_price_usd)
            VALUES (%s, %s, %s, %s);
            """,
            (order_id, "FANOUT_TEST_SKU2", 1, 1.00),
        )

    check = read_sql("checks/check_no_join_fanout_revenue.sql")
    with mock_connect.cursor() as cur:
        cur.execute(check)
        bad = cur.fetchall()

    assert bad == [], f"Revenue fanout detected (joined != baseline): {bad}"
