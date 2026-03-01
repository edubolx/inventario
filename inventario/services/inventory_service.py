from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from inventario.data.repositories import ImportEntryRepository, InventoryRepository, MovementRepository

MOVEMENT_TYPES = [
    "Entrada importacion",
    "Renta salida",
    "Renta retorno",
    "Venta",
    "Prestamo salida",
    "Prestamo retorno",
    "Transferencia",
    "Ajuste",
]


class InventoryError(ValueError):
    pass


@dataclass
class ImportCosts:
    costo_mercancia: float
    costo_pedimento: float
    gastos_aduanales: float

    @property
    def total(self) -> float:
        return float(self.costo_mercancia + self.costo_pedimento + self.gastos_aduanales)


class InventoryService:
    def __init__(
        self,
        inventory_repo: InventoryRepository,
        movement_repo: MovementRepository,
        import_entry_repo: ImportEntryRepository,
        timezone: ZoneInfo,
    ) -> None:
        self.inventory_repo = inventory_repo
        self.movement_repo = movement_repo
        self.import_entry_repo = import_entry_repo
        self.timezone = timezone

    def now_iso(self) -> str:
        return datetime.now(self.timezone).isoformat()

    def _normalized_sku(self, sku: str) -> str:
        val = sku.strip().upper()
        if not val:
            raise InventoryError("El SKU es obligatorio.")
        return val

    def _is_entry_type(self, movement_type: str, quantity: int) -> bool:
        return movement_type in {"Entrada importacion", "Renta retorno", "Prestamo retorno"} or (
            movement_type == "Ajuste" and quantity > 0
        )

    def _apply_stock(self, sku: str, delta: int) -> int:
        current_stock = self.inventory_repo.get_stock(sku)
        if current_stock is None:
            current_stock = 0
        new_stock = current_stock + delta
        if new_stock < 0:
            raise InventoryError(f"Stock insuficiente para SKU {sku}. Stock actual: {current_stock}.")
        self.inventory_repo.update_stock(sku, new_stock, self.now_iso())
        return new_stock

    def register_movement(
        self,
        movement_type: str,
        sku: str,
        quantity: int,
        notes: str | None = None,
        motivo_ajuste: str | None = None,
        adjustment_sign: int = 1,
        location_from: str | None = None,
        location_to: str | None = None,
        import_costs: ImportCosts | None = None,
    ) -> None:
        if movement_type not in MOVEMENT_TYPES:
            raise InventoryError("Tipo de movimiento no válido.")
        if not isinstance(quantity, int) or quantity <= 0:
            raise InventoryError("La cantidad debe ser un entero mayor a 0.")

        sku = self._normalized_sku(sku)
        now_iso = self.now_iso()
        stock_exists = self.inventory_repo.get_stock(sku) is not None

        if movement_type == "Ajuste" and not (motivo_ajuste or "").strip():
            raise InventoryError("El motivo del ajuste es obligatorio.")

        is_entry = self._is_entry_type(movement_type, quantity * adjustment_sign)
        if not stock_exists and (is_entry or movement_type == "Transferencia"):
            self.inventory_repo.upsert_sku(sku, now_iso)
            stock_exists = True

        if not stock_exists:
            raise InventoryError("El SKU no existe. Debes crear una entrada primero.")

        if movement_type == "Transferencia":
            out_id = self.movement_repo.insert_movement(
                sku=sku,
                movement_type=movement_type,
                quantity=-quantity,
                timestamp_iso=now_iso,
                notes=notes,
                location_from=location_from or "Almacén",
                location_to=location_to or "Casa/Cliente",
            )
            self._apply_stock(sku, -quantity)
            self.movement_repo.insert_movement(
                sku=sku,
                movement_type=movement_type,
                quantity=quantity,
                timestamp_iso=now_iso,
                notes=f"Par de transferencia #{out_id}",
                location_from=location_from or "Almacén",
                location_to=location_to or "Casa/Cliente",
            )
            self._apply_stock(sku, quantity)
            return

        if movement_type in {"Renta salida", "Venta", "Prestamo salida"}:
            delta = -quantity
        elif movement_type in {"Renta retorno", "Prestamo retorno", "Entrada importacion"}:
            delta = quantity
        elif movement_type == "Ajuste":
            delta = quantity * adjustment_sign
        else:
            raise InventoryError("Movimiento no soportado.")

        movement_id = self.movement_repo.insert_movement(
            sku=sku,
            movement_type=movement_type,
            quantity=delta,
            timestamp_iso=now_iso,
            notes=notes,
            motivo_ajuste=motivo_ajuste,
            location_from=location_from,
            location_to=location_to,
        )
        self._apply_stock(sku, delta)

        if movement_type == "Entrada importacion":
            if import_costs is None:
                raise InventoryError("Debes capturar los costos de importación.")
            self.import_entry_repo.insert_entry(
                movement_id=movement_id,
                sku=sku,
                quantity=quantity,
                costo_mercancia=import_costs.costo_mercancia,
                costo_pedimento=import_costs.costo_pedimento,
                gastos_aduanales=import_costs.gastos_aduanales,
                costo_total_entrada=import_costs.total,
                timestamp_iso=now_iso,
            )
