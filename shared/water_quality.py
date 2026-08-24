"""Diagnóstico de calidad de agua de riego.

Puerto directo (misma aritmética, mismos umbrales) de la lógica JS ya revisada
y corregida en ``analisis_agua_riego.html``. Cualquier cambio de fórmula debe
hacerse en ambos sitios o, mejor, retirar el HTML y dejar esto como única
fuente de verdad.

Fuente de los umbrales de infiltración: FAO Irrigation and Drainage Paper 29,
Ayers & Westcot (1985), Tabla 1 "Influence of SAR and ECw on infiltration".
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math

CONCENTRACION_HIPOCLORITO = 0.10  # 10% de cloro activo p/v en el hipoclorito comercial

BANDAS_INFILTRACION_FAO = [
    {"ras_max": 3, "ninguna": 0.7, "severa": 0.2},
    {"ras_max": 6, "ninguna": 1.2, "severa": 0.3},
    {"ras_max": 12, "ninguna": 1.9, "severa": 0.5},
    {"ras_max": 20, "ninguna": 2.9, "severa": 1.3},
    {"ras_max": 40, "ninguna": 5.0, "severa": 2.9},
]


@dataclass
class ResultadoAguaRiego:
    # Físicos
    ce_ds: float
    std_g_l: float
    po_atm: float
    dureza_f: float
    dureza_txt: str

    # meq/L
    ca_meq: float
    mg_meq: float
    na_meq: float
    k_meq: float
    hco3_meq: float
    cl_meq: float
    so4_meq: float
    no3_meq: float

    # Infiltración / sodicidad
    ras: float
    infiltracion_txt: str
    infiltracion_nivel: str  # "ok" | "moderado" | "severo"

    # Obturación calcárea
    obturacion_txt: str
    obturacion_nivel: str
    obturacion_detalle: str

    # Toxicidad de iones específicos
    cloruro_txt: str
    cloruro_nivel: str
    sodio_txt: str
    sodio_nivel: str
    boro_txt: str
    boro_nivel: str

    # Nutrientes gratuitos aportados por el agua (kg/ha en el volumen dado)
    n_kg_ha: float
    cao_kg_ha: float
    mgo_kg_ha: float
    k2o_kg_ha: float
    so3_kg_ha: float

    # Dosificación de ácidos para neutralizar bicarbonatos
    bic_neto_meq_l: float
    nitrico_ml_m3: float
    nitrico_total_l: float
    nitrico_n_extra_kg_ha: float
    fosforico_ml_m3: float
    fosforico_total_l: float
    sulfurico_ml_m3: float
    sulfurico_total_l: float
    aviso_fosforico: str

    # Cloración
    cloro_min_l: float
    cloro_max_l: float
    cloro_fe_mg_l: float

    # Balance de cargas (control de calidad de la analítica)
    sum_cationes_meq: float
    sum_aniones_meq: float
    error_cargas_pct: float
    electroneutralidad_txt: str

    # Datos para el gráfico de barras cationes/aniones
    grafico_cationes: dict = field(default_factory=dict)
    grafico_aniones: dict = field(default_factory=dict)


def _clasificar_dureza(dureza: float) -> str:
    if dureza < 7:
        return "Muy Dulce"
    if dureza <= 14:
        return "Dulce"
    if dureza <= 22:
        return "Medianamente Dulce"
    if dureza <= 32:
        return "Medianamente Dura"
    if dureza <= 54:
        return "Dura"
    return "Muy Dura"


def _banda_infiltracion(ras: float) -> dict:
    for banda in BANDAS_INFILTRACION_FAO:
        if ras <= banda["ras_max"]:
            return banda
    return BANDAS_INFILTRACION_FAO[-1]


def analizar_agua(
    *,
    vol_riego_m3_ha: float,
    ce_us_cm: float,
    ph: float,
    ca_mg_l: float,
    mg_mg_l: float,
    na_mg_l: float,
    k_mg_l: float,
    hco3_mg_l: float,
    cl_mg_l: float,
    so4_mg_l: float,
    no3_mg_l: float,
    b_mg_l: float,
    fe_mg_l: float,
) -> ResultadoAguaRiego:
    vol = vol_riego_m3_ha
    ce = ce_us_cm

    # 1. Físicos
    ce_ds = ce / 1000
    std = ce * 0.64 / 1000
    po = ce_ds * 0.36
    dureza = (ca_mg_l * 2.5 + mg_mg_l * 4.12) / 10
    dureza_txt = _clasificar_dureza(dureza)

    # 2. meq/L
    ca_meq = ca_mg_l / 20.04
    mg_meq = mg_mg_l / 12.16
    na_meq = na_mg_l / 23.00
    k_meq = k_mg_l / 39.10
    hco3_meq = hco3_mg_l / 61.02
    cl_meq = cl_mg_l / 35.46
    so4_meq = so4_mg_l / 48.03
    no3_meq = no3_mg_l / 62.00

    ras = na_meq / math.sqrt((ca_meq + mg_meq) / 2.0) if (ca_meq + mg_meq) > 0 else 0.0

    # 3. Infiltración (FAO-29, Ayers & Westcot 1985)
    banda = _banda_infiltracion(ras)
    if ce_ds < banda["severa"]:
        infiltracion_txt, infiltracion_nivel = "RESTRICCIÓN SEVERA", "severo"
    elif ce_ds < banda["ninguna"]:
        infiltracion_txt, infiltracion_nivel = "RESTRICCIÓN LIGERA-MODERADA", "moderado"
    else:
        infiltracion_txt, infiltracion_nivel = "Sin restricción", "ok"

    # Obturación calcárea (indicador simplificado, no Langelier/Ryznar: falta la temperatura)
    if ph > 7.5 and hco3_meq > 2.0 and ca_meq > 3.0:
        obturacion_txt, obturacion_nivel = "Riesgo Importante", "severo"
        obturacion_detalle = (
            "Riesgo importante de precipitación calcárea: pH alcalino, bicarbonatos "
            "altos y calcio disponible suficiente para formar CaCO3. Indicador "
            "simplificado (no sustituye un índice de Langelier/Ryznar con temperatura)."
        )
    elif ph > 7.5 and hco3_meq > 2.0:
        obturacion_txt, obturacion_nivel = "Riesgo Moderado", "moderado"
        obturacion_detalle = (
            "pH alcalino y bicarbonatos altos, pero el calcio disponible es moderado: "
            "riesgo de precipitación calcárea presente pero más limitado. Vigilar evolución."
        )
    else:
        obturacion_txt, obturacion_nivel = "OK (Riesgo Bajo)", "ok"
        obturacion_detalle = (
            "Sin combinación de pH alcalino y alcalinidad elevada: riesgo bajo de "
            "obturación por precipitación calcárea."
        )

    # Toxicidad de iones específicos
    if cl_meq < 4:
        cloruro_txt, cloruro_nivel = "Excelente (Sin riesgo)", "ok"
    elif cl_meq <= 10:
        cloruro_txt, cloruro_nivel = "Moderado (Suelo/Frutales)", "moderado"
    else:
        cloruro_txt, cloruro_nivel = "Peligroso (Grave)", "severo"

    if na_meq < 3:
        sodio_txt, sodio_nivel = "Sin riesgo", "ok"
    elif na_meq <= 9:
        sodio_txt, sodio_nivel = "Moderado", "moderado"
    else:
        sodio_txt, sodio_nivel = "Grave", "severo"

    if b_mg_l < 0.7:
        boro_txt, boro_nivel = "Sin riesgo", "ok"
    elif b_mg_l <= 3.0:
        boro_txt, boro_nivel = "Precaución", "moderado"
    else:
        boro_txt, boro_nivel = "Tóxico", "severo"

    # 4. Nutrientes gratuitos aportados por el agua (kg/ha en el volumen dado)
    n_kg_ha = (no3_mg_l * (14.0 / 62.0) * vol) / 1000.0
    ca_neto = (ca_mg_l * vol) / 1000.0
    cao_kg_ha = ca_neto * 1.399
    mg_neto = (mg_mg_l * vol) / 1000.0
    mgo_kg_ha = mg_neto * 1.658
    k_neto = (k_mg_l * vol) / 1000.0
    k2o_kg_ha = k_neto * 1.205
    s_neto = (so4_mg_l * (32.06 / 96.06) * vol) / 1000.0
    so3_kg_ha = s_neto * 2.497

    # 5. Dosificación de ácidos
    residual_seguro = 1.50
    bic_neto = max(0.0, hco3_meq - residual_seguro)

    nitrico_ml_m3 = bic_neto * 68.0
    nitrico_total_l = (nitrico_ml_m3 * vol) / 1000.0
    n_extra = bic_neto * 14.0 * vol / 1000.0

    fosforico_ml_m3 = bic_neto * 85.0
    fosforico_total_l = (fosforico_ml_m3 * vol) / 1000.0
    aviso_fosforico = (
        "El factor de 85 mL/m³·meq no se corresponde con un peso equivalente limpio "
        "mono/di/triprótico (a diferencia del nítrico y el sulfúrico, que sí encajan). "
        "El H3PO4 tiene su segunda constante de disociación (pKa2≈7.2) dentro del rango "
        "de pH de trabajo, por lo que la neutralización real sigue una curva de "
        "valoración y no un factor fijo. Se recomienda validar con una prueba de jarras "
        "antes de dosificar a ciegas."
    )

    sulfurico_ml_m3 = bic_neto * 28.0
    sulfurico_total_l = (sulfurico_ml_m3 * vol) / 1000.0

    # Cloración: dosis objetivo de cloro activo 15-20 ppm al final del riego.
    kg_cl_puro_min = (15.0 * vol) / 1000.0
    kg_cl_puro_max = (20.0 * vol) / 1000.0
    cloro_min_l = kg_cl_puro_min / CONCENTRACION_HIPOCLORITO
    cloro_max_l = kg_cl_puro_max / CONCENTRACION_HIPOCLORITO
    cloro_fe_mg_l = 0.65 * fe_mg_l

    # 6. Balance de cargas (control de calidad de la analítica)
    sum_cationes = ca_meq + mg_meq + na_meq + k_meq
    sum_aniones = hco3_meq + cl_meq + so4_meq + no3_meq
    error_cargas = (
        abs(sum_cationes - sum_aniones) / (sum_cationes + sum_aniones) * 100
        if (sum_cationes + sum_aniones) > 0
        else 0.0
    )
    if error_cargas <= 5.0:
        electroneutralidad_txt = (
            f"Balance de Cargas (Error): {error_cargas:.2f}%. El balance de cargas es "
            "excelente (<5%), lo que garantiza que el análisis de laboratorio es "
            "sumamente riguroso y confiable."
        )
    elif error_cargas <= 10.0:
        electroneutralidad_txt = (
            f"Balance de Cargas (Error): {error_cargas:.2f}%. El balance está en el "
            "rango tolerable (5-10%). El análisis es apto para uso agronómico."
        )
    else:
        electroneutralidad_txt = (
            f"Balance de Cargas (Error): {error_cargas:.2f}%. ¡PRECAUCIÓN! Desviación "
            "alta (>10%). Es posible que el laboratorio haya omitido algún elemento o "
            "exista un error de medición."
        )

    return ResultadoAguaRiego(
        ce_ds=ce_ds,
        std_g_l=std,
        po_atm=po,
        dureza_f=dureza,
        dureza_txt=dureza_txt,
        ca_meq=ca_meq,
        mg_meq=mg_meq,
        na_meq=na_meq,
        k_meq=k_meq,
        hco3_meq=hco3_meq,
        cl_meq=cl_meq,
        so4_meq=so4_meq,
        no3_meq=no3_meq,
        ras=ras,
        infiltracion_txt=infiltracion_txt,
        infiltracion_nivel=infiltracion_nivel,
        obturacion_txt=obturacion_txt,
        obturacion_nivel=obturacion_nivel,
        obturacion_detalle=obturacion_detalle,
        cloruro_txt=cloruro_txt,
        cloruro_nivel=cloruro_nivel,
        sodio_txt=sodio_txt,
        sodio_nivel=sodio_nivel,
        boro_txt=boro_txt,
        boro_nivel=boro_nivel,
        n_kg_ha=n_kg_ha,
        cao_kg_ha=cao_kg_ha,
        mgo_kg_ha=mgo_kg_ha,
        k2o_kg_ha=k2o_kg_ha,
        so3_kg_ha=so3_kg_ha,
        bic_neto_meq_l=bic_neto,
        nitrico_ml_m3=nitrico_ml_m3,
        nitrico_total_l=nitrico_total_l,
        nitrico_n_extra_kg_ha=n_extra,
        fosforico_ml_m3=fosforico_ml_m3,
        fosforico_total_l=fosforico_total_l,
        sulfurico_ml_m3=sulfurico_ml_m3,
        sulfurico_total_l=sulfurico_total_l,
        aviso_fosforico=aviso_fosforico,
        cloro_min_l=cloro_min_l,
        cloro_max_l=cloro_max_l,
        cloro_fe_mg_l=cloro_fe_mg_l,
        sum_cationes_meq=sum_cationes,
        sum_aniones_meq=sum_aniones,
        error_cargas_pct=error_cargas,
        electroneutralidad_txt=electroneutralidad_txt,
        grafico_cationes={"Ca²⁺": ca_meq, "Mg²⁺": mg_meq, "Na⁺": na_meq, "K⁺": k_meq},
        grafico_aniones={"HCO₃⁻": hco3_meq, "Cl⁻": cl_meq, "SO₄²⁻": so4_meq, "NO₃⁻": no3_meq},
    )


# Ejemplos precargados (mismos valores que los botones "Cargar ejemplo" del HTML)
EJEMPLOS = {
    "Marismas Sector B-XII": dict(
        meta_analitica="Analítica Marismas Sector B-XII",
        meta_finca="Sector B-XII",
        meta_empresa="Las Marismas de Lebrija, S.C.A.",
        ce_us_cm=1075, ph=7.78, ca_mg_l=65.9, mg_mg_l=30.9, na_mg_l=130.0, k_mg_l=6.84,
        hco3_mg_l=130.0, cl_mg_l=189.0, so4_mg_l=197.0, no3_mg_l=5.0, b_mg_l=0.10,
        fe_mg_l=0.025, mn_mg_l=0.005,
    ),
    "Patrón de Calidad Eurochem Agro": dict(
        meta_analitica="Patrón de Calidad Eurochem Agro",
        meta_finca="Parcela Demostración SGE",
        meta_empresa="Eurochem Agro Iberia S.L.",
        ce_us_cm=1148, ph=7.65, ca_mg_l=107.6, mg_mg_l=36.2, na_mg_l=47.0, k_mg_l=2.49,
        hco3_mg_l=151.2, cl_mg_l=56.0, so4_mg_l=167.2, no3_mg_l=107.3, b_mg_l=0.07,
        fe_mg_l=0.04, mn_mg_l=0.02,
    ),
}
