from pathlib import Path
import psycopg
import pytest

import order_metrics.cli as cli  


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


def _patch_read_sql(monkeypatch):
    """
    `read_sql` has innate custom path restrictions.
    They're replaced here so this test can read from the tmp_file created. 
    """
    monkeypatch.setattr(cli, "read_sql", lambda fp: Path(fp).read_text(encoding="utf-8"))


## -- happy path
def test_cmd_print_golden_stdout(mock_connect, tmp_path, monkeypatch, capsys):
    _setup_temp_table(mock_connect)
    p = tmp_path / "q.sql"
    p.write_text("SELECT k, v FROM t ORDER BY v DESC, k;", encoding="utf-8")
    sql_file = str(p)
    _patch_read_sql(monkeypatch)
    cli.cmd_print(mock_connect, sql_file, "Example Title")
    out = capsys.readouterr().out

    expected = (
        "\n"
        "== Example Title ==\n"
        "k  | v\n"
        "---+--\n"
        "GB | 2\n"
        "CA | 1\n"
    )
    assert out == expected

def test_cmd_print_stdout_exists_on_good_sql(mock_connect, tmp_path, monkeypatch, capsys):
    _setup_temp_table(mock_connect)
    p = tmp_path / "q.sql"
    p.write_text("SELECT k, v FROM t ORDER BY v DESC, k;", encoding="utf-8")
    sql_file = str(p)
    _patch_read_sql(monkeypatch)
    cli.cmd_print(mock_connect, sql_file, "Example Title")
    out = capsys.readouterr().out
    assert "== Example Title ==" in out
    assert "k" in out and "v" in out


## -- invalid cases
def test_cmd_print_bad_path_fails_from_read_sql(mock_connect, tmp_path, monkeypatch):
    _patch_read_sql(monkeypatch)
    missing = tmp_path / "missing.sql"      # make read_sql be a pure path read (read_sql should fail on a pure path)
    with pytest.raises(FileNotFoundError):
        cli.cmd_print(mock_connect, str(missing), "Example Title")

def test_cmd_print_invalid_sql_fails_from_run_query(mock_connect, tmp_path, monkeypatch):
    p = tmp_path / "bad.sql"
    p.write_text("SELEC 1;", encoding="utf-8")
    _patch_read_sql(monkeypatch)
    with pytest.raises(psycopg.Error):
        cli.cmd_print(mock_connect, str(p), "Bad")


## -- empty
def test_cmd_print_empty_result_prints_nothing(mock_connect, tmp_path, monkeypatch, capsys):
    p = tmp_path / "ddl.sql"
    p.write_text("CREATE TEMP TABLE z (a int);", encoding="utf-8")
    _patch_read_sql(monkeypatch)
    cli.cmd_print(mock_connect, str(p), "DDL")
    out = capsys.readouterr().out
    assert out == ""
