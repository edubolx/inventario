from __future__ import annotations

from typing import Iterable


class GoogleSheetsSync:
    def __init__(self, credentials_path: str | None, spreadsheet_id: str | None) -> None:
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id

    def enabled(self) -> bool:
        return bool(self.credentials_path and self.spreadsheet_id)

    def push_all(self, inventory_rows: Iterable[dict], movement_rows: Iterable[dict], import_rows: Iterable[dict]) -> str:
        if not self.enabled():
            return "Sincronización omitida: configura GOOGLE_SERVICE_ACCOUNT_FILE y GOOGLE_SPREADSHEET_ID."

        try:
            import gspread
            from google.oauth2.service_account import Credentials
        except Exception as exc:  # pragma: no cover
            return f"Sincronización no disponible: faltan dependencias ({exc})."

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(self.credentials_path, scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(self.spreadsheet_id)

        self._write_sheet(sh, "Inventario", list(inventory_rows))
        self._write_sheet(sh, "Movimientos", list(movement_rows))
        self._write_sheet(sh, "Entradas_Importacion", list(import_rows))
        return "Sincronización completada correctamente."

    def _write_sheet(self, spreadsheet, tab_name: str, rows: list[dict]) -> None:
        worksheet = None
        try:
            worksheet = spreadsheet.worksheet(tab_name)
        except Exception:
            worksheet = spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=20)

        if not rows:
            worksheet.clear()
            worksheet.update("A1", [["sin_datos"]])
            return

        headers = list(rows[0].keys())
        matrix = [headers] + [[str(row.get(h, "")) for h in headers] for row in rows]
        worksheet.clear()
        worksheet.update("A1", matrix)
