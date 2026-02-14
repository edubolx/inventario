from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from inventario.data.repositories import ImportEntryRepository, InventoryRepository, MovementRepository, SettingsRepository
from inventario.services.inventory_service import ImportCosts, InventoryError, MOVEMENT_TYPES, InventoryService
from inventario.sync.google_sheets import GoogleSheetsSync


def _as_df(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def render_app(
    service: InventoryService,
    inventory_repo: InventoryRepository,
    movement_repo: MovementRepository,
    import_repo: ImportEntryRepository,
    settings_repo: SettingsRepository,
    sheet_sync: GoogleSheetsSync,
) -> None:
    st.set_page_config(page_title="Inventario Intelsius", layout="wide")
    st.title("Inventario_Intelsius")

    page = st.sidebar.radio("Menú", ["Resumen de inventario", "Registrar movimiento", "Kardex", "Configuración"])

    if page == "Resumen de inventario":
        search = st.text_input("Buscar SKU o descripción")
        rows = inventory_repo.get_inventory(search)
        df = _as_df(rows)
        st.dataframe(df, use_container_width=True)
        if not df.empty:
            st.download_button(
                "Exportar inventario CSV",
                df.to_csv(index=False).encode("utf-8"),
                file_name="inventario.csv",
                mime="text/csv",
            )

    if page == "Registrar movimiento":
        with st.form("mov_form"):
            col1, col2 = st.columns(2)
            movement_type = col1.selectbox("Tipo de movimiento", MOVEMENT_TYPES)
            sku = col2.text_input("SKU")
            quantity = st.number_input("Cantidad", min_value=1, step=1, value=1)
            notes = st.text_area("Notas")

            motivo_ajuste = None
            adjustment_sign = 1
            if movement_type == "Ajuste":
                motivo_ajuste = st.text_input("Motivo del ajuste (obligatorio)")
                direction = st.selectbox("Dirección del ajuste", ["Incrementar", "Reducir"])
                adjustment_sign = 1 if direction == "Incrementar" else -1

            location_from, location_to = None, None
            if movement_type == "Transferencia":
                location_from = st.text_input("Ubicación origen", value="Almacén")
                location_to = st.text_input("Ubicación destino", value="Casa/Cliente")

            import_costs = None
            if movement_type == "Entrada importacion":
                c1, c2, c3 = st.columns(3)
                costo_mercancia = c1.number_input("Costo mercancía", min_value=0.0, value=0.0, step=1.0)
                costo_pedimento = c2.number_input("Costo pedimento", min_value=0.0, value=0.0, step=1.0)
                gastos_aduanales = c3.number_input("Gastos aduanales", min_value=0.0, value=0.0, step=1.0)
                import_costs = ImportCosts(costo_mercancia, costo_pedimento, gastos_aduanales)

            submitted = st.form_submit_button("Registrar")

        if submitted:
            try:
                service.register_movement(
                    movement_type=movement_type,
                    sku=sku,
                    quantity=int(quantity),
                    notes=notes,
                    motivo_ajuste=motivo_ajuste,
                    adjustment_sign=adjustment_sign,
                    location_from=location_from,
                    location_to=location_to,
                    import_costs=import_costs,
                )
                st.success("Movimiento registrado correctamente.")
                if settings_repo.get("sync_mode", "manual") == "automatico":
                    msg = sheet_sync.push_all(
                        inventory_repo.get_inventory(), movement_repo.list_movements(), import_repo.list_entries()
                    )
                    st.info(msg)
            except InventoryError as exc:
                st.error(str(exc))

    if page == "Kardex":
        visible = settings_repo.get("kardex_visible", "1") == "1"
        if not visible:
            st.warning("Kardex oculto. Actívalo en Configuración.")
            return

        sku_filter = st.text_input("Filtrar por SKU")
        type_filter = st.selectbox("Filtrar por tipo", ["Todos"] + MOVEMENT_TYPES)
        selected_type = None if type_filter == "Todos" else type_filter
        rows = movement_repo.list_movements(sku_filter.strip().upper() or None, selected_type)

        for r in rows:
            try:
                dt = datetime.fromisoformat(r["timestamp"]).astimezone(service.timezone)
                r["timestamp"] = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass

        df = _as_df(rows)
        st.dataframe(df, use_container_width=True)
        if not df.empty:
            st.download_button(
                "Exportar movimientos CSV",
                df.to_csv(index=False).encode("utf-8"),
                file_name="movimientos.csv",
                mime="text/csv",
            )

        import_df = _as_df(import_repo.list_entries())
        st.subheader("Entradas por importación")
        st.dataframe(import_df, use_container_width=True)
        if not import_df.empty:
            st.download_button(
                "Exportar entradas importación CSV",
                import_df.to_csv(index=False).encode("utf-8"),
                file_name="entradas_importacion.csv",
                mime="text/csv",
            )

    if page == "Configuración":
        st.subheader("Sincronización con Google Sheets")
        current_mode = settings_repo.get("sync_mode", "manual")
        mode = st.radio("Modo de sincronización", ["manual", "automatico"], index=0 if current_mode == "manual" else 1)
        if st.button("Guardar modo"):
            settings_repo.set("sync_mode", mode)
            st.success("Modo guardado")

        kardex_visible = settings_repo.get("kardex_visible", "1") == "1"
        show_kardex = st.checkbox("Mostrar Kardex en UI", value=kardex_visible)
        if st.button("Guardar visibilidad Kardex"):
            settings_repo.set("kardex_visible", "1" if show_kardex else "0")
            st.success("Visibilidad actualizada")

        if st.button("Sincronizar ahora"):
            msg = sheet_sync.push_all(inventory_repo.get_inventory(), movement_repo.list_movements(), import_repo.list_entries())
            st.info(msg)
