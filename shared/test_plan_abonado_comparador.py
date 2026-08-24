"""Pruebas del Comparador de Planes de Abonado.

Ejecutar con: python3 test_plan_abonado_comparador.py (desde shared/)
"""
import math

from plan_abonado_comparador import pf_sync_plan_eurochem, calc_linea, calc_plan
from plan_abonado_calc import legal_n_limit, pi_n_limit
from plan_abonado_data import PI_NOTES


def test_sync_plan_eurochem_ignora_dosis_cero():
    items = pf_sync_plan_eurochem(
        key_fondo="nitrofoska_special_12_12_17", dosis_fondo=300,
        key_cob1="0", dosis_cob1=0, key_cob2="entec_evo_27", dosis_cob2=0,
    )
    assert len(items) == 1
    assert items[0]["fert_key"] == "nitrofoska_special_12_12_17"
    assert items[0]["phase"] == "fondo"


def test_calc_linea_coste_y_nutrientes():
    item = {"fert_key": "entec_evo_24", "qty": 200.0, "phase": "fondo"}
    precios = {"entec_evo_24": 500.0}  # 500 EUR/tonelada
    linea = calc_linea(item, precios)
    assert math.isclose(linea.ca, 24.6)  # 12.3% de 200 kg
    assert math.isclose(linea.cost, 200 * 500 / 1000)  # 100 EUR
    assert linea.exento_tope is True  # ENTEC EVO 24 lleva inhibidor


def test_calc_linea_sin_inhibidor_no_exento():
    item = {"fert_key": "nitrofoska_special_12_12_17", "qty": 100.0, "phase": "fondo"}
    linea = calc_linea(item, {})
    assert linea.exento_tope is False
    assert linea.cost == 0.0  # sin precio -> coste 0


def test_calc_plan_supera_tope_fondo_sin_inhibidor():
    items = [{"fert_key": "nitrofoska_special_12_12_17", "qty": 300.0, "phase": "fondo"}]
    r = calc_plan(
        nombre="Plan Eurochem", items=items, precios={}, vulnerable=True, cap_aplica=True,
        limite_legal=None, pi_activo=False, limite_pi=None, precio_por_kg_cosecha=None,
    )
    assert math.isclose(r.fondo_cap_pct, 100.0)  # todo el N en fondo, sin exención
    assert r.excede_tope_fondo is True


def test_calc_plan_exento_con_inhibidor():
    items = [{"fert_key": "entec_evo_24", "qty": 300.0, "phase": "fondo"}]
    r = calc_plan(
        nombre="Plan Eurochem", items=items, precios={}, vulnerable=True, cap_aplica=True,
        limite_legal=None, pi_activo=False, limite_pi=None, precio_por_kg_cosecha=None,
    )
    assert math.isclose(r.fondo_cap_pct, 0.0)  # exento -> no cuenta en el tope
    assert r.excede_tope_fondo is False


def test_calc_plan_supera_limite_legal():
    limite = legal_n_limit("trigo", 8)  # 35 UFN/t * 8 t/ha = 280
    items = [{"fert_key": "entec_evo_27", "qty": 2000.0, "phase": "cobertera"}]  # 27% N * 2000 = 540 kg N/ha
    r = calc_plan(
        nombre="Alternativa", items=items, precios={}, vulnerable=True, cap_aplica=True,
        limite_legal=limite, pi_activo=False, limite_pi=None, precio_por_kg_cosecha=None,
    )
    assert r.n_ha > limite
    assert r.excede_limite_legal is True


def test_calc_plan_payback_kg_cosecha():
    items = [{"fert_key": "entec_evo_24", "qty": 200.0, "phase": "fondo"}]
    precios = {"entec_evo_24": 600.0}
    r = calc_plan(
        nombre="Plan Eurochem", items=items, precios=precios, vulnerable=False, cap_aplica=True,
        limite_legal=None, pi_activo=False, limite_pi=None, precio_por_kg_cosecha=0.5,
    )
    # coste = 200*600/1000 = 120 EUR/ha; payback = 120/0.5 = 240 kg de cosecha/ha
    assert math.isclose(r.payback_kg_ha, 240.0)


def test_pi_olivar_regimen_afecta_limite():
    assert pi_n_limit(PI_NOTES["olivar"], "secano_tradicional") == 70
    assert pi_n_limit(PI_NOTES["olivar"], "riego_intensivo") == 150


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"OK: {t.__name__}")
    print(f"\n{len(tests)} pruebas pasadas.")
