# -*- coding: utf-8 -*-
"""NutriLeaf Pro — diagnóstico foliar (puerto de nutrileaf_pro.html).

No incluye el histórico multi-año (localStorage, sparklines, export CSV) del
HTML original — queda fuera de este primer puerto.
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.nutrileaf_data import BASE_DE_DATOS_CULTIVOS, NOMBRES_NUTRIENTES  # noqa: E402
from shared.nutrileaf_calc import (  # noqa: E402
    analizar_suficiencia, evaluar_ratios, generar_recomendaciones,
    calcular_dris_olivo_3p, calcular_dris_olivo_10p, alertas_condicionales_olivo,
    calcular_dris_almendro, calcular_dris_caqui,
)
from shared.ui_common import render_header, render_print_button  # noqa: E402

st.set_page_config(page_title="NutriLeaf Pro", page_icon="🌿", layout="wide")
render_header("NutriLeaf Pro — Diagnóstico Foliar", "🌿")
render_print_button()

CULTIVOS_SELECCIONABLES = {
    "olivo": "Olivo", "viña": "Viña", "almendro": "Almendro", "caqui": "Caqui 'Rojo Brillante'",
    "citricos": "Cítricos", "aguacate": "Aguacate", "tomate": "Tomate",
    "melocoton": "Melocotón", "pistacho": "Pistacho", "personalizado": "Personalizado",
}
ELEMENTOS_BASE = ["N", "P", "K", "Ca", "Mg", "Fe", "Mn", "Zn", "Cu", "B"]
BADGE_COLOR = {"muy-bajo": "🔴", "bajo": "🟠", "optimo": "🟢", "alto": "🔵", "muy-alto": "🟣", "muted": "⚪"}

DEFAULTS = dict(
    cultivo="olivo", almendro_variedad="ferraduel",
    dris_sistema="secano", dris_zona="otra",
)
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)
for el in ELEMENTOS_BASE + ["Na", "S", "Cl"]:
    st.session_state.setdefault(f"val_{el}", 0.0)
for el in ELEMENTOS_BASE:
    st.session_state.setdefault(f"norm_{el}", 0.0)

st.sidebar.subheader("Configuración")
cultivo_keys = list(CULTIVOS_SELECCIONABLES.keys())
st.session_state.cultivo = st.sidebar.selectbox(
    "Cultivo", cultivo_keys, index=cultivo_keys.index(st.session_state.cultivo),
    format_func=lambda k: CULTIVOS_SELECCIONABLES[k],
)
cultivo = st.session_state.cultivo

if cultivo == "almendro":
    variedades = {"generico": "Genérico (sin DRIS)", "ferraduel": "Ferraduel", "ferragnes": "Ferragnès", "garrigues": "Garrigues"}
    var_keys = list(variedades.keys())
    st.session_state.almendro_variedad = st.sidebar.selectbox(
        "Variedad de almendro", var_keys, index=var_keys.index(st.session_state.almendro_variedad),
        format_func=lambda k: variedades[k],
    )
    normas_key = "almendro_" + st.session_state.almendro_variedad if st.session_state.almendro_variedad != "generico" else "almendro_generico"
elif cultivo != "personalizado":
    normas_key = cultivo
else:
    normas_key = None

if cultivo == "olivo":
    st.sidebar.markdown("**Configuración DRIS Olivo**")
    sistemas = {"secano": "Secano", "regadio": "Regadío", "superintensivo": "Superintensivo (seto)"}
    sist_keys = list(sistemas.keys())
    st.session_state.dris_sistema = st.sidebar.selectbox("Sistema de manejo", sist_keys, index=sist_keys.index(st.session_state.dris_sistema), format_func=lambda k: sistemas[k])
    zonas = {"otra": "Otra / no aplica", "Guadalquivir_Arcillas": "Valle del Guadalquivir (suelos arcillosos)"}
    zona_keys = list(zonas.keys())
    st.session_state.dris_zona = st.sidebar.selectbox("Zona edafoclimática", zona_keys, index=zona_keys.index(st.session_state.dris_zona), format_func=lambda k: zonas[k])

datos_cultivo = BASE_DE_DATOS_CULTIVOS.get(normas_key) if normas_key else None
if datos_cultivo:
    st.caption(f"Momento de muestreo: {datos_cultivo['ventanaMuestreo']['texto']}. Fuente: {datos_cultivo['fuenteCultivo']}")

st.subheader("Valores del análisis foliar")
if cultivo == "personalizado":
    st.markdown("**Niveles de referencia recomendados por tu laboratorio**")
    cc = st.columns(5)
    for i, el in enumerate(ELEMENTOS_BASE):
        st.session_state[f"norm_{el}"] = cc[i % 5].number_input(f"Óptimo {el}", value=st.session_state[f"norm_{el}"], key=f"normin_{el}")
    normas = {}
    for el in ELEMENTOS_BASE:
        opt = st.session_state[f"norm_{el}"]
        normas[el] = {"mb": opt * 0.7, "o_min": opt * 0.9, "o_max": opt * 1.1, "alto_max": opt * 1.3,
                      "unit": "%" if el in ("N", "P", "K", "Ca", "Mg") else "mg/kg"}
else:
    normas = datos_cultivo or {}

# "N" y "S" se etiquetan con el nombre completo: sueltas, el traductor automático del navegador
# las confunde con los puntos cardinales "Norte"/"Sur" (ver bug reportado en Fertirrigación).
ETIQUETA_ELEMENTO = {"N": "N (Nitrógeno)", "S": "S (Azufre)"}
cc = st.columns(5)
valores = {}
for i, el in enumerate(ELEMENTOS_BASE):
    etiqueta = ETIQUETA_ELEMENTO.get(el, el)
    valores[el] = cc[i % 5].number_input(f"{etiqueta} ({(normas.get(el) or {}).get('unit', '')})", value=st.session_state[f"val_{el}"], key=f"valin_{el}", step=0.01, format="%.3f")

if cultivo == "caqui":
    st.markdown("**Elementos adicionales del sistema DRIS de Caqui (13 elementos)**")
    cc2 = st.columns(3)
    valores["Na"] = cc2[0].number_input("Na (Sodio) (%)", value=st.session_state["val_Na"], key="valin_Na", format="%.4f")
    valores["S"] = cc2[1].number_input("S (Azufre) (%)", value=st.session_state["val_S"], key="valin_S", format="%.3f")
    valores["Cl"] = cc2[2].number_input("Cl (Cloruro) (%)", value=st.session_state["val_Cl"], key="valin_Cl_caqui", format="%.3f")
elif cultivo == "aguacate":
    valores["Cl"] = st.number_input("Cl⁻ (%) — umbral de toxicidad", value=st.session_state["val_Cl"], key="valin_Cl_aguacate", format="%.3f")

# Descartar elementos en cero (no introducidos) para que no contaminen DOP/ratios/DRIS con ceros falsos
valores_activos = {k: v for k, v in valores.items() if v}

st.markdown("---")

tabs = st.tabs(["📋 Estado nutricional", "⚖️ Ratios de equilibrio", "🧬 Sistema DRIS", "💊 Recomendaciones"])

# ================================================================== TAB 1: Suficiencia
with tabs[0]:
    if not valores_activos:
        st.info("Introduce los valores del análisis foliar arriba para ver el diagnóstico.")
    else:
        resultado = analizar_suficiencia(valores_activos, normas, cultivo)
        if resultado.elemento_mas_limitante:
            st.warning(
                f"**Factor limitante crítico detectado por DOP:** El elemento más limitante es el "
                f"**{resultado.elemento_mas_limitante}** con un déficit del "
                f"**{abs(resultado.dop_mas_limitante):.1f}%** sobre su nivel fisiológico óptimo de producción."
            )
        else:
            st.info("Sin nutrientes clasificables con la bibliografía disponible para este cultivo.")

        if datos_cultivo and datos_cultivo.get("ventanaMuestreo", {}).get("meses"):
            st.caption("⚠️ Recuerda comparar solo si la muestra se tomó en la ventana fenológica de referencia indicada arriba.")

        filas_data = [{"Elemento": f.elemento, "Valor": f.valor, "Rango óptimo": f.rango_optimo,
                       "Estado": f"{BADGE_COLOR.get(f.badge, '')} {f.estado}",
                       "DOP": f"{f.dop_pct:.1f}%" if f.dop_pct is not None else "N/D"} for f in resultado.filas]
        if resultado.cl_fila:
            f = resultado.cl_fila
            filas_data.append({"Elemento": f.elemento, "Valor": f.valor, "Rango óptimo": f.rango_optimo,
                                "Estado": f"{BADGE_COLOR.get(f.badge, '')} {f.estado}", "DOP": "N/A"})
        for el in resultado.sin_bibliografia:
            if valores_activos.get(el):
                filas_data.append({"Elemento": el, "Valor": valores_activos[el], "Rango óptimo": "—", "Estado": "⚪ SIN DATO", "DOP": "N/D"})

        st.dataframe(pd.DataFrame(filas_data), use_container_width=True, hide_index=True)

        if datos_cultivo:
            notas = [f"**Fuente de las tablas de referencia:** {datos_cultivo['fuenteCultivo']}"]
            for el, ref in datos_cultivo.items():
                if isinstance(ref, dict) and ref.get("nota"):
                    notas.append(f"• **{el}:** {ref['nota']}")
            st.caption("  \n".join(notas))

# ================================================================== TAB 2: Ratios
with tabs[1]:
    if not valores_activos:
        st.info("Introduce los valores del análisis foliar para ver los ratios de equilibrio.")
    else:
        filas_ratio, es_generico, fuente = evaluar_ratios(valores_activos, cultivo)
        if es_generico:
            st.caption("Umbrales genéricos universales (no calibrados específicamente para este cultivo).")
        else:
            st.caption(f"Fuente: {fuente}")
        color_icon = {"ok": "🟢", "warn": "🟠", "danger": "🔴", "muted": "⚪"}
        df_ratios = pd.DataFrame([{
            "Relación": f.nombre,
            "Valor": f"{f.valor:.2f}" if f.valor is not None else "N/D",
            "Rango": f"{f.minimo if f.minimo is not None else '—'} - {f.maximo if f.maximo is not None else '—'}",
            "Evaluación": f"{color_icon.get(f.color, '')} {f.evaluacion}",
        } for f in filas_ratio])
        st.dataframe(df_ratios, use_container_width=True, hide_index=True)

# ================================================================== TAB 3: DRIS
with tabs[2]:
    if not valores_activos:
        st.info("Introduce los valores del análisis foliar para calcular los índices DRIS.")
    elif cultivo == "olivo":
        st.subheader("DRIS Olivo — Modelo de 3 puntos (UCO / Beaufils)")
        try:
            r3 = calcular_dris_olivo_3p(valores_activos, st.session_state.dris_sistema)
            df3 = pd.DataFrame([{"Nutriente": f.nutriente, "Índice DRIS": f"{f.indice:.1f}", "Diagnóstico": f.descripcion, "Prioridad": f.prioridad} for f in r3.filas])
            st.dataframe(df3, use_container_width=True, hide_index=True)
            st.metric("Índice de Balance Nutricional (IBN)", f"{r3.ibn:.1f}")

            for a in alertas_condicionales_olivo(sistema=st.session_state.dris_sistema, zona=st.session_state.dris_zona, ind_n_3p=r3.ind_n, ind_k_3p=r3.ind_k):
                st.warning(a)

            st.subheader("DRIS Olivo — Modelo completo de 10 puntos (CSR / Jones)")
            filas10, ibn10 = calcular_dris_olivo_10p(valores_activos)
            df10 = pd.DataFrame([{"Nutriente": f.nutriente, "Índice DRIS": f"{f.indice:.1f}", "Diagnóstico": f.descripcion, "Prioridad": f.prioridad} for f in filas10])
            st.dataframe(df10, use_container_width=True, hide_index=True)
            st.metric("Índice de Balance Nutricional (IBN, 10P)", f"{ibn10:.1f}")
        except (KeyError, ZeroDivisionError):
            st.error("Introduce todos los macro y micronutrientes (N, P, K, Ca, Mg, B, Fe, Mn, Zn, Cu) con valores distintos de cero para calcular el DRIS de Olivo.")
    elif cultivo == "almendro":
        if st.session_state.almendro_variedad == "generico":
            st.warning('⚠️ Selecciona una variedad concreta (Ferraduel, Ferragnès o Garrigues) en la barra lateral para activar el DRIS de almendro. La norma genérica no tiene DRIS asociado — solo rango de suficiencia.')
        else:
            try:
                filas, ibn = calcular_dris_almendro(valores_activos, st.session_state.almendro_variedad)
                df = pd.DataFrame([{"Nutriente": f.nutriente, "Índice DRIS": f"{f.indice:.1f}", "Diagnóstico": f.descripcion, "Prioridad": f.prioridad} for f in filas])
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.metric("Índice de Balance Nutricional (IBN)", f"{ibn:.1f}")
                if st.session_state.almendro_variedad == "garrigues":
                    st.caption("⚠️ 3 de las 10 normas de Garrigues se reinterpretaron por posibles erratas de la Tabla 4 original (ver notas en el código fuente). Contrastar con los autores antes de un uso crítico.")
            except (KeyError, ZeroDivisionError):
                st.error("Introduce N, P, K, Ca y Mg con valores distintos de cero para calcular el DRIS de Almendro.")
    elif cultivo == "caqui":
        try:
            filas, ibn = calcular_dris_caqui(valores_activos)
            df = pd.DataFrame([{"Nutriente": f.nutriente, "Índice DRIS": f"{f.indice:.1f}", "Diagnóstico": f.descripcion, "Prioridad": f.prioridad} for f in filas])
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.metric("Índice de Balance Nutricional (IBN)", f"{ibn:.1f}")
        except (KeyError, ZeroDivisionError):
            st.error("Introduce los 13 elementos (N, P, K, Ca, Mg, Na, S, Cl, B, Cu, Fe, Mn, Zn) con valores distintos de cero para calcular el DRIS de Caqui.")
    else:
        st.info("El sistema DRIS solo está disponible para Olivo, Almendro y Caqui en esta conversión.")

# ================================================================== TAB 4: Recomendaciones
with tabs[3]:
    if not valores_activos:
        st.info("Introduce los valores del análisis foliar para generar recomendaciones de abonado.")
    else:
        resultado = analizar_suficiencia(valores_activos, normas, cultivo)
        recs = generar_recomendaciones(valores_activos, normas, resultado.sin_bibliografia)
        # Mismo orden que la tabla de suficiencia: más limitante primero
        orden = {f.elemento: i for i, f in enumerate(sorted(resultado.filas, key=lambda f: f.dop_pct if f.dop_pct is not None else 0))}
        recs.sort(key=lambda r: orden.get(r.elemento, 999))
        color_border = {"danger": "🔴", "warn": "🟠", "indigo": "🟣", "alto-consumo": "🔵", "ok": "🟢"}
        for r in recs:
            with st.container(border=True):
                st.markdown(f"### {color_border.get(r.color, '')} {r.elemento} ({r.estado})")
                st.write(r.accion)
                st.caption(f"Producto de referencia: {r.producto}")
                st.write(f"**Factor de ajuste sugerido:** {r.factor:.1f}x")
