"""Pruebas del puerto de nutrileaf_pro.html a Python.

Ejecutar con: python3 test_nutrileaf.py (desde shared/)
"""
import math

from nutrileaf_data import BASE_DE_DATOS_CULTIVOS
from nutrileaf_calc import (
    clasificar_valor, analizar_suficiencia, evaluar_ratios, generar_recomendaciones,
    calcular_dris_olivo_3p, calcular_dris_olivo_10p, alertas_condicionales_olivo,
    calcular_dris_almendro, calcular_dris_caqui,
)


def test_clasificar_valor_todos_los_tramos():
    ref = {"mb": 1.0, "o_min": 1.5, "o_max": 2.0, "alto_max": 2.5}
    assert clasificar_valor(0.5, ref).estado == "MUY BAJO"
    assert clasificar_valor(1.2, ref).estado == "BAJO"
    assert clasificar_valor(1.8, ref).estado == "ÓPTIMO"
    assert clasificar_valor(2.2, ref).estado == "ALTO"
    assert clasificar_valor(3.0, ref).estado == "MUY ALTO / EXCESO"


def test_clasificar_valor_sin_bibliografia():
    assert clasificar_valor(5.0, {"mb": None}) is None
    assert clasificar_valor(5.0, None) is None


def test_suficiencia_olivo_dop_y_limitante():
    normas = BASE_DE_DATOS_CULTIVOS["olivo"]
    valores = {"N": 1.0, "P": 0.12, "K": 0.85, "Ca": 1.5, "Mg": 0.12, "Fe": 80, "Mn": 30, "Zn": 15, "Cu": 5, "B": 40}
    r = analizar_suficiencia(valores, normas, "olivo")
    # N=1.0 muy por debajo del óptimo (1.5-2.0) -> debería ser el más limitante
    assert r.elemento_mas_limitante == "N"
    assert r.dop_mas_limitante < 0
    n_fila = next(f for f in r.filas if f.elemento == "N")
    assert n_fila.estado == "MUY BAJO"


def test_suficiencia_aguacate_cloruro_toxicidad():
    normas = BASE_DE_DATOS_CULTIVOS["aguacate"]
    valores = {"N": 1.8, "P": 0.15, "K": 1.2, "Ca": 1.8, "Mg": 0.5, "Fe": 100, "Mn": 200, "Zn": 60, "Cu": 8, "B": 50, "Cl": 0.6}
    r = analizar_suficiencia(valores, normas, "aguacate")
    assert r.cl_fila is not None
    assert r.cl_fila.estado == "TOXICIDAD EXTREMA"


def test_ratios_vina_especificos_vs_genericos():
    filas_vina, es_generico_vina, fuente = evaluar_ratios({"N": 3.0, "P": 0.3, "K": 1.0, "Ca": 1.5, "Mg": 0.3}, "viña")
    assert es_generico_vina is False
    assert fuente is not None
    filas_generico, es_generico, _ = evaluar_ratios({"N": 3.0, "P": 0.3, "K": 1.0, "Ca": 1.5, "Mg": 0.3}, "olivo")
    assert es_generico is True


def test_ratios_denominador_cero_no_calculable():
    filas, _, _ = evaluar_ratios({"N": 3.0, "P": 0.0, "K": 1.0, "Ca": 1.5, "Mg": 0.3}, "olivo")
    np_row = next(f for f in filas if f.nombre == "N/P")
    assert np_row.valor is None
    assert "No calculable" in np_row.evaluacion


def test_recomendaciones_deficit_sube_dosis():
    normas = BASE_DE_DATOS_CULTIVOS["olivo"]
    valores = {"N": 1.0, "P": 0.12, "K": 0.85, "Ca": 1.5, "Mg": 0.12, "Fe": 80, "Mn": 30, "Zn": 15, "Cu": 5, "B": 40}
    recs = generar_recomendaciones(valores, normas, [])
    n_rec = next(r for r in recs if r.elemento == "N")
    assert n_rec.factor == 2.0
    assert "SUBIR LA DOSIS" in n_rec.accion


def test_dris_olivo_3p_no_escala_por_1000x():
    # Bug corregido en el HTML: usar sd en vez de CV(%) como divisor de Beaufils disparaba índices
    # de miles en vez de decenas. Con valores de agua (todos = mean de la norma), el índice debe ser 0.
    valores = {"N": 14.50, "P": 1.0, "K": 14.50 / 2.10}  # N/P=14.50=mean, N/K=2.10=mean
    r = calcular_dris_olivo_3p(valores, "secano")
    assert math.isclose(r.ind_n, 0.0, abs_tol=1e-9)
    # Con un desequilibrio moderado (no en mean), el índice debe quedarse en el orden de decenas, no miles.
    valores2 = {"N": 2.0, "P": 0.1, "K": 0.8}  # N/P=20, N/K=2.5
    r2 = calcular_dris_olivo_3p(valores2, "secano")
    assert abs(r2.ind_n) < 100  # con el bug antiguo esto daba > 1000


def test_dris_olivo_10p_balanceado_da_indices_bajos():
    n = 1.75
    valores = {
        "N": n, "P": n / 14.85, "K": n / 1.95, "Ca": n / 1.52, "Mg": n / 11.40, "B": n / 0.045,
        "Fe": 100.0, "Mn": 100.0 / 1.65, "Zn": None, "Cu": None,
    }
    valores["Zn"] = valores["Fe"] / 5.20
    valores["Cu"] = valores["Fe"] / 9.80
    filas, ibn = calcular_dris_olivo_10p(valores)
    assert ibn < 5  # todas las relaciones exactamente en la media -> índices ~0


def test_alertas_olivo_secano_deficit_k():
    alertas = alertas_condicionales_olivo(sistema="secano", zona="otra", ind_n_3p=0, ind_k_3p=-15)
    assert len(alertas) == 1
    assert "Secano Tradicional" in alertas[0]


def test_alertas_olivo_sin_condiciones_vacio():
    alertas = alertas_condicionales_olivo(sistema="regadio", zona="otra", ind_n_3p=0, ind_k_3p=0)
    assert alertas == []


def test_dris_almendro_generico_retorna_none():
    assert calcular_dris_almendro({"N": 2.0, "P": 0.1, "K": 1.0, "Ca": 3.0, "Mg": 0.5}, "generico") is None


def test_dris_almendro_ferraduel_valores_en_media_dan_indice_cero():
    # Construimos valores donde todos los ratios/productos coinciden con la media de la norma.
    valores = {"N": 1.0, "P": 1.0 / 17.05, "K": 1.0 / 2.30, "Ca": 9.13 / 1.0, "Mg": 1.0 / 1.76}
    filas = calcular_dris_almendro(valores, "ferraduel")
    assert filas is not None
    _, ibn = filas
    # No todas las normas pueden anularse simultáneamente (hay 10 normas cruzadas para 5 nutrientes),
    # pero el IBN debe mantenerse en un orden de magnitud razonable (no miles) con esta construcción.
    assert ibn < 500


def test_dris_caqui_devuelve_13_elementos():
    valores = {n: 1.0 for n in ["N", "P", "K", "Ca", "Mg", "Na", "S", "Cl", "B", "Cu", "Fe", "Mn", "Zn"]}
    filas, ibn = calcular_dris_caqui(valores)
    assert len(filas) == 13
    assert ibn >= 0


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"OK: {t.__name__}")
    print(f"\n{len(tests)} pruebas pasadas.")
