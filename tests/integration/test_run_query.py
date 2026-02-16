import psycopg
import pytest

from order_metrics.cli import run_query 

def _setup_temp_table(mock_connect):
    """
    Two executions:
    - Makes an entirely mock table (called t).
    - Inserts two rows into t.
    Expects to be cleaned up and reinstansiated every new call.
    """
    with mock_connect.cursor() as cur:
        cur.execute("CREATE TEMP TABLE t (k text, v int);")
        cur.execute("INSERT INTO t (k, v) VALUES ('GB', 2), ('CA', 1);")


## -- happy path

def test_run_query_golden_headers_and_rows(mock_connect):
    _setup_temp_table(mock_connect)
    sql = "SELECT k, v FROM t ORDER BY v DESC, k;"
    headers, rows = run_query(mock_connect, sql)
    assert headers == ["k", "v"]
    assert rows == [("GB", 2), ("CA", 1)]

def test_run_query_golden_headers_and_rows_with_params(mock_connect):
    _setup_temp_table(mock_connect)
    sql = "SELECT k, v FROM t WHERE k = %(k)s ORDER BY v DESC, k;"
    headers, rows = run_query(mock_connect, sql, {"k": "GB"})
    assert headers == ["k", "v"]
    assert rows == [("GB", 2)]

def test_run_query_good_sql(mock_connect):
    _setup_temp_table(mock_connect)
    headers, rows = run_query(mock_connect, "SELECT k, v FROM t ORDER BY v DESC, k;")
    assert isinstance(headers, list)
    assert isinstance(rows, list)
    assert headers != []
    assert rows != []


## -- empty case & errors

def test_run_query_empty_statement_returns_empty_tuple(mock_connect):
    headers, rows = run_query(mock_connect, "CREATE TEMP TABLE x (a int);")     # creates own tmp table.
    assert (headers, rows) == ([], [])  # always tuple, never None

def test_run_query_invalid_sql_raises(mock_connect):
    with pytest.raises(psycopg.Error):
        run_query(mock_connect, "SELEC 1;")  # syntax error


## -- bad params

def test_run_query_bad_params_type_raises(mock_connect):
    with pytest.raises(TypeError):
        run_query(mock_connect, "SELECT 1;", params=["nope"])  # type: ignore[arg-type]

def test_run_query_unexpected_param_key_raises(mock_connect):
    with pytest.raises(ValueError, match="Unexpected params"):
        run_query(mock_connect, "SELECT 1;", {"x": 1})

def test_run_query_missing_param_key_raises(mock_connect):
    # params should never be an empty {} if provided
    with pytest.raises(ValueError, match="Missing params"):
        run_query(mock_connect, "SELECT %(x)s::int;", {})


