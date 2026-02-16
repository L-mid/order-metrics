from __future__ import annotations

import pytest

from order_metrics.db import load_db_config, connect


@pytest.fixture
def mock_connect():
    """
    pytest manages db connection lifecycle itself.
    - privated to prevent shadowing
    - shares connections across tests.
    - guarantee clean up (even on failure)
    - control isolation (transaction rollback)
    """
    cfg = load_db_config()
    with connect(cfg) as conn:
        # (tests can still call commit(), but we rollback at end)
        yield conn
        try:
            conn.rollback()     # important: tests can mutate tables / the db.
        finally:                # roll back any changes.
            pass

