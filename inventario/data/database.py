from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    categoria TEXT,
    unidad_medida TEXT,
    stock INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL,
    movement_type TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    notes TEXT,
    motivo_ajuste TEXT,
    location_from TEXT,
    location_to TEXT
);

CREATE TABLE IF NOT EXISTS import_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movement_id INTEGER NOT NULL,
    sku TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    costo_mercancia REAL NOT NULL,
    costo_pedimento REAL NOT NULL,
    gastos_aduanales REAL NOT NULL,
    costo_total_entrada REAL NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY(movement_id) REFERENCES movements(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA_SQL)
            conn.execute(
                "INSERT OR IGNORE INTO app_settings(key, value) VALUES('sync_mode','manual')"
            )
            conn.execute(
                "INSERT OR IGNORE INTO app_settings(key, value) VALUES('kardex_visible','1')"
            )
