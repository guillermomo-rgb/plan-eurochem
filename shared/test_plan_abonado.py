"""Pruebas del puerto de plan_abonado_integrado.html a Python.

Ejecutar con: python3 test_plan_abonado.py (desde shared/)
"""
import math

from plan_abonado_calc import (
    usda_texture_class, usda_texture_group, calcular_suelo, calcular_balance_n,
    calcular_p_k, calcular_plan_npk, legal_n_limit, pi_n_limit,
    generar_diagnostico_estrategia,
)


def test_usda_texture_arcilloso():
    # 50% arcilla, 30% limo, 20% arena -> Arcilloso (clay>=40, sand<=45, silt<40)
    assert usda_texture_class(20, 30, 50) == "Arcilloso"


def test_usda_texture_group_arenoso():
    g = usda_texture_group("Arenoso")
    assert g["cic_min"] == 0 and g["cic_max"] == 5


def test_suelo_da_arenoso_y_ajuste_n():
    r = calcular_suelo(
        arcilla=5, ph=7.0, ce=0.5, carbonatos=0, caliza_activa=0, cn=11, mo=1.5,
        nitratos_lab=10, n_kjeldahl=0.08, p_olsen=15, fe_ppm=2, mn_ppm=1, cu_ppm=0.3, zn_ppm=1,
        ca_meq=8, ca_ppm=1600, mg_meq=1, mg_ppm=120, k_meq=0.3, k_ppm=120, na_meq=0.2,
        profundidad=30, arena=85, limo=10,
    )
    assert r.ajuste_n_textura == 1.15  # arenoso -> +15% N
    assert r.da_calculada == 1.55


def test_suelo_cic_prioriza_medida_sobre_suma():
    r = calcular_suelo(
        arcilla=20, ph=7.0, ce=0.5, carbonatos=0, caliza_activa=0, cn=11, mo=1.5,
        nitratos_lab=10, n_kjeldahl=0.08, p_olsen=15, fe_ppm=2, mn_ppm=1, cu_ppm=0.3, zn_ppm=1,
        ca_meq=8, ca_ppm=1600, mg_meq=1, mg_ppm=120, k_meq=0.3, k_ppm=120, na_meq=0.2,
        profundidad=30, arena=40, limo=40, cic_medida=25.0,
    )
    assert math.isclose(r.cic, 25.0)
    assert "medida en laboratorio" in r.c_cic


def test_relacion_ca_mg_bloqueo_severo():
    r = calcular_suelo(
        arcilla=20, ph=7.0, ce=0.5, carbonatos=0, caliza_activa=0, cn=11, mo=1.5,
        nitratos_lab=10, n_kjeldahl=0.08, p_olsen=15, fe_ppm=2, mn_ppm=1, cu_ppm=0.3, zn_ppm=1,
        ca_meq=9.0, ca_ppm=1800, mg_meq=1.0, mg_ppm=120, k_meq=0.3, k_ppm=120, na_meq=0.2,
        profundidad=30, arena=40, limo=40,
    )
    assert math.isclose(r.rel_ca_mg, 9.0)
    assert "Bloqueo Severo de Mg" in r.c_rel_camg


def test_balance_n_rd1051_alerta():
    r = calcular_balance_n(
        rendimiento=8, coef_n=28, ajuste_n_textura=1.0, margen_perdidas=1.15,
        vol_riego=0, nitratos_agua=0, restos_cosecha=0, cubierta_veg=0,
        tipo_estiercol="gallinaza", dosis_estiercol_1=15, dosis_estiercol_2=0, dosis_estiercol_3=0,
        tipo_purin="0", dosis_purin_1=0, dosis_purin_2=0, dosis_purin_3=0,
        stock_nitratos=0, kg_n_mo=0, dep_atmosferica=0,
    )
    # gallinaza n=16 kg/t, dosis 15 t/ha -> 240 kg N/ha físicos > 170 -> alerta
    assert math.isclose(r.n_organico_fisico_actual, 240.0)
    assert r.supera_limite_rd1051 is True


def test_balance_n_necesidad_bruta():
    r = calcular_balance_n(
        rendimiento=8, coef_n=28, ajuste_n_textura=1.0, margen_perdidas=1.15,
        vol_riego=0, nitratos_agua=0, restos_cosecha=0, cubierta_veg=0,
        tipo_estiercol="0", dosis_estiercol_1=0, dosis_estiercol_2=0, dosis_estiercol_3=0,
        tipo_purin="0", dosis_purin_1=0, dosis_purin_2=0, dosis_purin_3=0,
        stock_nitratos=0, kg_n_mo=0, dep_atmosferica=0,
    )
    assert r.necesidad_bruta_n == round(8 * 28 * 1.0 * 1.15)


def test_p_k_caliza_activa_incrementa_p():
    r = calcular_p_k(rendimiento=8, coef_p=10, coef_k=25, p_factor=1.0, carb_p_factor=1.30, k_factor=1.0)
    assert r.p_necesidad_corregida == round(8 * 10 * 1.0 * 1.30)


def test_plan_npk_entec_evo_24_fondo():
    r = calcular_plan_npk(
        key_fondo="entec_evo_24", dosis_fondo=200, key_cob1="0", dosis_cob1=0,
        key_cob2="0", dosis_cob2=0, foliar_items=[],
        balance_final_n=100, p_necesidad=50, k_necesidad=50,
    )
    assert math.isclose(r.ca_total, 24.6)  # 12.3% de 200
    assert math.isclose(r.fondo.n, 48.0)  # 24% de 200
    assert r.pct_n_fondo == 100  # único aporte de N


def test_plan_npk_foliar_incluye_micros():
    r = calcular_plan_npk(
        key_fondo="0", dosis_fondo=0, key_cob1="0", dosis_cob1=0, key_cob2="0", dosis_cob2=0,
        foliar_items=[{"name": "Nitrofoska Foliar 10-5-33", "dosis": 10.0}],
        balance_final_n=100, p_necesidad=50, k_necesidad=50,
    )
    assert math.isclose(r.b_foliar, 200.0)  # 10 * 2% * 10
    assert math.isclose(r.k_total, 3.3)


def test_legal_n_limit_zvn():
    assert math.isclose(legal_n_limit("trigo", 8), 35 * 8)
    assert legal_n_limit("cultivo_inexistente", 8) is None


def test_pi_n_limit_olivar_regimen():
    from plan_abonado_data import PI_NOTES
    assert pi_n_limit(PI_NOTES["olivar"], "riego_intensivo") == 150
    assert pi_n_limit(PI_NOTES["olivar"], "secano_tradicional") == 70


def test_diagnostico_zvn_supera_tope_legal():
    html = generar_diagnostico_estrategia(
        n_restante=0, p_balance=0, k_balance=0, n_total=400, p_total=50, k_total=50,
        key_fondo="nitrofoska_special_12_12_17", pct_n_fondo=50, cultivo_key="trigo",
        vulnerable=True, produccion_integrada=False, rendimiento=8,
    )
    assert "Supera el tope legal de N" in html
    assert "Supera el 30% de N en fondo" in html  # sin inhibidor y 50% en fondo


def test_diagnostico_fondo_con_inhibidor_exento_del_30pct():
    html = generar_diagnostico_estrategia(
        n_restante=0, p_balance=0, k_balance=0, n_total=100, p_total=50, k_total=50,
        key_fondo="entec_evo_24", pct_n_fondo=90, cultivo_key="trigo",
        vulnerable=True, produccion_integrada=False, rendimiento=8,
    )
    assert "exento del tope del 30% en fondo" in html


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"OK: {t.__name__}")
    print(f"\n{len(tests)} pruebas pasadas.")
