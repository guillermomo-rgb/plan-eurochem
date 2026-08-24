"""Pruebas del puerto de analisis_agua_riego.html a Python.

Ejecutar con: python3 -m pytest shared/test_water_quality.py -v
(o python3 shared/test_water_quality.py si no hay pytest instalado)
"""
import math

from water_quality import analizar_agua, EJEMPLOS, CONCENTRACION_HIPOCLORITO


def test_ejemplo_marismas():
    d = EJEMPLOS["Marismas Sector B-XII"]
    r = analizar_agua(
        vol_riego_m3_ha=4000,
        ce_us_cm=d["ce_us_cm"], ph=d["ph"], ca_mg_l=d["ca_mg_l"], mg_mg_l=d["mg_mg_l"],
        na_mg_l=d["na_mg_l"], k_mg_l=d["k_mg_l"], hco3_mg_l=d["hco3_mg_l"],
        cl_mg_l=d["cl_mg_l"], so4_mg_l=d["so4_mg_l"], no3_mg_l=d["no3_mg_l"],
        b_mg_l=d["b_mg_l"], fe_mg_l=d["fe_mg_l"],
    )
    assert math.isclose(r.ce_ds, 1.075, rel_tol=1e-6)
    assert math.isclose(r.dureza_f, (65.9 * 2.5 + 30.9 * 4.12) / 10, rel_tol=1e-6)
    ca_meq = 65.9 / 20.04
    mg_meq = 30.9 / 12.16
    na_meq = 130.0 / 23.0
    ras_esperado = na_meq / math.sqrt((ca_meq + mg_meq) / 2.0)
    assert math.isclose(r.ras, ras_esperado, rel_tol=1e-6)


def test_chlorine_dosing_not_10x_underdosed():
    # Bug original: se mostraban los kg de cloro puro como si fueran litros de
    # producto al 10%, subdosificando por un factor de 10. Confirmamos que el
    # resultado ya divide por CONCENTRACION_HIPOCLORITO (0.10) y no al revés.
    r = analizar_agua(
        vol_riego_m3_ha=1000, ce_us_cm=1000, ph=7.5, ca_mg_l=80, mg_mg_l=24,
        na_mg_l=46, k_mg_l=15, hco3_mg_l=244, cl_mg_l=71, so4_mg_l=96,
        no3_mg_l=10, b_mg_l=0.1, fe_mg_l=0.02,
    )
    kg_cl_puro_min = (15.0 * 1000) / 1000.0  # 15 kg
    kg_cl_puro_max = (20.0 * 1000) / 1000.0  # 20 kg
    assert math.isclose(r.cloro_min_l, kg_cl_puro_min / CONCENTRACION_HIPOCLORITO)
    assert math.isclose(r.cloro_max_l, kg_cl_puro_max / CONCENTRACION_HIPOCLORITO)
    # Con 15-20 ppm y 1000 m3/ha, deben ser 150-200 L de producto al 10%, no 15-20 L.
    assert 149 < r.cloro_min_l < 151
    assert 199 < r.cloro_max_l < 201


def test_infiltracion_usa_las_5_bandas_fao():
    # RAS bajo (banda 0-3) pero CE muy baja -> debe marcar severa igualmente
    # (antes del fix solo se comprobaban 2 combinaciones puntuales).
    r = analizar_agua(
        vol_riego_m3_ha=1000, ce_us_cm=150, ph=7.0, ca_mg_l=40, mg_mg_l=10,
        na_mg_l=5, k_mg_l=2, hco3_mg_l=100, cl_mg_l=20, so4_mg_l=30,
        no3_mg_l=10, b_mg_l=0.1, fe_mg_l=0.02,
    )
    assert r.ras <= 3
    assert r.infiltracion_nivel == "severo"  # CE=0.15 dS/m < severa(0.2) de la banda 0-3


def test_obturacion_calcarea_requiere_calcio_suficiente():
    base = dict(
        vol_riego_m3_ha=1000, ce_us_cm=1200, ph=8.0, mg_mg_l=20, na_mg_l=30,
        k_mg_l=5, hco3_mg_l=400, cl_mg_l=50, so4_mg_l=60, no3_mg_l=10,
        b_mg_l=0.1, fe_mg_l=0.02,
    )
    # Poco calcio (ca_meq bajo) -> riesgo moderado, no importante
    r_bajo_ca = analizar_agua(ca_mg_l=20, **base)  # ca_meq ~ 1.0
    assert r_bajo_ca.obturacion_nivel == "moderado"
    # Mucho calcio -> riesgo importante
    r_alto_ca = analizar_agua(ca_mg_l=100, **base)  # ca_meq ~ 5.0
    assert r_alto_ca.obturacion_nivel == "severo"


def test_electroneutralidad_balance_perfecto():
    # Cationes y aniones (en meq/L) exactamente iguales -> error 0%
    # ca_meq = 40.08/20.04 = 2.0 meq/L; hco3_meq = 122.04/61.02 = 2.0 meq/L
    r = analizar_agua(
        vol_riego_m3_ha=1000, ce_us_cm=1000, ph=7.5,
        ca_mg_l=20.04 * 2, mg_mg_l=0, na_mg_l=0, k_mg_l=0,
        hco3_mg_l=61.02 * 2, cl_mg_l=0, so4_mg_l=0, no3_mg_l=0,
        b_mg_l=0.1, fe_mg_l=0.02,
    )
    assert math.isclose(r.error_cargas_pct, 0.0, abs_tol=1e-6)


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"OK: {t.__name__}")
    print(f"\n{len(tests)} pruebas pasadas.")
