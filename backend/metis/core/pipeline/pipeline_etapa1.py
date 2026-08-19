from metis.core.estadistica_descriptiva.descriptive import calcular_descriptiva
from metis.core.etapa1.homogeneity import (
    calcular_cramer,
    calcular_helmert,
    calcular_t_student,
    determinar_nivel_homogeneidad,
)
from metis.core.etapa1.independence import (
    calcular_anderson,
    calcular_wald_wolfowitz,
    determinar_nivel_independencia,
)
from metis.core.etapa1.outliers import calcular_chow
from metis.core.etapa1.trend import (
    calcular_ks_tendencia,
    calcular_mann_kendall,
    determinar_warnings_tendencia,
)
from metis.core.types import ContractResult, Etapa1Result, WarningItem
from metis.core.utils import filtrar_numericos
from metis.core.validacion.aggregation import (
    MOTIVO_HUECO_INTERIOR,
    AgregacionResult,
    agregar_a_maximos_anuales,
)
from metis.core.validacion.contract import timestamps_desordenados, validar_contrato


def _warnings_de_agregacion(agregacion: AgregacionResult) -> list[WarningItem]:
    extremos = [
        p for p in agregacion.periodos_descartados if p.motivo != MOTIVO_HUECO_INTERIOR
    ]
    interiores = [
        p for p in agregacion.periodos_descartados if p.motivo == MOTIVO_HUECO_INTERIOR
    ]

    warnings: list[WarningItem] = []

    if extremos:
        detalle = ", ".join(
            f"{p.anio} ({p.meses_presentes}/12 meses)" for p in extremos
        )
        periodo_efectivo = (
            f"{agregacion.timestamps[0]}–{agregacion.timestamps[-1]}"
            if agregacion.timestamps
            else "ningún año completo"
        )
        warnings.append(
            WarningItem(
                codigo="CONTRACT_PARTIAL_YEARS_TRIMMED",
                nivel="normal",
                descripcion=(
                    f"Se recortaron {len(extremos)} año(s) parcial(es) en los "
                    f"extremos del registro: {detalle}. Período efectivo del "
                    f"análisis: {periodo_efectivo}."
                ),
            )
        )

    if interiores:
        anios = ", ".join(str(p.anio) for p in interiores)
        warnings.append(
            WarningItem(
                codigo="CONTRACT_INCOMPLETE_YEARS_DISCARDED",
                nivel="normal",
                descripcion=(
                    f"Se descartaron {len(interiores)} año(s) incompleto(s) "
                    f"dentro del registro: {anios}."
                ),
            )
        )

    return warnings


def ejecutar_etapa1(
    serie: list,
    tipo_variable: str,
    resolucion_temporal: str | None = None,
    timestamps: list | None = None,
    cramer_particion: dict | str = "default",
    mes_inicio_anio: int = 7,
) -> Etapa1Result:

    # Capturados ANTES del paso 0 — PR 3 del plan de cierre de pendientes
    # no-test (DECISIÓN 058). serie/timestamps/resolucion_temporal se
    # reasignan más abajo si hubo agregación; estas tres variables guardan
    # los valores de entrada tal como llegaron, para que Etapa1Result
    # pueda exponer la serie original sin que services/ tenga que volver
    # a cargar el archivo.
    serie_original = serie
    timestamps_originales = timestamps
    resolucion_original = resolucion_temporal

    # ── 0a. Orden cronológico (Bloque H3, plan post-avance — DECISIÓN 030) ────
    # Segunda excepción al principio "detecta y advierte, no bloquea"
    # (la primera es n<10) — y tiene que evaluarse sobre los timestamps
    # CRUDOS, antes de cualquier otra cosa, incluida la agregación mensual
    # de más abajo. Dos motivos:
    #
    # (1) calcular_cramer() toma arr[-n_w:] asumiendo que son los últimos
    #     datos cronológicos del registro — con la serie desordenada el
    #     estadístico no mide lo que dice medir. Estructuralmente más
    #     cerca de n<10 (falta la condición mínima para que el número
    #     tenga sentido) que de un warning normal, donde el resultado
    #     sigue siendo válido aunque subóptimo.
    # (2) agregar_a_maximos_anuales() usa timestamps[0]/timestamps[-1]
    #     para fijar el rango de períodos a agregar (range(periodo_inicio,
    #     periodo_fin+1)) — con el archivo desordenado puede EXCLUIR
    #     períodos reales del registro en silencio: verificado que 3 años
    #     completos (36 meses reales) con dos bloques anuales invertidos
    #     entre sí agregan solo 2 años, con periodos_descartados=[] (ni
    #     siquiera un warning) — el tercer año simplemente desaparece.
    #     Evaluar el orden DESPUÉS de agregar no sirve para este caso:
    #     agregar_a_maximos_anuales() construye sus timestamps con
    #     range(), siempre ascendentes por construcción — cualquier
    #     desorden de origen ya se perdió para cuando llegarían a
    #     validar_contrato().
    #
    # Verificado antes de implementar (paso 1 de DECISIÓN 030) que ninguna
    # de las 9 series de referencia de la Fase 4 tiene desorden
    # cronológico — este cambio no invalida ningún resultado ya auditado.
    if timestamps is not None and timestamps_desordenados(timestamps):
        return Etapa1Result(
            contract=ContractResult(
                bloqueante=True,
                codigo_error="CONTRACT_WRONG_ORDER",
                warnings=[],
            ),
            descriptive=None,
            independencia=[],
            homogeneidad=[],
            tendencia=[],
            atipicos=[],
            nivel_independencia=None,
            nivel_homogeneidad=None,
            nivel_confianza="rechazado",
            warnings=[],
            serie_efectiva=filtrar_numericos(serie),
            timestamps_efectivos=timestamps,
            serie_original=serie_original,
            timestamps_originales=timestamps_originales,
            resolucion_original=resolucion_original,
        )

    # ── 0. Agregación temporal (Bloque F4) ────────────────────────────────────
    # Antes de validar_contrato() — así el conteo de la regla de n opera ya
    # sobre la serie agregada, y una serie mensual nunca corre la batería
    # estadística sobre los valores crudos (F2.1). Con resolucion_temporal
    # != "mensual" (incluido None) esta rama no hace nada — comportamiento
    # idéntico al de antes de este bloque.
    warnings_agregacion: list[WarningItem] = []
    if resolucion_temporal == "mensual":
        agregacion = agregar_a_maximos_anuales(serie, timestamps, mes_inicio_anio)
        serie = agregacion.serie
        timestamps = agregacion.timestamps
        resolucion_temporal = "anual"  # ya agregada — el resto del pipeline
        # la trata como cualquier serie anual, sin saber que hubo agregación
        warnings_agregacion = _warnings_de_agregacion(agregacion)

    # ── 1. Contrato de datos ──────────────────────────────────────────────────
    contract = validar_contrato(
        serie=serie,
        tipo_variable=tipo_variable,
        resolucion_temporal=resolucion_temporal,
        timestamps=timestamps,
    )

    if contract.bloqueante:
        return Etapa1Result(
            contract=contract,
            descriptive=None,
            independencia=[],
            homogeneidad=[],
            tendencia=[],
            atipicos=[],
            nivel_independencia=None,
            nivel_homogeneidad=None,
            nivel_confianza="rechazado",
            warnings=warnings_agregacion + contract.warnings,
            serie_efectiva=filtrar_numericos(serie),
            timestamps_efectivos=timestamps,
            serie_original=serie_original,
            timestamps_originales=timestamps_originales,
            resolucion_original=resolucion_original,
        )

    # Serie filtrada — solo valores numéricos para todas las pruebas
    valores_numericos = filtrar_numericos(serie)
    warnings: list[WarningItem] = warnings_agregacion + list(contract.warnings)

    # ── 2. Estadística descriptiva ────────────────────────────────────────────
    descriptive = calcular_descriptiva(valores_numericos)

    # ── 3. Independencia ──────────────────────────────────────────────────────
    anderson = calcular_anderson(valores_numericos)
    wald = calcular_wald_wolfowitz(valores_numericos)
    nivel_independencia, w_independencia = determinar_nivel_independencia(
        anderson, wald
    )
    warnings.extend(w_independencia)

    # ── 4. Homogeneidad ───────────────────────────────────────────────────────
    n_total = len(valores_numericos)
    # t-Student exige partición mitad/mitad (III-8) — distinta de la partición
    # 60%/30% de Cramer. calcular_cramer resuelve su propia partición
    # internamente vía cramer_particion, no depende de n1_t/n2_t.
    n1_t = n_total // 2
    n2_t = n_total - n1_t

    helmert = calcular_helmert(valores_numericos)
    t_student = calcular_t_student(valores_numericos, n1=n1_t, n2=n2_t)
    cramer = calcular_cramer(valores_numericos, particion=cramer_particion)
    nivel_homogeneidad, w_homogeneidad = determinar_nivel_homogeneidad(
        helmert, t_student, cramer
    )
    warnings.extend(w_homogeneidad)

    # ── 5. Tendencia ──────────────────────────────────────────────────────────
    mann_kendall = calcular_mann_kendall(valores_numericos)
    ks = calcular_ks_tendencia(valores_numericos)
    warnings.extend(determinar_warnings_tendencia(mann_kendall, ks))

    # ── 6. Atípicos (Chow) ────────────────────────────────────────────────────
    chow = calcular_chow(valores_numericos, tipo_variable=tipo_variable)
    if chow.warning_codigo == "TEST_WARNING_OUTLIER_DETECTED":
        warnings.append(
            WarningItem(
                codigo="TEST_WARNING_OUTLIER_DETECTED",
                nivel="normal",
                descripcion="Chow detectó un dato atípico — decisión pendiente del usuario",
            )
        )

    # ── Nivel de confianza global ─────────────────────────────────────────────
    if any(w.nivel == "critico" for w in warnings):
        nivel_confianza = "con_warnings"
    elif warnings:
        nivel_confianza = "con_warnings"
    else:
        nivel_confianza = "validado"

    return Etapa1Result(
        contract=contract,
        descriptive=descriptive,
        independencia=[anderson, wald],
        homogeneidad=[helmert, t_student, cramer],
        tendencia=[mann_kendall, ks],
        atipicos=[chow],
        nivel_independencia=nivel_independencia,
        nivel_homogeneidad=nivel_homogeneidad,
        nivel_confianza=nivel_confianza,
        warnings=warnings,
        serie_efectiva=valores_numericos,
        timestamps_efectivos=timestamps,
        serie_original=serie_original,
        timestamps_originales=timestamps_originales,
        resolucion_original=resolucion_original,
    )
