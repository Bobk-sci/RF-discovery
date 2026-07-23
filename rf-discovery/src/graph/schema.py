"""Création et ouverture de la base DuckDB (§6)."""
from __future__ import annotations

from pathlib import Path

import duckdb

_SCHEMA_SQL = Path(__file__).resolve().parents[2] / "sql" / "schema.sql"


def connect(db_path: str | Path) -> duckdb.DuckDBPyConnection:
    """Ouvre (ou crée) la base et garantit la présence du schéma."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(path))
    con.execute(_SCHEMA_SQL.read_text(encoding="utf-8"))
    return con


def init_empty(db_path: str | Path) -> None:
    """Initialise une base vide avec le schéma complet (jalon M0)."""
    con = connect(db_path)
    con.close()


if __name__ == "__main__":  # pragma: no cover - utilitaire de build
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "data/graph.duckdb"
    init_empty(target)
    print(f"Base initialisée : {target}")
