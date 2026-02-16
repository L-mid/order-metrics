from __future__ import annotations

import argparse
import re

from .db import connect, load_db_config
from .render import render_table
from .read_sql import read_sql


REPORTS = {
    "monthly": ("monthly_paid_metrics.sql", "Monthly paid metrics"),
    "country": ("country_paid_metrics.sql", "Country paid metrics"),
    "top-products": ("top_products_by_item_revenue.sql", "Top products by item revenue"),
}
ORDER = ["monthly", "country", "top-products"]

# sanity check at import time
if set(ORDER) != set(REPORTS):              # kill dupes
    missing = set(REPORTS) - set(ORDER)
    extra = set(ORDER) - set(REPORTS)
    # there should be NO MISSING OR EXTRA KEYS between order and reports.
    raise RuntimeError(f"ORDER/REPORTS mismatch. missing_in_order={missing} extra_in_order={extra}")


# It’s looking for psycopg "pyformat" named placeholders inside SQL.
# ex: ... WHERE country = %(country)s AND month >= %(month)s
_PARAM_RE = re.compile(r"%\((?P<k>[A-Za-z_][A-Za-z0-9_]*)\)s")
# it "finds valid params" by literally reading the placeholder names inside the SQL text.

def run_query(conn, sql: str, params: dict | None = None):
    """
    Curser stores:
    - the current statment
    - server's result description (cols)
    - it's current position while fetching rows.
    - optional params in execution
    """
    if params is not None and not isinstance(params, dict):
        raise TypeError("params must be a dict or None")
    expected = set(_PARAM_RE.findall(sql))      # dedupe for efficency     

    if params is None: 
        params = {}      # None is permitted
    else:
        got = set(params.keys())    
        extra = got - expected
        missing = expected - got
        if extra:
            raise ValueError(f"Unexpected params: {sorted(extra)}")
        if missing:
            raise ValueError(f"Missing params: {sorted(missing)}")
        # passes params through on neither

    with conn.cursor() as cur:
        cur.execute(sql, params)
        if cur.description is None:
            return [], []       # nothing to display
        # (Alternative: could return None or raise, but ([], []) makes printing logic easy later.)
        headers = [d.name for d in cur.description]
        rows = cur.fetchall()
        return headers, rows


def cmd_print(conn, sql_file: str, title: str):
    """Read `.sql`, run a query, then print its table."""
    sql = read_sql(sql_file)
    headers, rows = run_query(conn, sql)
    if headers == []:          # nothing to display, print nothing
        return
    print()
    print(f"== {title} ==")
    print(render_table(headers, rows))


def main(argv: list[str] | None = None) -> int:
    """
    Two modes for main():
        Normal CLI mode: 
            - run `python -m order_metrics.cli monthly` OR `order-metrics monthly`
            - argv -> None
            - argparse reads from the real command line: `sys.argv[1:]`
        Programmatic mode:
            - call: main(["monthly"])
            - argparse parses that list isdted of the real shell args.
            - handy for unit tests because it avoids subprocess.
            - Can reuse the CLI from another Python script.

    Some example usage:
        To query for top-products: `python -m order_metrics.cli top-products`
        To query all avalible:     `python -m order_metrics.cli all`

    """

    p = argparse.ArgumentParser(prog="order-metrics")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("monthly", help="Monthly paid_orders / paid_users / paid_revenue")
    sub.add_parser("country", help="Country breakdown")
    sub.add_parser("top-products", help="Top products by item revenue")
    sub.add_parser("all", help="Print all reports")

    args = p.parse_args(argv)

    cfg = load_db_config()
    with connect(cfg) as conn:
        if args.cmd == "all":
            keys = ORDER
        else:
            keys = [args.cmd]
        for k in keys:
            sql_file, title = REPORTS[k]        # fetches sql AND predefined title! (0, 1)
            cmd_print(conn, sql_file, title)    # put in executor
        conn.rollback()  # CLI is read-only. rollback any accidental changes

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
