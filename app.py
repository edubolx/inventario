from inventario.config import CONFIG
from inventario.data.database import Database
from inventario.data.repositories import ImportEntryRepository, InventoryRepository, MovementRepository, SettingsRepository
from inventario.services.inventory_service import InventoryService
from inventario.sync.google_sheets import GoogleSheetsSync
from inventario.ui.app_ui import render_app


def main() -> None:
    db = Database(CONFIG.db_path)
    db.initialize()

    inventory_repo = InventoryRepository(db)
    movement_repo = MovementRepository(db)
    import_repo = ImportEntryRepository(db)
    settings_repo = SettingsRepository(db)

    service = InventoryService(
        inventory_repo=inventory_repo,
        movement_repo=movement_repo,
        import_entry_repo=import_repo,
        timezone=CONFIG.timezone,
    )

    sync_client = GoogleSheetsSync(
        credentials_path=CONFIG.google_credentials_path,
        spreadsheet_id=CONFIG.google_spreadsheet_id,
    )

    render_app(service, inventory_repo, movement_repo, import_repo, settings_repo, sync_client)


if __name__ == "__main__":
    main()
