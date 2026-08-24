"""Catálogos de datos del Plan de Abonado Integrado. Puerto literal de las
constantes JS de plan_abonado_integrado.html.
"""

CULTIVO_EXTRACTIONS = {
    "trigo": {"n": 28, "p": 10, "k": 25, "label": "Trigo"},
    "cebada": {"n": 22, "p": 9, "k": 20, "label": "Cebada"},
    "avena": {"n": 22, "p": 9, "k": 20, "label": "Avena"},
    "triticale": {"n": 25, "p": 10, "k": 22, "label": "Triticale"},
    "maiz": {"n": 24, "p": 10, "k": 25, "label": "Maíz"},
    "girasol": {"n": 35, "p": 12, "k": 30, "label": "Girasol"},
    "colza": {"n": 45, "p": 18, "k": 40, "label": "Colza"},
    "algodon": {"n": 55, "p": 20, "k": 50, "label": "Algodón"},
    "garbanzo": {"n": 60, "p": 15, "k": 35, "label": "Garbanzo"},
    "guisante": {"n": 50, "p": 12, "k": 30, "label": "Guisante"},
    "olivar_si": {"n": 8, "p": 3, "k": 10, "label": "Olivar SI"},
    "olivar": {"n": 15, "p": 4, "k": 20, "label": "Olivar"},
    "almendro": {"n": 65, "p": 20, "k": 70, "label": "Almendro pepita"},
    "naranjo": {"n": 4, "p": 1.5, "k": 6, "label": "Naranjo"},
    "mandarino": {"n": 5, "p": 1.8, "k": 7, "label": "Mandarino"},
    "limonero": {"n": 5, "p": 1.8, "k": 7, "label": "Limonero"},
    "vinedo": {"n": 5, "p": 2, "k": 8, "label": "Viñedo"},
    "patata": {"n": 4.2, "p": 1.0, "k": 5.6, "label": "Patata"},
    "remolacha": {"n": 3.0, "p": 1.5, "k": 4.0, "label": "Remolacha azucarera"},
    "tabaco": {"n": 35, "p": 15, "k": 60, "label": "Tabaco"},
    "tomate_industria": {"n": 2.2, "p": 0.8, "k": 2.6, "label": "Tomate para industria"},
    "freson": {"n": 6.0, "p": 2.5, "k": 8.0, "label": "Fresa y fresón"},
    "aguacate": {"n": 12.0, "p": 7.0, "k": 20.0, "label": "Aguacate"},
}

# Catálogo de riqueza de fertilizantes granulados EuroChem (23 fórmulas oficiales), mismos datos
# que GRANULADOS_DB en fertirrigacion_data.py, con las claves snake_case propias de este programa.
FERT_DATA = {
    "0": {"n": 0, "p": 0, "k": 0, "mg": 0, "ca": 0, "s": 0, "label": "Ninguno"},
    "nitrofoska_special_12_12_17": {"n": 12, "no3": 4.8, "nh4": 7.2, "p": 12, "k": 17, "mg": 2, "ca": 0, "s": 20, "label": "NITROFOSKA SPECIAL (12-12-17)"},
    "perfect_15_5_20": {"n": 15, "no3": 7, "nh4": 8, "p": 5, "k": 20, "mg": 2, "ca": 0, "s": 22.5, "label": "NITROFOSKA PERFECT (15-5-20)"},
    "super_20_5_10": {"n": 20, "no3": 9.5, "nh4": 10.5, "p": 5, "k": 10, "mg": 3, "ca": 0, "s": 12.5, "label": "NITROFOSKA SUPER (20-5-10)"},
    "nitrofoska_mop_12_20_12": {"n": 12, "no3": 4.5, "nh4": 7.5, "p": 20, "k": 12, "mg": 0, "ca": 0, "s": 0, "label": "NITROFOSKA MOP (12-20-12)"},
    "nitrofoska_mop_15_15_15": {"n": 15, "no3": 6, "nh4": 9, "p": 15, "k": 15, "mg": 0, "ca": 0, "s": 5, "label": "NITROFOSKA MOP (15-15-15)"},
    "nitrofoska_mop_22_8_10": {"n": 22, "no3": 10.2, "nh4": 11.8, "p": 8, "k": 10, "mg": 0, "ca": 0, "s": 2.5, "label": "NITROFOSKA MOP (22-8-10)"},
    "nitrofoska_nitrofos_20_20": {"n": 20, "no3": 8.2, "nh4": 11.8, "p": 20, "k": 0, "mg": 0, "ca": 0, "s": 5, "label": "NITROFOSKA NITROFOS (20-20)"},
    "nplus_22_5_5": {"n": 22, "no3": 10, "nh4": 12, "p": 5, "k": 5, "mg": 2, "ca": 0, "s": 7.5, "label": "NITROFOSKA NPLUS (22-5-5)"},
    "entec_12_20_12": {"n": 12, "no3": 3.9, "nh4": 8.1, "p": 20, "k": 12, "mg": 0, "ca": 0, "s": 5, "label": "ENTEC 12 20 12"},
    "entec_13_9_16": {"n": 13, "no3": 3.6, "nh4": 9.4, "p": 9, "k": 16, "mg": 4, "ca": 0, "s": 20, "label": "ENTEC 13 9 16"},
    "entec_13_10_20": {"n": 13, "no3": 3.7, "nh4": 9.3, "p": 10, "k": 20, "mg": 0, "ca": 0, "s": 12.5, "label": "ENTEC 13 10 20"},
    "entec_15_13_13": {"n": 15, "no3": 5, "nh4": 10, "p": 13, "k": 13, "mg": 0, "ca": 0, "s": 12.5, "label": "ENTEC 15 13 13"},
    "entec_20_8_10": {"n": 20, "no3": 8.8, "nh4": 11.2, "p": 8, "k": 10, "mg": 2, "ca": 0, "s": 7.5, "label": "ENTEC 20 8 10"},
    "entec_20_10_10": {"n": 20, "no3": 8.6, "nh4": 11.4, "p": 10, "k": 10, "mg": 0, "ca": 0, "s": 7.5, "label": "ENTEC 20 10 10"},
    "entec_24_8_7": {"n": 24, "no3": 10.8, "nh4": 13.3, "p": 8, "k": 7, "mg": 0, "ca": 0, "s": 5, "label": "ENTEC 24 8 7"},
    "entec_25_15": {"n": 25, "no3": 11, "nh4": 14, "p": 15, "k": 0, "mg": 0, "ca": 0, "s": 2.5, "label": "ENTEC 25 15"},
    "entec_12_12_17": {"n": 12, "no3": 4.8, "nh4": 7.2, "p": 12, "k": 17, "mg": 2, "ca": 0, "s": 20, "label": "ENTEC NITROFOSKA ESPECIAL (12-12-17)"},
    "entec_nitrofoska_14_7_17": {"n": 14, "no3": 6.1, "nh4": 7.9, "p": 7, "k": 17, "mg": 2, "ca": 0, "s": 22.5, "label": "ENTEC NITROFOSKA (14-7-17)"},
    "entec_nitrofoska_21_8_11": {"n": 21, "no3": 9.7, "nh4": 11.3, "p": 8, "k": 11, "mg": 0, "ca": 0, "s": 10, "label": "ENTEC NITROFOSKA (21-8-11)"},
    "entec_evo_24": {"n": 24, "no3": 12, "nh4": 12, "p": 0, "k": 0, "mg": 0, "ca": 12.3, "s": 15, "label": "ENTEC EVO 24 (24% N)"},
    "entec_evo_27": {"n": 27, "no3": 13.5, "nh4": 13.5, "p": 0, "k": 0, "mg": 0, "ca": 0, "s": 0, "label": "ENTEC EVO 27 (27% N)"},
    "entec_evo_27s": {"n": 27, "no3": 13.5, "nh4": 13.5, "p": 0, "k": 0, "mg": 0, "ca": 9.2, "s": 10, "label": "ENTEC EVO 27S (27% N)"},
    "entec_evo_27_carbon_light": {"n": 27, "no3": 13.5, "nh4": 13.5, "p": 0, "k": 0, "mg": 0, "ca": 0, "s": 0, "label": "ENTEC EVO 27 CARBON LIGHT (27% N)"},
}

# Selectores de Cobertera 1/2 solo listan los productos de liberación rápida/ENTEC EVO (igual que
# el HTML): fórmulas pensadas para aplicación en cobertera, no todo el catálogo de fondo.
FERT_COBERTERA_KEYS = [
    "entec_evo_27", "entec_evo_27s", "entec_evo_27_carbon_light", "entec_evo_24",
    "entec_24_8_7", "nplus_22_5_5", "entec_20_8_10", "entec_20_10_10",
]
FERT_COBERTERA2_KEYS = ["entec_evo_27", "entec_evo_27s", "entec_evo_27_carbon_light", "entec_evo_24", "nplus_22_5_5"]

FOLIARES_DB = {
    "Nitrofoska Foliar 10-5-33": {"n": 10.3, "p": 5, "k": 33, "mg": 2, "ca": 0, "s": 12.8, "fe": 0.05, "mn": 0.05, "zn": 0.02, "cu": 0.02, "b": 2, "mo": 0.001},
    "Nitrofoska Foliar 24-8-20": {"n": 24, "p": 8, "k": 20, "mg": 2, "ca": 0, "s": 4.1, "fe": 0.05, "mn": 0.05, "zn": 0.02, "cu": 0.02, "b": 0.2, "mo": 0.001},
}

ESTIERCOL_DATA = {
    "0": {"n": 0, "y1": 0, "y2": 0, "y3": 0, "label": "Ninguno"},
    "bovino": {"n": 5.0, "y1": 0.50, "y2": 0.35, "y3": 0.15, "label": "Bovino"},
    "ovino": {"n": 9.0, "y1": 0.50, "y2": 0.35, "y3": 0.15, "label": "Ovino"},
    "caprino": {"n": 10.0, "y1": 0.50, "y2": 0.35, "y3": 0.15, "label": "Caprino"},
    "equino": {"n": 6.0, "y1": 0.50, "y2": 0.35, "y3": 0.15, "label": "Equino"},
    "gallinaza": {"n": 16.0, "y1": 0.60, "y2": 0.25, "y3": 0.15, "label": "Gallinaza"},
    "pollinaza": {"n": 20.0, "y1": 0.60, "y2": 0.25, "y3": 0.15, "label": "Pollinaza"},
    "porcino": {"n": 7.0, "y1": 0.50, "y2": 0.35, "y3": 0.15, "label": "Porcino"},
}

PURINES_DATA = {
    "0": {"n": 0, "y1": 0, "y2": 0, "y3": 0, "label": "Ninguno"},
    "porcino_cebo": {"n": 3.5, "y1": 0.70, "y2": 0.20, "y3": 0.10, "label": "Porcino cebo"},
    "porcino_maternidad": {"n": 3.0, "y1": 0.70, "y2": 0.20, "y3": 0.10, "label": "Porcino maternidad"},
    "vacuno_leche": {"n": 2.5, "y1": 0.70, "y2": 0.20, "y3": 0.10, "label": "Vacuno leche"},
    "vacuno_carne": {"n": 2.0, "y1": 0.70, "y2": 0.20, "y3": 0.10, "label": "Vacuno carne"},
    "ovino_caprino": {"n": 3.0, "y1": 0.70, "y2": 0.20, "y3": 0.10, "label": "Ovino/caprino"},
    "gallinaza_liquida": {"n": 6.0, "y1": 0.70, "y2": 0.15, "y3": 0.15, "label": "Gallinaza líquida"},
}

# Claves de FERT_DATA que llevan inhibidor de la nitrificación/ureasa o son liberación lenta —
# todas las gamas ENTEC, salvo las Nitrofoska "normales". Exime del tope del 30% de N en fondo
# en Zona Vulnerable a Nitratos (BOJA nº214/2020).
ENTEC_INHIBIDOR_KEYS = {
    "entec_12_12_17", "entec_20_10_10", "entec_20_8_10", "entec_25_15", "entec_15_13_13",
    "entec_12_20_12", "entec_13_10_20", "entec_evo_27s", "entec_evo_24",
    "entec_13_9_16", "entec_24_8_7", "entec_nitrofoska_14_7_17", "entec_nitrofoska_21_8_11",
    "entec_evo_27", "entec_evo_27_carbon_light",
}

# Notas de manejo de fondo/cobertera del Cuadro 4 (Anexo I, BOJA nº214/2020), Zona Vulnerable a
# Nitratos de Andalucía. ufnT = kg N/tonelada de producción esperada (tope legal = ufnT × rendimiento).
# cap30 = si aplica el tope genérico de máx. 30% del N total en fondo (salvo inhibidor/liberación lenta).
CULTIVO_ZVN_NOTES = {
    "trigo": {"ufnT": 35, "cap30": True, "fondoNote": "Máx. 30% del N total en fondo (exento con inhibidor o liberación lenta).", "coberteraNote": "Fraccionar en al menos 2 veces: ahijado y encañado."},
    "cebada": {"ufnT": 35, "cap30": True, "fondoNote": "Máx. 30% del N total en fondo (exento con inhibidor o liberación lenta).", "coberteraNote": "Fraccionar en al menos 2 veces: ahijado y encañado."},
    "avena": {"ufnT": 35, "cap30": True, "fondoNote": "Máx. 30% del N total en fondo (exento con inhibidor o liberación lenta).", "coberteraNote": "Fraccionar en al menos 2 veces: ahijado y encañado."},
    "triticale": {"ufnT": 35, "cap30": True, "fondoNote": "Máx. 30% del N total en fondo (exento con inhibidor o liberación lenta).", "coberteraNote": "Fraccionar en al menos 2 veces: ahijado y encañado."},
    "maiz": {"ufnT": 25, "cap30": True, "fondoNote": "Máx. 30% del N total en fondo (exento con inhibidor o liberación lenta). 25 UFN/t si el destino es grano; 35 UFN/t si es ensilado.", "coberteraNote": "Fraccionar en 2 veces: 30 cm de altura y al inicio de la floración. Prohibido N tras los primeros penachos."},
    "girasol": {"ufnT": 40, "cap30": True, "fondoNote": "Máx. 30% del N total en fondo (exento con inhibidor o liberación lenta).", "coberteraNote": "Fraccionar en 2 veces: 20 cm de altura e inicio de formación del capítulo."},
    "colza": {"ufnT": 47, "cap30": False, "fondoNote": "Se recomienda aplicar entre el 30-50% del N en fondo para favorecer la implantación otoñal (no aplica el tope genérico del 30%).", "coberteraNote": "El resto en cobertera a la salida de la parada invernal."},
    "algodon": {"ufnT": 55, "cap30": True, "fondoNote": "Máx. 30% del N total en fondo (exento con inhibidor o liberación lenta).", "coberteraNote": "Fraccionar en 2 aportaciones: 10 cm de altura e inicio de floración. Prohibida urea en 2ª cobertera y N tras maduración."},
    "garbanzo": {"ufnT": 45, "cap30": True, "fondoNote": "Abonado de fondo hasta que se produzca la simbiosis con Rhizobium sp.; formados los nódulos, no se recomiendan más aportes.", "coberteraNote": "Si la nodulación funciona correctamente, no son necesarios más aportes nitrogenados."},
    "guisante": {"ufnT": 45, "cap30": True, "fondoNote": "Abonado de fondo hasta que se produzca la simbiosis con Rhizobium sp.; formados los nódulos, no se recomiendan más aportes.", "coberteraNote": "Si la nodulación funciona correctamente, no son necesarios más aportes nitrogenados."},
    "olivar_si": {"ufnT": 20, "cap30": False, "fondoNote": "Prohibido en meses fríos (diciembre y enero) sobre suelo desnudo. No aplica el tope genérico del 30%.", "coberteraNote": "En secano: un único aporte primaveral amoniacal u orgánico. En fertirrigación, ajustar según necesidades."},
    "olivar": {"ufnT": 20, "cap30": False, "fondoNote": "Prohibido en meses fríos (diciembre y enero) sobre suelo desnudo. No aplica el tope genérico del 30%.", "coberteraNote": "En secano: un único aporte primaveral amoniacal u orgánico. En fertirrigación, ajustar según necesidades."},
    "almendro": {"ufnT": 25, "cap30": False, "fondoNote": "Aplicar la fracción de fondo antes de la floración y antes de la aparición de hojas. No aplica el tope genérico del 30%.", "coberteraNote": "Fraccionar según demanda. Análisis foliares bianuales y analítica de suelo cada 4 años."},
    "naranjo": {"ufnT": 6, "cap30": False, "fondoNote": "Prohibido en fondo durante la parada invernal o próximo a la maduración del fruto. No aplica el tope genérico del 30%.", "coberteraNote": "50% antes de floración y 50% tras el cuajado. En riego localizado, descontar el N del agua de riego."},
    "mandarino": {"ufnT": 6, "cap30": False, "fondoNote": "Prohibido en fondo durante la parada invernal o próximo a la maduración del fruto. No aplica el tope genérico del 30%.", "coberteraNote": "50% antes de floración y 50% tras el cuajado. En riego localizado, descontar el N del agua de riego."},
    "limonero": {"ufnT": 6, "cap30": False, "fondoNote": "Prohibido en fondo durante la parada invernal o próximo a la maduración del fruto. No aplica el tope genérico del 30%.", "coberteraNote": "50% antes de floración y 50% tras el cuajado. En riego localizado, descontar el N del agua de riego."},
    "vinedo": {"ufnT": 7.8, "cap30": True, "fondoNote": "Máx. 30% del N total en fondo (exento con inhibidor o liberación lenta).", "coberteraNote": "Fraccionar los aportes a lo largo del desarrollo vegetativo según demanda de la vid."},
    "patata": {"ufnT": 8, "cap30": True, "fondoNote": "Máx. 30% del N total en fondo (exento con inhibidor o liberación lenta). Prohibido purín/lixiviado líquido. 8 UFN/t si es variedad nacional; 6 UFN/t si es importada; 4 UFN/t para el resto de tubérculos.", "coberteraNote": "Fraccionar en 2 aportes. Prohibido aplicar N transcurridos 60 días desde la siembra."},
    "remolacha": {"ufnT": 4.2, "cap30": True, "fondoNote": "Máx. 30% del N total en fondo (exento con inhibidor o liberación lenta).", "coberteraNote": "Abonar cobertera en 2 veces: una en el aclareo y otra un mes después. Prohibido N cuando la raíz alcance 400 g."},
    "tabaco": {"ufnT": 60, "cap30": True, "fondoNote": "Máx. 30% del N total en fondo (exento con inhibidor o liberación lenta). Prohibidos los abonos de alta solubilidad antes del trasplante.", "coberteraNote": "Fraccionar en dos o más veces según las necesidades fisiológicas del cultivo."},
    "tomate_industria": {"ufnT": 4, "cap30": True, "fondoNote": "Máx. 30% del N total en fondo (exento con inhibidor o liberación lenta). Prohibido purín/lixiviado líquido.", "coberteraNote": "Diseñar el plan nutricional según analíticas de suelo y agua de riego; ajustar en fertirrigación."},
    "freson": {"ufnT": 4, "cap30": True, "fondoNote": "Máx. 30% del N total en fondo (exento con inhibidor o liberación lenta). Prohibido purín/lixiviado líquido.", "coberteraNote": "Fertirrigación obligatoria. Analizar anualmente el agua de riego y los niveles foliares."},
    "aguacate": {"ufnT": 25, "cap30": False, "fondoNote": "Se recomienda integrar directamente en fertirrigación. No aplica el tope genérico del 30%.", "coberteraNote": "Aportaciones semanales de marzo a octubre."},
}

# Restricciones de Producción Integrada (PI), independientes y ADICIONALES a las de ZVN.
PI_NOTES = {
    "trigo": {
        "nAbsLimit": None,
        "fondoNote": "100% del P₂O₅ y K₂O en fondo. El N en fondo no debe superar el 30% del total (rango adecuado: 0-25%).",
        "coberteraNote": "El resto del N se fracciona en al menos 2 coberteras: 1ª (50-60% del N total) antes del ahijado; 2ª (0-50%) en el encañado. Se admite un aporte tardío en espigado de 30-35 kg N/ha en forma nítrica para mejorar la proteína, sin riesgo relevante de lixiviación.",
    },
    "algodon": {
        "nAbsLimit": 200, "nAbsLimitAgroambiental": 118.3, "pkAbsLimit": 96,
        "fondoNote": "1/3 del N total, más la totalidad del P₂O₅ y K₂O (salvo en riego por goteo), en fondo.",
        "coberteraNote": "2º tercio del N: 1ª cobertera en fase de 4-5 hojas verdaderas. 3er tercio: 2ª cobertera al inicio de los primeros botones florales. Prohibida la urea en la 2ª cobertera y cualquier N tras la maduración de las cápsulas.",
    },
    "olivar": {
        "regimenLimits": {"secano_tradicional": 70, "secano_intensivo": 100, "riego_tradicional": 120, "riego_intensivo": 150},
        "fondoNote": "Abono de fondo orgánico o mineral amoniacal al inicio de la actividad vegetativa primaveral.",
        "coberteraNote": "En fertirrigación: 70% del N desde la salida del reposo hasta el endurecimiento del hueso de la aceituna; 70% del K desde el endurecimiento hasta el final. Prohibido abonar en las vedas estacionales de ZVN, salvo riego localizado o agricultura de precisión.",
    },
    "olivar_si": {
        "regimenLimits": {"secano_tradicional": 70, "secano_intensivo": 100, "riego_tradicional": 120, "riego_intensivo": 150},
        "fondoNote": "Abono de fondo orgánico o mineral amoniacal al inicio de la actividad vegetativa primaveral.",
        "coberteraNote": "En fertirrigación: 70% del N desde la salida del reposo hasta el endurecimiento del hueso de la aceituna; 70% del K desde el endurecimiento hasta el final. Prohibido abonar en las vedas estacionales de ZVN, salvo riego localizado o agricultura de precisión.",
    },
    "naranjo": {"goteoLimits": {"n": 240, "p": 80, "k": 140, "mg": 180}, "fondoNote": "Suministro continuo controlado vía fertirrigación o aporte basal primaveral.", "coberteraNote": "Variedades tempranas: fertilizar de febrero a agosto; tardías: de marzo a septiembre. Fraccionamiento máximo, mínimo semanal en fertirrigación. Prohibido aplicar N durante el cuajado del fruto. Descontar obligatoriamente el N nítrico aportado por el agua de riego."},
    "mandarino": {"goteoLimits": {"n": 240, "p": 80, "k": 140, "mg": 180}, "fondoNote": "Suministro continuo controlado vía fertirrigación o aporte basal primaveral.", "coberteraNote": "Variedades tempranas: fertilizar de febrero a agosto; tardías: de marzo a septiembre. Fraccionamiento máximo, mínimo semanal en fertirrigación. Prohibido aplicar N durante el cuajado del fruto. Descontar obligatoriamente el N nítrico aportado por el agua de riego."},
    "limonero": {"goteoLimits": {"n": 240, "p": 80, "k": 140, "mg": 180}, "fondoNote": "Suministro continuo controlado vía fertirrigación o aporte basal primaveral.", "coberteraNote": "Limón Fino: fertilizar de febrero a diciembre. Limón Verna: de febrero a noviembre. Fraccionamiento máximo, mínimo semanal en fertirrigación. Prohibido aplicar N durante el cuajado del fruto. Descontar obligatoriamente el N nítrico aportado por el agua de riego."},
}
