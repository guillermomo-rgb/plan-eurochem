"""Lógica de cálculo del Plan de Abonado Integrado.

Puerto directo (misma aritmética, mismos umbrales) de runCalculations() y
funciones auxiliares en plan_abonado_integrado.html. No incluye el módulo
"Comparador de Planes" (pfRender/pfCalcPlan/...) — ese subsistema de
comparación de costes entre el Plan Eurochem y alternativas del usuario
queda fuera de este primer puerto; se puede añadir después si hace falta.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

try:
    from .plan_abonado_data import (
        FERT_DATA, FOLIARES_DB, ESTIERCOL_DATA, PURINES_DATA,
        ENTEC_INHIBIDOR_KEYS, CULTIVO_ZVN_NOTES, PI_NOTES,
    )
except ImportError:
    from plan_abonado_data import (
        FERT_DATA, FOLIARES_DB, ESTIERCOL_DATA, PURINES_DATA,
        ENTEC_INHIBIDOR_KEYS, CULTIVO_ZVN_NOTES, PI_NOTES,
    )


def usda_texture_class(sand: float, silt: float, clay: float) -> str | None:
    if sand + silt + clay <= 0:
        return None
    if silt + 1.5 * clay < 15:
        return "Arenoso"
    if silt + 2 * clay < 30:
        return "Arenoso Franco"
    if 7 <= clay < 20 and sand > 52 and (silt + 2 * clay) >= 30:
        return "Franco Arenoso"
    if clay < 7 and silt < 50 and (silt + 2 * clay) >= 30:
        return "Franco Arenoso"
    if 7 <= clay < 27 and 28 <= silt < 50 and sand <= 52:
        return "Franco"
    if (silt >= 50 and 12 <= clay < 27) or (50 <= silt < 80 and clay < 12):
        return "Franco Limoso"
    if silt >= 80 and clay < 12:
        return "Limoso"
    if 20 <= clay < 35 and silt < 28 and sand > 45:
        return "Franco Arcillo Arenoso"
    if 27 <= clay < 40 and sand <= 20:
        return "Franco Arcillo Limoso"
    if 27 <= clay < 40 and 20 < sand <= 45:
        return "Franco Arcilloso"
    if clay >= 35 and sand > 45:
        return "Arcillo Arenoso"
    if clay >= 40 and silt >= 40:
        return "Arcillo Limoso"
    if clay >= 40 and sand <= 45 and silt < 40:
        return "Arcilloso"
    return "Franco"


def usda_texture_group(clase_usda: str | None) -> dict | None:
    if not clase_usda:
        return None
    if clase_usda in ("Arenoso", "Arenoso Franco", "Franco Arenoso"):
        return {"grupo": "Arenoso / Francoarenoso", "cic_min": 0, "cic_max": 5}
    if clase_usda in ("Franco", "Franco Limoso", "Limoso"):
        return {"grupo": "Franco / Franco-limoso", "cic_min": 5, "cic_max": 15}
    return {"grupo": "Arcilloso / Francoarcilloso", "cic_min": 15, "cic_max": 999}


@dataclass
class ResultadoSuelo:
    clase_usda: str | None
    da_calculada: float
    ajuste_n_textura: float
    c_arcilla: str
    c_textura_usda: str
    c_ph: str
    c_ce: str
    c_cn: str
    n_real_ppm: float
    c_nitratos: str
    c_kjeldahl: str
    p_factor: float
    p_suelo_lbl: str
    p_recomendacion_detalle: str
    k_factor: float
    k_suelo_lbl: str
    k_recomendacion_detalle: str
    c_fe: str; c_mn: str; c_cu: str; c_zn: str
    c_carbonatos: str
    carb_p_factor: float
    c_caliza_activa: str
    c_na_conv: str; c_mg_conv: str; c_ca_conv: str
    masa_suelo_kg: float
    kg_n_mo: float
    c_mo: str
    stock_nitratos: float
    cic: float
    c_cic: str
    sat_ca: float; sat_mg: float; sat_k: float; sat_na: float
    c_sat_ca: str; c_sat_mg: str; c_sat_k: str; c_psicalc: str
    rel_ca_mg: float; c_rel_camg: str
    rel_mg_k: float; c_rel_mgk: str
    rel_ca_k: float; c_rel_cak: str
    rel_ca_mg_k: float; c_rel_camgk: str
    woodruff: float; c_woodruff: str
    diag_k: str
    diag_mg: str


def calcular_suelo(
    *, arcilla: float, ph: float, ce: float, carbonatos: float, caliza_activa: float,
    cn: float, mo: float, nitratos_lab: float, n_kjeldahl: float, p_olsen: float,
    fe_ppm: float, mn_ppm: float, cu_ppm: float, zn_ppm: float,
    ca_meq: float, ca_ppm: float, mg_meq: float, mg_ppm: float, k_meq: float, k_ppm: float,
    na_meq: float, profundidad: float, arena: float, limo: float, cic_medida: float = 0.0,
) -> ResultadoSuelo:
    profundidad = profundidad or 30
    clase_usda = usda_texture_class(arena, limo, arcilla)

    if clase_usda in ("Arenoso", "Arenoso Franco"):
        da_calculada = 1.55
    elif clase_usda == "Franco Arenoso":
        da_calculada = 1.45
    elif clase_usda in ("Arcilloso", "Arcillo Arenoso", "Arcillo Limoso"):
        da_calculada = 1.20
    elif clase_usda:
        da_calculada = 1.35
    else:
        da_calculada = 1.25 if arcilla >= 40 else (1.45 if arcilla < 10 else 1.35)

    if arcilla < 10:
        c_arcilla, ajuste_n_textura = "Arenoso: Subir N un 15%", 1.15
    elif arcilla > 40:
        c_arcilla, ajuste_n_textura = "Arcilloso: Bajar N un 15%", 0.85
    else:
        c_arcilla, ajuste_n_textura = "Franco: Condiciones óptimas", 1.0

    if clase_usda:
        grupo = usda_texture_group(clase_usda)
        cic_max_txt = "25+" if grupo["cic_max"] == 999 else grupo["cic_max"]
        c_textura_usda = f"Clase USDA: {clase_usda} (CIC típica {grupo['cic_min']}-{cic_max_txt} meq/100g)"
    else:
        c_textura_usda = "Introduce Limo y Arena para clasificar por USDA"

    c_ph = "Suelo Ácido." if ph < 6.6 else ("Básico / Alcalino." if ph > 8.0 else "Neutro.")
    c_ce = "Suelo Sódico / Salino" if ce > 0.8 else "No salino"
    c_cn = "Liberación rápida (Min. activa)" if cn < 10 else ("Óptima / Estable" if cn <= 12 else "Acumula M.O. / Lenta")

    n_real_ppm = nitratos_lab / 4.42
    c_nitratos = f"N real: {n_real_ppm:.1f} ppm."
    c_kjeldahl = "Muy bajo" if n_kjeldahl < 0.05 else ("Bajo" if n_kjeldahl < 0.10 else "Normal/Alto")

    if p_olsen < 7:
        p_suelo_lbl, p_factor = "Muy Bajo", 1.25
        p_recomendacion_detalle = "Suelo muy bajo en P. Sobredosis del +25% para enriquecer."
    elif p_olsen < 12:
        p_suelo_lbl, p_factor = "Bajo", 1.15
        p_recomendacion_detalle = "Suelo bajo en P. Elevar dosis un +15% para enriquecimiento progresivo."
    elif p_olsen < 18:
        p_suelo_lbl, p_factor = "Normal", 1.0
        p_recomendacion_detalle = "Nivel de P adecuado. Se aplica dosis de mantenimiento sin corrección."
    elif p_olsen <= 25:
        p_suelo_lbl, p_factor = "Alto", 0.70
        p_recomendacion_detalle = "Suelo rico en P. Reducción a la baja de -30% para evitar exceso."
    else:
        p_suelo_lbl, p_factor = "Muy Alto", 0.50
        p_recomendacion_detalle = "Suelo excesivamente alto en P. Reducción severa del -50% en abonado de fondo."

    if k_ppm < 80:
        k_suelo_lbl, k_factor = "Muy Bajo", 1.25
        k_recomendacion_detalle = "Suelo muy pobre en K. Incrementar dosis un +25% para recarga del complejo."
    elif k_ppm <= 160:
        k_suelo_lbl, k_factor = "Bajo", 1.15
        k_recomendacion_detalle = "Suelo bajo en K. Se sobreabona un +15% para reposición."
    elif k_ppm <= 235:
        k_suelo_lbl, k_factor = "Medio", 1.0
        k_recomendacion_detalle = "Nivel de K óptimo. Fertilización equilibrada de mantenimiento."
    elif k_ppm <= 390:
        k_suelo_lbl, k_factor = "Alto", 0.70
        k_recomendacion_detalle = "Suelo rico en K. Se reduce la cobertera un -30% para evitar bloqueos de Mg."
    else:
        k_suelo_lbl, k_factor = "Muy Alto", 0.50
        k_recomendacion_detalle = "Suelo saturado en K. Reducción extrema del -50% para mitigar antagonismo Mg."

    c_fe = "Carencia grave Hierro" if fe_ppm < 1 else ("Bajo" if fe_ppm <= 3 else ("Medio / Normal" if fe_ppm <= 6 else "Alto"))
    c_mn = "Muy bajo" if mn_ppm < 0.5 else ("Bajo" if mn_ppm <= 1.5 else ("Medio" if mn_ppm <= 3 else "Alto"))
    c_cu = "Muy bajo" if cu_ppm < 0.2 else ("Bajo" if cu_ppm <= 0.4 else ("Medio" if cu_ppm <= 0.8 else "Alto"))
    c_zn = "Muy bajo" if zn_ppm < 0.5 else ("Bajo" if zn_ppm <= 1 else ("Medio" if zn_ppm <= 2 else "Alto"))

    c_carbonatos = "Suelo calizo: ver Caliza Activa para el riesgo real de bloqueo de P/Fe" if carbonatos > 25 else "Carbonatos bajo control"

    if caliza_activa > 15:
        carb_p_factor = 1.30
        p_recomendacion_detalle += " ¡Alerta de Caliza Activa muy alta! Incremento de un +30% de fósforo para contrarrestar precipitación insolubilizada."
        c_caliza_activa = "Muy alta: ¡Bloqueo severo! Sobreabonar P₂O₅ +30%. Riesgo de clorosis férrica."
    elif caliza_activa > 10:
        carb_p_factor = 1.15
        c_caliza_activa = "Alta: Elevar P₂O₅ +15%. Vigilar riesgo de clorosis férrica."
    elif caliza_activa > 6:
        carb_p_factor = 1.0
        c_caliza_activa = "Moderada: Vigilar bloqueo de P"
    else:
        carb_p_factor = 1.0
        c_caliza_activa = "Baja: sin riesgo relevante de bloqueo"

    c_na_conv = "Muy Bajo" if na_meq <= 0.3 else ("Bajo" if na_meq <= 0.6 else ("Normal" if na_meq <= 1 else "Alto"))
    c_mg_conv = "Bajo: Posible clorosis" if mg_ppm < 60 else ("Adecuado" if mg_ppm <= 180 else "Alto")
    c_ca_conv = "Bajo: Mala estructura" if ca_ppm < 1000 else ("Equilibrado" if ca_ppm <= 2000 else "Alto: Bloqueos")

    masa_suelo_kg = 10000 * (profundidad / 100) * da_calculada * 1000
    cn_efectivo = cn if cn > 0 else 11.5
    pct_n_en_mo = 0.58 / cn_efectivo
    kg_n_mo = masa_suelo_kg * (mo / 100) * 0.01 * pct_n_en_mo
    c_mo = f"Mineralización a {profundidad:.0f}cm (C/N {cn_efectivo:.1f}): {kg_n_mo:.1f} kg N."

    stock_nitratos = n_real_ppm * (masa_suelo_kg / 1000000)

    suma_bases = ca_meq + mg_meq + k_meq + na_meq
    usa_cic_medida = cic_medida > 0
    cic = cic_medida if usa_cic_medida else suma_bases
    cic_estimada = (0.5 * arcilla) + (2.0 * mo)
    if usa_cic_medida:
        c_cic = f"✅ CIC medida en laboratorio (prioritaria sobre la suma de bases, S={suma_bases:.1f} meq/100g)."
    elif ph > 7.5 or carbonatos > 2:
        c_cic = "⚠️ Alerta Calizo: Disolución de CaCO₃ en lab sobreestima Ca²⁺. CIC por suma está sobredimensionada. Si el boletín trae una CIC medida, introdúcela arriba."
    elif ph < 6.0:
        c_cic = "⚠️ Suelo Ácido: Suma subestima CIC al omitir acidez de cambio (H⁺+Al³⁺)."
    elif cic > 0:
        c_cic = f"Aproximación neutra estable. CIC Est. (Arcilla + MO): {cic_estimada:.1f} meq/100g."
    else:
        c_cic = "-"
    if clase_usda and cic > 0:
        grupo = usda_texture_group(clase_usda)
        dentro = grupo["cic_min"] <= cic <= grupo["cic_max"]
        cic_max_txt = "25+" if grupo["cic_max"] == 999 else grupo["cic_max"]
        c_cic += (
            f" {'✅' if dentro else '⚠️'} CIC {cic:.1f} meq/100g "
            f"{'coherente con' if dentro else 'fuera del rango típico de'} la clase {clase_usda} "
            f"({grupo['cic_min']}-{cic_max_txt})."
        )

    sat_ca = (ca_meq / cic) * 100 if cic > 0 else 0.0
    sat_mg = (mg_meq / cic) * 100 if cic > 0 else 0.0
    sat_k = (k_meq / cic) * 100 if cic > 0 else 0.0
    sat_na = (na_meq / cic) * 100 if cic > 0 else 0.0

    c_sat_ca = "⚠️ Bajo: Pérdida de estructura, acidez, desfloculación." if sat_ca < 60 else ("⚠️ Alto: Bloqueo inducido de Mg, K y microelementos." if sat_ca > 80 else "Óptimo (Rango MAPA: 60-80%)")
    c_sat_mg = "⚠️ Bajo: Clorosis en hojas viejas, baja fotosíntesis." if sat_mg < 10 else ("⚠️ Alto: Dispersión si Ca/Mg<2, endurecimiento del suelo." if sat_mg > 20 else "Óptimo (Rango MAPA: 10-20%)")
    c_sat_k = "⚠️ Bajo: Baja resistencia al estrés hídrico, merma calibre." if sat_k < 2 else ("⚠️ Alto: Consumo de lujo, bloqueo de absorción de Mg y Ca." if sat_k > 6 else "Óptimo (Rango MAPA: 2-6%)")
    c_psicalc = "🚨 Peligro: Degradación estructural severa (Sódico)." if sat_na > 15 else ("🚨 Riesgo: Suelo salino-sódico en transición." if sat_na > 5 else "Estable (Sin riesgo de sodicidad)")

    rel_ca_mg = (ca_meq / mg_meq) if mg_meq > 0 else 0.0
    if rel_ca_mg > 6.0:
        c_rel_camg = "🚨 Bloqueo Severo de Mg: Ca en exceso inhibe absorción de Mg." if rel_ca_mg > 8.0 else "⚠️ Bloqueo: Riesgo de clorosis intervenal en hojas viejas."
    elif rel_ca_mg < 3.0:
        c_rel_camg = "⚠️ Pérdida Estructura: Suelo pesado, encostramiento, asfixia radicular."
    else:
        c_rel_camg = "Floculación vs Estructura Equilibrada."

    rel_mg_k = (mg_meq / k_meq) if k_meq > 0 else 0.0
    if rel_mg_k > 6.0:
        c_rel_mgk = "🚨 Bloqueo K: Carencia inducida de K. Sufre estrés hídrico y calibre pequeño."
    elif rel_mg_k < 2.0:
        c_rel_mgk = "🚨 Bloqueo Mg: Carencia inducida de Mg por sobrefertilización potásica."
    else:
        c_rel_mgk = "Equilibrio Divalente/Monovalente Óptimo."

    rel_ca_k = (ca_meq / k_meq) if k_meq > 0 else 0.0
    if rel_ca_k > 30.0:
        c_rel_cak = "🚨 Antagonismo Ca → K: El K es insuficiente frente al Ca. Aportar vía foliar."
    elif rel_ca_k < 10.0:
        c_rel_cak = "⚠️ Antagonismo K → Ca: Puede inducir desórdenes (peseta en tomate o bitter pit)."
    else:
        c_rel_cak = "Óptimo."

    rel_ca_mg_k = ((ca_meq + mg_meq) / k_meq) if k_meq > 0 else 0.0
    if rel_ca_mg_k > 30.0:
        c_rel_camgk = "🚨 Deficiencia Inducida K: Divalentes bloquean K (requiere refuerzo potásico)."
    elif rel_ca_mg_k < 10.0:
        c_rel_camgk = "⚠️ Consumo de lujo o toxicidad de K con inhibición general de divalentes."
    else:
        c_rel_camgk = "Equilibrio Óptimo."

    woodruff = (k_meq / math.sqrt(ca_meq + mg_meq)) if (ca_meq + mg_meq) > 0 else 0.0
    if woodruff > 0.15:
        c_woodruff = "⚠️ Exceso de actividad de K respecto a divalentes."
    elif woodruff < 0.04:
        c_woodruff = "⚠️ Baja energía de cambio de K. Respuesta inmediata a aportes de potasio."
    else:
        c_woodruff = "Energía de reemplazamiento de K equilibrada."

    # Árbol de decisión Mulder
    if k_ppm < 80:
        diag_k = "🔴 CARENCIA REAL POR DÉFICIT ABSOLUTO. Se recomienda aporte edáfico directo de fondo/fertirriego."
    elif k_ppm >= 150:
        if rel_mg_k > 6 or rel_ca_k > 30 or rel_ca_mg_k > 35:
            diag_k = "🚨 BLOQUEO INDUCIDO (Carencia condicionada). El abono edáfico puede quedar retenido. Priorice aportes foliares en máxima demanda o reduzca aportes de Ca/Mg."
        else:
            diag_k = "🟢 NIVEL ÓPTIMO Y ASIMILABLE. Las relaciones de equilibrio catiónico son correctas."
    else:
        diag_k = "🟡 Zona de transición. Las relaciones de cambio son normales pero con reservas moderadas."

    if mg_ppm < 100:
        diag_mg = "🔴 CARENCIA REAL. Aporte sulfato de magnesio o dolomita (si pH < 6.5)."
    elif mg_ppm >= 180:
        if rel_ca_mg > 8:
            diag_mg = "🚨 BLOQUEO INDUCIDO POR CALCIO. El Ca libre impide la asimilación de Mg. Aplique magnesio quelatado o vía foliar."
        elif k_meq > 0 and (mg_meq / k_meq) < 2:
            diag_mg = "🚨 BLOQUEO INDUCIDO POR POTASIO. El exceso de K desplaza al Mg. Suspenda fertilización potásica temporalmente."
        else:
            diag_mg = "🟢 NIVEL ÓPTIMO Y ASIMILABLE. Relaciones con antagonistas equilibradas."
    else:
        diag_mg = "🟡 Zona de transición. Niveles moderados pero estables."

    return ResultadoSuelo(
        clase_usda=clase_usda, da_calculada=da_calculada, ajuste_n_textura=ajuste_n_textura,
        c_arcilla=c_arcilla, c_textura_usda=c_textura_usda, c_ph=c_ph, c_ce=c_ce, c_cn=c_cn,
        n_real_ppm=n_real_ppm, c_nitratos=c_nitratos, c_kjeldahl=c_kjeldahl,
        p_factor=p_factor, p_suelo_lbl=p_suelo_lbl, p_recomendacion_detalle=p_recomendacion_detalle,
        k_factor=k_factor, k_suelo_lbl=k_suelo_lbl, k_recomendacion_detalle=k_recomendacion_detalle,
        c_fe=c_fe, c_mn=c_mn, c_cu=c_cu, c_zn=c_zn, c_carbonatos=c_carbonatos,
        carb_p_factor=carb_p_factor, c_caliza_activa=c_caliza_activa,
        c_na_conv=c_na_conv, c_mg_conv=c_mg_conv, c_ca_conv=c_ca_conv,
        masa_suelo_kg=masa_suelo_kg, kg_n_mo=kg_n_mo, c_mo=c_mo, stock_nitratos=stock_nitratos,
        cic=cic, c_cic=c_cic, sat_ca=sat_ca, sat_mg=sat_mg, sat_k=sat_k, sat_na=sat_na,
        c_sat_ca=c_sat_ca, c_sat_mg=c_sat_mg, c_sat_k=c_sat_k, c_psicalc=c_psicalc,
        rel_ca_mg=rel_ca_mg, c_rel_camg=c_rel_camg, rel_mg_k=rel_mg_k, c_rel_mgk=c_rel_mgk,
        rel_ca_k=rel_ca_k, c_rel_cak=c_rel_cak, rel_ca_mg_k=rel_ca_mg_k, c_rel_camgk=c_rel_camgk,
        woodruff=woodruff, c_woodruff=c_woodruff, diag_k=diag_k, diag_mg=diag_mg,
    )


@dataclass
class ResultadoBalanceN:
    necesidad_bruta_n: int
    n_agua: int
    n_verde: float
    n_estiercol_mineralizado: float
    n_purin_mineralizado: float
    n_organico_total: float
    stock_nitratos: float
    kg_n_mo: float
    total_aportes_n: float
    balance_final_n: float
    n_organico_fisico_actual: float
    supera_limite_rd1051: bool


def calcular_balance_n(
    *, rendimiento: float, coef_n: float, ajuste_n_textura: float, margen_perdidas: float,
    vol_riego: float, nitratos_agua: float, restos_cosecha: float, cubierta_veg: float,
    tipo_estiercol: str, dosis_estiercol_1: float, dosis_estiercol_2: float, dosis_estiercol_3: float,
    tipo_purin: str, dosis_purin_1: float, dosis_purin_2: float, dosis_purin_3: float,
    stock_nitratos: float, kg_n_mo: float, dep_atmosferica: float,
) -> ResultadoBalanceN:
    necesidad_bruta_n = round(rendimiento * coef_n * ajuste_n_textura * margen_perdidas)
    n_agua = round((vol_riego * nitratos_agua) / (62000 / 14))
    n_verde = restos_cosecha + cubierta_veg

    d_est = ESTIERCOL_DATA.get(tipo_estiercol, ESTIERCOL_DATA["0"])
    n_estiercol = (d_est["n"] * dosis_estiercol_1 * d_est["y1"] + d_est["n"] * dosis_estiercol_2 * d_est["y2"]
                   + d_est["n"] * dosis_estiercol_3 * d_est["y3"])

    d_purin = PURINES_DATA.get(tipo_purin, PURINES_DATA["0"])
    n_purin = (d_purin["n"] * dosis_purin_1 * d_purin["y1"] + d_purin["n"] * dosis_purin_2 * d_purin["y2"]
               + d_purin["n"] * dosis_purin_3 * d_purin["y3"])

    n_organico_total = n_estiercol + n_purin
    total_aportes = stock_nitratos + kg_n_mo + dep_atmosferica + n_agua + n_verde + n_organico_total
    balance_final = max(0.0, necesidad_bruta_n - total_aportes)

    n_organico_fisico_actual = (d_est["n"] * dosis_estiercol_1) + (d_purin["n"] * dosis_purin_1)

    return ResultadoBalanceN(
        necesidad_bruta_n=necesidad_bruta_n, n_agua=n_agua, n_verde=n_verde,
        n_estiercol_mineralizado=n_estiercol, n_purin_mineralizado=n_purin,
        n_organico_total=n_organico_total, stock_nitratos=stock_nitratos, kg_n_mo=kg_n_mo,
        total_aportes_n=total_aportes, balance_final_n=balance_final,
        n_organico_fisico_actual=n_organico_fisico_actual,
        supera_limite_rd1051=(n_organico_fisico_actual > 170),
    )


@dataclass
class ResultadoPK:
    p_extraccion_teorica: float
    p_necesidad_corregida: int
    k_extraccion_teorica: float
    k_necesidad_corregida: int


def calcular_p_k(*, rendimiento: float, coef_p: float, coef_k: float, p_factor: float, carb_p_factor: float, k_factor: float) -> ResultadoPK:
    p_extraccion = rendimiento * coef_p
    p_necesidad = round(p_extraccion * p_factor * carb_p_factor)
    k_extraccion = rendimiento * coef_k
    k_necesidad = round(k_extraccion * k_factor)
    return ResultadoPK(p_extraccion, p_necesidad, k_extraccion, k_necesidad)


@dataclass
class LineaAbono:
    key: str
    dosis: float
    n: float; p: float; k: float; mg: float; ca: float; s: float


@dataclass
class ResultadoPlanNPK:
    fondo: LineaAbono
    cob1: LineaAbono
    cob2: LineaAbono
    foliar_items: list = field(default_factory=list)
    n_total: float = 0.0; p_total: float = 0.0; k_total: float = 0.0
    mg_total: float = 0.0; ca_total: float = 0.0; s_total: float = 0.0
    fe_foliar: float = 0.0; mn_foliar: float = 0.0; zn_foliar: float = 0.0
    cu_foliar: float = 0.0; b_foliar: float = 0.0; mo_foliar: float = 0.0
    pct_n_fondo: int = 0; pct_n_cob1: int = 0; pct_n_cob2: int = 0
    n_restante: float = 0.0
    p_balance: float = 0.0
    k_balance: float = 0.0


def _linea_fert(key: str, dosis: float) -> LineaAbono:
    d = FERT_DATA.get(key, FERT_DATA["0"])
    return LineaAbono(
        key=key, dosis=dosis,
        n=(d["n"] * dosis) / 100, p=(d["p"] * dosis) / 100, k=(d["k"] * dosis) / 100,
        mg=(d.get("mg", 0) * dosis) / 100, ca=(d.get("ca", 0) * dosis) / 100, s=(d.get("s", 0) * dosis) / 100,
    )


def calcular_plan_npk(
    *, key_fondo: str, dosis_fondo: float, key_cob1: str, dosis_cob1: float,
    key_cob2: str, dosis_cob2: float, foliar_items: list[dict],
    balance_final_n: float, p_necesidad: float, k_necesidad: float,
) -> ResultadoPlanNPK:
    fondo = _linea_fert(key_fondo, dosis_fondo)
    cob1 = _linea_fert(key_cob1, dosis_cob1)
    cob2 = _linea_fert(key_cob2, dosis_cob2)

    r = ResultadoPlanNPK(fondo=fondo, cob1=cob1, cob2=cob2)
    for item in foliar_items:
        prod = FOLIARES_DB.get(item["name"])
        if not prod:
            continue
        dosis = item["dosis"]
        r.foliar_items.append(item)
        r.n_total += dosis * prod["n"] / 100
        r.p_total += dosis * prod["p"] / 100
        r.k_total += dosis * prod["k"] / 100
        r.mg_total += dosis * prod["mg"] / 100
        r.ca_total += dosis * prod["ca"] / 100
        r.s_total += dosis * prod["s"] / 100
        r.fe_foliar += dosis * prod["fe"] * 10
        r.mn_foliar += dosis * prod["mn"] * 10
        r.zn_foliar += dosis * prod["zn"] * 10
        r.cu_foliar += dosis * prod["cu"] * 10
        r.b_foliar += dosis * prod["b"] * 10
        r.mo_foliar += dosis * prod["mo"] * 10

    r.n_total += fondo.n + cob1.n + cob2.n
    r.p_total += fondo.p + cob1.p + cob2.p
    r.k_total += fondo.k + cob1.k + cob2.k
    r.mg_total += fondo.mg + cob1.mg + cob2.mg
    r.ca_total += fondo.ca + cob1.ca + cob2.ca
    r.s_total += fondo.s + cob1.s + cob2.s

    if r.n_total > 0:
        r.pct_n_fondo = round((fondo.n / r.n_total) * 100)
        r.pct_n_cob1 = round((cob1.n / r.n_total) * 100)
        r.pct_n_cob2 = round((cob2.n / r.n_total) * 100)

    r.n_restante = balance_final_n - r.n_total
    r.p_balance = r.p_total - p_necesidad
    r.k_balance = r.k_total - k_necesidad
    return r


def legal_n_limit(cultivo_key: str, rendimiento: float) -> float | None:
    zvn = CULTIVO_ZVN_NOTES.get(cultivo_key)
    if not zvn or not zvn.get("ufnT") or not rendimiento:
        return None
    return zvn["ufnT"] * rendimiento


def pi_n_limit(pi_notes: dict, regimen_olivar: str = "secano_tradicional") -> float | None:
    if not pi_notes:
        return None
    if pi_notes.get("regimenLimits"):
        return pi_notes["regimenLimits"].get(regimen_olivar)
    if pi_notes.get("goteoLimits"):
        return pi_notes["goteoLimits"]["n"]
    if pi_notes.get("nAbsLimit") is not None:
        return pi_notes["nAbsLimit"]
    return None


def generar_diagnostico_estrategia(
    *, n_restante: float, p_balance: float, k_balance: float, n_total: float, p_total: float, k_total: float,
    key_fondo: str, pct_n_fondo: int, cultivo_key: str, vulnerable: bool, produccion_integrada: bool,
    rendimiento: float, regimen_olivar: str = "secano_tradicional",
) -> str:
    lines = ["<strong>🚜 Desempeño de la Estrategia Comercial:</strong><br>"]

    if n_restante > 10:
        lines.append(f"⚠️ <strong>N Insuficiente:</strong> Falta cubrir {n_restante:.1f} UF de Nitrógeno en las coberteras.<br>")
    elif n_restante < -15:
        lines.append(f"❌ <strong>Sobredosis de Nitrógeno:</strong> Exceso de {abs(n_restante):.1f} UF. Reduzca dosis para cumplir con el RD 1051.<br>")
    else:
        lines.append("✅ <strong>Nitrógeno optimizado:</strong> Satisface con precisión el balance de nutrientes.<br>")

    if p_balance < -15:
        lines.append(f"⚠️ <strong>Déficit de Fósforo:</strong> Faltan {abs(p_balance):.1f} kg P₂O₅/ha. Seleccione una fórmula de fondo con más fósforo.<br>")
    elif p_balance > 20:
        lines.append(f"ℹ️ <strong>Exceso de Fósforo:</strong> Superávit de {p_balance:.1f} kg P₂O₅/ha. Se sugiere reducir la dosis de fondo.<br>")
    else:
        lines.append("✅ <strong>Fósforo equilibrado:</strong> Satisface los objetivos edáficos y de la planta.<br>")

    if k_balance < -20:
        lines.append(f"⚠️ <strong>Déficit de Potasio:</strong> Faltan {abs(k_balance):.1f} kg K₂O/ha. Seleccione una fórmula con mayor riqueza en potasa.<br>")
    elif k_balance > 30:
        lines.append(f"ℹ️ <strong>Exceso de Potasio:</strong> Superávit de {k_balance:.1f} kg K₂O/ha. Puede interferir en la asimilación del Magnesio.<br>")
    else:
        lines.append("✅ <strong>Potasio equilibrado:</strong> Óptimo aporte al complejo arcillo-húmico.<br>")

    lines.append("<br><strong>⚖️ Cumplimiento Zona Vulnerable a Nitratos (Andalucía):</strong><br>")
    if not vulnerable:
        lines.append('ℹ️ Marca "Zona Vulnerable a Nitratos" arriba si esta parcela está en ZVN para activar los avisos de cumplimiento.<br>')
    else:
        limit = legal_n_limit(cultivo_key, rendimiento)
        if limit is None:
            lines.append("ℹ️ No tengo el tope legal verificado para este cultivo; introduce/verifica el límite del programa de actuación vigente.<br>")
        elif n_total > limit + 0.05:
            lines.append(f"❌ <strong>Supera el tope legal de N:</strong> {n_total:.1f} kg N/ha aportados frente a un máximo de {limit:.1f} kg N/ha (Cuadro 4, BOJA nº214/2020).<br>")
        else:
            lines.append(f"✅ <strong>Dentro del tope legal de N:</strong> {n_total:.1f} / {limit:.1f} kg N/ha.<br>")

        fondo_es_inhibidor = key_fondo in ENTEC_INHIBIDOR_KEYS
        zvn = CULTIVO_ZVN_NOTES.get(cultivo_key)
        cap_aplica = zvn["cap30"] if zvn else True
        if not cap_aplica:
            lines.append("ℹ️ Este cultivo no tiene el tope genérico del 30% en fondo (revisa su regla específica más abajo).<br>")
        elif fondo_es_inhibidor:
            lines.append("✅ El abono de fondo lleva inhibidor de la nitrificación/liberación lenta: exento del tope del 30% en fondo.<br>")
        elif pct_n_fondo > 30:
            lines.append(f"❌ <strong>Supera el 30% de N en fondo:</strong> {pct_n_fondo}% del N total va en fondo con un producto sin inhibidor. Usa un ENTEC (inhibidor) o reduce la dosis de fondo.<br>")
        else:
            lines.append(f"✅ <strong>Dentro del 30% en fondo:</strong> {pct_n_fondo}% del N total.<br>")

        if zvn:
            lines.append(f"<span style='font-weight:normal;'><strong>Fondo:</strong> {zvn['fondoNote']}<br><strong>Cobertera:</strong> {zvn['coberteraNote']}</span><br>")
        else:
            lines.append('<span style=\'font-weight:normal;\'>Selecciona un "Cultivo Objetivo" con notas ZVN verificadas para ver las restricciones específicas de fondo y cobertera.</span><br>')

    if produccion_integrada:
        lines.append("<br><strong>🌱 Producción Integrada (adicional a ZVN):</strong><br>")
        pi = PI_NOTES.get(cultivo_key)
        if not pi:
            lines.append("ℹ️ No tengo el reglamento de Producción Integrada verificado para este cultivo (solo Trigo, Algodón, Olivar y Cítricos). Aplica igualmente tu reglamento específico de PI.<br>")
        else:
            pi_limit = pi_n_limit(pi, regimen_olivar)
            if pi_limit is not None:
                if n_total > pi_limit + 0.05:
                    lines.append(f"❌ <strong>Supera el límite de N de Producción Integrada:</strong> {n_total:.1f} kg N/ha aportados frente a un máximo de {pi_limit:.1f} kg N/ha.<br>")
                else:
                    lines.append(f"✅ <strong>Dentro del límite de N de Producción Integrada:</strong> {n_total:.1f} / {pi_limit:.1f} kg N/ha.<br>")
            if pi.get("nAbsLimitAgroambiental") is not None:
                ok = n_total <= pi["nAbsLimitAgroambiental"]
                lines.append(f"{'✅' if ok else '⚠️'} Límite de ayuda agroambiental: {n_total:.1f} / {pi['nAbsLimitAgroambiental']} kg N/ha (solo si te acoges a esa ayuda).<br>")
            if pi.get("pkAbsLimit") is not None:
                p_ok = p_total <= pi["pkAbsLimit"]
                k_ok = k_total <= pi["pkAbsLimit"]
                lines.append(
                    f"{'✅' if p_ok else '❌'} P₂O₅ aportado: {p_total:.1f} / {pi['pkAbsLimit']} UF/ha máx. &nbsp;&nbsp;"
                    f"{'✅' if k_ok else '❌'} K₂O aportado: {k_total:.1f} / {pi['pkAbsLimit']} UF/ha máx.<br>"
                )
            if pi.get("goteoLimits"):
                gl = pi["goteoLimits"]
                p_ok_g = p_total <= gl["p"]
                k_ok_g = k_total <= gl["k"]
                lines.append(
                    f"Límites PI en riego por goteo: N {gl['n']}, P₂O₅ {gl['p']}, K₂O {gl['k']}, MgO {gl['mg']} kg/ha. "
                    f"&nbsp;{'✅ P dentro' if p_ok_g else '❌ P excedido'} · {'✅ K dentro' if k_ok_g else '❌ K excedido'}<br>"
                )
            lines.append(f"<span style='font-weight:normal;'><strong>Fondo (PI):</strong> {pi['fondoNote']}<br><strong>Cobertera (PI):</strong> {pi['coberteraNote']}</span><br>")

    return "".join(lines)


def generar_diagnostico_suelo(p_recomendacion_detalle: str, k_recomendacion_detalle: str) -> str:
    return f"- {p_recomendacion_detalle}<br>- {k_recomendacion_detalle}"
