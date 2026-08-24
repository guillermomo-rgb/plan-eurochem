# -*- coding: utf-8 -*-
"""Punto de entrada de la app Eurochem Agro. Usa páginas de Streamlit
(carpeta pages/) para cada herramienta — ver la barra lateral."""
import streamlit as st

st.set_page_config(page_title="Eurochem Agro — Herramientas", page_icon="🌱", layout="wide")

st.title("🌱 Eurochem Agro — Herramientas Agronómicas")
st.write(
    "Selecciona una herramienta en la barra lateral. Conversión en curso desde las "
    "versiones HTML originales; cada herramienta se traslada aquí de forma progresiva, "
    "revisando y validando la lógica de cálculo en el proceso."
)

st.markdown("---")
st.subheader("Disponibles")
st.markdown(
    "- **💧 Análisis de Agua de Riego** — calidad del agua, riesgos FAO-29 de "
    "infiltración y toxicidad, dosificación de ácidos y plan de cloración.\n"
    "- **🧪 Programa de Fertirrigación** — balance anual NPK+Mg+Ca+S, agua de riego, "
    "neutralización de ácidos, fondo granulado y foliares, plan mensual por fases, "
    "gotero de Sonneveld y dictamen agronómico experto."
)

st.subheader("Pendientes de convertir")
st.markdown(
    "- 📊 Plan de Abonado Integrado (balance NPK Eurochem, comparador de planes)\n"
    "- 🌿 NutriLeaf Pro (diagnóstico foliar DRIS)\n"
)
