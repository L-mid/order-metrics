from __future__ import annotations

from order_metrics.read_sql import read_sql


def test_paid_users_le_paid_orders(mock_connect):
    """
    Paid_users should not be greater than paid_orders.
    In any fixed month:
    - each paid order belongs to exactly one user.
    - users can have many orders, but can't have more distinct users than orders.
    - `paid_users` <= `paid_orders` should always be true.

    Failures usually mean:
    - accidental count of users from a different grain (eg. bad join, double counting)
    - or: bad query logic (mixing filters, grouping, etc)
    """
    sql =  read_sql("checks/check_paid_users_le_paid_orders.sql")
    with mock_connect.cursor() as cur:
        cur.execute(sql)
        bad_rows = cur.fetchall()
    assert bad_rows == [], f"Found months where paid_users > paid_orders: {bad_rows}"
