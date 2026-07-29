# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import base64  # 👈 Esta línea es vital para que cargue el logotipo de Eurochem

# =====================================================================
if "fondo_sum_n" not in st.session_state: st.session_state.fondo_sum_n = 0.0
if "fondo_sum_p" not in st.session_state: st.session_state.fondo_sum_p = 0.0
if "fondo_sum_k" not in st.session_state: st.session_state.fondo_sum_k = 0.0
if "fondo_sum_mg" not in st.session_state: st.session_state.fondo_sum_mg = 0.0
if "fondo_sum_ca" not in st.session_state: st.session_state.fondo_sum_ca = 0.0
if "fondo_sum_s" not in st.session_state: st.session_state.fondo_sum_s = 0.0
# =====================================================================
# === LAS 9 LÍNEAS MÁGICAS (DEFINICIÓN DE CLAVES DE SEGURIDAD) ===
n = "n"
p = "p"
k = "k"
mg = "mg"
ca = "ca"
s = "s"
nh4 = "nh4"
no3 = "no3"
ec_coeff = "ec_coeff"

# === TU BASE DE DATOS DE CULTIVOS COMPLETA (VERSIÓN BLINDADA CON COMILLAS) ===
CULTIVOS_DB = {
    "Caqui (Kaki)": { "n": 4.00, "p": 1.00, "k": 3.50, "mg": 0.60, "ca": 1.50, "s": 0.80, "limite_salino": 1.3 },
    "Pimiento": { "n": 4.40, "p": 1.60, "k": 5.50, "mg": 0.80, "ca": 2.50, "s": 1.80, "limite_salino": 1.8 },
    "Tomate": { "n": 2.20, "p": 0.80, "k": 2.60, "mg": 0.70, "ca": 2.00, "s": 1.50, "limite_salino": 2.5 },
    "Limonero": { "n": 5.00, "p": 1.20, "k": 4.00, "mg": 0.80, "ca": 1.80, "s": 0.90, "limite_salino": 1.7 },
    "Mandarino": { "n": 5.30, "p": 1.10, "k": 3.80, "mg": 0.70, "ca": 1.60, "s": 0.85, "limite_salino": 1.7 },
    "Naranjo": { "n": 4.10, "p": 1.50, "k": 3.50, "mg": 0.40, "ca": 2.00, "s": 1.20, "limite_salino": 1.7 },
    "Olivar SI": { "n": 8.00, "p": 4.00, "k": 12.00, "mg": 1.20, "ca": 2.50, "s": 1.00, "limite_salino": 2.5 },
    "Olivar": { "n": 12.00, "p": 4.00, "k": 10.00, "mg": 4.00, "ca": 8.00, "s": 2.00, "limite_salino": 2.5 },
    "Aguacate": { "n": 12.00, "p": 7.00, "k": 20.00, "mg": 1.50, "ca": 3.50, "s": 2.00, "limite_salino": 0.6 },
    "Almendro (pepita)": { "n": 65.00, "p": 25.00, "k": 70.00, "mg": 2.00, "ca": 8.00, "s": 10.00, "limite_salino": 1.5 },
    "Cebolla": { "n": 3.50, "p": 1.50, "k": 4.00, "mg": 0.50, "ca": 1.80, "s": 3.80, "limite_salino": 1.2 },
    "Patata": { "n": 4.50, "p": 1.80, "k": 7.50, "mg": 0.80, "ca": 1.00, "s": 0.90, "limite_salino": 1.7 },
    "Fresa": { "n": 4.50, "p": 1.50, "k": 6.50, "mg": 1.00, "ca": 2.00, "s": 1.00, "limite_salino": 1.0 },
    "Pistacho (grano seco)": { "n": 55.00, "p": 20.00, "k": 60.00, "mg": 12.00, "ca": 18.00, "s": 4.50, "limite_salino": 6.0 },
    "Vid vinificación": { "n": 4.00, "p": 1.50, "k": 5.00, "mg": 1.00, "ca": 2.00, "s": 0.90, "limite_salino": 1.5 },
    "Melocotón": { "n": 3.50, "p": 1.80, "k": 4.00, "mg": 0.80, "ca": 1.70, "s": 1.20, "limite_salino": 1.7 },
    "Nectarina": { "n": 4.00, "p": 1.00, "k": 6.00, "mg": 1.00, "ca": 1.80, "s": 1.20, "limite_salino": 1.7 },
    "Nispero": { "n": 8.00, "p": 4.00, "k": 8.00, "mg": 1.00, "ca": 2.20, "s": 1.50, "limite_salino": 1.5 },
    "Espárrago": { "n": 10.00, "p": 3.00, "k": 12.00, "mg": 1.50, "ca": 3.00, "s": 2.00, "limite_salino": 4.1 },
    "Sandía": { "n": 2.40, "p": 1.30, "k": 3.20, "mg": 0.80, "ca": 2.00, "s": 1.20, "limite_salino": 2.0 },
    "Algodón": { "n": 55.00, "p": 25.00, "k": 55.00, "mg": 12.00, "ca": 18.00, "s": 6.00, "limite_salino": 7.7 }
}

GRANULADOS_DB = {
 	    "ENTEC Nitrofoska Especial 12-12-17": { n: 12, p: 12, k: 17, mg: 3, ca: 0, s: 20 },
            "ENTEC 20-10-10": { n: 20, p: 10, k: 10, mg: 0, ca: 0, s: 7.5 },
            "Nitrofoska Perfect 15-5-20": { n: 15, p: 5, k: 20, mg: 2, ca: 0, s: 20 },
            "Nitrofoska Super 20-5-10": { n: 20, p: 5, k: 10, mg: 2, ca: 0, s: 12.5 },
            "ENTEC 20-8-10": { n: 20, p: 8, k: 10, mg: 2, ca: 0, s: 7.5 },
            "ENTEC 25-15": { n: 25, p: 15, k: 0, mg: 0, ca: 0, s: 5 },
            "ENTEC 15-13-13": { n: 15, p: 13, k: 13, mg: 0, ca: 0, s: 12.5 },
            "ENTEC Nitrofoska 14": { n: 14, p: 7, k: 17, mg: 2, ca: 0, s: 22.5 },
            "ENTEC 13-10-20": { n: 13, p: 10, k: 20, mg: 0, ca: 0, s: 7.5 },
            "Nitrofoska NPlus 22-5-5": { n: 22, p: 5, k: 5, mg: 2, ca: 0, s: 5 },
            "ENTEC Evo 27S": { n: 27, p: 0, k: 0, mg: 0, ca: 9.2, s: 10 },
            "ENTEC Evo 24": { n: 24, p: 0, k: 0, mg: 0, ca: 12.3, s: 15 }
   
}

SOLUBLES_DB = {
    	    "ENTEC Solub 21": { n: 21, p: 0, k: 0, mg: 0, ca: 0, s: 60, nh4: 21, no3: 0, ec_coeff: 0.8 },
            "ENTEC Solub 20-5-10": { n: 20, p: 5, k: 10, mg: 2, ca: 0, s: 27, nh4: 6, no3: 5, ec_coeff: 0.7 },
            "ENTEC Solub 11-5-30": { n: 11, p: 5, k: 30, mg: 2, ca: 0, s: 27, nh4: 9, no3: 6, ec_coeff: 0.75 },
            "ENTEC Solub 16-10-17": { n: 16, p: 10, k: 17, mg: 2, ca: 0, s: 12, nh4: 10, no3: 6, ec_coeff: 0.7 },
            "Nitrofoska Solub Calcium K": { n: 14, p: 7, k: 17, mg: 0, ca: 13, s: 0, nh4: 2, no3: 12, ec_coeff: 0.75 },
            "Nitrofoska Solub 7-5-40": { n: 7, p: 5, k: 40, mg: 0, ca: 0, s: 28, nh4: 3, no3: 4, ec_coeff: 0.6 },
            "Nitrofoska Solub 15-10-15": { n: 15, p: 10, k: 15, mg: 2, ca: 0, s: 30, nh4: 10.7, no3: 4.3, ec_coeff: 0.65 },
            "Nitrofoska Solub 13-40-13": { n: 13, p: 40, k: 13, mg: 0, ca: 0, s: 1.9, nh4: 8.8, no3: 4.2, ec_coeff: 0.55 },
            "Nitrofoska Solub 12-5-30": { n: 12, p: 5, k: 30, mg: 1, ca: 0, s: 22, nh4: 1.9, no3: 5.1, ec_coeff: 0.8 },
            "Nitrofoska Solub 7-12-40": { n: 7, p: 12, k: 40, mg: 0, ca: 0, s: 18.4, nh4: 9, no3: 6, ec_coeff: 0.6 },
            "Nitrofoska Solub 18-18-18": { n: 18, p: 18, k: 18, mg: 0, ca: 0, s: 11.5, nh4: 10, no3: 8, ec_coeff: 0.6 },
            "Nitrofoska Solub 20-5-5": { n: 20, p: 5, k: 5, mg: 2, ca: 0, s: 37, nh4: 15.6, no3: 4.4, ec_coeff: 0.85 },
            "Nitrato Cálcico Soluble": { n: 15.5, p: 0, k: 0, mg: 0, ca: 26.3, s: 0, nh4: 1.1, no3: 14.4, ec_coeff: 0.72 },
            "Nitrato Magnésico Soluble": { n: 11, p: 0, k: 0, mg: 15.4, ca: 0, s: 0, nh4: 0, no3: 11, ec_coeff: 0.68 },
            "NOP Solub": { n: 13, p: 0, k: 46, mg: 0, ca: 0, s: 0, nh4: 0, no3: 13, ec_coeff: 0.8 },
            "MAP Solub": { n: 12, p: 61, k: 0, mg: 0, ca: 0, s: 0, nh4: 12, no3: 0, ec_coeff: 0.52 },
            "UP solub": { n: 18, p: 44, k: 0, mg: 0, ca: 0, s: 0, nh4: 18, no3: 0, ec_coeff: 0.82 },
            "SOP solub": { n: 0, p: 0, k: 52, mg: 0, ca: 0, s: 45, nh4: 0, no3: 0, ec_coeff: 0.88 },
            "Sulfato de Magnesio": { n: 0, p: 0, k: 0, mg: 16, ca: 0, s: 32, nh4: 0, no3: 0, ec_coeff: 0.62 },
            "Ácido Fosfórico": { n: 0, p: 52, k: 0, mg: 0, ca: 0, s: 0, nh4: 0, no3: 0, ec_coeff: 0.48 },
            "Ácido Nítrico": { n: 15, p: 0, k: 0, mg: 0, ca: 0, s: 0, nh4: 0, no3: 15, ec_coeff: 0.5 }

}
# =====================================================================
# ✅ NUEVA INICIALIZACIÓN INTELIGENTE (Pégalo aquí)
# =====================================================================
if "crop" not in st.session_state:
    st.session_state.crop = "Caqui (Kaki)"

if "yield_val" not in st.session_state:
    st.session_state.yield_val = 10.0

# Inicializamos los coeficientes del cultivo por defecto en memoria
datos_iniciales = CULTIVOS_DB[st.session_state.crop]
for nutriente in ["n", "p", "k", "mg", "ca", "s"]:
    key_coef = f"coeff_{nutriente}"
    if key_coef not in st.session_state:
        st.session_state[key_coef] = float(datos_iniciales[nutriente])

# Inicializar las unidades fertilizantes totales si no existen
for nutriente_clave, letra in [("u_n", "n"), ("u_p", "p"), ("u_k", "k"), ("u_mg", "mg"), ("u_ca", "ca"), ("u_s", "s")]:
    if nutriente_clave not in st.session_state:
        st.session_state[nutriente_clave] = float(datos_iniciales[letra] * st.session_state.yield_val)

    
    st.session_state.extra_n = 0.0
    st.session_state.extra_p = 0.0
    st.session_state.extra_k = 0.0
    st.session_state.extra_mg = 0.0
    st.session_state.extra_ca = 0.0
    st.session_state.extra_s = 0.0

    st.session_state.water_ca = 80.0
    st.session_state.water_mg = 24.0
    st.session_state.water_k = 15.0
    st.session_state.water_na = 46.0
    st.session_state.water_nh4 = 0.0
    st.session_state.water_no3 = 10.0
    st.session_state.water_h2po4 = 0.0
    st.session_state.water_so4 = 96.0
    st.session_state.water_cl = 71.0
    st.session_state.water_hco3 = 244.0
    st.session_state.water_ec = 0.95

    st.session_state.acid_type = "Nítrico (60%)"
    st.session_state.acid_density = 1.37
    st.session_state.acid_purity = 60.0
    st.session_state.acid_eq_wt = 63.0
    st.session_state.acid_target_hco3 = 0.5

    st.session_state.fondo_items = [
        {"name": "ENTEC Nitrofoska Especial 14-7-17", "dosis": 150.0}
    ]

    months_presets = {
        1: {"name": "Enero", "water": 0.0, "num_riegos": 1, "cuba_vol": 1000, "flow_rate": 15, "solubles": []},
        2: {"name": "Febrero", "water": 0.0, "num_riegos": 1, "cuba_vol": 1000, "flow_rate": 15, "solubles": []},
        3: {"name": "Marzo", "water": 0.0, "num_riegos": 1, "cuba_vol": 1000, "flow_rate": 15, "solubles": []},
        4: {"name": "Abril", "water": 50.0, "num_riegos": 4, "cuba_vol": 1000, "flow_rate": 15, "solubles": []},
        5: {"name": "Brotación (Mayo)", "water": 120.0, "num_riegos": 8, "cuba_vol": 1000, "flow_rate": 15, "solubles": [
            {"name": "ENTEC Solub 20-5-10", "dosis": 100.0}
        ]},
        6: {"name": "Floración (Junio)", "water": 180.0, "num_riegos": 12, "cuba_vol": 1000, "flow_rate": 15, "solubles": []},
        7: {"name": "Engorde de Fruto (Julio)", "water": 270.0, "num_riegos": 15, "cuba_vol": 1000, "flow_rate": 15, "solubles": [
            {"name": "ENTEC Solub 15-5-30", "dosis": 220.0}
        ]},
        8: {"name": "Maduración (Agosto)", "water": 240.0, "num_riegos": 12, "cuba_vol": 1000, "flow_rate": 15, "solubles": [
            {"name": "ENTEC Solub 11-11-21", "dosis": 150.0}
        ]},
        9: {"name": "Septiembre", "water": 100.0, "num_riegos": 6, "cuba_vol": 1000, "flow_rate": 15, "solubles": []},
        10: {"name": "Octubre", "water": 40.0, "num_riegos": 2, "cuba_vol": 1000, "flow_rate": 15, "solubles": []},
        11: {"name": "Noviembre", "water": 0.0, "num_riegos": 1, "cuba_vol": 1000, "flow_rate": 15, "solubles": []},
        12: {"name": "Diciembre", "water": 0.0, "num_riegos": 1, "cuba_vol": 1000, "flow_rate": 15, "solubles": []}
    }
    st.session_state.monthly_data = months_presets
    st.session_state.logo_base64 = ""
    st.session_state.advisor = "G. Morales"
    st.session_state.farm = "Finca Ejemplo"
    st.session_state.date_issue = "2026-07-24"

# --- RE-SYNC WHEN CROP CHANGES ---
def on_crop_change():
    crop_data = CULTIVOS_DB[st.session_state.crop]
    st.session_state.coeff_n = crop_data["n"]
    st.session_state.coeff_p = crop_data["p"]
    st.session_state.coeff_k = crop_data["k"]
    st.session_state.coeff_mg = crop_data["mg"]
    st.session_state.coeff_ca = crop_data["ca"]
    st.session_state.coeff_s = crop_data["s"]

# --- SIDEBAR (CONTROLES GENERALES) ---
with st.sidebar:
    st.markdown("### 🏢 Identificación & Logotipo")
    
    # Logo loading and memory saving
    logo_file = st.file_uploader("📁 Cargar Logotipo (.jpg, .png)", type=["jpg", "png", "jpeg"])
    if logo_file is not None:
        file_bytes = logo_file.read()
        st.session_state.logo_base64 = base64.b64encode(file_bytes).decode("utf-8")
    
    if st.session_state.logo_base64:
        st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{st.session_state.logo_base64}" style="max-height:80px; max-width:100%; object-fit:contain;"/></div>', unsafe_allow_html=True)
        if st.button("🗑️ Eliminar Logo"):
            st.session_state.logo_base64 = ""
            st.rerun()
    else:
        st.info("💡 Coloca tu logo corporativo de Eurochem o del asesor.")
        
    st.session_state.advisor = st.text_input("Asesor Agrónomo:", st.session_state.advisor)
    st.session_state.farm = st.text_input("Finca / Productor:", st.session_state.farm)
    st.session_state.date_issue = st.text_input("Fecha Emisión:", st.session_state.date_issue)
  
  # 1. Inicializar variables básicas en la memoria si no existen
if "crop" not in st.session_state:
    st.session_state.crop = "Caqui (Kaki)"

if "yield_val" not in st.session_state:
    st.session_state.yield_val = 10.0

# Inicializar los valores de Nitrógeno, Fósforo, etc., al arrancar
datos_iniciales = CULTIVOS_DB[st.session_state.crop]
for nutriente_clave, letra in [("u_n", "n"), ("u_p", "p"), ("u_k", "k"), ("u_mg", "mg"), ("u_ca", "ca"), ("u_s", "s")]:
    if nutriente_clave not in st.session_state:
        st.session_state[nutriente_clave] = float(datos_iniciales[letra] * st.session_state.yield_val)

# 2. Dibujar los controles visuales en la pantalla
# =====================================================================
# ✅ SECCIÓN DE CONFIGURACIÓN DEL CULTIVO + DETECTOR (Pégalo aquí)
# =====================================================================
st.markdown("---")
st.markdown("### 🌾 Configuración Cultivo")

crop_list = list(CULTIVOS_DB.keys())
index_actual = crop_list.index(st.session_state.crop) if st.session_state.crop in crop_list else 0

# Desplegable de selección de cultivo
cultivo_elegido = st.selectbox(
    "Seleccione Cultivo:", 
    crop_list, 
    index=index_actual
)

# Entrada para el rendimiento esperado
rendimiento_elegido = st.number_input(
    "Rendimiento Esperado (t/ha):", 
    value=st.session_state.yield_val, 
    min_value=0.1, 
    step=1.0
)

# Sincronización automática de cultivo y rendimiento al cambiar de pestaña
hubo_cambio = False

if cultivo_elegido != st.session_state.crop:
    st.session_state.crop = cultivo_elegido
    datos_nuevos = CULTIVOS_DB[cultivo_elegido]
    
    st.session_state.coeff_n = float(datos_nuevos["n"])
    st.session_state.coeff_p = float(datos_nuevos["p"])
    st.session_state.coeff_k = float(datos_nuevos["k"])
    st.session_state.coeff_mg = float(datos_nuevos["mg"])
    st.session_state.coeff_ca = float(datos_nuevos["ca"])
    st.session_state.coeff_s = float(datos_nuevos["s"])
    
    st.session_state.u_n = float(st.session_state.coeff_n * st.session_state.yield_val)
    st.session_state.u_p = float(st.session_state.coeff_p * st.session_state.yield_val)
    st.session_state.u_k = float(st.session_state.coeff_k * st.session_state.yield_val)
    st.session_state.u_mg = float(st.session_state.coeff_mg * st.session_state.yield_val)
    st.session_state.u_ca = float(st.session_state.coeff_ca * st.session_state.yield_val)
    st.session_state.u_s = float(st.session_state.coeff_s * st.session_state.yield_val)
    hubo_cambio = True

if rendimiento_elegido != st.session_state.yield_val:
    st.session_state.yield_val = rendimiento_elegido
    
    st.session_state.u_n = float(st.session_state.coeff_n * st.session_state.yield_val)
    st.session_state.u_p = float(st.session_state.coeff_p * st.session_state.yield_val)
    st.session_state.u_k = float(st.session_state.coeff_k * st.session_state.yield_val)
    st.session_state.u_mg = float(st.session_state.coeff_mg * st.session_state.yield_val)
    st.session_state.u_ca = float(st.session_state.coeff_ca * st.session_state.yield_val)
    st.session_state.u_s = float(st.session_state.coeff_s * st.session_state.yield_val)
    hubo_cambio = True

if hubo_cambio:
    st.rerun()


# 3. DETECTOR DE CAMBIOS INTELIGENTE (Sincronización instantánea)
hubo_cambio = False

# Si el usuario cambia el cultivo en el desplegable...
if cultivo_elegido != st.session_state.crop:
    st.session_state.crop = cultivo_elegido
    hubo_cambio = True

# Si el usuario cambia el rendimiento...
if rendimiento_elegido != st.session_state.yield_val:
    st.session_state.yield_val = rendimiento_elegido
    hubo_cambio = True

# Si ha ocurrido cualquiera de los dos cambios, recalculamos los valores recomendados
if hubo_cambio:
    datos_nuevos = CULTIVOS_DB[st.session_state.crop]
    st.session_state.u_n = float(datos_nuevos["n"] * st.session_state.yield_val)
    st.session_state.u_p = float(datos_nuevos["p"] * st.session_state.yield_val)
    st.session_state.u_k = float(datos_nuevos["k"] * st.session_state.yield_val)
    st.session_state.u_mg = float(datos_nuevos["mg"] * st.session_state.yield_val)
    st.session_state.u_ca = float(datos_nuevos["ca"] * st.session_state.yield_val)
    st.session_state.u_s = float(datos_nuevos["s"] * st.session_state.yield_val)
    # Forzar recarga limpia de la página para aplicar los nuevos números de inmediato
    st.rerun()


# --- CABECERA PRINCIPAL ---
st.markdown(f"""
<div class="main-header">
    <h1>PLAN Fertirrigación Experto</h1>
    <p>Creado por {st.session_state.advisor} — © {st.session_state.advisor} & Eurochem Agro Iberia</p>
</div>
""", unsafe_allow_html=True)

# ----------------- EJECUCIÓN DE CÁLCULOS QUÍMICOS CENTRALES -----------------

# meq/L del Agua Base
meq_ca = st.session_state.water_ca / 20.04
meq_mg = st.session_state.water_mg / 12.16
meq_k = st.session_state.water_k / 39.1
meq_na = st.session_state.water_na / 23.0
meq_nh4 = st.session_state.water_nh4 / 18.04

meq_no3 = st.session_state.water_no3 / 62.0
meq_h2po4 = st.session_state.water_h2po4 / 97.0
meq_so4 = st.session_state.water_so4 / 48.03
meq_cl = st.session_state.water_cl / 35.45
meq_hco3 = st.session_state.water_hco3 / 61.02

sum_cat = meq_ca + meq_mg + meq_k + meq_na + meq_nh4
sum_ani = meq_no3 + meq_h2po4 + meq_so4 + meq_cl + meq_hco3

water_ratio_val = abs(sum_cat - sum_ani) / ((sum_cat + sum_ani) / 2) * 100 if (sum_cat + sum_ani) > 0 else 0.0
ras_val = (meq_na + meq_k) / np.sqrt((meq_ca + meq_mg) / 2) if (meq_ca + meq_mg) > 0 else 0.0

# Ácidos y Neutralización
neut_hco3 = max(0.0, meq_hco3 - st.session_state.acid_target_hco3)
acid_purity = st.session_state.acid_purity
acid_density = st.session_state.acid_density
acid_eq_wt = st.session_state.acid_eq_wt

acid_dose_l = 0.0
acid_dose_g = 0.0
if acid_purity > 0:
    acid_dose_l = (neut_hco3 * acid_eq_wt) / (acid_purity * acid_density * 10)
    acid_dose_g = acid_dose_l * acid_density * 1000

# Fondo Granulado Suma
fondo_sum_n, fondo_sum_p, fondo_sum_k, fondo_sum_mg, fondo_sum_ca, fondo_sum_s = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
for item in st.session_state.fondo_items:
    p = GRANULADOS_DB.get(item["name"])
    if p:
st.session_state.fondo_sum_n = dosis_fondo * (riqueza_n / 100.0)
st.session_state.fondo_sum_p = dosis_fondo * (riqueza_p / 100.0)
st.session_state.fondo_sum_k = dosis_fondo * (riqueza_k / 100.0)
st.session_state.fondo_sum_mg = dosis_fondo * (riqueza_mg / 100.0)
st.session_state.fondo_sum_ca = dosis_fondo * (riqueza_ca / 100.0)
st.session_state.fondo_sum_s = dosis_fondo * (riqueza_s / 100.0) 

# Bucle mensual para acumular agua, ácidos y solubles
water_annual_sum_n, water_annual_sum_p, water_annual_sum_k, water_annual_sum_mg, water_annual_sum_ca, water_annual_sum_s = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
acid_annual_sum_n, acid_annual_sum_p, acid_annual_sum_k, acid_annual_sum_mg, acid_annual_sum_ca, acid_annual_sum_s = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
solub_annual_sum_n, solub_annual_sum_p, solub_annual_sum_k, solub_annual_sum_mg, solub_annual_sum_ca, solub_annual_sum_s = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

for m in range(1, 13):
    m_data = st.session_state.monthly_data[m]
    
    # Agua
    w_n = m_data["water"] * st.session_state.water_no3 * 0.226 / 1000
    w_p = m_data["water"] * st.session_state.water_h2po4 * 0.732 / 1000
    w_k = m_data["water"] * st.session_state.water_k * 1.205 / 1000
    w_mg = m_data["water"] * st.session_state.water_mg * 1.658 / 1000
    w_ca = m_data["water"] * st.session_state.water_ca * 1.399 / 1000
    w_s = m_data["water"] * st.session_state.water_so4 * 0.833 / 1000
    
    water_annual_sum_n += w_n
    water_annual_sum_p += w_p
    water_annual_sum_k += w_k
    water_annual_sum_mg += w_mg
    water_annual_sum_ca += w_ca
    water_annual_sum_s += w_s

    # Ácido
    a_n, a_p, a_s = 0.0, 0.0, 0.0
    if m_data["water"] > 0:
        if st.session_state.acid_type == "Nítrico (60%)":
            a_n = (m_data["water"] * neut_hco3 * 14.0) / 1000
        elif st.session_state.acid_type == "Fosfórico (75%)":
            a_p = (m_data["water"] * neut_hco3 * 71.0) / 1000
        elif st.session_state.acid_type == "Sulfúrico (98%)":
            a_s = (m_data["water"] * neut_hco3 * 40.0) / 1000
            
    acid_annual_sum_n += a_n
    acid_annual_sum_p += a_p
    acid_annual_sum_s += a_s

    # Solubiles
    for sol in m_data["solubles"]:
        p = SOLUBLES_DB.get(sol["name"])
        if p:
            solub_annual_sum_n += sol["dosis"] * p["n"] / 100
            solub_annual_sum_p += sol["dosis"] * p["p"] / 100
            solub_annual_sum_k += sol["dosis"] * p["k"] / 100
            solub_annual_sum_mg += sol["dosis"] * p["mg"] / 100
            solub_annual_sum_ca += sol["dosis"] * p["ca"] / 100
            solub_annual_sum_s += sol["dosis"] * p["s"] / 100

# =====================================================================
# ✅ CÁLCULO DE NECESIDADES BÁSICAS (A) - COLOCADO ANTES DE LOS OBJETIVOS
# =====================================================================
# Multiplica el rendimiento por el coeficiente reactivo de la memoria (session_state)
base_n_ha = st.session_state.yield_val * st.session_state.coeff_n
base_p_ha = st.session_state.yield_val * st.session_state.coeff_p
base_k_ha = st.session_state.yield_val * st.session_state.coeff_k
base_mg_ha = st.session_state.yield_val * st.session_state.coeff_mg
base_ca_ha = st.session_state.yield_val * st.session_state.coeff_ca
base_s_ha = st.session_state.yield_val * st.session_state.coeff_s

# Target in Gotero = A - C - D1 - D2 + E
target_n_val = base_n_ha - fondo_sum_n - water_annual_sum_n - acid_annual_sum_n + st.session_state.extra_n
target_p_val = base_p_ha - fondo_sum_p - water_annual_sum_p - acid_annual_sum_p + st.session_state.extra_p
target_k_val = base_k_ha - fondo_sum_k - water_annual_sum_k + st.session_state.extra_k
target_mg_val = base_mg_ha - fondo_sum_mg - water_annual_sum_mg + st.session_state.extra_mg
target_ca_val = base_ca_ha - fondo_sum_ca - water_annual_sum_ca + st.session_state.extra_ca
target_s_val = base_s_ha - fondo_sum_s - water_annual_sum_s - acid_annual_sum_s + st.session_state.extra_s

# --- CREACIÓN DE PESTAÑAS (MIGRACIÓN PASO A PASO) ---
tab_bal, tab_water, tab_acid, tab_fondo, tab_monthly, tab_sonneveld, tab_dictamen = st.tabs([
    "🎯 Punto 1: Balance Anual",
    "💧 Punto 2: Analítica de Agua",
    "🧪 Punto 3: Neutralización",
    "📦 Punto 4: Fondo Granulado",
    "📅 Punto 5: Plan Mensual Fases",
    "🔬 Punto 7: Sonneveld & Gotero",
    "💡 Punto 8: Dictamen Agronómico"
])

# ================= TAB 1: BALANCE ANUAL =================
with tab_bal:
    st.markdown("### 🎯 Balance General de Nutrientes (UF - kg/ha-año)")
    
    # Extra inputs
    with st.expander("➕ Compensación / Margen de Seguridad Extra (E):"):
        col_e1, col_e2, col_e3, col_e4, col_e5, col_e6 = st.columns(6)
        st.session_state.extra_n = col_e1.number_input("N extra (kg/ha):", value=st.session_state.extra_n)
        st.session_state.extra_p = col_e2.number_input("P₂O₅ extra (kg/ha):", value=st.session_state.extra_p)
        st.session_state.extra_k = col_e3.number_input("K₂O extra (kg/ha):", value=st.session_state.extra_k)
        st.session_state.extra_mg = col_e4.number_input("MgO extra (kg/ha):", value=st.session_state.extra_mg)
        st.session_state.extra_ca = col_e5.number_input("CaO extra (kg/ha):", value=st.session_state.extra_ca)
        st.session_state.extra_s = col_e6.number_input("SO₃ extra (kg/ha):", value=st.session_state.extra_s)
# =====================================================================
# ✅ CASILLAS DE EDICIÓN DE COEFICIENTES EN EL EXPANDER (Sustituye aquí)
# =====================================================================
# Al usar 'key="coeff_X"', Streamlit lee el valor automáticamente de la memoria 
# al cambiar de cultivo y guarda de forma instantánea cualquier edición del usuario.
with st.expander("✏️ Editar Coeficientes de Extracción del Cultivo (kg/t):"):
    col_c1, col_c2, col_c3, col_c4, col_c5, col_c6 = st.columns(6)
    col_c1.number_input("Coeficiente N:", key="coeff_n", step=0.1)
    col_c2.number_input("Coeficiente P₂O₅:", key="coeff_p", step=0.1)
    col_c3.number_input("Coeficiente K₂O:", key="coeff_k", step=0.1)
    col_c4.number_input("Coeficiente MgO:", key="coeff_mg", step=0.1)
    col_c5.number_input("Coeficiente CaO:", key="coeff_ca", step=0.1)
    col_c6.number_input("Coeficiente SO₃:", key="coeff_s", step=0.1)
# === TABLA DE BALANCE (Caso sin sangría extra) ===
balance_data = {
    "Concepto Nutriente (kg/ha)": [
        "A) Necesidad Base Cultivo (A)",
        "C) Abonado de Fondo (C)",
        "D1) Crédito Agua de Riego (D1)",
        "D2) Crédito Ácido Regulador (D2)",
        "E) Compensación Extra (E)",
        "OBJETIVO EN GOTERO (Target = A-C-D1-D2+E)",
        "TOTAL APLICADO SOLUBLES",
        "BALANCE / DIFERENCIA"
    ], 
    base_n_ha = st.session_state.yield_val * st.session_state.coeff_n
    base_p_ha = st.session_state.yield_val * st.session_state.coeff_p
    base_k_ha = st.session_state.yield_val * st.session_state.coeff_k
    base_mg_ha = st.session_state.yield_val * st.session_state.coeff_mg
    base_ca_ha = st.session_state.yield_val * st.session_state.coeff_ca
    base_s_ha = st.session_state.yield_val * st.session_state.coeff_s

    "Nitrógeno (N)": [
        base_n_ha, 
        fondo_sum_n, 
        water_annual_sum_n, 
        acid_annual_sum_n, 
        st.session_state.extra_n, 
        target_n_val, 
        solub_annual_sum_n, 
        solub_annual_sum_n - target_n_val
    ],

    "Fósforo (P₂O₅)": [
        base_p_ha, 
        fondo_sum_p, 
        water_annual_sum_p, 
        acid_annual_sum_p, 
        st.session_state.extra_p, 
        target_p_val, 
        solub_annual_sum_p, 
        solub_annual_sum_p - target_p_val
    ],

    "Potasio (K₂O)": [
        base_k_ha, 
        fondo_sum_k, 
        water_annual_sum_k, 
        0.0, 
        st.session_state.extra_k, 
        target_k_val, 
        solub_annual_sum_k, 
        solub_annual_sum_k - target_k_val
    ],

    "Magnesio (MgO)": [
        base_mg_ha, 
        fondo_sum_mg, 
        water_annual_sum_mg, 
        0.0, 
        st.session_state.extra_mg, 
        target_mg_val, 
        solub_annual_sum_mg, 
        solub_annual_sum_mg - target_mg_val
    ],

    "Calcio (CaO)": [
        base_ca_ha, 
        fondo_sum_ca, 
        water_annual_sum_ca, 
        0.0, 
        st.session_state.extra_ca, 
        target_ca_val, 
        solub_annual_sum_ca, 
        solub_annual_sum_ca - target_ca_val
    ],

    "Azufre (SO₃)": [
        base_s_ha, 
        fondo_sum_s, 
        water_annual_sum_s, 
        acid_annual_sum_s, 
        st.session_state.extra_s, 
        target_s_val, 
        solub_annual_sum_s, 
        solub_annual_sum_s - target_s_val
    ]
}
# Se crea el DataFrame (Sin espacios al principio de la línea)
df_bal = pd.DataFrame(balance_data)
st.dataframe(df_bal.style.format(precision=1), use_container_width=True)

# === 📊 GRÁFICO DINÁMICO COMPARATIVO ===
st.markdown("### 📊 Gráfico Comparativo: Objetivo vs Aplicado")
fig, ax = plt.subplots(figsize=(10, 4))
nutrientes = ["N", "P₂O₅", "K₂O", "MgO", "CaO", "SO₃"]

# Valores objetivo y aplicados de Eurochem
targets = [target_n_val, target_p_val, target_k_val, target_mg_val, target_ca_val, target_s_val]
applied = [
    solub_annual_sum_n, 
    solub_annual_sum_p, 
    solub_annual_sum_k, 
    solub_annual_sum_mg, 
    solub_annual_sum_ca, 
    solub_annual_sum_s
]

x = np.arange(len(nutrientes))
width = 0.35

# Dibujamos las barras (Azul oscuro para Target y Verde para Solubles)
ax.bar(x - width/2, targets, width, label="Objetivo (Target)", color="#1E3D59")
ax.bar(x + width/2, applied, width, label="Aplicado (Solubles)", color="#17B890")

ax.set_ylabel("kg/ha")
ax.set_title("Comparativa de Nutrientes (Objetivo vs Aplicado)")
ax.set_xticks(x)
ax.set_xticklabels(nutrientes)
ax.legend()
ax.grid(True, linestyle="--", alpha=0.5)

st.pyplot(fig)


# ================= TAB 2: ANALÍTICA DE AGUA =================
with tab_water:
    st.markdown("### 💧 Análisis Químico del Agua de Riego")
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.subheader("Cationes (Cargas Positivas)")
        st.session_state.water_ca = st.number_input("Calcio (Ca²⁺) mg/L:", value=st.session_state.water_ca)
        st.session_state.water_mg = st.number_input("Magnesio (Mg²⁺) mg/L:", value=st.session_state.water_mg)
        st.session_state.water_k = st.number_input("Potasio (K⁺) mg/L:", value=st.session_state.water_k)
        st.session_state.water_na = st.number_input("Sodio (Na⁺) mg/L:", value=st.session_state.water_na)
        st.session_state.water_nh4 = st.number_input("Amonio (NH₄⁺) mg/L:", value=st.session_state.water_nh4)
        
    with col_w2:
        st.subheader("Aniones (Cargas Negativas)")
        st.session_state.water_no3 = st.number_input("Nitrato (NO₃⁻) mg/L:", value=st.session_state.water_no3)
        st.session_state.water_h2po4 = st.number_input("Fosfato (H₂PO₄⁻) mg/L:", value=st.session_state.water_h2po4)
        st.session_state.water_so4 = st.number_input("Sulfato (SO₄²⁻) mg/L:", value=st.session_state.water_so4)
        st.session_state.water_cl = st.number_input("Cloruro (Cl⁻) mg/L:", value=st.session_state.water_cl)
        st.session_state.water_hco3 = st.number_input("Bicarbonato (HCO₃⁻) mg/L:", value=st.session_state.water_hco3)

    st.session_state.water_ec = st.number_input("Conductividad Eléctrica Base del Agua (dS/m):", value=st.session_state.water_ec)

    st.markdown("---")
    st.subheader("📊 Balance Iónico y RAS Calculados:")
    col_res1, col_res2, col_res3 = st.columns(3)
    col_res1.metric("Suma Cationes (meq/L)", f"{sum_cat:.2f}")
    col_res2.metric("Suma Aniones (meq/L)", f"{sum_ani:.2f}")
    
    # Balance metric
    if water_ratio_val <= 5.0:
        col_res3.metric("Electroneutralidad (%)", f"{water_ratio_val:.1f}% ✅ Equilibrado")
    else:
        col_res3.metric("Electroneutralidad (%)", f"{water_ratio_val:.1f}% ⚠️ Desbalanceado")

    st.metric("Relación de Adsorción de Sodio (R.A.S.)", f"{ras_val:.2f}")

# ================= TAB 3: NEUTRALIZACIÓN =================
with tab_acid:
    st.markdown("### 🧪 Neutralización de Bicarbonatos y Elección del Ácido")
    
    st.session_state.acid_type = st.selectbox("Ácido Comercial Empleado:", ["Nítrico (60%)", "Fosfórico (75%)", "Sulfúrico (98%)", "Personalizado"])
    
    # Auto-adjust properties
    if st.session_state.acid_type == "Nítrico (60%)":
        st.session_state.acid_density = 1.37
        st.session_state.acid_purity = 60.0
        st.session_state.acid_eq_wt = 63.0
    elif st.session_state.acid_type == "Fosfórico (75%)":
        st.session_state.acid_density = 1.58
        st.session_state.acid_purity = 75.0
        st.session_state.acid_eq_wt = 98.0
    elif st.session_state.acid_type == "Sulfúrico (98%)":
        st.session_state.acid_density = 1.84
        st.session_state.acid_purity = 98.0
        st.session_state.acid_eq_wt = 49.0

    col_ac1, col_cda2 = st.columns(2)
    with col_ac1:
        st.session_state.acid_density = st.number_input("Densidad del ácido (kg/L):", value=st.session_state.acid_density)
        st.session_state.acid_purity = st.number_input("Pureza comercial (%):", value=st.session_state.acid_purity)
        st.session_state.acid_eq_wt = st.number_input("Peso equivalente químico:", value=st.session_state.acid_eq_wt)
    with col_cda2:
        st.session_state.acid_target_hco3 = st.number_input("Bicarbonato Objetivo Final en Gotero (meq/L):", value=st.session_state.acid_target_hco3)
        st.metric("meq/L de HCO₃⁻ a Neutralizar:", f"{neut_hco3:.2f}")

    st.markdown("---")
    st.subheader("📋 Consumo de Ácido Comercial Requerido:")
    col_out_ac1, col_out_ac2 = st.columns(2)
    col_out_ac1.metric("Dosis de Ácido Comercial (L / m³ de riego)", f"{acid_dose_l:.3f} L/m³")
    col_out_ac2.metric("Peso del Ácido Comercial (g / m³ de riego)", f"{acid_dose_g:.1f} g/m³")

# ================= TAB 4: FONDO GRANULADO =================
with tab_fondo:
    st.markdown("### 📦 Plan de Abonado de Fondo (Complexes Sólidos)")
    
    st.subheader("Añadir Fertilizante de Fondo")
    col_f1, col_f2 = st.columns([2, 1])
    sel_fondo = col_f1.selectbox("Complejo Granulado Eurochem:", list(GRANULADOS_DB.keys()))
    dosis_fondo = col_f2.number_input("Dosis (kg/ha):", value=150.0, step=25.0)
    
    if st.button("➕ Añadir Fertilizante de Fondo"):
        st.session_state.fondo_items.append({"name": sel_fondo, "dosis": dosis_fondo})
        st.rerun()

    st.markdown("---")
    st.subheader("Tabla de Fondo Aplicado:")
    
    if len(st.session_state.fondo_items) > 0:
        for idx, item in enumerate(st.session_state.fondo_items):
            col_col1, col_col2, col_col3 = st.columns([3, 2, 1])
            col_col1.markdown(f"**{item['name']}**")
            new_d = col_col2.number_input(f"Editar Dosis (kg/ha) - Ítem {idx+1}:", value=item["dosis"], key=f"f_dosis_{idx}")
            st.session_state.fondo_items[idx]["dosis"] = new_d
            if col_col3.button("🗑️", key=f"btn_del_f_{idx}"):
                st.session_state.fondo_items.pop(idx)
                st.rerun()
    else:
        st.info("No se han agregado abonos de fondo.")

    st.markdown("---")
    st.subheader("📋 Aportaciones Netas de Fondo (UF/ha):")
    col_u_f1, col_u_f2, col_u_f3, col_u_f4, col_u_f5, col_u_f6 = st.columns(6)
    col_u_f1.metric("N Fondo", f"{fondo_sum_n:.1f}")
    col_u_f2.metric("P₂O₅ Fondo", f"{fondo_sum_p:.1f}")
    col_u_f3.metric("K₂O Fondo", f"{fondo_sum_k:.1f}")
    col_u_f4.metric("MgO Fondo", f"{fondo_sum_mg:.1f}")
    col_u_f5.metric("CaO Fondo", f"{fondo_sum_ca:.1f}")
    col_u_f6.metric("SO₃ Fondo", f"{fondo_sum_s:.1f}")

# ================= TAB 5: PLAN MENSUAL (FASES) =================
with tab_monthly:
    st.markdown("### 📅 Planificación Mensual y Fases Fenológicas")
    
    month_names_select = [st.session_state.monthly_data[m]["name"] for m in range(1, 13)]
    sel_month_name = st.selectbox("Seleccione Fase Mensual a Programar:", month_names_select)
    m_idx = month_names_select.index(sel_month_name) + 1
    
    m_data = st.session_state.monthly_data[m_idx]
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.subheader("💧 Variables de Riego e Hidráulica")
        st.session_state.monthly_data[m_idx]["name"] = st.text_input("Nombre de la Fase / Mes:", m_data["name"])
        st.session_state.monthly_data[m_idx]["water"] = st.number_input("Volumen de Riego (m³/ha-mes):", value=m_data["water"], step=10.0)
        st.session_state.monthly_data[m_idx]["num_riegos"] = st.number_input("Número de Riegos en la Fase:", value=m_data["num_riegos"], min_value=1)
        st.session_state.monthly_data[m_idx]["cuba_vol"] = st.number_input("Volumen Cuba Madre (L):", value=m_data["cuba_vol"], min_value=100)
        st.session_state.monthly_data[m_idx]["flow_rate"] = st.number_input("Caudal gotero sector (L/h):", value=m_data["flow_rate"], min_value=1)

    with col_m2:
        st.subheader("🧪 Inyección de Solubles de Eurochem")
        sel_sol = st.selectbox("Seleccione Soluble Eurochem:", list(SOLUBLES_DB.keys()))
        dosis_sol = st.number_input("Dosis Mensual (kg/ha-mes):", value=100.0, step=10.0)
        
        # Previsualización
        sp = SOLUBLES_DB[sel_sol]
        st.markdown(f"""
        <div style="background-color: #fafcff; padding: 10px; border-radius: 4px; border: 1px solid #c8e6c9;">
            <strong>Aporte estimado:</strong><br/>
            N: {(dosis_sol * sp['n'] / 100):.1f} | 
            P₂O₅: {(dosis_sol * sp['p'] / 100):.1f} | 
            K₂O: {(dosis_sol * sp['k'] / 100):.1f} | 
            MgO: {(dosis_sol * sp['mg'] / 100):.1f} | 
            CaO: {(dosis_sol * sp['ca'] / 100):.1f} | 
            SO₃: {(dosis_sol * sp['s'] / 100):.1f} (kg/ha)
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("➕ Añadir Soluble a la Fase"):
            st.session_state.monthly_data[m_idx]["solubles"].append({"name": sel_sol, "dosis": dosis_sol})
            st.rerun()

    st.markdown("---")
    st.subheader(f"Tabla de Solubles en {st.session_state.monthly_data[m_idx]['name']}:")
    
    if len(m_data["solubles"]) > 0:
        for s_idx, sol in enumerate(m_data["solubles"]):
            col_sol1, col_sol2, col_sol3 = st.columns([3, 2, 1])
            col_sol1.markdown(f"**{sol['name']}**")
            new_s_d = col_sol2.number_input(f"Editar dosis (kg/ha) - {sol['name']}:", value=sol["dosis"], key=f"s_dosis_{m_idx}_{s_idx}")
            st.session_state.monthly_data[m_idx]["solubles"][s_idx]["dosis"] = new_s_d
            if col_sol3.button("🗑️", key=f"btn_del_s_{m_idx}_{s_idx}"):
                st.session_state.monthly_data[m_idx]["solubles"].pop(s_idx)
                st.rerun()
    else:
        st.info("No se han agregado abonos solubles en esta fase mensual.")

    # CALCULATE WATER + ACID + CRISTALINOS OF MONTH
    m_sol_n, m_sol_p, m_sol_k, m_sol_mg, m_sol_ca, m_sol_s = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    for sol in m_data["solubles"]:
        p = SOLUBLES_DB.get(sol["name"])
        if p:
            m_sol_n += sol["dosis"] * p["n"] / 100
            m_sol_p += sol["dosis"] * p["p"] / 100
            m_sol_k += sol["dosis"] * p["k"] / 100
            m_sol_mg += sol["dosis"] * p["mg"] / 100
            m_sol_ca += sol["dosis"] * p["ca"] / 100
            m_sol_s += sol["dosis"] * p["s"] / 100

    w_n = m_data["water"] * st.session_state.water_no3 * 0.226 / 1000
    w_p = m_data["water"] * st.session_state.water_h2po4 * 0.732 / 1000
    w_k = m_data["water"] * st.session_state.water_k * 1.205 / 1000
    w_mg = m_data["water"] * st.session_state.water_mg * 1.658 / 1000
    w_ca = m_data["water"] * st.session_state.water_ca * 1.399 / 1000
    w_s = m_data["water"] * st.session_state.water_so4 * 0.833 / 1000

    a_n, a_p, a_s = 0.0, 0.0, 0.0
    if m_data["water"] > 0:
        if st.session_state.acid_type == "Nítrico (60%)":
            a_n = (m_data["water"] * neut_hco3 * 14.0) / 1000
        elif st.session_state.acid_type == "Fosfórico (75%)":
            a_p = (m_data["water"] * neut_hco3 * 71.0) / 1000
        elif st.session_state.acid_type == "Sulfúrico (98%)":
            a_s = (m_data["water"] * neut_hco3 * 40.0) / 1000

    total_fase_n = m_sol_n + w_n + a_n
    total_fase_p = m_sol_p + w_p + a_p
    total_fase_k = m_sol_k + w_k
    total_fase_mg = m_sol_mg + w_mg
    total_fase_ca = m_sol_ca + w_ca
    total_fase_s = m_sol_s + w_s + a_s

    # Percentage over Target
    pct_fase_n = total_fase_n / target_n_val * 100 if target_n_val > 0 else 0.0
    pct_fase_p = total_fase_p / target_p_val * 100 if target_p_val > 0 else 0.0
    pct_fase_k = total_fase_k / target_k_val * 100 if target_k_val > 0 else 0.0
    pct_fase_mg = total_fase_mg / target_mg_val * 100 if target_mg_val > 0 else 0.0
    pct_fase_ca = total_fase_ca / target_ca_val * 100 if target_ca_val > 0 else 0.0
    pct_fase_s = total_fase_s / target_s_val * 100 if target_s_val > 0 else 0.0

    st.markdown("---")
    st.subheader("📊 Suministro Nutricional Consolidado de la Fase:")
    consolidated_data = {
        "Origen Nutricional (kg/ha)": [
            "1. Fertilizantes Cristalinos",
            "2. Aportes del Agua de Riego",
            "3. Aportes de Ácido Regulador",
            "Suma Suministro Total Neto",
            "% Aportado sobre el Objetivo Requerido (Gotero)"
        ],
        "N": [m_sol_n, w_n, a_n, total_fase_n, f"{pct_fase_n:.1f}%"],
        "P₂O₅": [m_sol_p, w_p, a_p, total_fase_p, f"{pct_fase_p:.1f}%"],
        "K₂O": [m_sol_k, w_k, 0.0, total_fase_k, f"{pct_fase_k:.1f}%"],
        "MgO": [m_sol_mg, w_mg, 0.0, total_fase_mg, f"{pct_fase_mg:.1f}%"],
        "CaO": [m_sol_ca, w_ca, 0.0, total_fase_ca, f"{pct_fase_ca:.1f}%"],
        "SO₃": [m_sol_s, w_s, a_s, total_fase_s, f"{pct_fase_s:.1f}%"]
    }
    st.table(pd.DataFrame(consolidated_data))

    # Laboratorio Gota
    st.markdown("---")
    st.subheader("🔬 Laboratorio de Gota y Cuba de la Fase")
    
    ec_gota = st.session_state.water_ec
    for sol in m_data["solubles"]:
        p = SOLUBLES_DB.get(sol["name"])
        if p and m_data["water"] > 0:
            conc = sol["dosis"] / m_data["water"]
            ec_gota += conc * p["ec_coeff"]
    if m_data["water"] > 0:
        ec_gota += (acid_dose_l * neut_hco3 * 0.05)

    total_solubles_mes_kg = sum([s["dosis"] for s in m_data["solubles"]])
    d_por_riego_kg = total_solubles_mes_kg / m_data["num_riegos"] if m_data["num_riegos"] > 0 else 0.0
    
    conc_cuba_gl = 0.0
    conc_cuba_pct = 0.0
    if m_data["cuba_vol"] > 0:
        conc_cuba_gl = (d_por_riego_kg / m_data["cuba_vol"]) * 1000
        conc_cuba_pct = (d_por_riego_kg / m_data["cuba_vol"]) * 100

    g_l_gotero = total_solubles_mes_kg / m_data["water"] if m_data["water"] > 0 else 0.0

    col_lab1, col_lab2 = st.columns(2)
    with col_lab1:
        st.metric("Conductividad Eléctrica Gota Final", f"{ec_gota:.2f} dS/m")
        crop_lim = CULTIVOS_DB[st.session_state.crop]["limite_salino"]
        if ec_gota > crop_lim:
            st.markdown(f'<div class="gota-alert-banner">⚠️ EXCESO DE SALINIDAD. Supera el límite de tolerancia del {st.session_state.crop} ({crop_lim:.2f} dS/m). Riesgo de mermas.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="gota-ok-banner">✅ Conductividad óptima para {st.session_state.crop} (límite: {crop_lim:.2f} dS/m).</div>', unsafe_allow_html=True)

    with col_lab2:
        st.metric("Concentración Gotero Final (g/L)", f"{g_l_gotero:.3f} g/L")
        st.metric("Concentración Solución Madre (Cuba)", f"{conc_cuba_pct:.2f}% ({conc_cuba_gl:.1f} g/L)")
        if conc_cuba_gl > 150.0:
            st.markdown('<div class="gota-alert-banner">⚠️ ALERTA: Cuba saturada (>150 g/L). Peligro de precipitados químicos.</div>', unsafe_allow_html=True)

# ================= TAB 6: SONNEVELD & GOTERO =================
with tab_sonneveld:
    st.markdown("### 🔬 Gotero de Sonneveld en la Fase")
    
    sel_month_sonn = st.selectbox("Inspeccionar gotero del mes:", month_names_select, key="sel_sonn")
    s_idx = month_names_select.index(sel_month_sonn) + 1
    sm = st.session_state.monthly_data[s_idx]

    # Re-calculate Gotero meq/L
    got_nh4 = meq_nh4
    got_no3 = meq_no3
    got_p = meq_h2po4
    got_s = meq_so4
    got_k = meq_k
    got_ca = meq_ca
    got_mg = meq_mg

    if st.session_state.acid_type == "Nítrico (60%)":
        got_no3 += neut_hco3
    elif st.session_state.acid_type == "Fosfórico (75%)":
        got_p += neut_hco3
    elif st.session_state.acid_type == "Sulfúrico (98%)":
        got_s += neut_hco3

    for sol in sm["solubles"]:
        p = SOLUBLES_DB.get(sol["name"])
        if p and sm["water"] > 0:
            conc_g_l = sol["dosis"] / sm["water"]
            got_nh4 += (conc_g_l * p["nh4"] * 10) / 14.0
            got_no3 += (conc_g_l * p["no3"] * 10) / 14.0
            got_p += (conc_g_l * p["p"] * 10) / 71.0
            got_s += (conc_g_l * p["s"] * 10) / 40.0
            got_k += (conc_g_l * p["k"] * 10) / 47.1
            got_ca += (conc_g_l * p["ca"] * 10) / 28.0
            got_mg += (conc_g_l * p["mg"] * 10) / 20.15

    # Sonneveld relations
    r_k_ca_mg = got_k / (got_ca + got_mg) if (got_ca + got_mg) > 0 else 0.0
    r_ca_mg = got_ca / got_mg if got_mg > 0 else 0.0
    r_k_mg = got_k / got_mg if got_mg > 0 else 0.0
    r_n_k = (got_no3 + got_nh4) / got_k if got_k > 0 else 0.0
    r_n_p = (got_no3 + got_nh4) / got_p if got_p > 0 else 0.0

    st.subheader(f"Relaciones Molares Calculadas ({sm['name']}):")
    
    # Comments dict
    comments = []
    
    # Relation 1
    if r_k_ca_mg < 0.30:
        c1 = "⚠️ Relación baja. Riesgo de deficiencia de Potasio por exceso de Calcio y Magnesio."
    elif r_k_ca_mg <= 0.50:
        c1 = "✅ Óptimo (0.30-0.50). Previene antagonismos de absorción con potasio."
    else:
        c1 = "⚠️ Relación alta. El exceso de Potasio puede bloquear la absorción de Calcio y Magnesio."
        
    # Relation 2
    if r_ca_mg < 2.50:
        c2 = "⚠️ Relación baja. Exceso de Magnesio que puede bloquear la absorción de Calcio."
    elif r_ca_mg <= 5.00:
        c2 = "✅ Óptimo (2.50-5.00). Controla el equilibrio de asimilación de calcio."
    else:
        c2 = "⚠️ Relación alta. El exceso de Calcio puede inducir deficiencias de Magnesio."

    # Relation 3
    if r_k_mg < 1.50:
        c3 = "⚠️ Relación baja. Riesgo de bajo nivel de Potasio activo en la planta."
    elif r_k_mg <= 3.00:
        c3 = "✅ Óptimo (1.50-3.00). Evita clorosis foliares de magnesio por exceso de potasio."
    else:
        c3 = "⚠️ Relación alta. El exceso de Potasio provoca clorosis foliar por deficiencia de Magnesio."

    # Relation 4
    if r_n_k < 1.00:
        c4 = "⚠️ Relación baja. Exceso de Potasio o falta de Nitrógeno (reduce el vigor)."
    elif r_n_k <= 1.60:
        c4 = "✅ Óptimo (1.00-1.60). Equilibrio vegetativo-productivo."
    else:
        c4 = "⚠️ Relación alta. Exceso de Nitrógeno o deficiencia de Potasio."

    # Relation 5
    if r_n_p < 8.00:
        c5 = "⚠️ Relación baja. Exceso de Fósforo o falta de Nitrógeno."
    elif r_n_p <= 12.00:
        c5 = "✅ Óptimo (8.00-12.00). Desarrollo de raíces y vigor."
    else:
        c5 = "⚠️ Relación alta. Exceso de Nitrógeno o deficiencia de Fósforo."

    df_sonn_r = pd.DataFrame({
        "Relación Molar": ["K / (Ca + Mg)", "Ca / Mg", "K / Mg", "N / K", "N / P"],
        "Valor Real": [r_k_ca_mg, r_ca_mg, r_k_mg, r_n_k, r_n_p],
        "Rango Óptimo Sonneveld": ["0.30 - 0.50", "2.50 - 5.00", "1.50 - 3.00", "1.00 - 1.60", "8.00 - 12.00"],
        "Diagnóstico": [c1, c2, c3, c4, c5]
    })
    st.table(df_sonn_r)

    # Triada Chart
    cat_sum_molar = got_k + got_ca + got_mg
    if cat_sum_molar > 0:
        pct_k = (got_k / cat_sum_molar) * 100
        pct_ca = (got_ca / cat_sum_molar) * 100
        pct_mg = (got_mg / cat_sum_molar) * 100
    else:
        pct_k, pct_ca, pct_mg = 33.3, 33.3, 33.3

    st.markdown("### 📊 Tríada Catiónica (Porcentajes Molares de K:Ca:Mg):")
    st.progress(pct_k / 100, text=f"Potasio (K⁺): {pct_k:.1f}%")
    st.progress(pct_ca / 100, text=f"Calcio (Ca²⁺): {pct_ca:.1f}%")
    st.progress(pct_mg / 100, text=f"Magnesio (Mg²⁺): {pct_mg:.1f}%")

# ================= TAB 7: DICTAMEN EXPERTO =================
with tab_dictamen:
    st.markdown("### 💡 Diagnóstico Agronómico General de Riesgos")
    
    # Calculate Active CE Gota again for selected month
    sel_month_dict = st.selectbox("Ver diagnóstico del mes:", month_names_select, key="sel_dict")
    d_idx = month_names_select.index(sel_month_dict) + 1
    sd = st.session_state.monthly_data[d_idx]

    ec_gota_activa = st.session_state.water_ec
    for sol in sd["solubles"]:
        p = SOLUBLES_DB.get(sol["name"])
        if p and sd["water"] > 0:
            conc = sol["dosis"] / sd["water"]
            ec_gota_activa += conc * p["ec_coeff"]
    if sd["water"] > 0:
        ec_gota_activa += (acid_dose_l * neut_hco3 * 0.05)

    threshold_crop = CULTIVOS_DB[st.session_state.crop]["limite_salino"]

    # Warning 1: Salinity
    if ec_gota_activa > threshold_crop:
        loss_p = (ec_gota_activa - threshold_crop) * 10.0
        st.error(f"❌ **RIESGO DE SALINIDAD EN {sd['name'].upper()}**: La conductividad en el gotero ({ec_gota_activa:.2f} dS/m) excede el umbral de tolerancia del {st.session_state.crop} ({threshold_crop:.2f} dS/m). Pérdida de rendimiento estimada: **{loss_p:.0f}%**.")
    else:
        st.success(f"✅ **SALINIDAD CONTROLADA EN {sd['name'].upper()}**: Conductividad de la gota ({ec_gota_activa:.2f} dS/m) óptima para el cultivo.")

    # Warning 2: RAS
    if ras_val > 9.0:
        st.error(f"❌ **PELIGRO DE SODICIDAD DE SUELO (RAS: {ras_val:.1f})**: Estructura del suelo propensa a la dispersión de arcillas y compactación severa.")
    elif ras_val > 6.0:
        st.warning(f"⚠️ **RIESGO DE SODICIDAD MODERADO (RAS: {ras_val:.1f})**: Reducción de infiltración de agua. Vigile el drenaje.")
    else:
        st.success(f"✅ **SODIO EQUILIBRADO (RAS: {ras_val:.2f})**: El agua es segura y no representa riesgos estructurales para el suelo.")

    # Warning 3: Chlorine
    if meq_cl > 4.0:
        st.warning("⚠️ **ALERTA POR TOXICIDAD DE CLORUROS**: Concentración de cloruros supera 4.0 meq/L. Cuidado en variedades sensibles de cítricos o frutales de hueso.")
    else:
        st.success("✅ **CONCENTRACIÓN DE CLORUROS SEGURA**: No se prevén mermas por toxicidad foliar.")

    # Warning 4: Bicarbonatos
    hco3_mg_l = st.session_state.water_hco3
    if hco3_mg_l > 150.0:
        st.warning(f"⚠️ **RIESGO DE OBTURACIÓN CALIZA EN GOTERO**: Alta concentración de Bicarbonatos ({hco3_mg_l:.1f} mg/L). Se aconseja inyectar ácido regularmente.")
    else:
        st.success("✅ **RIESGO BAJO DE OBTURACIÓN**: Los niveles de carbonatos están controlados.")
