"""Lógica de cálculo de NutriLeaf Pro (diagnóstico foliar).

Puerto directo de procesarAnalisisFoliar(), procesarDrisOlivoCompleto(),
procesarDrisAlmendro() y procesarDrisCaqui() en nutrileaf_pro.html.

No incluye el histórico multi-año (localStorage, sparklines, export CSV) del
HTML original — queda fuera de este primer puerto.
"""
from __future__ import annotations

from dataclasses import dataclass, field

try:
    from .nutrileaf_data import (
        RATIOS_ESPECIFICOS_CULTIVO, RATIOS_GENERICOS, TEXTOS_RATIOS_GENERICOS,
        FERTILIZANTE_CATALOG, NORMAS_DRIS_OLIVO_3P, NORMAS_DRIS_OLIVO_10P,
        NORMAS_ALMENDRO_DRIS, NORMS_DRIS_CAQUI, NUTRIENTES_CAQUI, NOMBRES_NUTRIENTES,
    )
except ImportError:
    from nutrileaf_data import (
        RATIOS_ESPECIFICOS_CULTIVO, RATIOS_GENERICOS, TEXTOS_RATIOS_GENERICOS,
        FERTILIZANTE_CATALOG, NORMAS_DRIS_OLIVO_3P, NORMAS_DRIS_OLIVO_10P,
        NORMAS_ALMENDRO_DRIS, NORMS_DRIS_CAQUI, NUTRIENTES_CAQUI, NOMBRES_NUTRIENTES,
    )


@dataclass
class Clasificacion:
    estado: str
    badge: str
    factor: float


def clasificar_valor(val: float, ref: dict | None) -> Clasificacion | None:
    if not ref or ref.get("mb") is None:
        return None
    if val is None:
        return None
    if val < ref["mb"]:
        return Clasificacion("MUY BAJO", "muy-bajo", 2.0)
    if val < ref["o_min"]:
        return Clasificacion("BAJO", "bajo", 1.5)
    if val <= ref["o_max"]:
        return Clasificacion("ÓPTIMO", "optimo", 1.0)
    if ref.get("alto_max") is None or val <= ref["alto_max"]:
        return Clasificacion("ALTO", "alto", 0.5)
    return Clasificacion("MUY ALTO / EXCESO", "muy-alto", 0.0)


@dataclass
class FilaSuficiencia:
    elemento: str
    valor: float
    unidad: str
    rango_optimo: str
    estado: str
    badge: str
    dop_pct: float | None  # None si no calculable


@dataclass
class ResultadoSuficiencia:
    filas: list = field(default_factory=list)
    sin_bibliografia: list = field(default_factory=list)
    elemento_mas_limitante: str | None = None
    dop_mas_limitante: float | None = None
    cl_fila: FilaSuficiencia | None = None  # aguacate: umbral de toxicidad, no de suficiencia


def analizar_suficiencia(valores: dict, normas: dict, cultivo: str) -> ResultadoSuficiencia:
    r = ResultadoSuficiencia()
    list_dop = []

    for el, val in valores.items():
        if el == "Cl" and cultivo != "caqui":
            continue  # en Aguacate el Cl se trata aparte (toxicidad); en Caqui es un elemento DRIS más
        ref = normas.get(el)
        if not ref or ref.get("mb") is None or val is None:
            r.sin_bibliografia.append(el)
            continue
        opt = (ref["o_min"] + ref["o_max"]) / 2
        dop = ((val - opt) / opt) * 100 if opt != 0 else None
        if dop is not None:
            list_dop.append((el, dop))
        clasif = clasificar_valor(val, ref)
        r.filas.append(FilaSuficiencia(
            elemento=el, valor=val, unidad=ref["unit"],
            rango_optimo=f"{ref['o_min']:.2f} - {ref['o_max']:.2f}",
            estado=clasif.estado, badge=clasif.badge, dop_pct=dop,
        ))

    if cultivo == "aguacate" and normas.get("Cl") and valores.get("Cl") is not None:
        ref_cl = normas["Cl"]
        val_cl = valores["Cl"]
        estado_cl, badge_cl = "SEGURO", "optimo"
        if val_cl > ref_cl["alto_max"]:
            estado_cl, badge_cl = "TOXICIDAD EXTREMA", "muy-alto"
        elif val_cl > ref_cl["o_max"]:
            estado_cl, badge_cl = "RIESGO DE TOXICIDAD", "alto"
        r.cl_fila = FilaSuficiencia(
            elemento="Cl⁻", valor=val_cl, unidad=ref_cl["unit"],
            rango_optimo=f"< {ref_cl['o_max']:.2f} (seguro)", estado=estado_cl, badge=badge_cl, dop_pct=None,
        )

    if list_dop:
        list_dop.sort(key=lambda t: t[1])
        r.elemento_mas_limitante, r.dop_mas_limitante = list_dop[0]

    return r


@dataclass
class FilaRatio:
    nombre: str
    valor: float | None
    minimo: float | None
    maximo: float | None
    evaluacion: str
    color: str  # ok | warn | danger


def evaluar_ratios(valores: dict, cultivo: str) -> tuple[list[FilaRatio], bool, str | None]:
    """Devuelve (filas, es_generico, fuente)."""
    especifico = RATIOS_ESPECIFICOS_CULTIVO.get(cultivo)
    es_generico = especifico is None
    fuente = especifico["fuente"] if especifico else None
    defs = especifico["ratios"] if especifico else RATIOS_GENERICOS

    filas = []
    for r in defs:
        try:
            val = r["calc"](valores)
        except (KeyError, TypeError, ZeroDivisionError):
            val = None
        if val is None or val != val or val in (float("inf"), float("-inf")):
            filas.append(FilaRatio(r["name"], None, r.get("min"), r.get("max"), "No calculable (denominador nulo o dato faltante).", "muted"))
            continue

        evaluacion, color = "Equilibrada", "ok"
        minimo, maximo = r.get("min"), r.get("max")
        if minimo is not None and val < minimo:
            color = "warn"
            evaluacion = (TEXTOS_RATIOS_GENERICOS[r["name"]]["bajo"] if es_generico and r["name"] in TEXTOS_RATIOS_GENERICOS
                          else r.get("labelBajo", "Desbalanceado (Bajo)"))
        elif maximo is not None and val > maximo:
            color = "danger"
            evaluacion = (TEXTOS_RATIOS_GENERICOS[r["name"]]["alto"] if es_generico and r["name"] in TEXTOS_RATIOS_GENERICOS
                          else r.get("labelAlto", "Desbalanceado (Alto)"))
        filas.append(FilaRatio(r["name"], val, minimo, maximo, evaluacion, color))

    return filas, es_generico, fuente


@dataclass
class Recomendacion:
    elemento: str
    estado: str
    factor: float
    color: str
    accion: str
    producto: str


def generar_recomendaciones(valores: dict, normas: dict, sin_bibliografia: list) -> list[Recomendacion]:
    recs = []
    for el, val in valores.items():
        if el in sin_bibliografia or el == "Cl":
            continue
        ref = normas.get(el)
        rec_cat = FERTILIZANTE_CATALOG.get(el)
        if not rec_cat:
            continue
        clasif = clasificar_valor(val, ref)
        if not clasif:
            continue

        factor = clasif.factor
        color_map = {"MUY BAJO": "danger", "BAJO": "warn", "MUY ALTO / EXCESO": "indigo", "ALTO": "alto-consumo", "ÓPTIMO": "ok"}
        color = color_map.get(clasif.estado, "ok")

        tipo = rec_cat["type"]
        producto = rec_cat["fertilizer"]
        if tipo == "macro":
            if factor > 1.0:
                accion = f"RECOMENDACIÓN GENERAL DE ABONADO (SUELO): SUBIR LA DOSIS aplicada en el suelo o fertirrigación. Factor corrector de {factor:.1f}x."
            elif factor < 1.0:
                accion = f"RECOMENDACIÓN GENERAL DE ABONADO (SUELO): BAJAR O ANULAR LA DOSIS (factor corrector de {factor:.1f}x) para reducir costes y evitar consumos de lujo o toxicidades."
            else:
                accion = "RECOMENDACIÓN GENERAL DE ABONADO (SUELO): Mantener dosis estándar del plan de abonado general (factor corrector de 1.0x)."
        elif tipo == "micro":
            if factor > 1.0:
                accion = f"TRATAMIENTO CORRECTOR FOLIAR DIRECTO: Aplicaciones foliares específicas de {producto} con factor corrector de {factor:.1f}x. Alta eficiencia por asimilación inmediata vía cutícula/estomas."
            elif factor < 1.0:
                accion = f"RECOMENDACIÓN FOLIAR: Anular aportes foliares específicos de este micronutriente (factor corrector de {factor:.1f}x)."
            else:
                accion = "RECOMENDACIÓN FOLIAR: Estado óptimo. Aplicaciones estándar de mantenimiento si el cultivo tiene alta demanda fisiológica (factor corrector de 1.0x)."
        else:  # secondary (Ca, Mg)
            if factor > 1.0:
                accion = (f"RECOMENDACIÓN FOLIAR EN ÚLTIMO TÉRMINO: Aspersión foliar con {producto}, factor de ajuste de "
                          f"{factor:.1f}x únicamente en último término. {el} es poco móvil por floema: la aspersión foliar "
                          f"solo corrige tejidos tratados localmente; la corrección definitiva debe ser radicular.")
            elif factor < 1.0:
                accion = f"RECOMENDACIÓN FOLIAR: Exceso detectado (factor corrector de {factor:.1f}x). Anular todo aporte foliar de {el}."
            else:
                accion = "RECOMENDACIÓN FOLIAR: Nivel óptimo. No se requiere intervención (factor corrector de 1.0x)."

        recs.append(Recomendacion(el, clasif.estado, factor, color, accion, producto))

    # Mismo orden que listDop (más limitante primero) — recomendaciones para elementos con bibliografía.
    return recs


# --------------------------------------------------------------- DRIS genérico (clasificación compartida)

def _clasificar_indice_dris(val: float) -> tuple[str, str]:
    if val < -10:
        return "Déficit Fuerte", "danger"
    if val < -2:
        return "Déficit Ligero", "warn"
    if val > 10:
        return "Exceso Fuerte", "indigo"
    if val > 2:
        return "Exceso Ligero", "alto-consumo"
    return "Equilibrado", "ok"


@dataclass
class FilaDris:
    nutriente: str
    indice: float
    descripcion: str
    color: str
    prioridad: str


def _tabla_dris(indices: dict, nombres: dict | None = None) -> tuple[list[FilaDris], float]:
    items = sorted(indices.items(), key=lambda kv: kv[1])
    ibn = sum(abs(v) for v in indices.values())
    filas = []
    for idx, (nut, val) in enumerate(items):
        desc, color = _clasificar_indice_dris(val)
        if desc == "Déficit Fuerte":
            prioridad = f"Alta (Prioridad {idx + 1})"
        elif desc == "Déficit Ligero":
            prioridad = f"Moderada (Prioridad {idx + 1})"
        elif desc == "Exceso Fuerte":
            prioridad = "No Aplicar / Reducir"
        elif desc == "Exceso Ligero":
            prioridad = "No Aplicar"
        else:
            prioridad = "Baja / Mantenimiento"
        nombre = (nombres or {}).get(nut, nut)
        filas.append(FilaDris(nombre, val, desc, color, prioridad))
    return filas, ibn


# --------------------------------------------------------------- DRIS Olivo

def _beaufils_func(val: float, mean: float, sd: float) -> float:
    cv = (sd / mean) * 100
    if val > mean:
        return ((val / mean) - 1) * (1000 / cv)
    if val < mean:
        return (1 - (mean / val)) * (1000 / cv)
    return 0.0


def _jones_func(val: float, mean: float, cv: float) -> float:
    if val >= mean:
        return ((val / mean) - 1) * (1000 / cv)
    return (1 - (mean / val)) * (1000 / cv)


@dataclass
class ResultadoDrisOlivo3P:
    filas: list
    ibn: float
    ind_n: float
    ind_p: float
    ind_k: float


def calcular_dris_olivo_3p(valores: dict, sistema: str) -> ResultadoDrisOlivo3P:
    normas = NORMAS_DRIS_OLIVO_3P[sistema]
    r_np = valores["N"] / valores["P"]
    r_nk = valores["N"] / valores["K"]
    r_kp = valores["K"] / valores["P"]

    f_np = _beaufils_func(r_np, normas["NP"]["mean"], normas["NP"]["sd"])
    f_nk = _beaufils_func(r_nk, normas["NK"]["mean"], normas["NK"]["sd"])
    f_kp = _beaufils_func(r_kp, normas["KP"]["mean"], normas["KP"]["sd"])

    ind_n = (f_np + f_nk) / 2
    ind_p = (-f_np - f_kp) / 2
    ind_k = (-f_nk + f_kp) / 2

    filas, ibn = _tabla_dris({"Nitrógeno (N)": ind_n, "Fósforo (P)": ind_p, "Potasio (K)": ind_k})
    return ResultadoDrisOlivo3P(filas=filas, ibn=ibn, ind_n=ind_n, ind_p=ind_p, ind_k=ind_k)


def calcular_dris_olivo_10p(valores: dict) -> tuple[list[FilaDris], float]:
    n = NORMAS_DRIS_OLIVO_10P
    r = {
        "NP": valores["N"] / valores["P"], "NK": valores["N"] / valores["K"],
        "NCa": valores["N"] / valores["Ca"], "NMg": valores["N"] / valores["Mg"], "NB": valores["N"] / valores["B"],
        "KP": valores["K"] / valores["P"], "KCa": valores["K"] / valores["Ca"],
        "KMg": valores["K"] / valores["Mg"], "KB": valores["K"] / valores["B"],
        "PCa": valores["P"] / valores["Ca"], "PMg": valores["P"] / valores["Mg"],
        "CaMg": valores["Ca"] / valores["Mg"],
        "FeMn": valores["Fe"] / valores["Mn"], "FeZn": valores["Fe"] / valores["Zn"], "FeCu": valores["Fe"] / valores["Cu"],
        "ZnCu": valores["Zn"] / valores["Cu"], "MnZn": valores["Mn"] / valores["Zn"],
    }
    f = {k: _jones_func(r[k], n[k]["mean"], n[k]["cv"]) for k in r}

    indices = {
        "Nitrógeno (N)": (f["NP"] + f["NK"] + f["NCa"] + f["NMg"] + f["NB"]) / 5,
        "Fósforo (P)": (f["PCa"] + f["PMg"] - f["NP"] - f["KP"]) / 4,
        "Potasio (K)": (f["KP"] + f["KCa"] + f["KMg"] + f["KB"] - f["NK"]) / 5,
        "Calcio (Ca)": (f["CaMg"] - f["NCa"] - f["KCa"] - f["PCa"]) / 4,
        "Magnesio (Mg)": (-f["NMg"] - f["KMg"] - f["PMg"] - f["CaMg"]) / 4,
        "Boro (B)": (-f["NB"] - f["KB"]) / 2,
        "Hierro (Fe)": (f["FeMn"] + f["FeZn"] + f["FeCu"]) / 3,
        "Manganeso (Mn)": (f["MnZn"] - f["FeMn"]) / 2,
        "Zinc (Zn)": (f["ZnCu"] - f["FeZn"] - f["MnZn"]) / 3,
        "Cobre (Cu)": (-f["FeCu"] - f["ZnCu"]) / 2,
    }
    return _tabla_dris(indices)


def alertas_condicionales_olivo(*, sistema: str, zona: str, ind_n_3p: float, ind_k_3p: float) -> list[str]:
    alertas = []
    if sistema == "secano" and ind_k_3p < -12:
        alertas.append(
            f"Alerta DRIS en Secano Tradicional: Se observa un fuerte déficit de Potasio (Índice DRIS: {ind_k_3p:.1f}). "
            "En olivares de secano, la falta prolongada de humedad estival restringe la absorción radicular de Potasio y "
            "Boro por flujo de masa. El índice DRIS negativo refleja este bloqueo. Se sugiere priorizar correcciones "
            "mediante aplicaciones foliares concentradas a inicios de primavera (brotación) y durante el post-endurecimiento "
            "del hueso, evitando la dependencia exclusiva del sistema radicular seco."
        )
    if sistema == "superintensivo" and ind_n_3p > 10:
        alertas.append(
            f"Alerta DRIS en Superintensivo: Se observa un exceso severo de Nitrógeno (Índice DRIS: {ind_n_3p:.1f}). "
            "El exceso relativo de Nitrógeno frente al Fósforo y Potasio en sistemas en seto estimula un excesivo vigor "
            "vegetativo y el alargamiento de entrenudos. Esto acelera el sombreado interior de la pared productiva y "
            "reduce la tasa de renovación de brotes fructíferos. Se recomienda suprimir aportes nitrogenados y reequilibrar "
            "con fertilizaciones ricas en Fósforo y Potasio para mantener la estructura compacta del seto."
        )
    if zona == "Guadalquivir_Arcillas" and ind_k_3p < -15 and ind_n_3p > 5:
        alertas.append(
            "Alerta Específica para Valle del Guadalquivir: Los suelos arcillosos/vérticos presentan una alta tasa de "
            "fijación de Potasio en los espacios interlaminares de las arcillas durante el secado del suelo. El exceso "
            "relativo de Nitrógeno agrava este escenario. Se aconseja fraccionar los aportes de Potasio mediante "
            "fertirrigación continua en el bulbo húmedo para saturar la capacidad de fijación edáfica y restablecer el "
            "balance DRIS foliar."
        )
    return alertas


# --------------------------------------------------------------- DRIS Almendro

def _beaufils_ratio_f(sample_ratio: float, mean: float, cv: float) -> float:
    if sample_ratio > mean:
        return ((sample_ratio / mean) - 1) * (1000 / cv)
    if sample_ratio < mean:
        return (1 - (mean / sample_ratio)) * (1000 / cv)
    return 0.0


def _beaufils_product_f(sample_product: float, mean: float, sd: float) -> float:
    # Convención Beaufils: el término de una norma tipo producto se suma con el MISMO signo a los
    # índices de ambos nutrientes implicados (a diferencia de las normas tipo ratio, que se suman con
    # signo opuesto al numerador/denominador). Ver Beaufils (1973); Walworth & Sumner (1987).
    return (sample_product - mean) * (10 / sd)


def calcular_dris_indices_almendro(valores: dict, norms_list: list[dict], nutrientes: list[str]) -> dict:
    indices = {}
    for nut in nutrientes:
        suma, n = 0.0, 0
        for norm in norms_list:
            if norm["type"] == "ratio":
                ratio_val = valores[norm["num"]] / valores[norm["den"]]
                f = _beaufils_ratio_f(ratio_val, norm["mean"], norm["cv"])
                if norm["num"] == nut:
                    suma += f; n += 1
                elif norm["den"] == nut:
                    suma -= f; n += 1
            elif norm["type"] == "product":
                if norm["a"] == nut or norm["b"] == nut:
                    prod_val = valores[norm["a"]] * valores[norm["b"]]
                    f = _beaufils_product_f(prod_val, norm["mean"], norm["sd"])
                    suma += f; n += 1
        indices[nut] = suma / n if n > 0 else 0.0
    return indices


def calcular_dris_almendro(valores: dict, variedad: str) -> tuple[list[FilaDris], float] | None:
    if variedad == "generico" or variedad not in NORMAS_ALMENDRO_DRIS:
        return None
    nutrientes = ["N", "P", "K", "Ca", "Mg"]
    nombres = {"N": "Nitrógeno", "P": "Fósforo", "K": "Potasio", "Ca": "Calcio", "Mg": "Magnesio"}
    indices = calcular_dris_indices_almendro(valores, NORMAS_ALMENDRO_DRIS[variedad], nutrientes)
    return _tabla_dris({nombres[n]: v for n, v in indices.items()})


# --------------------------------------------------------------- DRIS Caqui

def calcular_dris_indices_caqui(valores: dict) -> dict:
    """Índice lineal de Jones: f(Y/X) = [(Y/X)_muestra - (y/x)_norma] / SD_norma. El índice de cada
    nutriente es la media de sus f(+) como numerador menos sus f como denominador."""
    indices = {}
    for nut in NUTRIENTES_CAQUI:
        suma, n = 0.0, 0
        for norm in NORMS_DRIS_CAQUI:
            ratio_val = valores[norm["num"]] / valores[norm["den"]]
            f = (ratio_val - norm["mean"]) / norm["sd"]
            if norm["num"] == nut:
                suma += f; n += 1
            elif norm["den"] == nut:
                suma -= f; n += 1
        indices[nut] = suma / n if n > 0 else 0.0
    return indices


def calcular_dris_caqui(valores: dict) -> tuple[list[FilaDris], float]:
    indices = calcular_dris_indices_caqui(valores)
    return _tabla_dris({NOMBRES_NUTRIENTES.get(n, n): v for n, v in indices.items()})
