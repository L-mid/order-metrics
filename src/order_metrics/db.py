from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

import psycopg


@dataclass(frozen=True)
class DbConfig:
    """Frozen, raises error if mutated."""
    dsn: str


def load_db_config() -> DbConfig:
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError("Missing DATABASE_URL env var (e.g. postgres://user:pass@localhost:5432/db)")
    return DbConfig(dsn=dsn)


@contextmanager
def connect(cfg: DbConfig):
    """
    Centralized connector.
    Inits DSN loading/config and the DB connection session.
    - autocommit=False so tests can wrap in transactions and rollback
    - yields `conn` for cleanup after (currently no special logic)
    """
    # <- the connection is closed automatically
    with psycopg.connect(cfg.dsn, autocommit=False) as conn:
        yield conn

