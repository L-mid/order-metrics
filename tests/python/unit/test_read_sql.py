"""
SQL Reader.
- can read a known file
- errors on absolute paths
- errors on `..` as paths
- missing file gives custom error.
"""

import pytest 

from order_metrics.read_sql import read_sql  

def test_read_sql_reads_existing_file():
    """
    SQL file `monthly_paid_metrics.sql`, 
    from absolute path `src/order_metrics/sql/monthly_paid_revenue.sql`.
    """
    # from base SQL directory
    text = read_sql("monthly_paid_metrics.sql")
    assert isinstance(text, str)
    assert len(text) > 0

    # nesting inside SQL (checks dir):
    text = read_sql("checks/check_no_join_fanout_revenue.sql")     # existing example
    assert isinstance(text, str)
    assert len(text) > 0


def test_read_sql_rejects_absolute_path():
    with pytest.raises(ValueError, match="must be relative"):
        read_sql("/etc/passwd")  # any absolute-style path

def test_read_sql_rejects_dotdot_traversal():
    with pytest.raises(ValueError, match=r"\.\."):
        read_sql("../secrets.sql")

def test_read_sql_missing_file_raises_nice_error():
    with pytest.raises(FileNotFoundError, match="SQL not found: order_metrics/sql/nope.sql"):
        read_sql("nope.sql")