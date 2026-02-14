# Inventario_Intelsius

Aplicación local de inventario (usuario único) con Streamlit + SQLite.

## Requisitos
- Windows 10/11
- Python 3.11+

## Instalación (Windows / PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecutar
```powershell
streamlit run app.py
```
Abre `http://localhost:8501`.

## Base de datos
- SQLite local en `inventario.db` (o valor de `INVENTARIO_DB_PATH`).
- Kardex siempre se guarda en DB, pero puede ocultarse en UI.

## Sincronización opcional con Google Sheets
1. Crear Service Account en Google Cloud.
2. Habilitar Google Sheets API.
3. Descargar JSON de credenciales.
4. Crear `.env` basado en `.env.example` con:
   - `GOOGLE_SERVICE_ACCOUNT_FILE`
   - `GOOGLE_SPREADSHEET_ID`
5. Compartir el spreadsheet con el email de la service account.

La app sincroniza (manual o automático) a las hojas:
- `Inventario`
- `Movimientos`
- `Entradas_Importacion`

Si la sync falla, la operación local de inventario no se detiene.

## Exportaciones
Desde UI puedes exportar a CSV:
- inventario
- movimientos
- entradas de importación

## Pruebas
```bash
pytest -q
```
