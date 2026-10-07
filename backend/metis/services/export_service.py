import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from metis.reportes.pdf import generar_pdf_analisis, nombre_archivo_pdf
from metis.services.analysis_service import get_analysis_by_id, simular_exclusion


class SimulacionNoDisponibleError(Exception):
    """El análisis persistido no tiene lo necesario para simular la exclusión
    de puntos: la serie analizada con sus años (`etapa1.datos`, ausente en
    registros anteriores a DECISIÓN 058) o una Etapa 1 que no quedó bloqueada
    por el contrato. El borde lo traduce a 400 CONTRACT_EXCLUSION_INVALID."""


async def exportar_pdf(
    analysis_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
    autor: str | None = None,
) -> tuple[bytes, str] | None:
    """PDF de un análisis persistido de CU-01 (DECISIÓN 075), generado en el
    momento y nunca guardado en disco (`constraints.md`, "PDF de exportación").

    Parte del mismo dict que `GET /history/{id}` — mismo guard de pertenencia,
    así que un análisis ajeno o inexistente devuelve None sin distinguir los
    dos casos. El maquetado (ReportLab + gráficos de matplotlib) es CPU-bound:
    corre en un hilo para no frenar el event loop mientras se arma.
    """
    detalle = await get_analysis_by_id(analysis_id=analysis_id, user_id=user_id, db=db)
    if detalle is None:
        return None
    pdf = await asyncio.to_thread(generar_pdf_analisis, detalle, autor)
    return pdf, nombre_archivo_pdf(detalle)


def _simular_desde_detalle(detalle: dict, indices_excluidos: list[int]) -> dict:
    """La misma simulación que `POST /analysis/simulate-exclusion` (DECISIÓN
    071), pero con la entrada tomada del análisis persistido y no del cliente:
    la serie analizada y sus años, la configuración y la distribución elegida.
    Del cliente solo llegan los índices — el PDF no puede mostrar una serie que
    no sea la del análisis."""
    etapa1 = detalle.get("etapa1") or {}
    datos = etapa1.get("datos") or {}
    serie = datos.get("serie_efectiva")
    timestamps = datos.get("timestamps_efectivos")
    if (
        (etapa1.get("contract") or {}).get("bloqueante")
        or not serie
        or not timestamps
        or len(timestamps) != len(serie)
    ):
        raise SimulacionNoDisponibleError(
            "Este análisis no tiene registrada la serie analizada con sus años: "
            "no se puede simular la exclusión de puntos."
        )

    seleccion = (detalle.get("etapa2") or {}).get("seleccion")
    return simular_exclusion(
        serie=serie,
        anios=[t["anio"] for t in timestamps],
        tipo_variable=detalle["tipo_variable"],
        cramer_particion=(detalle.get("configuracion") or {}).get(
            "cramer_particion", "default"
        ),
        indices_excluidos=indices_excluidos,
        etapas=[2 if e == "2" else 1 for e in detalle.get("etapas") or ["1"]],
        seleccion=(
            {
                "distribucion": seleccion["distribucion"],
                "metodo": seleccion["metodo"],
                "periodos_retorno": seleccion["periodos_retorno"],
            }
            if seleccion
            else None
        ),
    )


async def exportar_pdf_simulacion(
    analysis_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
    indices_excluidos: list[int],
    autor: str | None = None,
) -> tuple[bytes, str] | None:
    """PDF del análisis registrado más los resultados sin los puntos excluidos
    (DECISIÓN 075, addendum). La simulación se recalcula acá, no se guarda y no
    toca `decisiones` (DECISIÓN 062, "explorar no es decidir").

    None si el análisis no existe o no es del usuario. Levanta
    `SimulacionNoDisponibleError` si el análisis no se puede simular y
    `ExclusionInvalidaError` (core/) si los índices no aplican a la serie.
    """
    detalle = await get_analysis_by_id(analysis_id=analysis_id, user_id=user_id, db=db)
    if detalle is None:
        return None
    simulacion = await asyncio.to_thread(
        _simular_desde_detalle, detalle, indices_excluidos
    )
    pdf = await asyncio.to_thread(
        generar_pdf_analisis, detalle, autor, None, simulacion
    )
    return pdf, nombre_archivo_pdf(detalle, simulacion=True)
