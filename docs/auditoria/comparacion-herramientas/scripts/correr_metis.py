"""Corre el motor de METIS (backend/metis/core) sobre las 9 series de la tesis
y deja los resultados en resultados/metis_*.csv. Es el mismo código que usa la
aplicación: ejecutar_etapa1() + ejecutar_etapa2() + calcular_eventos_diseno().

Correr desde la raíz del repo, con el entorno del backend:
    python docs/auditoria/comparacion-herramientas/scripts/correr_metis.py
"""

import csv
import math
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[3] / "backend"))

from series import estaciones  # noqa: E402

from metis.core.estadistica_descriptiva.descriptive import calcular_descriptiva  # noqa: E402
from metis.core.etapa1.homogeneity import calcular_cramer  # noqa: E402
from metis.core.etapa2.design_events import calcular_eventos_diseno  # noqa: E402
from metis.core.pipeline.pipeline_etapa1 import ejecutar_etapa1  # noqa: E402
from metis.core.pipeline.pipeline_etapa2 import (  # noqa: E402
    _DISTRIBUCIONES,
    ejecutar_etapa2,
)

RES = AQUI.parent / "resultados"
PERIODOS = [2, 5, 10, 20, 25, 50, 100, 200, 500]
MODULOS = dict(_DISTRIBUCIONES)


def _prueba(r1, grupo: str, nombre: str):
    return next(t for t in getattr(r1, grupo) if t.prueba == nombre)


def main() -> None:
    RES.mkdir(exist_ok=True)
    filas_series, filas_e1, filas_q, filas_par = [], [], [], []
    for e in estaciones():
        serie = e["serie"]
        for i, v in enumerate(serie):
            filas_series.append({"estacion": e["clave"], "i": i + 1, "valor": v})
        ts = [f"{1938 + i}-07-01" for i in range(len(serie))]
        r1 = ejecutar_etapa1(serie, "caudal_precipitacion", "anual", ts)
        bloqueo = r1.contract.codigo_error if r1.contract.bloqueante else ""
        fila = {"estacion": e["clave"], "n": len(serie), "bloqueo_contrato": bloqueo}
        x = np.array(serie, dtype=float)
        d = calcular_descriptiva(serie)
        fila.update(
            {
                "media": d.media,
                "desvio": d.desvio_estandar,
                "asimetria_g": d.coef_asimetria,
                "curtosis_k": d.curtosis_no_sesgada,
            }
        )
        if not bloqueo:
            h = _prueba(r1, "homogeneidad", "helmert")
            t = _prueba(r1, "homogeneidad", "t_student")
            a = _prueba(r1, "independencia", "anderson")
            w = _prueba(r1, "independencia", "wald_wolfowitz")
            mk = _prueba(r1, "tendencia", "mann_kendall")
            ks = _prueba(r1, "tendencia", "kolmogorov_smirnov")
            ch = _prueba(r1, "atipicos", "chow")
            cr = _prueba(r1, "homogeneidad", "cramer").explicacion.terminos
            fila.update(
                {
                    "helmert_s_menos_c": h.estadistico,
                    "t_student": t.estadistico,
                    "t_student_critico": t.valor_critico,
                    "cramer_tw1": cr.get("t_w1"),
                    "cramer_tw2": cr.get("t_w2"),
                    "anderson_lags_fuera": a.explicacion.terminos["lags_fuera"],
                    "anderson_k_max": a.explicacion.terminos["k_max"],
                    "anderson_r1": a.explicacion.desglose[0]["r_k"],
                    "ww_rachas": w.explicacion.terminos["r"],
                    "ww_z": w.estadistico,
                    "mk_z": mk.estadistico,
                    "ks_z": ks.estadistico,
                    "chow_estadistico": ch.estadistico,
                    "chow_kn": ch.valor_critico,
                    "chow_veredicto": ch.veredicto,
                    "nivel_confianza": r1.nivel_confianza,
                    "nivel_independencia": r1.nivel_independencia,
                    "nivel_homogeneidad": r1.nivel_homogeneidad,
                    "anderson_veredicto": a.veredicto,
                    "ww_veredicto": w.veredicto,
                    "helmert_veredicto": h.veredicto,
                    "t_student_veredicto": t.veredicto,
                    "cramer_veredicto": _prueba(r1, "homogeneidad", "cramer").veredicto,
                    "mk_veredicto": mk.veredicto,
                    "ks_veredicto": ks.veredicto,
                }
            )
        else:
            # METIS no analiza series de menos de 10 datos (único bloqueo por
            # longitud). Para poder comparar las pruebas igual, se corren las
            # funciones de core/ directamente, fuera del pipeline.
            cr = calcular_cramer(serie).explicacion.terminos
            fila.update({"cramer_tw1": cr.get("t_w1"), "cramer_tw2": cr.get("t_w2")})
        filas_e1.append(fila)

        # Etapa 2: la grilla completa, aunque Etapa 1 haya rechazado la serie
        # (la tesis también publica los parámetros "con fines académicos").
        r2 = ejecutar_etapa2(x, tiene_ceros=bool(np.any(x == 0)))
        for d in r2.ranking:
            for m in d.metodos:
                filas_par.append(
                    {
                        "estacion": e["clave"],
                        "distribucion": d.distribucion,
                        "metodo": m.metodo,
                        "status": m.status,
                        "eea": m.eea,
                        "parametros": ";".join(f"{k}={v:.6g}" for k, v in (m.parametros or {}).items()),
                    }
                )
                if m.status != "ok" or not m.parametros:
                    continue
                for ev in calcular_eventos_diseno(MODULOS[d.distribucion], m.parametros, PERIODOS):
                    filas_q.append(
                        {
                            "estacion": e["clave"],
                            "distribucion": d.distribucion,
                            "metodo": m.metodo,
                            "T": ev.periodo_retorno,
                            "metis": ev.valor,
                        }
                    )
    for nombre, filas in [
        ("series", filas_series),
        ("metis_etapa1", filas_e1),
        ("metis_parametros", filas_par),
        ("metis_cuantiles", filas_q),
    ]:
        claves = list(dict.fromkeys(k for f in filas for k in f))
        with open(RES / f"{nombre}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=claves, lineterminator="\n")
            w.writeheader()
            w.writerows(filas)
        print(f"{nombre}.csv: {len(filas)} filas")


if __name__ == "__main__":
    main()
