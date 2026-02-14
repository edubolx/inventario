from __future__ import annotations

import os
from dataclasses import dataclass
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class AppConfig:
    db_path: str = os.getenv("INVENTARIO_DB_PATH", "inventario.db")
    timezone: ZoneInfo = ZoneInfo("America/Mexico_City")
    google_credentials_path: str | None = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    google_spreadsheet_id: str | None = os.getenv("GOOGLE_SPREADSHEET_ID")


CONFIG = AppConfig()
