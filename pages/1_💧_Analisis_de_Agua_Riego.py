# -*- coding: utf-8 -*-
"""Análisis de calidad de agua de riego (puerto de analisis_agua_riego.html)."""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.water_quality import analizar_agua, EJEMPLOS  # noqa: E402
from shared.ui_common import render_header, render_print_button  # noqa: E402

st.set_page_config(page_title="Análisis de Agua de Riego", page_icon="💧", layout="wide")

DEFAULTS = dict(
    meta_analitica="", meta_finca="", meta_empresa="",
    vol_riego_m3_ha=4000.0, ce_us_cm=950.0, ph=7.5,
    ca_mg_l=80.0, mg_mg_l=24.0, na_mg_l=46.0, k_mg_l=15.0,
    hco3_mg_l=244.0, cl_mg_l=71.0, so4_mg_l=96.0, no3_mg_l=10.0,
    b_mg_l=0.10, fe_mg_l=0.02, mn_mg_l=0.005,
)
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)


def _cargar_ejemplo(nombre: str) -> None:
    for k, v in EJEMPLOS[nombre].items():
        st.session_state[k] = float(v) if isinstance(v, (int, float)) else v


render_header("Análisis de Agua de Riego", "💧")
render_print_button()
st.caption(
    "Criterios FAO-29 (Ayers & Westcot, 1985) para infiltración y toxicidad iónica. "
    "Indicador de obturación calcárea simplificado (no sustituye un índice de "
    "Langelier/Ryznar, que requiere además la temperatura del agua)."
)

with st.sidebar:
    st.subheader("Identificación")
    st.session_state.meta_analitica = st.text_input("Analítica / Referencia", st.session_state.meta_analitica)
    st.session_state.meta_finca = st.text_input("Finca / Parcela", st.session_state.meta_finca)
    st.session_state.meta_empresa = st.text_input("Empresa / Titular", st.session_state.meta_empresa)

    st.subheader("Ejemplos precargados")
    ejemplo = st.selectbox("Cargar un caso de ejemplo:", ["—"] + list(EJEMPLOS.keys()))
    if ejemplo != "—" and st.button("Cargar ejemplo"):
        _cargar_ejemplo(ejemplo)
        st.rerun()

st.subheader("Datos de la analítica")
col1, col2, col3 = st.columns(3)
with col1:
    st.session_state.vol_riego_m3_ha = st.number_input("Volumen de riego (m³/ha)", value=st.session_state.vol_riego_m3_ha, step=100.0)
    st.session_state.ce_us_cm = st.number_input("CE (µS/cm)", value=st.session_state.ce_us_cm, step=10.0)
    st.session_state.ph = st.number_input("pH", value=st.session_state.ph, step=0.1)
with col2:
    st.markdown("**Cationes (mg/L)**")
    st.session_state.ca_mg_l = st.number_input("Calcio (Ca²⁺)", value=st.session_state.ca_mg_l)
    st.session_state.mg_mg_l = st.number_input("Magnesio (Mg²⁺)", value=st.session_state.mg_mg_l)
    st.session_state.na_mg_l = st.number_input("Sodio (Na⁺)", value=st.session_state.na_mg_l)
    st.session_state.k_mg_l = st.number_input("Potasio (K⁺)", value=st.session_state.k_mg_l)
with col3:
    st.markdown("**Aniones (mg/L)**")
    st.session_state.hco3_mg_l = st.number_input("Bicarbonato (HCO₃⁻)", value=st.session_state.hco3_mg_l)
    st.session_state.cl_mg_l = st.number_input("Cloruro (Cl⁻)", value=st.session_state.cl_mg_l)
    st.session_state.so4_mg_l = st.number_input("Sulfato (SO₄²⁻)", value=st.session_state.so4_mg_l)
    st.session_state.no3_mg_l = st.number_input("Nitrato (NO₃⁻)", value=st.session_state.no3_mg_l)

col4, col5 = st.columns(2)
with col4:
    st.session_state.b_mg_l = st.number_input("Boro (B) mg/L", value=st.session_state.b_mg_l, step=0.01, format="%.2f")
with col5:
    st.session_state.fe_mg_l = st.number_input("Hierro (Fe) mg/L", value=st.session_state.fe_mg_l, step=0.01, format="%.3f")

r = analizar_agua(
    vol_riego_m3_ha=st.session_state.vol_riego_m3_ha,
    ce_us_cm=st.session_state.ce_us_cm,
    ph=st.session_state.ph,
    ca_mg_l=st.session_state.ca_mg_l,
    mg_mg_l=st.session_state.mg_mg_l,
    na_mg_l=st.session_state.na_mg_l,
    k_mg_l=st.session_state.k_mg_l,
    hco3_mg_l=st.session_state.hco3_mg_l,
    cl_mg_l=st.session_state.cl_mg_l,
    so4_mg_l=st.session_state.so4_mg_l,
    no3_mg_l=st.session_state.no3_mg_l,
    b_mg_l=st.session_state.b_mg_l,
    fe_mg_l=st.session_state.fe_mg_l,
)

NIVEL_ICONO = {"ok": "✅", "moderado": "⚠️", "severo": "❌"}

st.markdown("---")
st.subheader("Parámetros físicos")
c1, c2, c3, c4 = st.columns(4)
c1.metric("CE", f"{r.ce_ds:.3f} dS/m")
c2.metric("STD", f"{r.std_g_l:.2f} g/L")
c3.metric("Presión osmótica", f"{r.po_atm:.2f} atm")
c4.metric("Dureza", f"{r.dureza_f:.1f} °F")
c4.caption(r.dureza_txt)

st.subheader("Riesgos de infiltración, obturación y toxicidad")
c1, c2 = st.columns(2)
with c1:
    st.metric("R.A.S.", f"{r.ras:.2f}")
    st.write(f"{NIVEL_ICONO[r.infiltracion_nivel]} **Infiltración (FAO-29):** {r.infiltracion_txt}")
    st.write(f"{NIVEL_ICONO[r.obturacion_nivel]} **Obturación calcárea:** {r.obturacion_txt}")
    st.caption(r.obturacion_detalle)
with c2:
    st.write(f"{NIVEL_ICONO[r.cloruro_nivel]} **Cloruro** ({r.cl_meq:.2f} meq/L): {r.cloruro_txt}")
    st.write(f"{NIVEL_ICONO[r.sodio_nivel]} **Sodio** ({r.na_meq:.2f} meq/L): {r.sodio_txt}")
    st.write(f"{NIVEL_ICONO[r.boro_nivel]} **Boro** ({st.session_state.b_mg_l:.2f} mg/L): {r.boro_txt}")

st.markdown("---")
st.subheader("💰 Nutrientes gratuitos aportados por el agua de riego")
df_nut = pd.DataFrame(
    {
        "Nutriente": ["N (de NO₃⁻)", "CaO", "MgO", "K₂O", "SO₃"],
        f"kg/ha en {st.session_state.vol_riego_m3_ha:.0f} m³": [
            r.n_kg_ha, r.cao_kg_ha, r.mgo_kg_ha, r.k2o_kg_ha, r.so3_kg_ha,
        ],
    }
)
st.dataframe(df_nut.style.format({df_nut.columns[1]: "{:.2f}"}), use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("🧪 Dosificación de ácidos para neutralizar bicarbonatos")
st.metric("Bicarbonato a neutralizar", f"{r.bic_neto_meq_l:.2f} meq/L")
ca1, ca2, ca3 = st.columns(3)
with ca1:
    st.markdown("**Ácido nítrico**")
    st.write(f"{r.nitrico_ml_m3:.1f} mL/m³")
    st.write(f"Consumo total: {r.nitrico_total_l:.1f} L")
    st.success(f"¡Aporta gratis {r.nitrico_n_extra_kg_ha:.2f} kg N/ha!")
with ca2:
    st.markdown("**Ácido fosfórico**")
    st.write(f"{r.fosforico_ml_m3:.1f} mL/m³")
    st.write(f"Consumo total: {r.fosforico_total_l:.1f} L")
    st.warning(r.aviso_fosforico)
with ca3:
    st.markdown("**Ácido sulfúrico**")
    st.write(f"{r.sulfurico_ml_m3:.1f} mL/m³")
    st.write(f"Consumo total: {r.sulfurico_total_l:.1f} L")

st.markdown("---")
st.subheader("🧴 Plan de cloración")
cl1, cl2 = st.columns(2)
cl1.metric("Producto comercial (10% Cl activo)", f"{r.cloro_min_l:.1f} – {r.cloro_max_l:.1f} L")
cl2.metric("Cloro consumido por el hierro disuelto", f"{r.cloro_fe_mg_l:.3f} mg/L")

st.markdown("---")
st.subheader("⚖️ Balance de cargas (control de calidad de la analítica)")
st.write(r.electroneutralidad_txt)

st.markdown("---")
st.subheader("📊 Cationes vs. aniones (meq/L)")
df_bal = pd.DataFrame({"meq/L": {**r.grafico_cationes, **r.grafico_aniones}})
st.bar_chart(df_bal)
