from zoneinfo import ZoneInfo

import pytest

from inventario.data.database import Database
from inventario.data.repositories import ImportEntryRepository, InventoryRepository, MovementRepository
from inventario.services.inventory_service import ImportCosts, InventoryError, InventoryService


@pytest.fixture
def service(tmp_path):
    db = Database(str(tmp_path / "test.db"))
    db.initialize()
    inv = InventoryRepository(db)
    mov = MovementRepository(db)
    imp = ImportEntryRepository(db)
    return InventoryService(inv, mov, imp, ZoneInfo("America/Mexico_City")), inv, mov, imp


def test_prevent_negative_stock(service):
    svc, *_ = service
    with pytest.raises(InventoryError):
        svc.register_movement("Venta", "SKU1", 1)


def test_auto_create_sku_on_entry(service):
    svc, inv, *_ = service
    svc.register_movement(
        "Entrada importacion",
        "sku1",
        5,
        import_costs=ImportCosts(costo_mercancia=100, costo_pedimento=10, gastos_aduanales=20),
    )
    assert inv.get_stock("SKU1") == 5


def test_transfer_creates_two_records(service):
    svc, _, mov, _ = service
    svc.register_movement(
        "Entrada importacion",
        "sku2",
        2,
        import_costs=ImportCosts(costo_mercancia=100, costo_pedimento=10, gastos_aduanales=20),
    )
    svc.register_movement("Transferencia", "sku2", 1)
    transfer_rows = [r for r in mov.list_movements("SKU2", "Transferencia")]
    assert len(transfer_rows) == 2
    assert sorted([r["quantity"] for r in transfer_rows]) == [-1, 1]


def test_ajuste_requires_reason(service):
    svc, *_ = service
    svc.register_movement(
        "Entrada importacion",
        "sku3",
        1,
        import_costs=ImportCosts(costo_mercancia=100, costo_pedimento=10, gastos_aduanales=20),
    )
    with pytest.raises(InventoryError):
        svc.register_movement("Ajuste", "sku3", 1, motivo_ajuste="")
