# Inventario_Intelsius

Aplicación local de inventario (usuario único) con Streamlit + SQLite.

## Requisitos
- Windows 10/11
- Python 3.11+

## Instalación (Windows / PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Ejecutar
> Recomendado: usar `python -m streamlit` para evitar problemas de PATH.

```powershell
python -m streamlit run app.py
```

Abre `http://localhost:8501`.

## Solución rápida de problemas en Windows
- **¿"Attempting uninstall" durante `pip install`?**
  Sí, es normal. `pip` puede desinstalar versiones previas para instalar las compatibles con `requirements.txt`.
- **¿`streamlit` no se reconoce como comando?**
  Ejecuta la app con:
  ```powershell
  python -m streamlit run app.py
  ```
  Así no dependes de que el directorio `Scripts` esté en `PATH`.
- **¿No activaste el entorno virtual?**
  Vuelve a activar antes de ejecutar:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **¿PowerShell bloquea scripts?**
  Ejecuta temporalmente:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```

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
