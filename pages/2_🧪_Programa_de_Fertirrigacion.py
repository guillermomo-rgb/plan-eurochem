# -*- coding: utf-8 -*-
"""Programa de Fertirrigación (puerto de programa_fertirrigacion.html)."""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.fertirrigacion_data import (  # noqa: E402
    CULTIVO_EXTRACCIONES, LIMITES_SALINOS, GRANULADOS_DB, FOLIARES_DB, SOLUBLES_DB,
    FASES_INFO, SOLUCIONES_REFERENCIA_HIDROPONIA, monthly_data_por_defecto,
)
from shared.fertirrigacion_calc import (  # noqa: E402
    analizar_agua, calcular_acido, calcular_fondo, calcular_foliar,
    calcular_creditos_anuales, calcular_balance_anual, calcular_fase_mensual,
    meses_con_conflicto_tanque, calcular_gotero_sonneveld, sugerencias_fase,
    generar_dictamen_experto, calcular_reparto_anual, calcular_resumen_anual, ACIDOS_PRESETS,
)
from shared.ui_common import render_header, render_print_button  # noqa: E402

st.set_page_config(page_title="Programa de Fertirrigación", page_icon="🧪", layout="wide")
render_header("Programa de Fertirrigación", "🧪")
render_print_button()

# ---------------------------------------------------------------- Estado inicial
DEFAULTS = dict(
    crop="Caqui (Kaki)", yield_val=10.0,
    extra_n=0.0, extra_p=0.0, extra_k=0.0, extra_mg=0.0, extra_ca=0.0, extra_s=0.0,
    water_ca_mg_l=80.0, water_mg_mg_l=24.0, water_na_mg_l=46.0, water_k_mg_l=15.0, nh4_mg_l=0.0,
    water_no3_mg_l=10.0, h2po4_mg_l=0.0, water_so4_mg_l=96.0, water_cl_mg_l=71.0, water_hco3_mg_l=244.0,
    water_ec=0.95, water_ph=7.5, water_b=0.10, water_fe=0.02,
    acid_type="Nítrico (60%)", acid_target_hco3=1.5,
    acid_custom_n=0.0, acid_custom_p=0.0, acid_custom_s=0.0,
    fondo_items=[{"name": "ENTEC Nitrofoska Especial 12-12-17", "dosis": 300.0}],
    foliar_items=[],
    sonneveld_month=5,
)
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)
st.session_state.setdefault("custom_crops", {})
st.session_state.setdefault("custom_limites", {})
if "coeffs" not in st.session_state:
    st.session_state.coeffs = dict(CULTIVO_EXTRACCIONES[st.session_state.crop])
if "monthly_data" not in st.session_state:
    st.session_state.monthly_data = monthly_data_por_defecto()
if "acid_density" not in st.session_state or "acid_purity" not in st.session_state:
    preset = ACIDOS_PRESETS[st.session_state.acid_type]
    st.session_state.acid_density = preset["density"]
    st.session_state.acid_purity = preset["purity"]
    st.session_state.acid_eq_wt = preset["eq_wt"]

crops_disponibles = list(CULTIVO_EXTRACCIONES.keys()) + list(st.session_state.custom_crops.keys())
NIVEL_ICONO = {"ok": "✅", "moderado": "⚠️", "severo": "❌"}
NIVEL_ICONO_DICTAMEN = {"ok": "✅", "warn": "⚠️", "danger": "❌"}

tabs = st.tabs([
    "1. Balance Anual", "2. Agua de Riego", "3. Neutralización de Ácidos",
    "4. Fondo y Foliar", "5. Plan Mensual", "7. Sonneveld", "8. Dictamen Experto",
])

# ================================================================== PUNTO 1: Cultivo + Balance
with tabs[0]:
    st.subheader("Cultivo y rendimiento esperado")
    c1, c2 = st.columns(2)
    with c1:
        nuevo_crop = st.selectbox(
            "Cultivo", crops_disponibles, index=crops_disponibles.index(st.session_state.crop),
            format_func=lambda c: f"{c} (personalizado)" if c in st.session_state.custom_crops else c,
        )
        if nuevo_crop != st.session_state.crop:
            st.session_state.crop = nuevo_crop
            st.session_state.coeffs = dict(st.session_state.custom_crops.get(nuevo_crop) or CULTIVO_EXTRACCIONES[nuevo_crop])
    with c2:
        st.session_state.yield_val = st.number_input("Rendimiento esperado (t/ha)", value=st.session_state.yield_val, step=1.0)

    with st.expander("➕ Añadir Cultivo Nuevo"):
        nc1, nc2 = st.columns(2)
        nc_nombre = nc1.text_input("Nombre del cultivo", key="nc_nombre")
        nc_salino = nc2.number_input("Límite de salinidad de la gota (dS/m)", value=2.0, step=0.1, key="nc_salino")
        ncc = st.columns(6)
        nc_n = ncc[0].number_input("N (Nitrógeno)", value=0.0, step=0.1, key="nc_n")
        nc_p = ncc[1].number_input("P₂O₅", value=0.0, step=0.1, key="nc_p")
        nc_k = ncc[2].number_input("K₂O", value=0.0, step=0.1, key="nc_k")
        nc_mg = ncc[3].number_input("MgO", value=0.0, step=0.1, key="nc_mg")
        nc_ca = ncc[4].number_input("CaO", value=0.0, step=0.1, key="nc_ca")
        nc_s = ncc[5].number_input("SO₃", value=0.0, step=0.1, key="nc_s")
        if st.button("💾 Guardar cultivo nuevo"):
            if not nc_nombre.strip():
                st.error("Introduce un nombre para el cultivo.")
            else:
                nombre = nc_nombre.strip()
                st.session_state.custom_crops[nombre] = {"n": nc_n, "p": nc_p, "k": nc_k, "mg": nc_mg, "ca": nc_ca, "s": nc_s}
                st.session_state.custom_limites[nombre] = nc_salino
                st.session_state.crop = nombre
                st.session_state.coeffs = dict(st.session_state.custom_crops[nombre])
                st.success(f'Cultivo "{nombre}" guardado. Ya está seleccionado arriba.')
                st.rerun()

    with st.expander("✏️ Editar coeficientes de extracción (kg/t)"):
        cc = st.columns(6)
        labels = [("n", "N (Nitrógeno)"), ("p", "P₂O₅"), ("k", "K₂O"), ("mg", "MgO"), ("ca", "CaO"), ("s", "SO₃")]
        for i, (key, label) in enumerate(labels):
            # Sin `key=`: el valor mostrado debe reflejar siempre st.session_state.coeffs,
            # que cambia al elegir otro cultivo. Con un `key` fijo por nutriente, Streamlit
            # ignoraría el nuevo `value=` tras el primer render (mismo bug que el selector de
            # mes en el Punto 5), y los coeficientes se quedarían congelados en el primer cultivo.
            st.session_state.coeffs[key] = cc[i].number_input(label, value=float(st.session_state.coeffs[key]), step=0.1)

    with st.expander("➕ Compensación / margen de seguridad extra (E)"):
        ce = st.columns(6)
        st.session_state.extra_n = ce[0].number_input("N extra", value=st.session_state.extra_n)
        st.session_state.extra_p = ce[1].number_input("P₂O₅ extra", value=st.session_state.extra_p)
        st.session_state.extra_k = ce[2].number_input("K₂O extra", value=st.session_state.extra_k)
        st.session_state.extra_mg = ce[3].number_input("MgO extra", value=st.session_state.extra_mg)
        st.session_state.extra_ca = ce[4].number_input("CaO extra", value=st.session_state.extra_ca)
        st.session_state.extra_s = ce[5].number_input("SO₃ extra", value=st.session_state.extra_s)

    balance_placeholder = st.empty()  # se rellena tras calcular todo (más abajo)

# ================================================================== PUNTO 2: Agua
with tabs[1]:
    st.subheader("Analítica de agua de riego")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Cationes (mg/L)**")
        st.session_state.water_ca_mg_l = st.number_input("Ca²⁺", value=st.session_state.water_ca_mg_l)
        st.session_state.water_mg_mg_l = st.number_input("Mg²⁺", value=st.session_state.water_mg_mg_l)
        st.session_state.water_na_mg_l = st.number_input("Na⁺", value=st.session_state.water_na_mg_l)
        st.session_state.water_k_mg_l = st.number_input("K⁺", value=st.session_state.water_k_mg_l)
        st.session_state.nh4_mg_l = st.number_input("NH₄⁺", value=st.session_state.nh4_mg_l)
    with c2:
        st.markdown("**Aniones (mg/L)**")
        st.session_state.water_no3_mg_l = st.number_input("NO₃⁻", value=st.session_state.water_no3_mg_l)
        st.session_state.h2po4_mg_l = st.number_input("H₂PO₄⁻", value=st.session_state.h2po4_mg_l)
        st.session_state.water_so4_mg_l = st.number_input("SO₄²⁻", value=st.session_state.water_so4_mg_l)
        st.session_state.water_cl_mg_l = st.number_input("Cl⁻", value=st.session_state.water_cl_mg_l)
        st.session_state.water_hco3_mg_l = st.number_input("HCO₃⁻", value=st.session_state.water_hco3_mg_l)
    with c3:
        st.markdown("**Otros parámetros**")
        st.session_state.water_ec = st.number_input("CE (dS/m)", value=st.session_state.water_ec, step=0.05)
        st.session_state.water_ph = st.number_input("pH", value=st.session_state.water_ph, step=0.1)
        st.session_state.water_b = st.number_input("Boro (mg/L)", value=st.session_state.water_b, step=0.01, format="%.2f")
        st.session_state.water_fe = st.number_input("Hierro (mg/L)", value=st.session_state.water_fe, step=0.01, format="%.3f")

    agua_placeholder = st.empty()

# ================================================================== PUNTO 3: Ácidos
with tabs[2]:
    st.subheader("Neutralización de bicarbonatos")
    tipos_acido = list(ACIDOS_PRESETS.keys()) + ["Personalizado"]
    nuevo_tipo = st.selectbox("Tipo de ácido", tipos_acido, index=tipos_acido.index(st.session_state.acid_type))
    if nuevo_tipo != st.session_state.acid_type:
        st.session_state.acid_type = nuevo_tipo
        if nuevo_tipo in ACIDOS_PRESETS:
            preset = ACIDOS_PRESETS[nuevo_tipo]
            st.session_state.acid_density = preset["density"]
            st.session_state.acid_purity = preset["purity"]
            st.session_state.acid_eq_wt = preset["eq_wt"]

    c1, c2, c3 = st.columns(3)
    st.session_state.acid_density = c1.number_input("Densidad (kg/L)", value=st.session_state.acid_density)
    st.session_state.acid_purity = c2.number_input("Pureza (%)", value=st.session_state.acid_purity)
    st.session_state.acid_eq_wt = c3.number_input("Peso equivalente", value=st.session_state.acid_eq_wt)
    st.session_state.acid_target_hco3 = st.number_input("Bicarbonato objetivo residual (meq/L)", value=st.session_state.acid_target_hco3, step=0.1)

    if st.session_state.acid_type == "Personalizado":
        st.markdown("**Aporte del ácido personalizado (kg elemento / meq HCO₃⁻ neutralizado / m³)**")
        cc = st.columns(3)
        st.session_state.acid_custom_n = cc[0].number_input("N (Nitrógeno)", value=st.session_state.acid_custom_n)
        st.session_state.acid_custom_p = cc[1].number_input("P₂O₅", value=st.session_state.acid_custom_p)
        st.session_state.acid_custom_s = cc[2].number_input("SO₃", value=st.session_state.acid_custom_s)

    acido_placeholder = st.empty()

# ================================================================== PUNTO 4: Fondo + Foliar
with tabs[3]:
    st.subheader("📦 Abonado de fondo granulado")
    c1, c2, c3 = st.columns([3, 1, 1])
    sel_fondo = c1.selectbox("Producto", list(GRANULADOS_DB.keys()), key="sel_fondo")
    dosis_fondo = c2.number_input("Dosis (kg/ha)", value=150.0, step=25.0, key="dosis_fondo_input")
    if c3.button("➕ Añadir", key="add_fondo"):
        st.session_state.fondo_items.append({"name": sel_fondo, "dosis": dosis_fondo})
        st.rerun()

    for idx, item in enumerate(st.session_state.fondo_items):
        cc = st.columns([3, 1, 1])
        cc[0].write(item["name"])
        nueva_dosis = cc[1].number_input("kg/ha", value=float(item["dosis"]), key=f"fondo_dosis_{idx}", label_visibility="collapsed")
        st.session_state.fondo_items[idx]["dosis"] = nueva_dosis
        if cc[2].button("🗑️", key=f"del_fondo_{idx}"):
            st.session_state.fondo_items.pop(idx)
            st.rerun()

    fondo_placeholder = st.empty()

    st.markdown("---")
    st.subheader("🌿 Aplicación foliar")
    c1, c2, c3 = st.columns([3, 1, 1])
    sel_foliar = c1.selectbox("Producto foliar", list(FOLIARES_DB.keys()), key="sel_foliar")
    dosis_foliar = c2.number_input("Dosis (kg-L/ha)", value=1.0, step=0.1, key="dosis_foliar_input")
    if c3.button("➕ Añadir", key="add_foliar"):
        st.session_state.foliar_items.append({"name": sel_foliar, "dosis": dosis_foliar})
        st.rerun()

    for idx, item in enumerate(st.session_state.foliar_items):
        cc = st.columns([3, 1, 1])
        cc[0].write(item["name"])
        nueva_dosis = cc[1].number_input("kg-L/ha", value=float(item["dosis"]), step=0.1, key=f"foliar_dosis_{idx}", label_visibility="collapsed")
        st.session_state.foliar_items[idx]["dosis"] = nueva_dosis
        if cc[2].button("🗑️", key=f"del_foliar_{idx}"):
            st.session_state.foliar_items.pop(idx)
            st.rerun()

    foliar_placeholder = st.empty()

# ================================================================== PUNTO 5: Plan Mensual
with tabs[4]:
    st.subheader("📅 Plan mensual por fases")
    meses_nombres = [st.session_state.monthly_data[m]["name"] for m in range(1, 13)]
    st.session_state.setdefault("mes_editado", 5)
    mes_sel_nombre = st.selectbox("Mes a editar", meses_nombres, index=st.session_state.mes_editado - 1, key="mes_editado_selector")
    m_idx = meses_nombres.index(mes_sel_nombre) + 1
    st.session_state.mes_editado = m_idx
    month = st.session_state.monthly_data[m_idx]

    c1, c2 = st.columns(2)
    with c1:
        month["water"] = st.number_input("Volumen de riego (m³/ha·mes)", value=float(month["water"]), step=10.0, key=f"mw_{m_idx}")
        month["num_riegos"] = st.number_input("Número de riegos", value=int(month["num_riegos"]), min_value=0, key=f"mnr_{m_idx}")
        month["cuba_vol"] = st.number_input("Volumen cuba madre (L)", value=float(month["cuba_vol"]), min_value=0.0, key=f"mcv_{m_idx}")
        month["flow_rate"] = st.number_input("Caudal gotero (L/h)", value=float(month["flow_rate"]), min_value=0.0, key=f"mfr_{m_idx}")
        month["tiempo_riego"] = st.number_input("Tiempo de riego por evento (h)", value=float(month["tiempo_riego"]), min_value=0.0, key=f"mtr_{m_idx}")
        fases_keys = list(FASES_INFO.keys())
        month["fase"] = st.selectbox("Fase fenológica", fases_keys, index=fases_keys.index(month["fase"]),
                                      format_func=lambda k: FASES_INFO[k]["label"], key=f"mfase_{m_idx}")
    with c2:
        st.markdown("**Añadir fertilizante soluble**")
        sel_sol = st.selectbox("Producto", list(SOLUBLES_DB.keys()), key=f"sel_sol_{m_idx}")
        dosis_sol = st.number_input("Dosis (kg/ha·mes)", value=50.0, step=10.0, key=f"dosis_sol_{m_idx}")
        if st.button("➕ Añadir soluble", key=f"add_sol_{m_idx}"):
            month["solubles"].append({"name": sel_sol, "dosis": dosis_sol})
            st.rerun()

        for idx, item in enumerate(month["solubles"]):
            cc = st.columns([3, 1, 1])
            cc[0].write(item["name"])
            nueva_dosis = cc[1].number_input("kg/ha", value=float(item["dosis"]), key=f"sol_dosis_{m_idx}_{idx}", label_visibility="collapsed")
            month["solubles"][idx]["dosis"] = nueva_dosis
            if cc[2].button("🗑️", key=f"del_sol_{m_idx}_{idx}"):
                month["solubles"].pop(idx)
                st.rerun()

    fase_placeholder = st.empty()

# ================================================================== PUNTO 7: Sonneveld
with tabs[5]:
    st.subheader("🔬 Gotero de Sonneveld")
    meses_nombres = [st.session_state.monthly_data[m]["name"] for m in range(1, 13)]
    mes_sonn_nombre = st.selectbox("Mes a inspeccionar", meses_nombres,
                                    index=st.session_state.sonneveld_month - 1, key="sonneveld_sel")
    st.session_state.sonneveld_month = meses_nombres.index(mes_sonn_nombre) + 1
    sonneveld_placeholder = st.empty()

    with st.expander("📖 Soluciones nutritivas clásicas de hidroponía (solo referencia comparativa)"):
        df_ref = pd.DataFrame(SOLUCIONES_REFERENCIA_HIDROPONIA).set_index("nombre")
        st.dataframe(df_ref, use_container_width=True)

# ================================================================== PUNTO 8: Dictamen
with tabs[6]:
    st.subheader("💡 Dictamen agronómico experto")
    dictamen_placeholder = st.empty()

# ================================================================== CÁLCULO CENTRAL (equivalente a calculateAll())
monthly_data = st.session_state.monthly_data
water_composition = dict(
    no3_mg_l=st.session_state.water_no3_mg_l, h2po4_mg_l=st.session_state.h2po4_mg_l,
    k_mg_l=st.session_state.water_k_mg_l, mg_mg_l=st.session_state.water_mg_mg_l,
    ca_mg_l=st.session_state.water_ca_mg_l, so4_mg_l=st.session_state.water_so4_mg_l,
)
vol_anual = sum(monthly_data[m]["water"] for m in range(1, 13))

agua = analizar_agua(
    ca_mg_l=st.session_state.water_ca_mg_l, mg_mg_l=st.session_state.water_mg_mg_l,
    na_mg_l=st.session_state.water_na_mg_l, k_mg_l=st.session_state.water_k_mg_l, nh4_mg_l=st.session_state.nh4_mg_l,
    no3_mg_l=st.session_state.water_no3_mg_l, h2po4_mg_l=st.session_state.h2po4_mg_l,
    so4_mg_l=st.session_state.water_so4_mg_l, cl_mg_l=st.session_state.water_cl_mg_l, hco3_mg_l=st.session_state.water_hco3_mg_l,
    water_ec_ds_m=st.session_state.water_ec, ph=st.session_state.water_ph,
    b_mg_l=st.session_state.water_b, fe_mg_l=st.session_state.water_fe, vol_anual_m3_ha=vol_anual,
)

acido = calcular_acido(
    meq_hco3=agua.meq_hco3, target_hco3=st.session_state.acid_target_hco3,
    purity=st.session_state.acid_purity, density=st.session_state.acid_density, eq_wt=st.session_state.acid_eq_wt,
)
acid_custom = dict(n=st.session_state.acid_custom_n, p=st.session_state.acid_custom_p, s=st.session_state.acid_custom_s)

fondo = calcular_fondo(st.session_state.fondo_items)
foliar = calcular_foliar(st.session_state.foliar_items)

creditos = calcular_creditos_anuales(
    monthly_data=monthly_data, water_composition=water_composition,
    acid_type=st.session_state.acid_type, acid_custom=acid_custom, neut_hco3=acido.neut_hco3_meq_l,
)
balance = calcular_balance_anual(
    yield_val=st.session_state.yield_val, coeffs=st.session_state.coeffs,
    fondo=fondo, creditos=creditos, extra=dict(
        n=st.session_state.extra_n, p=st.session_state.extra_p, k=st.session_state.extra_k,
        mg=st.session_state.extra_mg, ca=st.session_state.extra_ca, s=st.session_state.extra_s,
    ),
)
resumen_anual = calcular_resumen_anual(base=balance.base, fondo=fondo, creditos=creditos)
meses_conflicto = meses_con_conflicto_tanque(monthly_data=monthly_data)
umbral_salino = st.session_state.custom_limites.get(st.session_state.crop, LIMITES_SALINOS.get(st.session_state.crop, 1.5))

fase_actual = calcular_fase_mensual(
    month=monthly_data[st.session_state.mes_editado if "mes_editado" in st.session_state else 5],
    water_composition=water_composition, water_ec_ds_m=st.session_state.water_ec,
    acid_type=st.session_state.acid_type, acid_custom=acid_custom, neut_hco3=acido.neut_hco3_meq_l,
    target=balance.target, umbral_salino=umbral_salino,
)

reparto_anual = calcular_reparto_anual(
    monthly_data=monthly_data, water_composition=water_composition, water_ec_ds_m=st.session_state.water_ec,
    acid_type=st.session_state.acid_type, acid_custom=acid_custom, neut_hco3=acido.neut_hco3_meq_l,
    target=balance.target, umbral_salino=umbral_salino,
)

sonneveld = calcular_gotero_sonneveld(
    mes=monthly_data[st.session_state.sonneveld_month], agua=agua, water_ec_ds_m=st.session_state.water_ec,
    acid_type=st.session_state.acid_type, acid_custom=acid_custom, neut_hco3=acido.neut_hco3_meq_l,
)
sugerencias = sugerencias_fase(
    monthly_data[st.session_state.sonneveld_month]["fase"],
    dict(r_k_ca_mg=sonneveld.r_k_ca_mg, r_ca_mg=sonneveld.r_ca_mg, r_k_mg=sonneveld.r_k_mg,
         r_n_k=sonneveld.r_n_k, r_n_p=sonneveld.r_n_p),
)

dictamen = generar_dictamen_experto(
    ec_gota=fase_actual.ec_gota, ras_val=agua.ras, meq_cl=agua.meq_cl, hco3_mg_l=st.session_state.water_hco3_mg_l,
    meses_conflicto_tanque=meses_conflicto, crop=st.session_state.crop, umbral_salino=umbral_salino,
)

# ---------------------------------------------------------------- Render Punto 1 (balance)
with balance_placeholder.container():
    st.markdown("---")
    st.subheader("Balance anual de nutrientes (kg/ha·año)")
    filas = ["A) Necesidad base cultivo", "C) Abonado de fondo", "D1) Crédito agua de riego",
             "D2) Crédito ácido regulador", "E) Compensación extra", "Objetivo en gotero (Target)",
             "F) Foliar aplicado", "Total aplicado (solubles)", "Balance / diferencia"]
    cols = {"n": "N", "p": "P₂O₅", "k": "K₂O", "mg": "MgO", "ca": "CaO", "s": "SO₃"}
    data = {"Concepto": filas}
    for key, label in cols.items():
        data[label] = [
            balance.base[key], fondo.__dict__[key], creditos.water[key],
            creditos.acid.get(key, 0.0), 0.0, balance.target[key],
            foliar.__dict__[key], creditos.solub[key], balance.diff[key],
        ]
        # E) usa el extra correspondiente
        extra_key = f"extra_{key}"
        data[label][4] = st.session_state.get(extra_key, 0.0)
    df_balance = pd.DataFrame(data)
    st.dataframe(df_balance.style.format({v: "{:.1f}" for v in cols.values()}), use_container_width=True, hide_index=True)
    st.caption("El foliar (F) no se resta del objetivo en gotero — es un aporte complementario para corregir carencias puntuales, igual que en el HTML original.")

    cc = st.columns(6)
    for i, (key, label) in enumerate(cols.items()):
        cc[i].metric(f"Cobertura fondo {label}", f"{balance.cobertura_fondo_pct[key]:.1f}%")

    st.markdown("---")
    st.subheader("📋 Resumen final: granulado + ácido + agua + solubles frente al objetivo")
    df_resumen = pd.DataFrame([{
        "Nutriente": f.nutriente, "Granulado (fondo)": f.granulado, "Ácido": f.acido,
        "Agua": f.agua, "Solubles (fertirrigación)": f.soluble, "Total aportado": f.total_aportado,
        "Necesidad total": f.necesidad_base, "Balance (falta/excede)": f.balance,
        "% cubierto": f.pct_cubierto,
    } for f in resumen_anual])
    cols_numericas_resumen = [c for c in df_resumen.columns if c != "Nutriente"]
    st.dataframe(
        df_resumen.style.format({c: "{:.1f}" for c in cols_numericas_resumen}),
        use_container_width=True, hide_index=True,
    )
    for f in resumen_anual:
        if abs(f.pct_cubierto - 100) <= 10:
            st.success(f"✅ {f.nutriente}: cubierto ({f.pct_cubierto:.0f}% del objetivo, balance {f.balance:+.1f} kg/ha).")
        elif f.balance < 0:
            st.warning(f"⚠️ {f.nutriente}: faltan {abs(f.balance):.1f} kg/ha ({f.pct_cubierto:.0f}% del objetivo cubierto).")
        else:
            st.warning(f"⚠️ {f.nutriente}: excede en {f.balance:.1f} kg/ha ({f.pct_cubierto:.0f}% del objetivo).")
    st.caption(
        "Ácido = crédito de N/P₂O₅/SO₃ que aporta el ácido regulador al neutralizar bicarbonatos "
        "(no aporta a K₂O/MgO/CaO). No incluye ni el foliar (F) ni la compensación extra (E), que "
        "quedan reflejados en la tabla de arriba."
    )

# ---------------------------------------------------------------- Render Punto 2 (agua)
with agua_placeholder.container():
    st.markdown("---")
    st.subheader("Diagnóstico del agua")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("STD", f"{agua.std_gl:.2f} g/L")
    c2.metric("Presión osmótica", f"{agua.po_atm:.2f} atm")
    c3.metric("Dureza", f"{agua.dureza_gf:.1f} °F")
    c4.metric("R.A.S. (con K)", f"{agua.ras:.2f}")

    c1, c2 = st.columns(2)
    with c1:
        st.write(f"{NIVEL_ICONO[agua.infiltracion_nivel]} **Infiltración (FAO-29):** {agua.infiltracion_txt}")
        st.write(f"{NIVEL_ICONO[agua.obturacion_nivel]} **Obturación calcárea:** {agua.obturacion_txt}")
        st.write(f"Balance de cargas del agua: {agua.water_ratio_pct:.1f}%")
    with c2:
        st.write(f"{NIVEL_ICONO[agua.cl_nivel]} **Cloruro** ({agua.meq_cl:.2f} meq/L): {agua.cl_txt}")
        st.write(f"{NIVEL_ICONO[agua.na_nivel]} **Sodio** ({agua.meq_na:.2f} meq/L): {agua.na_txt}")
        st.write(f"{NIVEL_ICONO[agua.b_nivel]} **Boro** ({st.session_state.water_b:.2f} mg/L): {agua.b_txt}")

    st.markdown(f"**Volumen de riego anual (Puntos 5):** {agua.vol_anual_m3_ha:.0f} m³/ha")
    st.markdown("**💰 Caja de ahorros de nutrientes gratuitos del agua (informativo)**")
    df_ahorro = pd.DataFrame({
        "Nutriente": ["N", "CaO", "MgO", "K₂O", "SO₃"],
        "kg/ha·año": [agua.ahorro_n_kg_ha, agua.ahorro_cao_kg_ha, agua.ahorro_mgo_kg_ha, agua.ahorro_k2o_kg_ha, agua.ahorro_so3_kg_ha],
    })
    st.dataframe(df_ahorro.style.format({"kg/ha·año": "{:.1f}"}), use_container_width=True, hide_index=True)

    st.markdown("**🧴 Plan de cloración**")
    st.write(f"Producto comercial (10% Cl activo): {agua.cloro_min_l:.0f} – {agua.cloro_max_l:.0f} L/año")
    st.write(f"Cloro consumido por el hierro disuelto: {agua.cloro_fe_mg_l:.3f} mg/L")

# ---------------------------------------------------------------- Render Punto 3 (ácido)
with acido_placeholder.container():
    st.markdown("---")
    st.metric("Bicarbonato a neutralizar", f"{acido.neut_hco3_meq_l:.2f} meq/L")
    c1, c2 = st.columns(2)
    c1.metric("Dosis de ácido", f"{acido.dose_l:.3f} L/m³")
    c2.metric("Peso de ácido", f"{acido.dose_g:.1f} g/m³")

# ---------------------------------------------------------------- Render Punto 4 (fondo + foliar)
with fondo_placeholder.container():
    st.markdown("**Totales de fondo aplicado**")
    df_fondo = pd.DataFrame([{"Producto": i.name, "Dosis (kg/ha)": i.dosis, "N": i.n, "P₂O₅": i.p,
                               "K₂O": i.k, "MgO": i.mg, "CaO": i.ca, "SO₃": i.s} for i in fondo.items])
    if not df_fondo.empty:
        st.dataframe(df_fondo.style.format({c: "{:.1f}" for c in df_fondo.columns if c != "Producto"}), use_container_width=True, hide_index=True)
    st.write(f"**Total: {fondo.total_dosis:.0f} kg/ha — N: {fondo.n:.1f} | P₂O₅: {fondo.p:.1f} | "
             f"K₂O: {fondo.k:.1f} | MgO: {fondo.mg:.1f} | CaO: {fondo.ca:.1f} | SO₃: {fondo.s:.1f} kg/ha**")

    st.markdown("**% de las necesidades totales del cultivo cubierto por el fondo**")
    cols_nut = {"n": "N", "p": "P₂O₅", "k": "K₂O", "mg": "MgO", "ca": "CaO", "s": "SO₃"}
    df_cobertura = pd.DataFrame({
        "Nutriente": list(cols_nut.values()),
        "Fondo (kg/ha)": [fondo.__dict__[k] for k in cols_nut],
        "Necesidad total (kg/ha)": [balance.base[k] for k in cols_nut],
        "% de la necesidad": [balance.cobertura_fondo_pct[k] for k in cols_nut],
    })
    st.dataframe(
        df_cobertura.style.format({"Fondo (kg/ha)": "{:.1f}", "Necesidad total (kg/ha)": "{:.1f}", "% de la necesidad": "{:.1f}%"}),
        use_container_width=True, hide_index=True,
    )

with foliar_placeholder.container():
    st.markdown("**Totales foliares aplicados**")
    df_foliar = pd.DataFrame([{"Producto": i.name, "Dosis": i.dosis, "N": i.n, "P₂O₅": i.p, "K₂O": i.k,
                                "MgO": i.mg, "CaO": i.ca, "SO₃": i.s, "Fe(g)": i.fe, "Mn(g)": i.mn,
                                "Zn(g)": i.zn, "Cu(g)": i.cu, "B(g)": i.b, "Mo(g)": i.mo} for i in foliar.items])
    if not df_foliar.empty:
        st.dataframe(df_foliar.style.format({c: "{:.2f}" for c in df_foliar.columns if c != "Producto"}), use_container_width=True, hide_index=True)
    st.write(f"**Macros (kg/ha) — N: {foliar.n:.2f} | P₂O₅: {foliar.p:.2f} | K₂O: {foliar.k:.2f} | "
             f"MgO: {foliar.mg:.2f} | CaO: {foliar.ca:.2f} | SO₃: {foliar.s:.2f}**")
    st.write(f"**Micros (g/ha) — Fe: {foliar.fe:.1f} | Mn: {foliar.mn:.1f} | Zn: {foliar.zn:.1f} | "
             f"Cu: {foliar.cu:.1f} | B: {foliar.b:.1f} | Mo: {foliar.mo:.2f}**")

# ---------------------------------------------------------------- Render Punto 5 (fase mensual)
with fase_placeholder.container():
    st.markdown("---")
    st.subheader(f"Resultados de la fase: {month['name']}")
    if fase_actual.hay_conflicto_tanque:
        st.error("💥 RIESGO DE PRECIPITADO: esta fase mezcla productos Tanque A (cálcicos) con Tanque B (sulfatos/fosfatos). Inyéctalos desde cubas separadas.")

    cols = {"n": "N", "p": "P₂O₅", "k": "K₂O", "mg": "MgO", "ca": "CaO", "s": "SO₃"}
    df_fase = pd.DataFrame({
        "Origen": ["1. Fertilizantes cristalinos", "2. Aporte del agua", "3. Aporte de ácido", "Suma total", "% del objetivo"],
        **{label: [
            fase_actual.sol_sum[k], fase_actual.water_credit[k], fase_actual.acid_credit.get(k, 0.0),
            fase_actual.suma_total[k], fase_actual.pct_objetivo[k],
        ] for k, label in cols.items()},
    })
    st.dataframe(df_fase.style.format({v: "{:.1f}" for v in cols.values()}), use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("CE de la gota", f"{fase_actual.ec_gota:.2f} dS/m")
    c2.metric("Concentración cuba", f"{fase_actual.conc_cuba_pct:.2f}% ({fase_actual.conc_cuba_gl:.1f} g/L)")
    c3.metric("Emisores/ha estimados", f"{fase_actual.emisores_ha:.0f}")
    if fase_actual.cuba_saturada:
        st.warning("⚠️ Cuba saturada (>150 g/L). Riesgo de precipitados químicos.")
    if fase_actual.supera_umbral_salino:
        st.warning(f"⚠️ La CE de la gota ({fase_actual.ec_gota:.2f} dS/m) supera el umbral del cultivo ({umbral_salino:.1f} dS/m).")
    st.metric("Bomba inyectora estimada", f"{fase_actual.bomba_l_h:.0f} L/h")

    st.markdown("---")
    st.markdown(f"**📊 Reparto anual de unidades por mes — vía fertirrigación (% sobre el objetivo, ya con el fondo descontado)**")
    cols_reparto = {"n": "N", "p": "P₂O₅", "k": "K₂O", "mg": "MgO", "ca": "CaO", "s": "SO₃"}
    filas_reparto = []
    for fila in reparto_anual:
        registro = {"Mes": fila.mes}
        for key, label in cols_reparto.items():
            registro[f"{label} (kg/ha)"] = fila.kg[key]
            registro[f"{label} (%)"] = fila.pct_objetivo[key]
        registro["CE gota (dS/m)"] = fila.ec_gota
        registro["¿Supera CE cultivo?"] = "⚠️ Sí" if fila.supera_umbral_salino else "OK"
        filas_reparto.append(registro)
    df_reparto = pd.DataFrame(filas_reparto)
    cols_numericas_reparto = [c for c in df_reparto.columns if c not in ("Mes", "¿Supera CE cultivo?")]
    st.dataframe(
        df_reparto.style.format({c: "{:.1f}" for c in cols_numericas_reparto}),
        use_container_width=True, hide_index=True,
    )
    st.caption(
        f"El % de cada nutriente es sobre el objetivo en gotero (necesidad total menos lo ya cubierto por el "
        f"fondo, el agua de riego y el ácido regulador). El umbral de CE de la gota usado es el de "
        f"{st.session_state.crop}: {umbral_salino:.1f} dS/m."
    )

# ---------------------------------------------------------------- Render Punto 7 (Sonneveld)
with sonneveld_placeholder.container():
    CATIONES_LABEL = {"ca": "Ca²⁺", "mg": "Mg²⁺", "k": "K⁺", "na": "Na⁺", "nh4": "NH₄⁺"}
    ANIONES_LABEL = {"no3": "NO₃⁻", "p": "H₂PO₄⁻", "s": "SO₄²⁻", "cl": "Cl⁻", "hco3": "HCO₃⁻"}

    def _tabla_ion(etiquetas: dict) -> pd.DataFrame:
        return pd.DataFrame([{
            "Ion": label,
            "meq/L Agua": sonneveld.meq_agua[key], "meq/L Fert": sonneveld.meq_fert[key],
            "meq/L Ácido": sonneveld.meq_acido[key], "meq/L Total": sonneveld.meq_total[key],
            "mg/L Total": sonneveld.mg_total[key],
        } for key, label in etiquetas.items()])

    st.markdown("**Cationes en solución gotero (meq/L y mg/L, por origen)**")
    df_cat = _tabla_ion(CATIONES_LABEL)
    st.dataframe(df_cat.style.format({c: "{:.2f}" for c in df_cat.columns if c != "Ion"}), use_container_width=True, hide_index=True)

    st.markdown("**Aniones en solución gotero (meq/L y mg/L, por origen)**")
    df_ani = _tabla_ion(ANIONES_LABEL)
    st.dataframe(df_ani.style.format({c: "{:.2f}" for c in df_ani.columns if c != "Ion"}), use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Equilibrio de cargas**")
        st.write(f"Suma cationes: {sonneveld.total_cat_meq:.2f} meq/L ({sonneveld.total_cat_mg:.0f} mg/L)")
        st.write(f"Suma aniones: {sonneveld.total_ani_meq:.2f} meq/L ({sonneveld.total_ani_mg:.0f} mg/L)")
        st.write(f"Diferencia de carga: {sonneveld.diferencia_carga_meq:.2f} meq/L")
        st.write(f"Electroneutralidad: {sonneveld.electroneutralidad_pct:.1f}%")
    with c2:
        st.markdown("**CE de la gota, por origen**")
        st.write(f"CE del agua: {sonneveld.ec_agua:.2f} dS/m")
        st.write(f"CE aportada por el fertilizante: {sonneveld.ec_fert:.2f} dS/m")
        st.write(f"CE aportada por el ácido: {sonneveld.ec_acido:.2f} dS/m")
        st.write(f"**CE total de la gota: {sonneveld.ec_total:.2f} dS/m**")
    with c3:
        st.markdown("**Tríada catiónica (% molar K:Ca:Mg)**")
        st.progress(min(sonneveld.triad_pct["k"] / 100, 1.0), text=f"K: {sonneveld.triad_pct['k']:.0f}%")
        st.progress(min(sonneveld.triad_pct["ca"] / 100, 1.0), text=f"Ca: {sonneveld.triad_pct['ca']:.0f}%")
        st.progress(min(sonneveld.triad_pct["mg"] / 100, 1.0), text=f"Mg: {sonneveld.triad_pct['mg']:.0f}%")

    st.markdown("**Relaciones molares Sonneveld**")
    ratios = [
        ("K / (Ca+Mg)", sonneveld.r_k_ca_mg, "0.30 - 0.50", sonneveld.comentarios["k_ca_mg"]),
        ("Ca / Mg", sonneveld.r_ca_mg, "2.50 - 5.00", sonneveld.comentarios["ca_mg"]),
        ("K / Mg", sonneveld.r_k_mg, "1.50 - 3.00", sonneveld.comentarios["k_mg"]),
        ("N / K", sonneveld.r_n_k, "1.00 - 1.60", sonneveld.comentarios["n_k"]),
        ("N / P", sonneveld.r_n_p, "8.00 - 12.00", sonneveld.comentarios["n_p"]),
    ]
    df_ratios = pd.DataFrame([{"Relación": r[0], "Valor": r[1], "Rango óptimo": r[2], "Diagnóstico": r[3][0]} for r in ratios])
    st.dataframe(df_ratios.style.format({"Valor": "{:.2f}"}), use_container_width=True, hide_index=True)

    fase_info = FASES_INFO[monthly_data[st.session_state.sonneveld_month]["fase"]]
    st.markdown(f"**Fase: {fase_info['label']}** — prioridad: {fase_info['prioridad']}")
    if sugerencias:
        for s in sugerencias:
            st.warning(s)
    else:
        st.success("✅ La solución de esta fase no contradice la prioridad nutricional esperada.")

# ---------------------------------------------------------------- Render Punto 8 (dictamen)
with dictamen_placeholder.container():
    for alerta in dictamen:
        if alerta.nivel == "ok":
            st.success(f"{NIVEL_ICONO_DICTAMEN[alerta.nivel]} {alerta.mensaje}")
        elif alerta.nivel == "warn":
            st.warning(f"{NIVEL_ICONO_DICTAMEN[alerta.nivel]} {alerta.mensaje}")
        else:
            st.error(f"{NIVEL_ICONO_DICTAMEN[alerta.nivel]} {alerta.mensaje}")
