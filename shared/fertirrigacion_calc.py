"""Lógica de cálculo del Programa de Fertirrigación.

Puerto directo (misma aritmética, mismos umbrales) de calculateAll() y
funciones auxiliares en programa_fertirrigacion.html. Cualquier cambio de
fórmula debe hacerse en ambos sitios, o mejor, retirar el HTML y dejar esto
como única fuente de verdad.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

try:
    from .fertirrigacion_data import FASES_INFO, GRANULADOS_DB, SOLUBLES_DB, FOLIARES_DB
except ImportError:  # ejecutado como script suelto (p.ej. desde los tests)
    from fertirrigacion_data import FASES_INFO, GRANULADOS_DB, SOLUBLES_DB, FOLIARES_DB

BANDAS_INFILTRACION_FAO = [
    {"ras_max": 3, "ninguna": 0.7, "severa": 0.2},
    {"ras_max": 6, "ninguna": 1.2, "severa": 0.3},
    {"ras_max": 12, "ninguna": 1.9, "severa": 0.5},
    {"ras_max": 20, "ninguna": 2.9, "severa": 1.3},
    {"ras_max": 40, "ninguna": 5.0, "severa": 2.9},
]

ACIDOS_PRESETS = {
    "Nítrico (60%)": {"density": 1.37, "purity": 60.0, "eq_wt": 63.0},
    "Fosfórico (75%)": {"density": 1.58, "purity": 75.0, "eq_wt": 98.0},
    "Sulfúrico (98%)": {"density": 1.84, "purity": 98.0, "eq_wt": 49.0},
}


def _banda_infiltracion(ras: float) -> dict:
    for banda in BANDAS_INFILTRACION_FAO:
        if ras <= banda["ras_max"]:
            return banda
    return BANDAS_INFILTRACION_FAO[-1]


@dataclass
class ResultadoAgua:
    meq_ca: float; meq_mg: float; meq_k: float; meq_na: float; meq_nh4: float
    meq_no3: float; meq_h2po4: float; meq_so4: float; meq_cl: float; meq_hco3: float
    sum_cat: float; sum_ani: float; water_ratio_pct: float
    ras: float  # R.A.S. sódico CON potasio integrado (distinto del RAS clásico de analisis_agua_riego)
    std_gl: float; po_atm: float; dureza_gf: float
    infiltracion_txt: str; infiltracion_nivel: str
    obturacion_txt: str; obturacion_nivel: str
    cl_txt: str; cl_nivel: str
    na_txt: str; na_nivel: str
    b_txt: str; b_nivel: str
    vol_anual_m3_ha: float
    ahorro_n_kg_ha: float; ahorro_cao_kg_ha: float; ahorro_mgo_kg_ha: float
    ahorro_k2o_kg_ha: float; ahorro_so3_kg_ha: float
    cloro_min_l: float; cloro_max_l: float; cloro_fe_mg_l: float


def analizar_agua(
    *, ca_mg_l: float, mg_mg_l: float, na_mg_l: float, k_mg_l: float, nh4_mg_l: float,
    no3_mg_l: float, h2po4_mg_l: float, so4_mg_l: float, cl_mg_l: float, hco3_mg_l: float,
    water_ec_ds_m: float, ph: float, b_mg_l: float, fe_mg_l: float, vol_anual_m3_ha: float,
) -> ResultadoAgua:
    meq_ca = ca_mg_l / 20.04
    meq_mg = mg_mg_l / 12.16
    meq_k = k_mg_l / 39.1
    meq_na = na_mg_l / 23.0
    meq_nh4 = nh4_mg_l / 18.04
    meq_no3 = no3_mg_l / 62.0
    meq_h2po4 = h2po4_mg_l / 97.0
    meq_so4 = so4_mg_l / 48.03
    meq_cl = cl_mg_l / 35.45
    meq_hco3 = hco3_mg_l / 61.02

    sum_cat = meq_ca + meq_mg + meq_k + meq_na + meq_nh4
    sum_ani = meq_no3 + meq_h2po4 + meq_so4 + meq_cl + meq_hco3
    water_ratio_pct = abs(sum_cat - sum_ani) / ((sum_cat + sum_ani) / 2) * 100 if (sum_cat + sum_ani) > 0 else 0.0

    ras = (meq_na + meq_k) / math.sqrt((meq_ca + meq_mg) / 2) if (meq_ca + meq_mg) > 0 else 0.0

    std_gl = water_ec_ds_m * 0.64
    po_atm = water_ec_ds_m * 0.36
    dureza_gf = (ca_mg_l * 2.5 + mg_mg_l * 4.12) / 10

    banda = _banda_infiltracion(ras)
    if water_ec_ds_m < banda["severa"]:
        infiltracion_txt, infiltracion_nivel = "Restricción Severa", "severo"
    elif water_ec_ds_m < banda["ninguna"]:
        infiltracion_txt, infiltracion_nivel = "Restricción Ligera-Moderada", "moderado"
    else:
        infiltracion_txt, infiltracion_nivel = "Sin restricción", "ok"

    if ph > 7.5 and meq_hco3 > 2.0 and meq_ca > 3.0:
        obturacion_txt, obturacion_nivel = "Riesgo Importante", "severo"
    elif ph > 7.5 and meq_hco3 > 2.0:
        obturacion_txt, obturacion_nivel = "Riesgo Moderado", "moderado"
    else:
        obturacion_txt, obturacion_nivel = "Riesgo Bajo", "ok"

    if meq_cl < 4:
        cl_txt, cl_nivel = "Excelente", "ok"
    elif meq_cl <= 10:
        cl_txt, cl_nivel = "Moderado", "moderado"
    else:
        cl_txt, cl_nivel = "Peligroso", "severo"

    if meq_na < 3:
        na_txt, na_nivel = "Sin riesgo", "ok"
    elif meq_na <= 9:
        na_txt, na_nivel = "Moderado", "moderado"
    else:
        na_txt, na_nivel = "Grave", "severo"

    if b_mg_l < 0.7:
        b_txt, b_nivel = "Sin riesgo", "ok"
    elif b_mg_l <= 3.0:
        b_txt, b_nivel = "Precaución", "moderado"
    else:
        b_txt, b_nivel = "Tóxico", "severo"

    ahorro_n = (no3_mg_l * (14.0 / 62.0) * vol_anual_m3_ha) / 1000.0
    ahorro_cao = (ca_mg_l * vol_anual_m3_ha / 1000.0) * 1.399
    ahorro_mgo = (mg_mg_l * vol_anual_m3_ha / 1000.0) * 1.658
    ahorro_k2o = (k_mg_l * vol_anual_m3_ha / 1000.0) * 1.205
    ahorro_so3 = (so4_mg_l * (32.06 / 96.06) * vol_anual_m3_ha / 1000.0) * 2.497

    kg_cl_min = (15.0 * vol_anual_m3_ha) / 1000.0
    kg_cl_max = (20.0 * vol_anual_m3_ha) / 1000.0
    cloro_min_l = kg_cl_min / 0.10
    cloro_max_l = kg_cl_max / 0.10
    cloro_fe_mg_l = 0.65 * fe_mg_l

    return ResultadoAgua(
        meq_ca=meq_ca, meq_mg=meq_mg, meq_k=meq_k, meq_na=meq_na, meq_nh4=meq_nh4,
        meq_no3=meq_no3, meq_h2po4=meq_h2po4, meq_so4=meq_so4, meq_cl=meq_cl, meq_hco3=meq_hco3,
        sum_cat=sum_cat, sum_ani=sum_ani, water_ratio_pct=water_ratio_pct, ras=ras,
        std_gl=std_gl, po_atm=po_atm, dureza_gf=dureza_gf,
        infiltracion_txt=infiltracion_txt, infiltracion_nivel=infiltracion_nivel,
        obturacion_txt=obturacion_txt, obturacion_nivel=obturacion_nivel,
        cl_txt=cl_txt, cl_nivel=cl_nivel, na_txt=na_txt, na_nivel=na_nivel, b_txt=b_txt, b_nivel=b_nivel,
        vol_anual_m3_ha=vol_anual_m3_ha,
        ahorro_n_kg_ha=ahorro_n, ahorro_cao_kg_ha=ahorro_cao, ahorro_mgo_kg_ha=ahorro_mgo,
        ahorro_k2o_kg_ha=ahorro_k2o, ahorro_so3_kg_ha=ahorro_so3,
        cloro_min_l=cloro_min_l, cloro_max_l=cloro_max_l, cloro_fe_mg_l=cloro_fe_mg_l,
    )


@dataclass
class ResultadoAcido:
    neut_hco3_meq_l: float
    dose_l: float
    dose_g: float


def calcular_acido(*, meq_hco3: float, target_hco3: float, purity: float, density: float, eq_wt: float) -> ResultadoAcido:
    neut_hco3 = max(0.0, meq_hco3 - target_hco3)
    dose_l = 0.0
    dose_g = 0.0
    if purity > 0:
        dose_l = (neut_hco3 * eq_wt) / (purity * density * 10)
        dose_g = dose_l * density * 1000
    return ResultadoAcido(neut_hco3_meq_l=neut_hco3, dose_l=dose_l, dose_g=dose_g)


def creditos_acido_mes(*, water_m3: float, neut_hco3: float, acid_type: str, custom: dict | None = None) -> dict:
    """a_n/a_p/a_s aportados por el ácido regulador en un mes con `water_m3` de riego."""
    a_n = a_p = a_s = 0.0
    if water_m3 > 0:
        if acid_type == "Nítrico (60%)":
            a_n = (water_m3 * neut_hco3 * 14.0) / 1000
        elif acid_type == "Fosfórico (75%)":
            a_p = (water_m3 * neut_hco3 * 71.0) / 1000
        elif acid_type == "Sulfúrico (98%)":
            a_s = (water_m3 * neut_hco3 * 40.0) / 1000
        elif acid_type == "Personalizado" and custom:
            a_n = (water_m3 * neut_hco3 * custom.get("n", 0.0)) / 1000
            a_p = (water_m3 * neut_hco3 * custom.get("p", 0.0)) / 1000
            a_s = (water_m3 * neut_hco3 * custom.get("s", 0.0)) / 1000
    return {"n": a_n, "p": a_p, "s": a_s}


def creditos_agua_mes(*, water_m3: float, no3_mg_l: float, h2po4_mg_l: float, k_mg_l: float, mg_mg_l: float, ca_mg_l: float, so4_mg_l: float) -> dict:
    return {
        "n": water_m3 * no3_mg_l * 0.226 / 1000,
        "p": water_m3 * h2po4_mg_l * 0.732 / 1000,
        "k": water_m3 * k_mg_l * 1.205 / 1000,
        "mg": water_m3 * mg_mg_l * 1.658 / 1000,
        "ca": water_m3 * ca_mg_l * 1.399 / 1000,
        "s": water_m3 * so4_mg_l * 0.833 / 1000,
    }


@dataclass
class ItemAbono:
    name: str
    dosis: float
    n: float; p: float; k: float; mg: float; ca: float; s: float


@dataclass
class ResultadoFondo:
    items: list = field(default_factory=list)
    total_dosis: float = 0.0
    n: float = 0.0; p: float = 0.0; k: float = 0.0; mg: float = 0.0; ca: float = 0.0; s: float = 0.0


def calcular_fondo(fondo_items: list[dict]) -> ResultadoFondo:
    r = ResultadoFondo()
    for it in fondo_items:
        prod = GRANULADOS_DB.get(it["name"])
        if not prod:
            continue
        dosis = it["dosis"]
        n = dosis * prod["n"] / 100
        p = dosis * prod["p"] / 100
        k = dosis * prod["k"] / 100
        mg = dosis * prod["mg"] / 100
        ca = dosis * prod["ca"] / 100
        s = dosis * prod["s"] / 100
        r.items.append(ItemAbono(it["name"], dosis, n, p, k, mg, ca, s))
        r.total_dosis += dosis
        r.n += n; r.p += p; r.k += k; r.mg += mg; r.ca += ca; r.s += s
    return r


@dataclass
class ItemFoliar:
    name: str
    dosis: float
    n: float; p: float; k: float; mg: float; ca: float; s: float
    fe: float; mn: float; zn: float; cu: float; b: float; mo: float


@dataclass
class ResultadoFoliar:
    items: list = field(default_factory=list)
    total_dosis: float = 0.0
    n: float = 0.0; p: float = 0.0; k: float = 0.0; mg: float = 0.0; ca: float = 0.0; s: float = 0.0
    fe: float = 0.0; mn: float = 0.0; zn: float = 0.0; cu: float = 0.0; b: float = 0.0; mo: float = 0.0


def calcular_foliar(foliar_items: list[dict]) -> ResultadoFoliar:
    r = ResultadoFoliar()
    for it in foliar_items:
        prod = FOLIARES_DB.get(it["name"])
        if not prod:
            continue
        dosis = it["dosis"]
        n = dosis * prod["n"] / 100
        p = dosis * prod["p"] / 100
        k = dosis * prod["k"] / 100
        mg = dosis * prod["mg"] / 100
        ca = dosis * prod["ca"] / 100
        s = dosis * prod["s"] / 100
        fe = dosis * prod["fe"] * 10
        mn = dosis * prod["mn"] * 10
        zn = dosis * prod["zn"] * 10
        cu = dosis * prod["cu"] * 10
        b = dosis * prod["b"] * 10
        mo = dosis * prod["mo"] * 10
        r.items.append(ItemFoliar(it["name"], dosis, n, p, k, mg, ca, s, fe, mn, zn, cu, b, mo))
        r.total_dosis += dosis
        r.n += n; r.p += p; r.k += k; r.mg += mg; r.ca += ca; r.s += s
        r.fe += fe; r.mn += mn; r.zn += zn; r.cu += cu; r.b += b; r.mo += mo
    return r


@dataclass
class CreditosAnuales:
    water: dict
    acid: dict
    solub: dict


def calcular_creditos_anuales(*, monthly_data: dict, water_composition: dict, acid_type: str, acid_custom: dict, neut_hco3: float) -> CreditosAnuales:
    water_sum = {"n": 0.0, "p": 0.0, "k": 0.0, "mg": 0.0, "ca": 0.0, "s": 0.0}
    acid_sum = {"n": 0.0, "p": 0.0, "s": 0.0}
    solub_sum = {"n": 0.0, "p": 0.0, "k": 0.0, "mg": 0.0, "ca": 0.0, "s": 0.0}

    for m in range(1, 13):
        month = monthly_data[m]
        w = creditos_agua_mes(water_m3=month["water"], **water_composition)
        for k in water_sum:
            water_sum[k] += w[k]

        a = creditos_acido_mes(water_m3=month["water"], neut_hco3=neut_hco3, acid_type=acid_type, custom=acid_custom)
        for k in acid_sum:
            acid_sum[k] += a[k]

        for item in month["solubles"]:
            prod = SOLUBLES_DB.get(item["name"])
            if not prod:
                continue
            dosis = item["dosis"]
            solub_sum["n"] += dosis * prod["n"] / 100
            solub_sum["p"] += dosis * prod["p"] / 100
            solub_sum["k"] += dosis * prod["k"] / 100
            solub_sum["mg"] += dosis * prod["mg"] / 100
            solub_sum["ca"] += dosis * prod["ca"] / 100
            solub_sum["s"] += dosis * prod["s"] / 100

    return CreditosAnuales(water=water_sum, acid=acid_sum, solub=solub_sum)


@dataclass
class BalanceAnual:
    base: dict
    target: dict
    diff: dict
    cobertura_fondo_pct: dict


def calcular_balance_anual(*, yield_val: float, coeffs: dict, fondo: ResultadoFondo, creditos: CreditosAnuales, extra: dict) -> BalanceAnual:
    base = {k: yield_val * coeffs[k] for k in ("n", "p", "k", "mg", "ca", "s")}

    target = {
        "n": base["n"] - fondo.n - creditos.water["n"] - creditos.acid["n"] + extra.get("n", 0.0),
        "p": base["p"] - fondo.p - creditos.water["p"] - creditos.acid["p"] + extra.get("p", 0.0),
        "k": base["k"] - fondo.k - creditos.water["k"] + extra.get("k", 0.0),
        "mg": base["mg"] - fondo.mg - creditos.water["mg"] + extra.get("mg", 0.0),
        "ca": base["ca"] - fondo.ca - creditos.water["ca"] + extra.get("ca", 0.0),
        "s": base["s"] - fondo.s - creditos.water["s"] - creditos.acid["s"] + extra.get("s", 0.0),
    }
    diff = {k: creditos.solub.get(k, 0.0) - target[k] for k in target}
    cobertura = {k: (fondo.__dict__[k] / base[k] * 100 if base[k] > 0 else 0.0) for k in ("n", "p", "k", "mg", "ca", "s")}
    return BalanceAnual(base=base, target=target, diff=diff, cobertura_fondo_pct=cobertura)


@dataclass
class ResultadoFase:
    sol_sum: dict
    water_credit: dict
    acid_credit: dict
    suma_total: dict
    pct_objetivo: dict
    hay_conflicto_tanque: bool
    ec_gota: float
    conc_gota_gl: float
    conc_cuba_pct: float
    conc_cuba_gl: float
    cuba_saturada: bool
    emisores_ha: float
    bomba_l_h: float
    supera_umbral_salino: bool


def calcular_fase_mensual(
    *, month: dict, water_composition: dict, water_ec_ds_m: float, acid_type: str, acid_custom: dict,
    neut_hco3: float, target: dict, umbral_salino: float,
) -> ResultadoFase:
    sol_sum = {"n": 0.0, "p": 0.0, "k": 0.0, "mg": 0.0, "ca": 0.0, "s": 0.0}
    hay_tanque_a = hay_tanque_b = False
    for item in month["solubles"]:
        prod = SOLUBLES_DB.get(item["name"])
        if not prod:
            continue
        dosis = item["dosis"]
        sol_sum["n"] += dosis * prod["n"] / 100
        sol_sum["p"] += dosis * prod["p"] / 100
        sol_sum["k"] += dosis * prod["k"] / 100
        sol_sum["mg"] += dosis * prod["mg"] / 100
        sol_sum["ca"] += dosis * prod["ca"] / 100
        sol_sum["s"] += dosis * prod["s"] / 100
        if dosis > 0:
            if prod["tanque"] == "A":
                hay_tanque_a = True
            if prod["tanque"] == "B":
                hay_tanque_b = True

    water_credit = creditos_agua_mes(water_m3=month["water"], **water_composition)
    acid_credit = creditos_acido_mes(water_m3=month["water"], neut_hco3=neut_hco3, acid_type=acid_type, custom=acid_custom)

    suma_total = {
        "n": sol_sum["n"] + water_credit["n"] + acid_credit["n"],
        "p": sol_sum["p"] + water_credit["p"] + acid_credit["p"],
        "k": sol_sum["k"] + water_credit["k"],
        "mg": sol_sum["mg"] + water_credit["mg"],
        "ca": sol_sum["ca"] + water_credit["ca"],
        "s": sol_sum["s"] + water_credit["s"] + acid_credit["s"],
    }
    pct_objetivo = {k: (suma_total[k] / target[k] * 100 if target[k] > 0 else 0.0) for k in suma_total}

    ec_gota = water_ec_ds_m
    for item in month["solubles"]:
        prod = SOLUBLES_DB.get(item["name"])
        if prod and month["water"] > 0:
            conc = item["dosis"] / month["water"]
            ec_gota += conc * prod["ec_coeff"]
    if month["water"] > 0:
        ec_gota += neut_hco3 * 0.05

    total_solubles_mes_kg = sum(s["dosis"] for s in month["solubles"])
    conc_gota_gl = total_solubles_mes_kg / month["water"] if month["water"] > 0 else 0.0

    dosis_por_riego_kg = total_solubles_mes_kg / month["num_riegos"] if month["num_riegos"] > 0 else 0.0
    conc_cuba_gl = 0.0
    conc_cuba_pct = 0.0
    if month["cuba_vol"] > 0:
        conc_cuba_gl = (dosis_por_riego_kg / month["cuba_vol"]) * 1000
        conc_cuba_pct = (dosis_por_riego_kg / month["cuba_vol"]) * 100

    caudal_por_riego_m3 = month["water"] / month["num_riegos"] if month["num_riegos"] > 0 else 0.0
    tiempo_riego_horas = month.get("tiempo_riego") or 0.0
    emisores_ha = 0.0
    if month["flow_rate"] > 0 and tiempo_riego_horas > 0:
        emisores_ha = (caudal_por_riego_m3 * 1000) / (month["flow_rate"] * tiempo_riego_horas)

    tiempo_inyectora_h = tiempo_riego_horas * 0.8
    bomba_l_h = month["cuba_vol"] / tiempo_inyectora_h if tiempo_inyectora_h > 0 else 0.0

    return ResultadoFase(
        sol_sum=sol_sum, water_credit=water_credit, acid_credit=acid_credit, suma_total=suma_total,
        pct_objetivo=pct_objetivo, hay_conflicto_tanque=(hay_tanque_a and hay_tanque_b),
        ec_gota=ec_gota, conc_gota_gl=conc_gota_gl, conc_cuba_pct=conc_cuba_pct, conc_cuba_gl=conc_cuba_gl,
        cuba_saturada=(conc_cuba_gl > 150), emisores_ha=emisores_ha, bomba_l_h=bomba_l_h,
        supera_umbral_salino=(ec_gota > umbral_salino),
    )


def meses_con_conflicto_tanque(*, monthly_data: dict) -> list[str]:
    meses = []
    for m in range(1, 13):
        month = monthly_data[m]
        hay_a = hay_b = False
        for item in month["solubles"]:
            prod = SOLUBLES_DB.get(item["name"])
            if prod and item["dosis"] > 0:
                if prod["tanque"] == "A":
                    hay_a = True
                if prod["tanque"] == "B":
                    hay_b = True
        if hay_a and hay_b:
            meses.append(month["name"])
    return meses


@dataclass
class ResultadoGoteroSonneveld:
    meq: dict  # ca, mg, k, na, nh4, no3, p, s, cl, hco3 en el gotero
    total_cat: float
    total_ani: float
    electroneutralidad_pct: float
    r_k_ca_mg: float
    r_ca_mg: float
    r_k_mg: float
    r_n_k: float
    r_n_p: float
    comentarios: dict  # una clave por ratio -> (texto, nivel)
    triad_pct: dict  # k, ca, mg


def calcular_gotero_sonneveld(
    *, mes: dict, agua: ResultadoAgua, acid_type: str, acid_custom: dict, neut_hco3: float,
) -> ResultadoGoteroSonneveld:
    got_nh4 = agua.meq_nh4
    got_no3 = agua.meq_no3
    got_p = agua.meq_h2po4
    got_s = agua.meq_so4
    got_k = agua.meq_k
    got_ca = agua.meq_ca
    got_mg = agua.meq_mg
    got_hco3 = max(0.0, agua.meq_hco3 - neut_hco3)

    if acid_type == "Nítrico (60%)":
        got_no3 += neut_hco3
    elif acid_type == "Fosfórico (75%)":
        got_p += neut_hco3
    elif acid_type == "Sulfúrico (98%)":
        got_s += neut_hco3
    elif acid_type == "Personalizado" and acid_custom:
        if acid_custom.get("n", 0.0) > 0:
            got_no3 += neut_hco3
        if acid_custom.get("p", 0.0) > 0:
            got_p += neut_hco3
        if acid_custom.get("s", 0.0) > 0:
            got_s += neut_hco3

    for item in mes["solubles"]:
        prod = SOLUBLES_DB.get(item["name"])
        if prod and mes["water"] > 0:
            conc_g_l = item["dosis"] / mes["water"]
            got_nh4 += (conc_g_l * prod["nh4"] * 10) / 14.0
            got_no3 += (conc_g_l * prod["no3"] * 10) / 14.0
            got_p += (conc_g_l * prod["p"] * 10) / 71.0
            got_s += (conc_g_l * prod["s"] * 10) / 40.0
            got_k += (conc_g_l * prod["k"] * 10) / 47.1
            got_ca += (conc_g_l * prod["ca"] * 10) / 28.0
            got_mg += (conc_g_l * prod["mg"] * 10) / 20.15

    total_cat = got_ca + got_mg + got_k + agua.meq_na + got_nh4
    total_ani = got_no3 + got_p + got_s + agua.meq_cl + got_hco3
    electroneutralidad_pct = abs(total_cat - total_ani) / ((total_cat + total_ani) / 2) * 100 if (total_cat + total_ani) > 0 else 0.0

    r_k_ca_mg = got_k / (got_ca + got_mg) if (got_ca + got_mg) > 0 else 0.0
    r_ca_mg = got_ca / got_mg if got_mg > 0 else 0.0
    r_k_mg = got_k / got_mg if got_mg > 0 else 0.0
    r_n_k = (got_no3 + got_nh4) / got_k if got_k > 0 else 0.0
    r_n_p = (got_no3 + got_nh4) / got_p if got_p > 0 else 0.0

    def _c(val, lo, hi, msg_low, msg_ok, msg_high):
        if val < lo:
            return (msg_low, "severo")
        if val <= hi:
            return (msg_ok, "ok")
        return (msg_high, "severo")

    comentarios = {
        "k_ca_mg": _c(r_k_ca_mg, 0.30, 0.50,
                      "Relación baja. Riesgo de deficiencia de Potasio por exceso de Calcio y Magnesio.",
                      "Óptimo (0.30-0.50). Previene antagonismos de absorción con potasio.",
                      "Relación alta. El exceso de Potasio puede bloquear la absorción de Calcio y Magnesio."),
        "ca_mg": _c(r_ca_mg, 2.50, 5.00,
                    "Relación baja. Exceso de Magnesio que puede bloquear la absorción de Calcio.",
                    "Óptimo (2.50-5.00). Controla el equilibrio de asimilación de calcio.",
                    "Relación alta. El exceso de Calcio puede inducir deficiencias de Magnesio."),
        "k_mg": _c(r_k_mg, 1.50, 3.00,
                   "Relación baja. Riesgo de bajo nivel de Potasio activo en la planta.",
                   "Óptimo (1.50-3.00). Evita clorosis foliares de magnesio por exceso de potasio.",
                   "Relación alta. El exceso de Potasio provoca clorosis foliar por deficiencia de Magnesio."),
        "n_k": _c(r_n_k, 1.00, 1.60,
                  "Relación baja. Exceso de Potasio o falta de Nitrógeno (reduce el vigor).",
                  "Óptimo (1.00-1.60). Equilibrio vegetativo-productivo.",
                  "Relación alta. Exceso de Nitrógeno (reblandecimiento foliar) o deficiencia de Potasio."),
        "n_p": _c(r_n_p, 8.00, 12.00,
                  "Relación baja. Exceso de Fósforo o falta de Nitrógeno.",
                  "Óptimo (8.00-12.00). Desarrollo de raíces y vigor.",
                  "Relación alta. Exceso de Nitrógeno o deficiencia de Fósforo (afecta enraizamiento)."),
    }

    cat_sum_molar = got_k + got_ca + got_mg
    if cat_sum_molar > 0:
        triad_pct = {"k": got_k / cat_sum_molar * 100, "ca": got_ca / cat_sum_molar * 100, "mg": got_mg / cat_sum_molar * 100}
    else:
        triad_pct = {"k": 33.3, "ca": 33.3, "mg": 33.3}

    return ResultadoGoteroSonneveld(
        meq={"ca": got_ca, "mg": got_mg, "k": got_k, "na": agua.meq_na, "nh4": got_nh4,
             "no3": got_no3, "p": got_p, "s": got_s, "cl": agua.meq_cl, "hco3": got_hco3},
        total_cat=total_cat, total_ani=total_ani, electroneutralidad_pct=electroneutralidad_pct,
        r_k_ca_mg=r_k_ca_mg, r_ca_mg=r_ca_mg, r_k_mg=r_k_mg, r_n_k=r_n_k, r_n_p=r_n_p,
        comentarios=comentarios, triad_pct=triad_pct,
    )


def sugerencias_fase(fase_key: str, ratios: dict) -> list[str]:
    """Orientación por fase fenológica según los ratios Sonneveld ya calculados (guía conceptual)."""
    info = FASES_INFO.get(fase_key, FASES_INFO["sin_fase"])
    r_k_ca_mg, r_ca_mg, r_k_mg, r_n_k, r_n_p = (
        ratios["r_k_ca_mg"], ratios["r_ca_mg"], ratios["r_k_mg"], ratios["r_n_k"], ratios["r_n_p"]
    )
    sugerencias = []
    if fase_key == "arranque":
        if r_n_p > 12.00:
            sugerencias.append(f"Esta fase prioriza P disponible para el arranque radicular, pero tu relación N/P ({r_n_p:.2f}) es alta: hay más N relativo (o menos P) de lo recomendado. Considera reforzar el aporte de P.")
    elif fase_key == "vegetativo":
        if r_n_k < 1.00:
            sugerencias.append(f"En crecimiento vegetativo se espera N suficiente para biomasa y área foliar, pero tu relación N/K ({r_n_k:.2f}) es baja: el K relativo es alto. Revisa si el N está siendo limitante.")
    elif fase_key == "floracion":
        if r_n_k > 1.60:
            sugerencias.append(f"En floración se recomienda reducir la dependencia de N y reforzar K/Ca, pero tu relación N/K ({r_n_k:.2f}) es alta. Considera bajar el aporte de N y/o subir K.")
        if r_k_ca_mg < 0.30:
            sugerencias.append(f"Se espera reforzar K en esta fase; tu relación K/(Ca+Mg) ({r_k_ca_mg:.2f}) es baja. Valora aumentar el aporte de K.")
    elif fase_key in ("cuajado", "engorde"):
        if r_k_ca_mg < 0.30:
            sugerencias.append(f"En {info['label'].lower()} se espera K alto relativo para calibre y calidad; tu relación K/(Ca+Mg) ({r_k_ca_mg:.2f}) es baja. Considera reforzar K.")
        if r_n_k > 1.60:
            sugerencias.append(f"Se recomienda N controlado en esta fase; tu relación N/K ({r_n_k:.2f}) es alta. Valora reducir el aporte de N.")
    elif fase_key == "maduracion":
        if r_n_k > 1.60:
            sugerencias.append(f"En maduración se recomienda reducir N y mantener K; tu relación N/K ({r_n_k:.2f}) sigue siendo alta. Considera bajar la dosis de fertilizantes nitrogenados.")
        if r_k_ca_mg < 0.30:
            sugerencias.append(f"Se recomienda mantener K en esta fase; tu relación K/(Ca+Mg) ({r_k_ca_mg:.2f}) es baja para el objetivo de calidad y maduración.")
    elif fase_key == "precosecha":
        sugerencias.append("En pre-cosecha el objetivo es no forzar crecimiento vegetativo: evita subir N y vigila que la CE no se dispare.")
    return sugerencias


@dataclass
class AlertaDictamen:
    nivel: str  # ok | warn | danger
    mensaje: str


def generar_dictamen_experto(
    *, ec_gota: float, ras_val: float, meq_cl: float, hco3_mg_l: float,
    meses_conflicto_tanque: list[str], crop: str, umbral_salino: float,
) -> list[AlertaDictamen]:
    alertas = []

    if ec_gota > umbral_salino:
        loss_pct = (ec_gota - umbral_salino) * 10.0
        alertas.append(AlertaDictamen("danger",
            f"⚠️ RIESGO DE SALINIDAD. La conductividad de la gota ({ec_gota:.2f} dS/m) supera el umbral de "
            f"tolerancia de {crop} ({umbral_salino:.2f} dS/m). Pérdida de rendimiento orientativa (pendiente "
            f"genérica, no calibrada por cultivo): ~{loss_pct:.0f}%."))
    else:
        alertas.append(AlertaDictamen("ok",
            f"Conductividad óptima para {crop}. La conductividad de gota ({ec_gota:.2f} dS/m) está por debajo "
            f"del límite de tolerancia del cultivo ({umbral_salino:.2f} dS/m)."))

    if ras_val > 9:
        alertas.append(AlertaDictamen("danger",
            f"❌ PELIGRO DE DEGRADACIÓN ESTRUCTURAL (RAS: {ras_val:.1f}). El agua es fuertemente sódica. Existe "
            f"riesgo inminente de asfixia radicular y compactación severa del suelo."))
    elif ras_val > 6:
        alertas.append(AlertaDictamen("warn",
            f"⚠️ ALERTA DE SODICIDAD (RAS: {ras_val:.1f}). Riesgo moderado de dispersión de arcillas y pérdida "
            f"de infiltración física en el suelo. Se recomienda vigilar el drenaje."))
    else:
        alertas.append(AlertaDictamen("ok",
            "Sodio equilibrado. La relación de adsorción de sodio (RAS) del agua de riego es óptima y no "
            "representa riesgos estructurales."))

    if meq_cl > 4:
        alertas.append(AlertaDictamen("warn",
            "⚠️ TOXICIDAD POR CLORUROS MODERADA. La concentración de cloruros supera 4.0 meq/L. Riesgo de "
            "quemaduras marginales en frutales u hortalizas sensibles."))
    else:
        alertas.append(AlertaDictamen("ok", "Concentración de cloruros óptima. No se prevén toxicidades marginales en hojas."))

    if hco3_mg_l > 150:
        alertas.append(AlertaDictamen("warn",
            "⚠️ RIESGO DE OBTURACIONES CALIZAS. Se detecta una alta presencia de bicarbonatos en el agua base. "
            "Asegure el mantenimiento regular de inyección de ácido."))
    else:
        alertas.append(AlertaDictamen("ok",
            "Riesgo de obturaciones bajo. El tratamiento regulador del ácido neutraliza el exceso de carbonatos."))

    if meses_conflicto_tanque:
        alertas.append(AlertaDictamen("danger",
            f"💥 RIESGO DE PRECIPITADO EN: {', '.join(meses_conflicto_tanque)}. Estas fases mezclan productos "
            f"Tanque A (cálcicos) con productos Tanque B (sulfatos/fosfatos), lo que puede formar yeso o "
            f"fosfato cálcico insoluble y obturar los goteros. Inyecta cada grupo desde una cuba separada."))
    else:
        alertas.append(AlertaDictamen("ok",
            "Sin conflictos de tanque detectados en la planificación anual. Los productos cálcicos (Tanque A) "
            "y los sulfatados/fosfatados (Tanque B) no coinciden en ninguna fase."))

    return alertas
