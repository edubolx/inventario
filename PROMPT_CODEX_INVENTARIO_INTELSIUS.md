# Prompt final para Codex — Inventario_Intelsius

Usa el siguiente prompt exacto en Codex para generar el proyecto completo:

---

**PROMPT START**

Design and generate a complete minimal local inventory management application in Python with the following requirements.

## Project identity
- Project name: `Inventario_Intelsius`
- Main language for UI and messages: Spanish
- Target OS for run instructions: Windows

## General objective
Create a lightweight, single-user, local inventory system that runs on a personal computer. The system must be simple, maintainable, and not over-engineered.

## Tech stack
- Python 3.11+
- Streamlit for the user interface
- SQLite as the local database
- Optional Google Sheets synchronization as a mirror view
- No authentication
- No external backend services
- No cloud dependencies required for core operation

## Architecture requirements
Use a clean, minimal structure with explicit separation of:
1. UI layer
2. Business logic layer
3. Data access layer

Keep code modular and readable, with practical abstractions only.

## Functional requirements
Support these movement types:
- Entrada importacion
- Renta salida
- Renta retorno
- Venta
- Prestamo salida
- Prestamo retorno
- Transferencia
- Ajuste

Business rules:
1. Stock must NEVER go negative.
2. If a SKU does not exist, auto-create it only on entry-type movements.
3. Single user only.
4. Main scope: one warehouse, plus real-world external locations represented through movement types (e.g., casa/cliente) without full multi-warehouse complexity.
5. No multiple inventory states.
6. Kardex (movement history) must always be stored in DB, but can be hidden in UI.
7. Stock must be updated immediately on each movement.
8. Transferencia must create two internal records:
   - one negative movement
   - one positive movement
9. Quantity must be integer only (no decimals).
10. Ajuste must always require a mandatory reason (`motivo`).

Entry-type movements for SKU auto-creation:
- Entrada importacion
- Renta retorno
- Prestamo retorno
- Ajuste (only if positive)
- Positive side of Transferencia

## Importation cost requirements (Mexico context)
When movement type is `Entrada importacion`, capture and store cost details for inventory entry including:
- costo_mercancia
- costo_pedimento
- gastos_aduanales
- costo_total_entrada (calculated or stored consistently)

These fields must be persisted and available for reports/export/sync.

## Database design
Create SQLite tables (you may add practical extra columns like unique constraints and audit timestamps):

### Table: inventory
- id
- sku (unique)
- descripcion (optional but recommended)
- categoria (optional)
- unidad_medida (optional)
- stock (integer)
- created_at
- updated_at

### Table: movements
- id
- sku
- movement_type
- quantity (integer)
- timestamp (timezone-aware display, stored safely)
- notes
- motivo_ajuste (required only for Ajuste)
- location_from (optional, for traceability)
- location_to (optional, for traceability)

### Table: import_entries
- id
- movement_id (FK to movements)
- sku
- quantity
- costo_mercancia
- costo_pedimento
- gastos_aduanales
- costo_total_entrada
- timestamp

## Interface requirements (Streamlit)
Provide a simple Spanish UI with at least these pages:

### Page 1: Resumen de inventario
- Table with current stock per SKU
- Search/filter
- Low-stock friendly visibility (simple highlight optional)

### Page 2: Registrar movimiento
Form fields:
- Tipo de movimiento (select)
- SKU
- Cantidad (integer)
- Notas
- Motivo (mandatory for Ajuste)
- Extra fields for Entrada importacion:
  - costo_mercancia
  - costo_pedimento
  - gastos_aduanales

Validation:
- Prevent negative resulting stock with a clear Spanish error message.
- Enforce integer quantity.
- Enforce required motivo for Ajuste.

### Page 3 (optional but recommended): Kardex
- Chronological movement history
- Filters by SKU, movement type, date range
- Visibility toggle in UI (show/hide kardex module)

### Page 4 (optional but recommended): Configuración y sincronización
- Toggle sync mode: `manual` or `automatico`
- If manual: button "Sincronizar ahora"
- If automatic: trigger sync after successful movement registration

## Timezone and datetime
- Display times in `America/Mexico_City` (CDMX)
- Keep internal consistency in storage (document chosen strategy)

## Google Sheets sync (optional module)
Implement optional synchronization using service account credentials file (not hardcoded):
- Push inventory snapshot to sheet: `Inventario`
- Push movements table to sheet: `Movimientos`
- Push importation entries/cost table to sheet: `Entradas_Importacion`

Requirements:
- Do NOT hardcode credentials.
- Provide placeholders and setup instructions.
- Sync failures must not break core local operation.

## Export requirements
From UI, support local exports:
- CSV export for inventory
- CSV export for movements
- CSV export for import entries
- If easy to add cleanly, include Excel export too.

## Code quality
- Use classes for business logic/services.
- Use functions/repositories for DB operations.
- Include basic error handling and clear Spanish user messages.
- Add concise comments/docstrings to explain structure.
- Keep code minimal and clean.
- Avoid unnecessary abstractions, microservices, and complex DI.

## Deliverables
Generate all of the following:
1. Full project structure
2. All Python files
3. `requirements.txt`
4. `.env.example` (if config is needed)
5. SQL initialization/migration strategy (simple)
6. `README.md` with Windows-first run instructions
7. Example service-account setup steps for Google Sheets sync
8. Basic tests for critical rules (negative stock prevention, SKU auto-creation, transferencia double record, ajuste motivo required)

## Constraints
- Lightweight local business tool.
- No authentication system.
- No cloud dependency for core usage.
- Keep naming, UI labels, and validations in Spanish.

**PROMPT END**

---

Sugerencia: pégalo en una sesión nueva de Codex para obtener una generación limpia del proyecto completo.
