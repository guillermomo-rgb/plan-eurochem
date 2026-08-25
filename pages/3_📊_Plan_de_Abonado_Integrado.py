# -*- coding: utf-8 -*-
"""Plan de Abonado Integrado (puerto de plan_abonado_integrado.html), incluido
el módulo "Comparador de Planes" (comparación de costes entre el Plan Eurochem
y alternativas del usuario)."""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.plan_abonado_data import (  # noqa: E402
    CULTIVO_EXTRACTIONS, FERT_DATA, FERT_COBERTERA_KEYS, FERT_COBERTERA2_KEYS,
    FOLIARES_DB, ESTIERCOL_DATA, PURINES_DATA, PI_NOTES, CULTIVO_ZVN_NOTES,
)
from shared.plan_abonado_calc import (  # noqa: E402
    calcular_suelo, calcular_balance_n, calcular_p_k, calcular_plan_npk,
    generar_diagnostico_estrategia, generar_diagnostico_suelo,
    legal_n_limit, pi_n_limit,
)
from shared.plan_abonado_comparador import (  # noqa: E402
    pf_default_state, pf_sync_plan_eurochem, calc_plan as pf_calc_plan,
)
from shared.ui_common import render_header, render_print_button  # noqa: E402

st.set_page_config(page_title="Plan de Abonado Integrado", page_icon="📊", layout="wide")
render_header("Plan de Abonado Integrado", "📊")
render_print_button()

DEFAULTS = dict(
    arcilla=20.0, arena=40.0, limo=40.0, suelo_ph=7.0, ce=0.5, carbonatos=0.0, caliza_activa=0.0,
    cn=11.0, mo=1.5, nitratos_lab=10.0, n_kjeldahl=0.08, p_olsen=15.0,
    fe_ppm=2.0, mn_ppm=1.0, cu_ppm=0.3, zn_ppm=1.0,
    ca_meq=8.0, ca_ppm=1600.0, mg_meq=1.0, mg_ppm=120.0, k_meq=0.3, k_ppm=120.0, na_meq=0.2,
    profundidad=30.0, cic_medida=0.0,
    cultivo="trigo", rendimiento=8.0, margen_perdidas=1.15,
    vol_riego=0.0, nitratos_agua=0.0, restos_cosecha=0.0, cubierta_veg=0.0, dep_atmosferica=0.0,
    tipo_estiercol="0", dosis_estiercol_1=0.0, dosis_estiercol_2=0.0, dosis_estiercol_3=0.0,
    tipo_purin="0", dosis_purin_1=0.0, dosis_purin_2=0.0, dosis_purin_3=0.0,
    key_fondo="nitrofoska_special_12_12_17", dosis_fondo=300.0,
    key_cob1="0", dosis_cob1=0.0, key_cob2="0", dosis_cob2=0.0,
    zona_vulnerable=False, produccion_integrada=False, regimen_olivar="secano_tradicional",
    pa_foliar_items=[],
    precio_venta=0.0, precio_venta_unit="kg",
    pf_precios={}, pf_planes_alternativos=[],
)
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)

cultivos_disponibles = list(CULTIVO_EXTRACTIONS.keys())
fert_fondo_keys = list(FERT_DATA.keys())

tabs = st.tabs(["🌱 Suelo y Balance de N", "🚜 Plan NPK Eurochem", "⚖️ Cumplimiento Legal", "💰 Comparador de Planes"])

# ================================================================== TAB 1: Suelo
with tabs[0]:
    st.subheader("Analítica de suelo")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Textura**")
        st.session_state.arcilla = st.number_input("Arcilla (%)", value=st.session_state.arcilla)
        st.session_state.arena = st.number_input("Arena (%)", value=st.session_state.arena)
        st.session_state.limo = st.number_input("Limo (%)", value=st.session_state.limo)
        st.session_state.profundidad = st.number_input("Profundidad de muestreo (cm)", value=st.session_state.profundidad)
    with c2:
        st.markdown("**Química general**")
        st.session_state.suelo_ph = st.number_input("pH", value=st.session_state.suelo_ph, step=0.1)
        st.session_state.ce = st.number_input("CE (dS/m)", value=st.session_state.ce, step=0.1)
        st.session_state.carbonatos = st.number_input("Carbonatos totales (%)", value=st.session_state.carbonatos)
        st.session_state.caliza_activa = st.number_input("Caliza activa (%)", value=st.session_state.caliza_activa)
        st.session_state.cn = st.number_input("Relación C/N", value=st.session_state.cn)
        st.session_state.mo = st.number_input("Materia orgánica (%)", value=st.session_state.mo, step=0.1)
    with c3:
        st.markdown("**Nitrógeno y P**")
        st.session_state.nitratos_lab = st.number_input("Nitratos de laboratorio (ppm NO₃⁻)", value=st.session_state.nitratos_lab)
        st.session_state.n_kjeldahl = st.number_input("N Kjeldahl (%)", value=st.session_state.n_kjeldahl, format="%.3f")
        st.session_state.p_olsen = st.number_input("P Olsen (ppm)", value=st.session_state.p_olsen)

    st.markdown("**Bases de cambio y micronutrientes**")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.session_state.ca_meq = st.number_input("Ca²⁺ (meq/100g)", value=st.session_state.ca_meq)
        st.session_state.ca_ppm = st.number_input("Ca²⁺ (ppm)", value=st.session_state.ca_ppm)
    with c2:
        st.session_state.mg_meq = st.number_input("Mg²⁺ (meq/100g)", value=st.session_state.mg_meq)
        st.session_state.mg_ppm = st.number_input("Mg²⁺ (ppm)", value=st.session_state.mg_ppm)
    with c3:
        st.session_state.k_meq = st.number_input("K⁺ (meq/100g)", value=st.session_state.k_meq)
        st.session_state.k_ppm = st.number_input("K⁺ (ppm)", value=st.session_state.k_ppm)
    with c4:
        st.session_state.na_meq = st.number_input("Na⁺ (meq/100g)", value=st.session_state.na_meq)
        st.session_state.cic_medida = st.number_input("CIC medida en laboratorio (meq/100g, 0=usar suma de bases)", value=st.session_state.cic_medida)

    c1, c2, c3, c4 = st.columns(4)
    st.session_state.fe_ppm = c1.number_input("Fe (ppm)", value=st.session_state.fe_ppm)
    st.session_state.mn_ppm = c2.number_input("Mn (ppm)", value=st.session_state.mn_ppm)
    st.session_state.cu_ppm = c3.number_input("Cu (ppm)", value=st.session_state.cu_ppm)
    st.session_state.zn_ppm = c4.number_input("Zn (ppm)", value=st.session_state.zn_ppm)

    suelo_placeholder = st.empty()

    st.markdown("---")
    st.subheader("Cultivo objetivo y necesidades")
    c1, c2 = st.columns(2)
    with c1:
        if st.session_state.cultivo not in cultivos_disponibles:
            st.session_state.cultivo = cultivos_disponibles[0]
        st.session_state.cultivo = st.selectbox("Cultivo objetivo", cultivos_disponibles,
                                                  index=cultivos_disponibles.index(st.session_state.cultivo),
                                                  format_func=lambda k: CULTIVO_EXTRACTIONS[k]["label"])
        st.session_state.rendimiento = st.number_input("Rendimiento esperado (t/ha)", value=st.session_state.rendimiento)
        st.session_state.margen_perdidas = st.number_input("Margen de pérdidas (factor, ej. 1.15 = +15%)", value=st.session_state.margen_perdidas, step=0.05)
    with c2:
        st.session_state.vol_riego = st.number_input("Volumen de riego (m³/ha)", value=st.session_state.vol_riego)
        st.session_state.nitratos_agua = st.number_input("Nitratos del agua de riego (mg/L NO₃⁻)", value=st.session_state.nitratos_agua)
        st.session_state.dep_atmosferica = st.number_input("Deposición atmosférica de N (kg/ha)", value=st.session_state.dep_atmosferica)
        st.session_state.restos_cosecha = st.number_input("Restos de cosecha (kg N/ha)", value=st.session_state.restos_cosecha)
        st.session_state.cubierta_veg = st.number_input("Cubierta vegetal (kg N/ha)", value=st.session_state.cubierta_veg)

    st.markdown("**Enmiendas orgánicas**")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("*Estiércol sólido (mineralización a 3 años)*")
        estiercol_keys = list(ESTIERCOL_DATA.keys())
        st.session_state.tipo_estiercol = st.selectbox("Tipo de estiércol", estiercol_keys,
                                                         index=estiercol_keys.index(st.session_state.tipo_estiercol),
                                                         format_func=lambda k: ESTIERCOL_DATA[k]["label"])
        st.session_state.dosis_estiercol_1 = st.number_input("Dosis año actual (t/ha)", value=st.session_state.dosis_estiercol_1, key="de1")
        st.session_state.dosis_estiercol_2 = st.number_input("Dosis año -1 (t/ha)", value=st.session_state.dosis_estiercol_2, key="de2")
        st.session_state.dosis_estiercol_3 = st.number_input("Dosis año -2 (t/ha)", value=st.session_state.dosis_estiercol_3, key="de3")
    with c2:
        st.markdown("*Purines (mineralización a 3 años)*")
        purin_keys = list(PURINES_DATA.keys())
        st.session_state.tipo_purin = st.selectbox("Tipo de purín", purin_keys,
                                                     index=purin_keys.index(st.session_state.tipo_purin),
                                                     format_func=lambda k: PURINES_DATA[k]["label"])
        st.session_state.dosis_purin_1 = st.number_input("Dosis año actual (m³/ha)", value=st.session_state.dosis_purin_1, key="dp1")
        st.session_state.dosis_purin_2 = st.number_input("Dosis año -1 (m³/ha)", value=st.session_state.dosis_purin_2, key="dp2")
        st.session_state.dosis_purin_3 = st.number_input("Dosis año -2 (m³/ha)", value=st.session_state.dosis_purin_3, key="dp3")
        if st.session_state.cultivo in ("olivar", "olivar_si") and (
            st.session_state.dosis_purin_1 or st.session_state.dosis_purin_2 or st.session_state.dosis_purin_3
        ):
            st.error("⚠️ ALERTA LEGAL: El Reglamento de Producción Integrada de Olivar prohíbe estrictamente el uso de purines o deyecciones líquidas.")

    balance_placeholder = st.empty()

# ================================================================== TAB 2: Plan NPK
with tabs[1]:
    st.subheader("Abonado de fondo y cobertera")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.key_fondo = st.selectbox("Fondo", fert_fondo_keys, index=fert_fondo_keys.index(st.session_state.key_fondo),
                                                    format_func=lambda k: FERT_DATA[k]["label"])
        st.session_state.dosis_fondo = st.number_input("Dosis fondo (kg/ha)", value=st.session_state.dosis_fondo, step=25.0)
    with c2:
        cob1_keys = ["0"] + FERT_COBERTERA_KEYS
        st.session_state.key_cob1 = st.selectbox("Cobertera 1", cob1_keys, index=cob1_keys.index(st.session_state.key_cob1) if st.session_state.key_cob1 in cob1_keys else 0,
                                                   format_func=lambda k: FERT_DATA[k]["label"])
        st.session_state.dosis_cob1 = st.number_input("Dosis cobertera 1 (kg/ha)", value=st.session_state.dosis_cob1, step=25.0)
        cob2_keys = ["0"] + FERT_COBERTERA2_KEYS
        st.session_state.key_cob2 = st.selectbox("Cobertera 2", cob2_keys, index=cob2_keys.index(st.session_state.key_cob2) if st.session_state.key_cob2 in cob2_keys else 0,
                                                   format_func=lambda k: FERT_DATA[k]["label"])
        st.session_state.dosis_cob2 = st.number_input("Dosis cobertera 2 (kg/ha)", value=st.session_state.dosis_cob2, step=25.0)

    st.markdown("---")
    st.subheader("🌿 Aplicación foliar")
    c1, c2, c3 = st.columns([3, 1, 1])
    sel_foliar = c1.selectbox("Producto foliar", list(FOLIARES_DB.keys()), key="pf_sel_foliar")
    dosis_foliar = c2.number_input("Dosis (kg-L/ha)", value=1.0, step=0.1, key="pf_dosis_foliar")
    if c3.button("➕ Añadir", key="pf_add_foliar"):
        st.session_state.pa_foliar_items.append({"name": sel_foliar, "dosis": dosis_foliar})
        st.rerun()
    for idx, item in enumerate(st.session_state.pa_foliar_items):
        cc = st.columns([3, 1, 1])
        cc[0].write(item["name"])
        nueva_dosis = cc[1].number_input("kg-L/ha", value=float(item["dosis"]), step=0.1, key=f"pf_foliar_dosis_{idx}", label_visibility="collapsed")
        st.session_state.pa_foliar_items[idx]["dosis"] = nueva_dosis
        if cc[2].button("🗑️", key=f"pf_del_foliar_{idx}"):
            st.session_state.pa_foliar_items.pop(idx)
            st.rerun()

    plan_placeholder = st.empty()

# ================================================================== TAB 3: Legal
with tabs[2]:
    st.session_state.zona_vulnerable = st.checkbox("📍 Parcela en Zona Vulnerable a Nitratos (Andalucía)", value=st.session_state.zona_vulnerable)
    st.session_state.produccion_integrada = st.checkbox("🌱 Explotación en Producción Integrada", value=st.session_state.produccion_integrada)
    if st.session_state.cultivo in ("olivar", "olivar_si") and st.session_state.produccion_integrada:
        regimenes = list(PI_NOTES["olivar"]["regimenLimits"].keys())
        st.session_state.regimen_olivar = st.selectbox("Régimen de cultivo del olivar (PI)", regimenes,
                                                         index=regimenes.index(st.session_state.regimen_olivar))
    diagnostico_placeholder = st.empty()

# ================================================================== TAB 4: Comparador de Planes
with tabs[3]:
    st.subheader("💰 Precio de venta de la cosecha")
    c1, c2 = st.columns(2)
    st.session_state.precio_venta = c1.number_input("Precio de venta", value=st.session_state.precio_venta, step=0.01)
    st.session_state.precio_venta_unit = c2.selectbox("Unidad", ["kg", "t"], index=["kg", "t"].index(st.session_state.precio_venta_unit))

    st.subheader("📋 Catálogo de fertilizantes — precio (€/tonelada)")
    st.caption("Solo hace falta poner precio a los productos que uses en el Plan Eurochem o en tus alternativas.")
    fert_keys_precio = [k for k in FERT_DATA if k != "0"]
    cols_precio = st.columns(3)
    for i, key in enumerate(fert_keys_precio):
        st.session_state.pf_precios[key] = cols_precio[i % 3].number_input(
            FERT_DATA[key]["label"], value=float(st.session_state.pf_precios.get(key, 0.0)),
            step=10.0, key=f"precio_{key}",
        )

    st.markdown("---")
    st.subheader("➕ Planes alternativos")
    if st.button("➕ Añadir plan alternativo"):
        st.session_state.pf_planes_alternativos.append({
            "nombre": f"Alternativa {len(st.session_state.pf_planes_alternativos) + 1}", "items": [],
        })
        st.rerun()

    for p_idx, plan_alt in enumerate(st.session_state.pf_planes_alternativos):
        with st.container(border=True):
            cc = st.columns([3, 1])
            plan_alt["nombre"] = cc[0].text_input("Nombre del plan", value=plan_alt["nombre"], key=f"pf_alt_nombre_{p_idx}")
            if cc[1].button("🗑️ Eliminar plan", key=f"pf_del_plan_{p_idx}"):
                st.session_state.pf_planes_alternativos.pop(p_idx)
                st.rerun()

            ac1, ac2, ac3, ac4 = st.columns([3, 1, 1, 1])
            sel_key = ac1.selectbox("Fertilizante", fert_keys_precio, format_func=lambda k: FERT_DATA[k]["label"], key=f"pf_alt_sel_{p_idx}")
            sel_qty = ac2.number_input("Dosis (kg/ha)", value=100.0, step=25.0, key=f"pf_alt_qty_{p_idx}")
            sel_fase = ac3.selectbox("Fase", ["fondo", "cobertera"], key=f"pf_alt_fase_{p_idx}")
            if ac4.button("➕ Añadir", key=f"pf_alt_add_{p_idx}"):
                plan_alt["items"].append({"fert_key": sel_key, "qty": sel_qty, "phase": sel_fase})
                st.rerun()

            for it_idx, it in enumerate(plan_alt["items"]):
                ic = st.columns([3, 1, 1, 1])
                ic[0].write(FERT_DATA[it["fert_key"]]["label"])
                ic[1].write(f"{it['qty']:.0f} kg/ha")
                ic[2].write(it["phase"])
                if ic[3].button("🗑️", key=f"pf_del_item_{p_idx}_{it_idx}"):
                    plan_alt["items"].pop(it_idx)
                    st.rerun()

    comparador_placeholder = st.empty()

# ================================================================== CÁLCULO CENTRAL
coef = CULTIVO_EXTRACTIONS[st.session_state.cultivo]

suelo = calcular_suelo(
    arcilla=st.session_state.arcilla, ph=st.session_state.suelo_ph, ce=st.session_state.ce,
    carbonatos=st.session_state.carbonatos, caliza_activa=st.session_state.caliza_activa,
    cn=st.session_state.cn, mo=st.session_state.mo, nitratos_lab=st.session_state.nitratos_lab,
    n_kjeldahl=st.session_state.n_kjeldahl, p_olsen=st.session_state.p_olsen,
    fe_ppm=st.session_state.fe_ppm, mn_ppm=st.session_state.mn_ppm, cu_ppm=st.session_state.cu_ppm, zn_ppm=st.session_state.zn_ppm,
    ca_meq=st.session_state.ca_meq, ca_ppm=st.session_state.ca_ppm, mg_meq=st.session_state.mg_meq, mg_ppm=st.session_state.mg_ppm,
    k_meq=st.session_state.k_meq, k_ppm=st.session_state.k_ppm, na_meq=st.session_state.na_meq,
    profundidad=st.session_state.profundidad, arena=st.session_state.arena, limo=st.session_state.limo,
    cic_medida=st.session_state.cic_medida,
)

balance_n = calcular_balance_n(
    rendimiento=st.session_state.rendimiento, coef_n=coef["n"], ajuste_n_textura=suelo.ajuste_n_textura,
    margen_perdidas=st.session_state.margen_perdidas, vol_riego=st.session_state.vol_riego,
    nitratos_agua=st.session_state.nitratos_agua, restos_cosecha=st.session_state.restos_cosecha,
    cubierta_veg=st.session_state.cubierta_veg, tipo_estiercol=st.session_state.tipo_estiercol,
    dosis_estiercol_1=st.session_state.dosis_estiercol_1, dosis_estiercol_2=st.session_state.dosis_estiercol_2,
    dosis_estiercol_3=st.session_state.dosis_estiercol_3, tipo_purin=st.session_state.tipo_purin,
    dosis_purin_1=st.session_state.dosis_purin_1, dosis_purin_2=st.session_state.dosis_purin_2,
    dosis_purin_3=st.session_state.dosis_purin_3, stock_nitratos=suelo.stock_nitratos, kg_n_mo=suelo.kg_n_mo,
    dep_atmosferica=st.session_state.dep_atmosferica,
)

pk = calcular_p_k(rendimiento=st.session_state.rendimiento, coef_p=coef["p"], coef_k=coef["k"],
                   p_factor=suelo.p_factor, carb_p_factor=suelo.carb_p_factor, k_factor=suelo.k_factor)

plan = calcular_plan_npk(
    key_fondo=st.session_state.key_fondo, dosis_fondo=st.session_state.dosis_fondo,
    key_cob1=st.session_state.key_cob1, dosis_cob1=st.session_state.dosis_cob1,
    key_cob2=st.session_state.key_cob2, dosis_cob2=st.session_state.dosis_cob2,
    foliar_items=st.session_state.pa_foliar_items, balance_final_n=balance_n.balance_final_n,
    p_necesidad=pk.p_necesidad_corregida, k_necesidad=pk.k_necesidad_corregida,
)

diagnostico_html = generar_diagnostico_estrategia(
    n_restante=plan.n_restante, p_balance=plan.p_balance, k_balance=plan.k_balance,
    n_total=plan.n_total, p_total=plan.p_total, k_total=plan.k_total,
    key_fondo=st.session_state.key_fondo, pct_n_fondo=plan.pct_n_fondo, cultivo_key=st.session_state.cultivo,
    vulnerable=st.session_state.zona_vulnerable, produccion_integrada=st.session_state.produccion_integrada,
    rendimiento=st.session_state.rendimiento, regimen_olivar=st.session_state.regimen_olivar,
)
diagnostico_suelo_html = generar_diagnostico_suelo(suelo.p_recomendacion_detalle, suelo.k_recomendacion_detalle)

# ---------------------------------------------------------------- Render Tab 1
with suelo_placeholder.container():
    st.markdown("---")
    st.subheader("Diagnóstico del suelo")
    st.write(f"Densidad aparente calculada: **{suelo.da_calculada:.2f} kg/L** — {suelo.c_arcilla}")
    st.write(suelo.c_textura_usda)
    c1, c2, c3 = st.columns(3)
    c1.write(f"pH: {suelo.c_ph}")
    c2.write(f"CE: {suelo.c_ce}")
    c3.write(f"C/N: {suelo.c_cn}")
    st.write(suelo.c_nitratos + " " + suelo.c_kjeldahl)
    st.write(suelo.c_mo)
    st.write(f"P Olsen: {suelo.p_suelo_lbl} (factor {suelo.p_factor:.2f}) — {suelo.c_caliza_activa}")
    st.write(f"K asimilable: {suelo.k_suelo_lbl} (factor {suelo.k_factor:.2f})")
    c1, c2, c3, c4 = st.columns(4)
    c1.write(f"Fe: {suelo.c_fe}"); c2.write(f"Mn: {suelo.c_mn}"); c3.write(f"Cu: {suelo.c_cu}"); c4.write(f"Zn: {suelo.c_zn}")

    st.markdown("**Complejo de cambio (CIC) y saturación de bases**")
    st.write(f"CIC: **{suelo.cic:.2f} meq/100g** — {suelo.c_cic}")
    df_sat = pd.DataFrame({
        "Base": ["Ca²⁺", "Mg²⁺", "K⁺", "Na⁺ (PSI)"],
        "Saturación (%)": [suelo.sat_ca, suelo.sat_mg, suelo.sat_k, suelo.sat_na],
        "Diagnóstico": [suelo.c_sat_ca, suelo.c_sat_mg, suelo.c_sat_k, suelo.c_psicalc],
    })
    st.dataframe(df_sat.style.format({"Saturación (%)": "{:.1f}"}), use_container_width=True, hide_index=True)

    st.markdown("**Relaciones catiónicas y antagonismos**")
    df_rel = pd.DataFrame({
        "Relación": ["Ca/Mg", "Mg/K", "Ca/K", "(Ca+Mg)/K", "Woodruff K/√(Ca+Mg)"],
        "Valor": [suelo.rel_ca_mg, suelo.rel_mg_k, suelo.rel_ca_k, suelo.rel_ca_mg_k, suelo.woodruff],
        "Diagnóstico": [suelo.c_rel_camg, suelo.c_rel_mgk, suelo.c_rel_cak, suelo.c_rel_camgk, suelo.c_woodruff],
    })
    st.dataframe(df_rel.style.format({"Valor": "{:.2f}"}), use_container_width=True, hide_index=True)
    st.markdown(suelo.diag_k, unsafe_allow_html=True)
    st.markdown(suelo.diag_mg, unsafe_allow_html=True)

with balance_placeholder.container():
    st.markdown("---")
    st.subheader("Balance de Nitrógeno")
    df_n = pd.DataFrame({
        "Origen": ["Necesidad bruta (objetivo)", "Stock de nitratos en suelo", "Mineralización de M.O.",
                   "Deposición atmosférica", "Agua de riego", "Restos/cubierta vegetal",
                   "Enmiendas orgánicas (estiércol+purín)", "Total de aportes", "Balance final a cubrir"],
        "kg N/ha": [balance_n.necesidad_bruta_n, balance_n.stock_nitratos, balance_n.kg_n_mo,
                    st.session_state.dep_atmosferica, balance_n.n_agua, balance_n.n_verde,
                    balance_n.n_organico_total, balance_n.total_aportes_n, balance_n.balance_final_n],
    })
    st.dataframe(df_n.style.format({"kg N/ha": "{:.1f}"}), use_container_width=True, hide_index=True)

    if balance_n.supera_limite_rd1051:
        st.error(f"⚠️ EXCESO LEGAL: Aporte orgánico actual de {balance_n.n_organico_fisico_actual:.1f} kg N/ha supera el límite de 170 kg N/ha (RD 1051/2022).")
    else:
        st.success(f"✅ Cumplimiento de Límites del RD 1051/2022 ({balance_n.n_organico_fisico_actual:.1f} kg N/ha orgánico).")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Necesidad de P₂O₅ corregida", f"{pk.p_necesidad_corregida} kg/ha", help=f"Extracción teórica: {pk.p_extraccion_teorica:.1f} kg/ha")
    with c2:
        st.metric("Necesidad de K₂O corregida", f"{pk.k_necesidad_corregida} kg/ha", help=f"Extracción teórica: {pk.k_extraccion_teorica:.1f} kg/ha")

    st.markdown("**Diagnóstico de correcciones de suelo (P y K)**")
    st.markdown(diagnostico_suelo_html, unsafe_allow_html=True)

# ---------------------------------------------------------------- Render Tab 2
with plan_placeholder.container():
    st.markdown("---")
    st.subheader("Aporte total del plan")
    cols = {"n": "N", "p": "P₂O₅", "k": "K₂O", "mg": "MgO", "ca": "CaO", "s": "SO₃"}
    df_plan = pd.DataFrame({
        "Origen": ["Fondo", "Cobertera 1", "Cobertera 2", "Total plan"],
        **{label: [
            getattr(plan.fondo, key), getattr(plan.cob1, key), getattr(plan.cob2, key),
            getattr(plan, f"{key}_total"),
        ] for key, label in cols.items()},
    })
    st.dataframe(df_plan.style.format({v: "{:.1f}" for v in cols.values()}), use_container_width=True, hide_index=True)

    if plan.foliar_items:
        st.write(f"**Micronutrientes vía foliar (g/ha):** Fe: {plan.fe_foliar:.1f} | Mn: {plan.mn_foliar:.1f} | "
                 f"Zn: {plan.zn_foliar:.1f} | Cu: {plan.cu_foliar:.1f} | B: {plan.b_foliar:.1f} | Mo: {plan.mo_foliar:.2f}")

    c1, c2, c3 = st.columns(3)
    c1.metric("N restante a cubrir en cobertera", f"{max(plan.n_restante, 0):.1f} UF")
    c2.metric("Balance P₂O₅", f"{'+' if plan.p_balance >= 0 else ''}{plan.p_balance:.1f} kg/ha")
    c3.metric("Balance K₂O", f"{'+' if plan.k_balance >= 0 else ''}{plan.k_balance:.1f} kg/ha")
    st.write(f"% de N aportado por fase — Fondo: {plan.pct_n_fondo}% | Cobertera 1: {plan.pct_n_cob1}% | Cobertera 2: {plan.pct_n_cob2}%")

# ---------------------------------------------------------------- Render Tab 3
with diagnostico_placeholder.container():
    st.markdown("---")
    st.markdown(diagnostico_html, unsafe_allow_html=True)

# ---------------------------------------------------------------- Render Tab 4 (Comparador de Planes)
zvn_notes_cultivo = CULTIVO_ZVN_NOTES.get(st.session_state.cultivo)
cap_aplica = zvn_notes_cultivo["cap30"] if zvn_notes_cultivo else True
limite_legal_pf = legal_n_limit(st.session_state.cultivo, st.session_state.rendimiento)
pi_notes_cultivo = PI_NOTES.get(st.session_state.cultivo)
limite_pi_pf = pi_n_limit(pi_notes_cultivo, st.session_state.regimen_olivar) if (st.session_state.produccion_integrada and pi_notes_cultivo) else None
precio_kg_cosecha = (
    st.session_state.precio_venta / 1000.0 if st.session_state.precio_venta_unit == "t" else st.session_state.precio_venta
) or None

items_eurochem = pf_sync_plan_eurochem(
    key_fondo=st.session_state.key_fondo, dosis_fondo=st.session_state.dosis_fondo,
    key_cob1=st.session_state.key_cob1, dosis_cob1=st.session_state.dosis_cob1,
    key_cob2=st.session_state.key_cob2, dosis_cob2=st.session_state.dosis_cob2,
)
planes_calculados = [pf_calc_plan(
    nombre="Plan Eurochem", items=items_eurochem, precios=st.session_state.pf_precios,
    vulnerable=st.session_state.zona_vulnerable, cap_aplica=cap_aplica, limite_legal=limite_legal_pf,
    pi_activo=st.session_state.produccion_integrada, limite_pi=limite_pi_pf, precio_por_kg_cosecha=precio_kg_cosecha,
)]
for plan_alt in st.session_state.pf_planes_alternativos:
    planes_calculados.append(pf_calc_plan(
        nombre=plan_alt["nombre"], items=plan_alt["items"], precios=st.session_state.pf_precios,
        vulnerable=st.session_state.zona_vulnerable, cap_aplica=cap_aplica, limite_legal=limite_legal_pf,
        pi_activo=st.session_state.produccion_integrada, limite_pi=limite_pi_pf, precio_por_kg_cosecha=precio_kg_cosecha,
    ))

with comparador_placeholder.container():
    st.markdown("---")
    st.subheader("📊 Comparativa de planes")
    df_comp = pd.DataFrame([{
        "Plan": r.nombre, "Coste (€/ha)": r.cost_ha, "N (kg/ha)": r.n_ha, "P₂O₅": r.p_ha, "K₂O": r.k_ha,
        "MgO": r.mg_ha, "CaO": r.ca_ha, "SO₃": r.s_ha, "% N en fondo (sin exención)": r.fondo_cap_pct,
        "€/kg cosecha (payback)": f"{r.payback_kg_ha:.1f}" if r.payback_kg_ha is not None else "—",
    } for r in planes_calculados])
    cols_numericas = [c for c in df_comp.columns if c not in ("Plan", "€/kg cosecha (payback)")]
    st.dataframe(
        df_comp.style.format({c: "{:.1f}" for c in cols_numericas}),
        use_container_width=True, hide_index=True,
    )

    for r in planes_calculados:
        avisos = []
        if r.excede_tope_fondo:
            avisos.append(f"❌ **{r.nombre}** supera el 30% de N en fondo sin inhibidor ({r.fondo_cap_pct:.0f}%).")
        if r.excede_limite_legal:
            avisos.append(f"❌ **{r.nombre}** supera el tope legal de N en Zona Vulnerable ({r.n_ha:.1f} / {limite_legal_pf:.1f} kg N/ha).")
        if r.excede_limite_pi:
            avisos.append(f"❌ **{r.nombre}** supera el límite de N de Producción Integrada ({r.n_ha:.1f} / {limite_pi_pf:.1f} kg N/ha).")
        for a in avisos:
            st.error(a)
        if not avisos and (r.cost_ha > 0 or r.n_ha > 0):
            st.success(f"✅ **{r.nombre}** dentro de los límites de cumplimiento comprobados.")
