from __future__ import annotations

from datetime import datetime

from inventario.data.database import Database


class InventoryRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def get_inventory(self, search: str | None = None):
        query = "SELECT * FROM inventory"
        params: tuple = ()
        if search:
            query += " WHERE sku LIKE ? OR COALESCE(descripcion,'') LIKE ?"
            token = f"%{search}%"
            params = (token, token)
        query += " ORDER BY sku"
        with self.db.connect() as conn:
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    def get_stock(self, sku: str) -> int | None:
        with self.db.connect() as conn:
            row = conn.execute("SELECT stock FROM inventory WHERE sku=?", (sku,)).fetchone()
            return None if row is None else int(row["stock"])

    def upsert_sku(self, sku: str, now_iso: str) -> None:
        with self.db.connect() as conn:
            conn.execute(
                """
                INSERT INTO inventory(sku, stock, created_at, updated_at)
                VALUES (?, 0, ?, ?)
                ON CONFLICT(sku) DO UPDATE SET updated_at=excluded.updated_at
                """,
                (sku, now_iso, now_iso),
            )

    def update_stock(self, sku: str, new_stock: int, now_iso: str) -> None:
        with self.db.connect() as conn:
            conn.execute(
                "UPDATE inventory SET stock=?, updated_at=? WHERE sku=?",
                (new_stock, now_iso, sku),
            )


class MovementRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def insert_movement(
        self,
        sku: str,
        movement_type: str,
        quantity: int,
        timestamp_iso: str,
        notes: str | None,
        motivo_ajuste: str | None = None,
        location_from: str | None = None,
        location_to: str | None = None,
    ) -> int:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO movements(sku, movement_type, quantity, timestamp, notes, motivo_ajuste, location_from, location_to)
                VALUES(?,?,?,?,?,?,?,?)
                """,
                (
                    sku,
                    movement_type,
                    quantity,
                    timestamp_iso,
                    notes,
                    motivo_ajuste,
                    location_from,
                    location_to,
                ),
            )
            return int(cur.lastrowid)

    def list_movements(self, sku: str | None = None, movement_type: str | None = None):
        clauses = []
        params = []
        if sku:
            clauses.append("sku = ?")
            params.append(sku)
        if movement_type:
            clauses.append("movement_type = ?")
            params.append(movement_type)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.db.connect() as conn:
            return [
                dict(r)
                for r in conn.execute(
                    f"SELECT * FROM movements {where} ORDER BY timestamp DESC, id DESC", params
                ).fetchall()
            ]


class ImportEntryRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def insert_entry(
        self,
        movement_id: int,
        sku: str,
        quantity: int,
        costo_mercancia: float,
        costo_pedimento: float,
        gastos_aduanales: float,
        costo_total_entrada: float,
        timestamp_iso: str,
    ) -> None:
        with self.db.connect() as conn:
            conn.execute(
                """
                INSERT INTO import_entries(
                    movement_id, sku, quantity, costo_mercancia, costo_pedimento,
                    gastos_aduanales, costo_total_entrada, timestamp
                ) VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    movement_id,
                    sku,
                    quantity,
                    costo_mercancia,
                    costo_pedimento,
                    gastos_aduanales,
                    costo_total_entrada,
                    timestamp_iso,
                ),
            )

    def list_entries(self):
        with self.db.connect() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM import_entries ORDER BY timestamp DESC").fetchall()]


class SettingsRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, key: str, default: str | None = None) -> str | None:
        with self.db.connect() as conn:
            row = conn.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
            return default if row is None else str(row["value"])

    def set(self, key: str, value: str) -> None:
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO app_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )
