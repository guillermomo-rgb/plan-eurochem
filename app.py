# -*- coding: utf-8 -*-
"""Punto de entrada de la app Eurochem Agro. Usa páginas de Streamlit
(carpeta pages/) para cada herramienta — ver la barra lateral."""
import streamlit as st

st.set_page_config(page_title="Eurochem Agro — Herramientas", page_icon="🌱", layout="wide")

st.title("🌱 Eurochem Agro — Herramientas Agronómicas")
st.write(
    "Selecciona una herramienta en la barra lateral. Convertidas desde las versiones "
    "HTML originales, revisando y validando la lógica de cálculo en el proceso."
)

st.markdown("---")
st.subheader("Disponibles")
st.markdown(
    "- **💧 Análisis de Agua de Riego** — calidad del agua, riesgos FAO-29 de "
    "infiltración y toxicidad, dosificación de ácidos y plan de cloración.\n"
    "- **🧪 Programa de Fertirrigación** — balance anual NPK+Mg+Ca+S, agua de riego, "
    "neutralización de ácidos, fondo granulado y foliares, plan mensual por fases, "
    "gotero de Sonneveld y dictamen agronómico experto.\n"
    "- **📊 Plan de Abonado Integrado** — analítica de suelo (textura USDA, CIC, "
    "saturación de bases, antagonismos catiónicos), balance de N con enmiendas "
    "orgánicas, plan NPK Eurochem con foliares, y cumplimiento de Zona Vulnerable "
    "a Nitratos y Producción Integrada.\n"
    "- **🌿 NutriLeaf Pro** — diagnóstico foliar de suficiencia (DOP) y ratios de "
    "equilibrio para 9 cultivos, sistema DRIS completo para Olivo (3 y 10 puntos), "
    "Almendro (por variedad) y Caqui, y recomendaciones de abonado con factor de "
    "corrección."
)

st.subheader("Fuera de alcance de esta conversión")
st.markdown(
    "- Comparador de planes de abonado (coste Plan Eurochem vs. alternativas) del "
    "Plan de Abonado Integrado\n"
    "- Histórico multi-año, sparklines y exportación CSV de NutriLeaf Pro\n"
)
