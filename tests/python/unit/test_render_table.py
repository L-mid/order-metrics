from __future__ import annotations

import pytest

from order_metrics.render import render_table


def test_render_table_output_not_empty():
    out = render_table(["a"], [[1], [2]])
    assert out.strip() != ""
    assert "a" in out  # header present

def test_render_table_golden():
    """`assert out == expected`, exactly"""
    out = render_table(["id", "name"], [[1, "Al"], [22, "Bob"]])
    expected = (
        "id | name\n"
        "---+-----\n"
        "1  | Al  \n"
        "22 | Bob "
    )
    assert out == expected


def test_render_table_width_alignment():
    # col1 must widen to fit "2222"
    out = render_table(["id", "name"], [[1, "Al"], [2222, "Bob"]])
    lines = out.splitlines()

    # For every line that contains a column separator '|',
    # record the character index of the first '|'.
    pipe_idxs = [ln.index("|") for ln in lines if "|" in ln]

    # Expecting at least header + one data row to contain '|'
    # (otherwise this alignment test would be meaningless).
    assert len(pipe_idxs) >= 2
    # If columns are aligned, the first '|' appears in the same position on every line.
    assert len(set(pipe_idxs)) == 1, pipe_idxs      # all pipe positions are identical (set dedupes)


def test_render_table_stringifies_common_containers():
    out = render_table(["x", "y", "z"], [[[1, 2], (3, 4), {}]])
    assert "[1, 2]" in out
    assert "(3, 4)" in out
    assert "{}" in out


def test_render_table_raises_if_str_raises():
    # example: a custom class that raises on becoming a string.
    class Bad:
        def __str__(self) -> str:
            raise RuntimeError("nope")

    with pytest.raises(RuntimeError, match="nope"):
        render_table(["x"], [[Bad()]])