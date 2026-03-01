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

## Guía rápida desde cero (primer uso)

### 1) Abrir la app
1. Abre una terminal PowerShell dentro de la carpeta del proyecto.
2. Activa el entorno virtual (desde la raíz del proyecto):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   Si aparece el error *"la ejecución de scripts está deshabilitada"*, ejecuta primero (solo para esta terminal):
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```
   y luego vuelve a correr `.\.venv\Scripts\Activate.ps1`.

   Si ya estás dentro de `C:\...\.venv\Scripts>`, entonces ejecuta:
   ```powershell
   .\Activate.ps1
   ```
   (con `./` o `\.\` al inicio; en PowerShell no basta con escribir `Activate.ps1`).
3. **Asegúrate de estar en la raíz del proyecto** (donde existe `app.py`). Si estás en `.venv\Scripts`, regresa con:
   ```powershell
   cd ..\..
   ```
4. Inicia la app:
   ```powershell
   python -m streamlit run app.py
   ```
5. En tu navegador, abre `http://localhost:8501`.

### 2) Conocer el menú lateral
La app tiene 4 secciones principales:
- **Resumen de inventario**: consulta existencias por SKU o descripción.
- **Registrar movimiento**: captura entradas, salidas, ajustes y transferencias.
- **Kardex**: historial de movimientos con filtros y exportaciones.
- **Configuración**: sincronización a Google Sheets y visibilidad del Kardex.

### 3) Registrar tu primer movimiento
1. Entra a **Registrar movimiento**.
2. Selecciona el **Tipo de movimiento**.
3. Escribe el **SKU** (recomendado: usar siempre el mismo formato).
4. Captura la **Cantidad** y agrega **Notas** si aplica.
5. Haz clic en **Registrar**.

Notas según el tipo:
- **Ajuste**: pide motivo obligatorio y si incrementa o reduce.
- **Transferencia**: pide ubicación origen y destino.
- **Entrada importacion**: pide costos (mercancía, pedimento y aduanales).

### 4) Revisar existencias
1. Ve a **Resumen de inventario**.
2. Usa el buscador para filtrar por SKU o descripción.
3. Descarga el reporte con **Exportar inventario CSV**.

### 5) Consultar historial (Kardex)
1. Ve a **Kardex**.
2. Filtra por SKU o por tipo de movimiento.
3. Exporta movimientos o entradas de importación en CSV.

Si no aparece Kardex, habilítalo en **Configuración > Mostrar Kardex en UI**.

### 6) Configurar sincronización (opcional)
En **Configuración** puedes:
- Elegir modo **manual** o **automatico**.
- Ejecutar **Sincronizar ahora** cuando lo necesites.

Para usar Google Sheets, agrega en `.env`:
- `GOOGLE_SERVICE_ACCOUNT_FILE`
- `GOOGLE_SPREADSHEET_ID`

> ⚠️ **Importante:** las variables van en el archivo **`.env`** (en la raíz del proyecto), **no** en `.venv`.

### 6.1) Activar sincronización paso a paso
1. Verifica que exista un archivo `.env` en la raíz del proyecto (misma carpeta que `app.py`).
2. Asegúrate de tener estas 2 líneas:
   ```env
   GOOGLE_SERVICE_ACCOUNT_FILE=./credentials/google-service-account.json
   GOOGLE_SPREADSHEET_ID=tu_spreadsheet_id
   ```
3. Confirma que el archivo JSON de la service account exista en la ruta indicada.
4. Comparte tu Google Sheet con el correo de la service account (permiso Editor).
5. Reinicia la app (`Ctrl + C` y luego `python -m streamlit run app.py`).
6. En la app, entra a **Configuración**:
   - Debe aparecer: **"Google Sheets configurado correctamente."**
   - Elige modo **manual** o **automatico** y guarda.
   - Haz clic en **Sincronizar ahora** para probar.

Si la configuración está bien, verás datos en las pestañas del spreadsheet: `Inventario`, `Movimientos` y `Entradas_Importacion`.

### 7) Cerrar y volver a abrir sin perder datos
- Tus datos se guardan en SQLite local (`inventario.db`).
- Para cerrar, detén Streamlit con `Ctrl + C` en la terminal.
- Para volver a entrar, repite el comando `python -m streamlit run app.py`.

## Solución rápida de problemas en Windows
- **¿"Attempting uninstall" durante `pip install`?**
  Sí, es normal. `pip` puede desinstalar versiones previas para instalar las compatibles con `requirements.txt`.
- **¿`streamlit` no se reconoce como comando?**
  Ejecuta la app con:
  ```powershell
  python -m streamlit run app.py
  ```
  Así no dependes de que el directorio `Scripts` esté en `PATH`.
- **¿Error: "Activate.ps1 no se reconoce"?**
  En PowerShell debes incluir la ruta relativa:
  - Desde la carpeta raíz del proyecto:
    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```
  - Si ya estás dentro de `.venv\Scripts`:
    ```powershell
    .\Activate.ps1
    ```
- **¿Error: "la ejecución de scripts está deshabilitada" (`PSSecurityException`)?**
  En esa misma ventana de PowerShell, habilita scripts de forma temporal:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
  Luego ejecuta de nuevo:
  ```powershell
  .\Activate.ps1
  ```
  Si prefieres no tocar la política de scripts, puedes usar CMD en su lugar:
  ```cmd
  .venv\Scripts\activate.bat
  ```

- **¿Error: "File does not exist: app.py" al ejecutar Streamlit?**
  Estás en la carpeta equivocada (por ejemplo `.venv\Scripts`). Debes ejecutar Streamlit desde la raíz del proyecto:
  ```powershell
  cd C:\Inventario_Intelsius
  python -m streamlit run app.py
  ```
  Si quieres quedarte dentro de `.venv\Scripts`, usa ruta relativa al archivo:
  ```powershell
  python -m streamlit run ..\..\app.py
  ```

- **¿Puse `GOOGLE_SPREADSHEET_ID` en `.venv` y no sincroniza?**
  Muévelo al archivo `.env` en la raíz del proyecto (no dentro de `.venv`).
  Luego reinicia Streamlit y entra a **Configuración > Sincronizar ahora**.

- **¿Sigue saliendo "Sincronización omitida" aunque ya llené `.env`?**
  Revisa estos puntos rápidos:
  1. El archivo se llama exactamente `.env` (no `.env.txt`).
  2. No dejes espacios en blanco antes del nombre de la variable.
  3. Reinicia la app después de guardar `.env`.
  4. Verifica que ambas variables tengan valor:
     - `GOOGLE_SERVICE_ACCOUNT_FILE`
     - `GOOGLE_SPREADSHEET_ID`

## Base de datos
- SQLite local en `inventario.db` (o valor de `INVENTARIO_DB_PATH`).
- Kardex siempre se guarda en DB, pero puede ocultarse en UI.

## Sincronización opcional con Google Sheets
1. Crear Service Account en Google Cloud.
2. Habilitar Google Sheets API.
3. Descargar JSON de credenciales.
4. Crear `.env` (en la raíz del proyecto) basado en `.env.example` con:
   - `GOOGLE_SERVICE_ACCOUNT_FILE`
   - `GOOGLE_SPREADSHEET_ID`
5. Compartir el spreadsheet con el email de la service account.


> La app carga automáticamente las variables del archivo `.env` al iniciar.

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
