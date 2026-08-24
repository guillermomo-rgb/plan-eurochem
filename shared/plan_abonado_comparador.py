"""Comparador de Planes de Abonado — Plan Eurochem vs. Alternativas.

Puerto de pfSyncEurochemPlan()/pfCalcLine()/pfCalcPlan() y funciones asociadas
en plan_abonado_integrado.html, simplificado para reutilizar directamente el
catálogo FERT_DATA (mismas 23 claves que el resto del programa) en vez de un
catálogo paralelo con nombres propios — el HTML original mantenía dos
catálogos distintos (PF_EUROCHEM_PRODUCTS y fertData) y una tabla de
traducción entre ambos (FERT_KEY_TO_PF_NAME) solo para poder sincronizarlos;
aquí no hace falta esa traducción porque es un único catálogo.
"""
from __future__ import annotations

from dataclasses import dataclass, field

try:
    from .plan_abonado_data import FERT_DATA, ENTEC_INHIBIDOR_KEYS
    from .plan_abonado_calc import legal_n_limit, pi_n_limit
except ImportError:
    from plan_abonado_data import FERT_DATA, ENTEC_INHIBIDOR_KEYS
    from plan_abonado_calc import legal_n_limit, pi_n_limit


def pf_default_state() -> dict:
    return {"planes_alternativos": [], "precios": {}}


def pf_sync_plan_eurochem(*, key_fondo: str, dosis_fondo: float, key_cob1: str, dosis_cob1: float,
                            key_cob2: str, dosis_cob2: float) -> list[dict]:
    """Reconstruye los ítems del "Plan Eurochem" a partir de los 3 selectores de fondo/cobertera,
    para que participe en la comparativa de costes como referencia (igual que pfSyncEurochemPlan)."""
    items = []
    for key, qty, phase in ((key_fondo, dosis_fondo, "fondo"), (key_cob1, dosis_cob1, "cobertera"), (key_cob2, dosis_cob2, "cobertera")):
        if key and key != "0" and qty:
            items.append({"fert_key": key, "qty": qty, "phase": phase})
    return items


@dataclass
class LineaComparador:
    fert_key: str
    label: str
    qty: float
    cost: float
    n: float; p: float; k: float; mg: float; ca: float; s: float
    exento_tope: bool  # lleva inhibidor/liberación lenta


def calc_linea(item: dict, precios: dict) -> LineaComparador:
    fert = FERT_DATA.get(item["fert_key"], FERT_DATA["0"])
    qty = item["qty"]
    precio_tonelada = precios.get(item["fert_key"], 0.0)
    cost = qty * (precio_tonelada / 1000.0)
    return LineaComparador(
        fert_key=item["fert_key"], label=fert.get("label", item["fert_key"]), qty=qty, cost=cost,
        n=qty * fert["n"] / 100, p=qty * fert["p"] / 100, k=qty * fert["k"] / 100,
        mg=qty * fert.get("mg", 0) / 100, ca=qty * fert.get("ca", 0) / 100, s=qty * fert.get("s", 0) / 100,
        exento_tope=item["fert_key"] in ENTEC_INHIBIDOR_KEYS,
    )


@dataclass
class ResultadoPlanComparador:
    nombre: str
    lineas: list = field(default_factory=list)
    cost_ha: float = 0.0
    n_ha: float = 0.0; p_ha: float = 0.0; k_ha: float = 0.0
    mg_ha: float = 0.0; ca_ha: float = 0.0; s_ha: float = 0.0
    fondo_cap_pct: float = 0.0
    excede_tope_fondo: bool = False
    excede_limite_legal: bool = False
    excede_limite_pi: bool = False
    payback_kg_ha: float | None = None


def calc_plan(
    *, nombre: str, items: list[dict], precios: dict, vulnerable: bool, cap_aplica: bool,
    limite_legal: float | None, pi_activo: bool, limite_pi: float | None, precio_por_kg_cosecha: float | None,
) -> ResultadoPlanComparador:
    lineas = [calc_linea(it, precios) for it in items]
    r = ResultadoPlanComparador(nombre=nombre, lineas=lineas)
    r.cost_ha = sum(l.cost for l in lineas)
    r.n_ha = sum(l.n for l in lineas)
    r.p_ha = sum(l.p for l in lineas)
    r.k_ha = sum(l.k for l in lineas)
    r.mg_ha = sum(l.mg for l in lineas)
    r.ca_ha = sum(l.ca for l in lineas)
    r.s_ha = sum(l.s for l in lineas)

    n_fondo_sin_exencion = sum(
        l.n for l, it in zip(lineas, items) if it.get("phase", "fondo") == "fondo" and not l.exento_tope
    )
    r.fondo_cap_pct = (n_fondo_sin_exencion / r.n_ha * 100) if r.n_ha > 0 else 0.0
    r.excede_tope_fondo = vulnerable and cap_aplica and r.fondo_cap_pct > 30.0001

    r.excede_limite_legal = vulnerable and limite_legal is not None and r.n_ha > limite_legal + 0.05
    r.excede_limite_pi = pi_activo and limite_pi is not None and r.n_ha > limite_pi + 0.05

    if r.cost_ha > 0 and precio_por_kg_cosecha:
        r.payback_kg_ha = r.cost_ha / precio_por_kg_cosecha

    return r
