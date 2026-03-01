from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=True)


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None:
        value = os.getenv(f"\ufeff{name}")
    if value is None:
        return default
    value = value.strip()
    return value or default


@dataclass(frozen=True)
class AppConfig:
    db_path: str = _env("INVENTARIO_DB_PATH", "inventario.db") or "inventario.db"
    timezone: ZoneInfo = ZoneInfo("America/Mexico_City")
    google_credentials_path: str | None = _env("GOOGLE_SERVICE_ACCOUNT_FILE")
    google_spreadsheet_id: str | None = _env("GOOGLE_SPREADSHEET_ID")


CONFIG = AppConfig()
