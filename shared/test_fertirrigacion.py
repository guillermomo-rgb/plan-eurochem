"""Pruebas del puerto de programa_fertirrigacion.html a Python.

Ejecutar con: python3 test_fertirrigacion.py (desde shared/)
"""
import math

from fertirrigacion_calc import (
    analizar_agua, calcular_acido, calcular_fondo, calcular_foliar,
    calcular_creditos_anuales, calcular_balance_anual, calcular_fase_mensual,
    meses_con_conflicto_tanque, calcular_gotero_sonneveld, generar_dictamen_experto,
    creditos_acido_mes, creditos_agua_mes,
)
from fertirrigacion_data import monthly_data_por_defecto, CULTIVO_EXTRACCIONES

WATER_DEFAULT = dict(
    ca_mg_l=80.0, mg_mg_l=24.0, na_mg_l=46.0, k_mg_l=15.0, nh4_mg_l=0.0,
    no3_mg_l=10.0, h2po4_mg_l=0.0, so4_mg_l=96.0, cl_mg_l=71.0, hco3_mg_l=244.0,
    water_ec_ds_m=0.95, ph=7.5, b_mg_l=0.1, fe_mg_l=0.02, vol_anual_m3_ha=0.0,
)


def test_ras_incluye_potasio():
    # Este RAS (fertirrigación) suma K a Na, a diferencia del RAS clásico de analisis_agua_riego.
    r = analizar_agua(**WATER_DEFAULT)
    meq_ca, meq_mg, meq_k, meq_na = 80 / 20.04, 24 / 12.16, 15 / 39.1, 46 / 23.0
    esperado = (meq_na + meq_k) / math.sqrt((meq_ca + meq_mg) / 2)
    assert math.isclose(r.ras, esperado, rel_tol=1e-9)


def test_chlorination_dose_matches_water_analysis_fix():
    r = analizar_agua(**{**WATER_DEFAULT, "vol_anual_m3_ha": 1000.0})
    kg_cl_min = 15.0 * 1000 / 1000.0
    assert math.isclose(r.cloro_min_l, kg_cl_min / 0.10)
    assert 149 < r.cloro_min_l < 151


def test_acido_nitrico_matches_dosing_spec():
    # HNO3 60%, densidad 1.37, peso equiv. 63.0 (monoprótico) — mismos valores que la ficha real.
    r = calcular_acido(meq_hco3=4.0, target_hco3=1.5, purity=60.0, density=1.37, eq_wt=63.0)
    assert math.isclose(r.neut_hco3_meq_l, 2.5)
    esperado_l = (2.5 * 63.0) / (60.0 * 1.37 * 10)
    assert math.isclose(r.dose_l, esperado_l, rel_tol=1e-9)


def test_fondo_granulado_entec_evo_24():
    fondo = calcular_fondo([{"name": "ENTEC Evo 24", "dosis": 200.0}])
    # ca: 12.3% de 200 kg/ha = 24.6 kg/ha CaO
    assert math.isclose(fondo.ca, 24.6, rel_tol=1e-9)
    assert math.isclose(fondo.n, 48.0, rel_tol=1e-9)  # 24% de 200
    assert math.isclose(fondo.p, 0.0)
    assert math.isclose(fondo.total_dosis, 200.0)


def test_foliar_micros_g_ha():
    foliar = calcular_foliar([{"name": "Nitrofoska Foliar 10-5-33", "dosis": 10.0}])
    # b: 2% de etiqueta -> g/ha = dosis * pct * 10 = 10 * 2 * 10 = 200 g/ha
    assert math.isclose(foliar.b, 200.0, rel_tol=1e-9)
    assert math.isclose(foliar.k, 3.3, rel_tol=1e-9)  # 33% de 10 kg = 3.3 kg/ha


def test_producto_desconocido_se_ignora_sin_crash():
    fondo = calcular_fondo([{"name": "Producto Inexistente", "dosis": 100.0}])
    assert fondo.n == 0.0 and fondo.total_dosis == 0.0 and len(fondo.items) == 0


def test_creditos_anuales_y_balance_caqui():
    monthly = monthly_data_por_defecto()
    monthly[5]["water"] = 100.0
    monthly[5]["solubles"] = [{"name": "Nitrofoska Solub 18-18-18", "dosis": 50.0}]

    water_comp = {k: WATER_DEFAULT[k] for k in
                  ("no3_mg_l", "h2po4_mg_l", "k_mg_l", "mg_mg_l", "ca_mg_l", "so4_mg_l")}
    acido = calcular_acido(meq_hco3=244.0 / 61.02, target_hco3=1.5, purity=60.0, density=1.37, eq_wt=63.0)

    creditos = calcular_creditos_anuales(
        monthly_data=monthly, water_composition=water_comp,
        acid_type="Nítrico (60%)", acid_custom={}, neut_hco3=acido.neut_hco3_meq_l,
    )
    # Solubles: 18% N de 50 kg = 9.0 kg/ha de N
    assert math.isclose(creditos.solub["n"], 9.0, rel_tol=1e-9)
    # Agua: 100 m3 * 10 mg/L NO3 * 0.226 / 1000 = 0.226 kg/ha
    assert math.isclose(creditos.water["n"], 100 * 10 * 0.226 / 1000, rel_tol=1e-9)

    fondo = calcular_fondo([])
    balance = calcular_balance_anual(
        yield_val=10.0, coeffs=CULTIVO_EXTRACCIONES["Caqui (Kaki)"], fondo=fondo,
        creditos=creditos, extra={},
    )
    coeffs = CULTIVO_EXTRACCIONES["Caqui (Kaki)"]
    assert math.isclose(balance.base["n"], 10.0 * coeffs["n"])
    esperado_target_n = balance.base["n"] - 0.0 - creditos.water["n"] - creditos.acid["n"]
    assert math.isclose(balance.target["n"], esperado_target_n, rel_tol=1e-9)


def test_conflicto_tanque_detectado():
    monthly = monthly_data_por_defecto()
    monthly[5]["solubles"] = [
        {"name": "Nitrato Cálcico Soluble", "dosis": 50.0},  # Tanque A
        {"name": "SOP solub", "dosis": 50.0},  # Tanque B
    ]
    meses = meses_con_conflicto_tanque(monthly_data=monthly)
    assert monthly[5]["name"] in meses


def test_sin_conflicto_tanque_si_dosis_cero():
    monthly = monthly_data_por_defecto()
    monthly[5]["solubles"] = [
        {"name": "Nitrato Cálcico Soluble", "dosis": 0.0},
        {"name": "SOP solub", "dosis": 50.0},
    ]
    meses = meses_con_conflicto_tanque(monthly_data=monthly)
    assert monthly[5]["name"] not in meses


def test_fase_mensual_cuba_saturada():
    month = {
        "name": "Julio", "water": 10.0, "num_riegos": 1, "cuba_vol": 100.0,
        "flow_rate": 2.0, "tiempo_riego": 2.0, "fase": "engorde",
        "solubles": [{"name": "SOP solub", "dosis": 20.0}],
    }
    water_comp = {k: WATER_DEFAULT[k] for k in
                  ("no3_mg_l", "h2po4_mg_l", "k_mg_l", "mg_mg_l", "ca_mg_l", "so4_mg_l")}
    r = calcular_fase_mensual(
        month=month, water_composition=water_comp, water_ec_ds_m=0.95,
        acid_type="Nítrico (60%)", acid_custom={}, neut_hco3=0.5,
        target={"n": 10, "p": 10, "k": 10, "mg": 10, "ca": 10, "s": 10},
        umbral_salino=1.5,
    )
    # dosis_por_riego = 20kg / 1 riego = 20kg; conc_cuba_gl = 20/100*1000 = 200 g/L > 150
    assert r.cuba_saturada is True
    assert math.isclose(r.conc_cuba_gl, 200.0, rel_tol=1e-9)


def test_gotero_sonneveld_balance_perfecto_sin_solubles():
    monthly = monthly_data_por_defecto()
    agua = analizar_agua(**WATER_DEFAULT)
    r = calcular_gotero_sonneveld(
        mes=monthly[1], agua=agua, acid_type="Ninguno", acid_custom={}, neut_hco3=0.0,
    )
    # Sin ácido ni solubles, el gotero es exactamente el agua base (menos el HCO3 no neutralizado)
    assert math.isclose(r.meq["ca"], agua.meq_ca)
    assert math.isclose(r.meq["hco3"], agua.meq_hco3)  # neut_hco3=0 -> sin cambio


def test_dictamen_alerta_salinidad_y_tanque():
    alertas = generar_dictamen_experto(
        ec_gota=3.0, ras_val=2.0, meq_cl=1.0, hco3_mg_l=50.0,
        meses_conflicto_tanque=["Julio"], crop="Tomate", umbral_salino=2.5,
    )
    niveles = [a.nivel for a in alertas]
    assert niveles[0] == "danger"  # salinidad superada
    assert niveles[-1] == "danger"  # conflicto de tanque
    assert "Julio" in alertas[-1].mensaje


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"OK: {t.__name__}")
    print(f"\n{len(tests)} pruebas pasadas.")
