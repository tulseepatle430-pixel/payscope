"""SQLAlchemy engine factory for the Postgres analytics database."""
from __future__ import annotations

from sqlalchemy import Engine, create_engine

from config.settings import sqlalchemy_url

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(sqlalchemy_url(), pool_pre_ping=True)
    return _engine
