"""Catálogos de datos del Programa de Fertirrigación (cultivos, fertilizantes,
soluciones de referencia). Puerto literal de las constantes JS de
programa_fertirrigacion.html — misma fuente de verdad que ese HTML.
"""

# 22 cultivos con coeficientes de extracción (kg/t) y límites de salinidad (dS/m)
CULTIVO_EXTRACCIONES = {
    "Caqui (Kaki)": {"n": 4.00, "p": 1.00, "k": 3.50, "mg": 0.60, "ca": 1.50, "s": 0.80},
    "Pimiento": {"n": 5.00, "p": 1.60, "k": 6.50, "mg": 0.80, "ca": 2.00, "s": 0.90},
    "Tomate": {"n": 3.00, "p": 1.00, "k": 5.50, "mg": 0.80, "ca": 2.00, "s": 0.70},
    "Limonero": {"n": 5.00, "p": 1.20, "k": 4.00, "mg": 0.80, "ca": 1.80, "s": 0.90},
    "Mandarino": {"n": 5.00, "p": 1.10, "k": 3.80, "mg": 0.70, "ca": 1.60, "s": 0.85},
    "Naranjo": {"n": 5.00, "p": 1.00, "k": 3.50, "mg": 0.60, "ca": 1.50, "s": 0.80},
    "Olivar SI": {"n": 8.00, "p": 4.00, "k": 12.00, "mg": 1.20, "ca": 2.50, "s": 1.00},
    "Olivar": {"n": 12.00, "p": 4.00, "k": 10.00, "mg": 4.00, "ca": 8.00, "s": 2.00},
    "Aguacate": {"n": 20.00, "p": 15.00, "k": 20.00, "mg": 1.50, "ca": 1.00, "s": 1.10},
    "Almendro (pepita)": {"n": 65.00, "p": 25.00, "k": 70.00, "mg": 15.00, "ca": 20.00, "s": 5.00},
    "Cebolla": {"n": 4.00, "p": 1.20, "k": 4.50, "mg": 0.80, "ca": 1.50, "s": 0.75},
    "Patata": {"n": 4.50, "p": 1.80, "k": 7.50, "mg": 0.80, "ca": 1.00, "s": 0.90},
    "Fresa": {"n": 4.50, "p": 1.50, "k": 6.50, "mg": 1.00, "ca": 2.00, "s": 1.00},
    "Pistacho (grano seco)": {"n": 55.00, "p": 20.00, "k": 60.00, "mg": 12.00, "ca": 18.00, "s": 4.50},
    "Vid vinificación": {"n": 4.00, "p": 1.50, "k": 5.00, "mg": 1.00, "ca": 2.00, "s": 0.90},
    "Trigo blando": {"n": 35.00, "p": 10.00, "k": 18.00, "mg": 4.00, "ca": 6.00, "s": 3.50},
    "Cebada": {"n": 22.00, "p": 10.00, "k": 20.00, "mg": 4.00, "ca": 5.00, "s": 3.00},
    "Maíz grano": {"n": 35.00, "p": 10.00, "k": 25.00, "mg": 5.00, "ca": 4.00, "s": 3.50},
    "Espárrago": {"n": 10.00, "p": 3.00, "k": 12.00, "mg": 1.50, "ca": 3.00, "s": 2.0},
    "Colza": {"n": 60.00, "p": 30.00, "k": 45.00, "mg": 12.00, "ca": 25.00, "s": 6.50},
    "Algodón": {"n": 55.00, "p": 25.00, "k": 55.00, "mg": 12.00, "ca": 18.00, "s": 6.00},
}

LIMITES_SALINOS = {
    "Caqui (Kaki)": 2.0, "Pimiento": 1.5, "Tomate": 2.5, "Limonero": 1.7, "Mandarino": 1.7,
    "Naranjo": 1.7, "Olivar SI": 3.5, "Olivar": 3.5, "Aguacate": 1.3, "Almendro (pepita)": 1.5,
    "Cebolla": 1.2, "Patata": 1.7, "Fresa": 1.0, "Pistacho (grano seco)": 4.5,
    "Vid vinificación": 1.5, "Trigo blando": 6.0, "Cebada": 8.0, "Maíz grano": 1.7,
    "Espárrago": 1.5, "Colza": 1.5, "Algodón": 7.7,
}

# Prioridades/tendencias nutricionales por fase fenológica (guía conceptual, no receta numérica
# universal — Guía práctica de fertirrigación, sección 10, con base FAO/Penn State/OSU/UF-IFAS).
FASES_INFO = {
    "sin_fase": {"label": "Sin fase específica / Reposo", "prioridad": "—", "tendencia": "Sin prioridad nutricional específica definida para esta fase.", "objetivo": "—"},
    "arranque": {"label": "Arranque / Brotación", "prioridad": "N + P + Ca", "tendencia": "N moderado; P disponible; Ca estable; CE moderada", "objetivo": "Raíz, brotación y establecimiento"},
    "vegetativo": {"label": "Crecimiento vegetativo", "prioridad": "N + K + Ca + Mg", "tendencia": "Sube N/K según demanda; Mg y S acompañan", "objetivo": "Biomasa y área foliar"},
    "floracion": {"label": "Prefloración / Floración", "prioridad": "P + K + Ca + B", "tendencia": "Reducir dependencia de N; reforzar K/Ca; micronutrientes según cultivo", "objetivo": "Floración, cuajado"},
    "cuajado": {"label": "Cuajado / Crecimiento de fruto", "prioridad": "K + Ca + Mg", "tendencia": "K alto relativo; Ca estable; N controlado", "objetivo": "Translocación, calibre y calidad"},
    "engorde": {"label": "Engorde / Llenado", "prioridad": "K + Ca + Mg", "tendencia": "K dominante; N moderado-bajo", "objetivo": "Materia seca, calibre y calidad"},
    "maduracion": {"label": "Maduración", "prioridad": "K; N bajo", "tendencia": "Reducir N; mantener K según cultivo", "objetivo": "Calidad y maduración"},
    "precosecha": {"label": "Pre-cosecha", "prioridad": "Según extracción y análisis", "tendencia": "Evitar exceso de CE y de N", "objetivo": "No forzar crecimiento vegetativo"},
}

# Soluciones nutritivas clásicas de hidroponía — solo referencia comparativa, no aplicables
# directamente a fertirrigación en suelo. Macros en meq/L, micros en ppm.
SOLUCIONES_REFERENCIA_HIDROPONIA = [
    {"nombre": "Steiner 100%", "nh4": 0, "no3": 12, "p": 1, "s": 7, "k": 7, "ca": 9, "mg": 4, "fe": 1.33, "mn": 0.62, "zn": 0.11, "b": 0.05, "cu": 0.02, "mo": 0.04},
    {"nombre": "Hoagland & Arnon I", "nh4": 0, "no3": 15, "p": 1, "s": 4, "k": 6, "ca": 10, "mg": 4, "fe": 1, "mn": 0.5, "zn": 0.05, "b": 0.5, "cu": 0.02, "mo": 0.048},
    {"nombre": "Hoagland & Arnon II", "nh4": 1, "no3": 14, "p": 1, "s": 4, "k": 6, "ca": 8, "mg": 4, "fe": 1, "mn": 0.5, "zn": 0.05, "b": 0.5, "cu": 0.02, "mo": 0.011},
    {"nombre": "Long Ashton – Hewitt", "nh4": 0, "no3": 12, "p": 1.32, "s": 3, "k": 4, "ca": 8, "mg": 3, "fe": 2.8, "mn": 0.55, "zn": 0.065, "b": 0.54, "cu": 0.064, "mo": 0.048},
    {"nombre": "Knop", "nh4": 0, "no3": 14.66, "p": 1.84, "s": 2.03, "k": 4.31, "ca": 12.19, "mg": 2.03, "fe": 0, "mn": 0, "zn": 0, "b": 0, "cu": 0, "mo": 0},
]

# 23 complejos granulados de fondo — catálogo oficial completo EuroChem (misma tabla que
# programa_fertirrigacion.html / plan_abonado_integrado.html). nh4/no3 en % absoluto del
# producto (nh4+no3 = n), no en % del N.
GRANULADOS_DB = {
    "Nitrofoska Special 12-12-17": {"n": 12, "no3": 4.8, "nh4": 7.2, "p": 12, "k": 17, "mg": 2, "ca": 0, "s": 20},
    "Nitrofoska Perfect 15-5-20": {"n": 15, "no3": 7, "nh4": 8, "p": 5, "k": 20, "mg": 2, "ca": 0, "s": 22.5},
    "Nitrofoska Super 20-5-10": {"n": 20, "no3": 9.5, "nh4": 10.5, "p": 5, "k": 10, "mg": 3, "ca": 0, "s": 12.5},
    "Nitrofoska MOP 12-20-12": {"n": 12, "no3": 4.5, "nh4": 7.5, "p": 20, "k": 12, "mg": 0, "ca": 0, "s": 0},
    "Nitrofoska MOP 15-15-15": {"n": 15, "no3": 6, "nh4": 9, "p": 15, "k": 15, "mg": 0, "ca": 0, "s": 5},
    "Nitrofoska MOP 22-8-10": {"n": 22, "no3": 10.2, "nh4": 11.8, "p": 8, "k": 10, "mg": 0, "ca": 0, "s": 2.5},
    "Nitrofoska Nitrofos 20-20": {"n": 20, "no3": 8.2, "nh4": 11.8, "p": 20, "k": 0, "mg": 0, "ca": 0, "s": 5},
    "Nitrofoska N Plus 22-5-5": {"n": 22, "no3": 10, "nh4": 12, "p": 5, "k": 5, "mg": 2, "ca": 0, "s": 7.5},
    "ENTEC 12-20-12": {"n": 12, "no3": 3.9, "nh4": 8.1, "p": 20, "k": 12, "mg": 0, "ca": 0, "s": 5},
    "ENTEC 13-9-16": {"n": 13, "no3": 3.6, "nh4": 9.4, "p": 9, "k": 16, "mg": 4, "ca": 0, "s": 20},
    "ENTEC 13-10-20": {"n": 13, "no3": 3.7, "nh4": 9.3, "p": 10, "k": 20, "mg": 0, "ca": 0, "s": 12.5},
    "ENTEC 15-13-13": {"n": 15, "no3": 5, "nh4": 10, "p": 13, "k": 13, "mg": 0, "ca": 0, "s": 12.5},
    "ENTEC 20-8-10": {"n": 20, "no3": 8.8, "nh4": 11.2, "p": 8, "k": 10, "mg": 2, "ca": 0, "s": 7.5},
    "ENTEC 20-10-10": {"n": 20, "no3": 8.6, "nh4": 11.4, "p": 10, "k": 10, "mg": 0, "ca": 0, "s": 7.5},
    "ENTEC 24-8-7": {"n": 24, "no3": 10.8, "nh4": 13.3, "p": 8, "k": 7, "mg": 0, "ca": 0, "s": 5},
    "ENTEC 25-15": {"n": 25, "no3": 11, "nh4": 14, "p": 15, "k": 0, "mg": 0, "ca": 0, "s": 2.5},
    "ENTEC Nitrofoska Especial 12-12-17": {"n": 12, "no3": 4.8, "nh4": 7.2, "p": 12, "k": 17, "mg": 2, "ca": 0, "s": 20},
    "ENTEC Nitrofoska 14-7-17": {"n": 14, "no3": 6.1, "nh4": 7.9, "p": 7, "k": 17, "mg": 2, "ca": 0, "s": 22.5},
    "ENTEC Nitrofoska 21-8-11": {"n": 21, "no3": 9.7, "nh4": 11.3, "p": 8, "k": 11, "mg": 0, "ca": 0, "s": 10},
    "ENTEC Evo 24": {"n": 24, "no3": 12, "nh4": 12, "p": 0, "k": 0, "mg": 0, "ca": 12.3, "s": 15},
    "ENTEC Evo 27": {"n": 27, "no3": 13.5, "nh4": 13.5, "p": 0, "k": 0, "mg": 0, "ca": 0, "s": 0},
    "ENTEC Evo 27S": {"n": 27, "no3": 13.5, "nh4": 13.5, "p": 0, "k": 0, "mg": 0, "ca": 9.2, "s": 10},
    "ENTEC Evo 27 Carbon Light": {"n": 27, "no3": 13.5, "nh4": 13.5, "p": 0, "k": 0, "mg": 0, "ca": 0, "s": 0},
}

# Catálogo de productos foliares/correctores. Composiciones reales tomadas de sus fichas de
# datos (PDS) oficiales EuroChem Agro Iberia S.L. (EU) 2019/1009, rev. 1.03 de 23-sep-2025.
FOLIARES_DB = {
    "Nitrofoska Foliar 10-5-33": {"n": 10.3, "p": 5, "k": 33, "mg": 2, "ca": 0, "s": 12.8, "fe": 0.05, "mn": 0.05, "zn": 0.02, "cu": 0.02, "b": 2, "mo": 0.001},
    "Nitrofoska Foliar 24-8-20": {"n": 24, "p": 8, "k": 20, "mg": 2, "ca": 0, "s": 4.1, "fe": 0.05, "mn": 0.05, "zn": 0.02, "cu": 0.02, "b": 0.2, "mo": 0.001},
}

# 22 fertilizantes solubles Eurochem. 'tanque': A = cálcicos, B = sulfatos/fosfatos, N = neutro
# — no mezclar nunca A con B en la misma cuba (riesgo de precipitado de CaSO4/fosfato cálcico).
SOLUBLES_DB = {
    "ENTEC Solub 21": {"n": 21, "p": 0, "k": 0, "mg": 0, "ca": 0, "s": 60, "nh4": 21, "no3": 0, "ec_coeff": 0.8, "tanque": "B"},
    "ENTEC Solub 20-5-10": {"n": 20, "p": 5, "k": 10, "mg": 2, "ca": 0, "s": 27, "nh4": 6, "no3": 5, "ec_coeff": 0.7, "tanque": "B"},
    "ENTEC Solub 11-5-30": {"n": 11, "p": 5, "k": 30, "mg": 2, "ca": 0, "s": 27, "nh4": 9, "no3": 6, "ec_coeff": 0.75, "tanque": "B"},
    "ENTEC Solub 16-10-17": {"n": 16, "p": 10, "k": 17, "mg": 2, "ca": 0, "s": 12, "nh4": 10, "no3": 6, "ec_coeff": 0.7, "tanque": "B"},
    "Nitrofoska Solub Calcium K": {"n": 14, "p": 7, "k": 17, "mg": 0, "ca": 13, "s": 0, "nh4": 2, "no3": 12, "ec_coeff": 0.75, "tanque": "A"},
    "Nitrofoska Solub 7-5-40": {"n": 7, "p": 5, "k": 40, "mg": 0, "ca": 0, "s": 28, "nh4": 3, "no3": 4, "ec_coeff": 0.6, "tanque": "B"},
    "Nitrofoska Solub 15-10-15": {"n": 15, "p": 10, "k": 15, "mg": 2, "ca": 0, "s": 30, "nh4": 10.7, "no3": 4.3, "ec_coeff": 0.65, "tanque": "B"},
    "Nitrofoska Solub 13-40-13": {"n": 13, "p": 40, "k": 13, "mg": 0, "ca": 0, "s": 1.9, "nh4": 8.8, "no3": 4.2, "ec_coeff": 0.55, "tanque": "B"},
    "Nitrofoska Solub 12-5-30": {"n": 12, "p": 5, "k": 30, "mg": 1, "ca": 0, "s": 22, "nh4": 1.9, "no3": 5.1, "ec_coeff": 0.8, "tanque": "B"},
    "Nitrofoska Solub 7-12-40": {"n": 7, "p": 12, "k": 40, "mg": 0, "ca": 0, "s": 18.4, "nh4": 9, "no3": 6, "ec_coeff": 0.6, "tanque": "B"},
    "Nitrofoska Solub 18-18-18": {"n": 18, "p": 18, "k": 18, "mg": 0, "ca": 0, "s": 11.5, "nh4": 10, "no3": 8, "ec_coeff": 0.6, "tanque": "B"},
    "Nitrofoska Solub 20-5-5": {"n": 20, "p": 5, "k": 5, "mg": 2, "ca": 0, "s": 37, "nh4": 15.6, "no3": 4.4, "ec_coeff": 0.85, "tanque": "B"},
    "Nitrato Cálcico Soluble": {"n": 15.5, "p": 0, "k": 0, "mg": 0, "ca": 26.3, "s": 0, "nh4": 1.1, "no3": 14.4, "ec_coeff": 0.72, "tanque": "A"},
    "Nitrato Magnésico Soluble": {"n": 11, "p": 0, "k": 0, "mg": 15.4, "ca": 0, "s": 0, "nh4": 0, "no3": 11, "ec_coeff": 0.68, "tanque": "N"},
    "NOP Solub": {"n": 13, "p": 0, "k": 46, "mg": 0, "ca": 0, "s": 0, "nh4": 0, "no3": 13, "ec_coeff": 0.8, "tanque": "N"},
    "MAP Solub": {"n": 12, "p": 61, "k": 0, "mg": 0, "ca": 0, "s": 0, "nh4": 12, "no3": 0, "ec_coeff": 0.52, "tanque": "B"},
    "UP solub": {"n": 18, "p": 44, "k": 0, "mg": 0, "ca": 0, "s": 0, "nh4": 18, "no3": 0, "ec_coeff": 0.82, "tanque": "B"},
    "SOP solub": {"n": 0, "p": 0, "k": 52, "mg": 0, "ca": 0, "s": 45, "nh4": 0, "no3": 0, "ec_coeff": 0.88, "tanque": "B"},
    "Sulfato de Magnesio": {"n": 0, "p": 0, "k": 0, "mg": 16, "ca": 0, "s": 32, "nh4": 0, "no3": 0, "ec_coeff": 0.62, "tanque": "B"},
    "Ácido Fosfórico": {"n": 0, "p": 52, "k": 0, "mg": 0, "ca": 0, "s": 0, "nh4": 0, "no3": 0, "ec_coeff": 0.48, "tanque": "B"},
    "Ácido Nítrico": {"n": 15, "p": 0, "k": 0, "mg": 0, "ca": 0, "s": 0, "nh4": 0, "no3": 15, "ec_coeff": 0.5, "tanque": "N"},
}

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

FASE_POR_DEFECTO_MES = {
    1: "sin_fase", 2: "sin_fase", 3: "arranque", 4: "arranque", 5: "floracion",
    6: "cuajado", 7: "engorde", 8: "engorde", 9: "maduracion", 10: "precosecha",
    11: "sin_fase", 12: "sin_fase",
}


def monthly_data_por_defecto() -> dict:
    """Estado inicial de los 12 meses, igual que monthlyData en el HTML."""
    data = {}
    for m in range(1, 13):
        data[m] = {
            "name": MESES[m - 1],
            "water": 0.0,
            "num_riegos": 0,
            "cuba_vol": 1000.0,
            "flow_rate": 1.6,
            "tiempo_riego": 2.0,
            "fase": FASE_POR_DEFECTO_MES[m],
            "solubles": [],
        }
    data[5]["solubles"] = [
        {"name": "Nitrofoska Solub 18-18-18", "dosis": 0.0},
        {"name": "MAP Solub", "dosis": 0.0},
    ]
    data[7]["solubles"] = [
        {"name": "ENTEC Solub 11-5-30", "dosis": 0.0},
        {"name": "Nitrato Cálcico Soluble", "dosis": 0.0},
    ]
    data[8]["solubles"] = [{"name": "SOP solub", "dosis": 0.0}]
    return data
