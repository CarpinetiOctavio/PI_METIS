from metis.core.contract import validar_contrato
from metis.core.descriptive import calcular_descriptiva
from metis.core.homogeneity import (
    calcular_cramer,
    calcular_helmert,
    calcular_t_student,
    determinar_nivel_homogeneidad,
)
from metis.core.independence import (
    calcular_anderson,
    calcular_wald_wolfowitz,
    determinar_nivel_independencia,
)
from metis.core.outliers import calcular_chow
from metis.core.trend import (
    calcular_ks_tendencia,
    calcular_mann_kendall,
    determinar_warnings_tendencia,
)
from metis.core.types import Etapa1Result, WarningItem
from metis.core.utils import filtrar_numericos


def ejecutar_etapa1(
    serie: list,
    tipo_variable: str,
    resolucion_temporal: str | None = None,
    timestamps: list | None = None,
    cramer_particion: dict | str = "default",
) -> Etapa1Result:

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
            warnings=contract.warnings,
        )

    # Serie filtrada — solo valores numéricos para todas las pruebas
    valores_numericos = filtrar_numericos(serie)
    warnings: list[WarningItem] = list(contract.warnings)

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
    if cramer_particion == "default":
        n1 = int(n_total * 0.60)
        n2 = int(n_total * 0.30)
    else:
        n1 = int(n_total * cramer_particion["n1_pct"] / 100)
        n2 = int(n_total * cramer_particion["n2_pct"] / 100)

    helmert = calcular_helmert(valores_numericos)
    t_student = calcular_t_student(valores_numericos, n1=n1, n2=n2)
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
    )
