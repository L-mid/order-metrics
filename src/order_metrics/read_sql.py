"""
SQL-related things here.

Eventually maybe:
- templating, query registry, validation helpers.
"""

from __future__ import annotations

from importlib import resources
from pathlib import PurePosixPath


def read_sql(rel_path: str) -> str:
    """
    Treat SQL paths as package-relative POSIX paths (stable across OSes)
    - `resources.files` used for representing installed package contents.
    - `joinpath` moves into the `order_metrics/sql/ directory` inside the package.
    """
    rp = PurePosixPath(rel_path)
    if rp.is_absolute() or ".." in rp.parts:
        raise ValueError("SQL path must be relative and must not contain '..'")
    
    base = resources.files("order_metrics").joinpath("sql")
    file = base.joinpath(*rp.parts)
    try:
        return file.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"SQL not found: order_metrics/sql/{rel_path}")
    
