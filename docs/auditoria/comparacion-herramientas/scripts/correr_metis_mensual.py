"""Una serie MENSUAL real cargada en METIS tal como la recibiría la aplicación:
el parser infiere la resolución, el paso 0 agrega a máximos anuales y recién
ahí corre la batería de Etapa 1 (DECISIÓN 057 y 066). Sirve para comparar con
SAMHIA, que corre sus pruebas sobre los valores mensuales sin agregar.

    python correr_metis_mensual.py ruta/al/archivo.xlsx COLUMNA_FECHA COLUMNA_VALOR

El archivo de ejemplo (UCC-DAT-ESR-AH-001-26-00.xlsx, el que usa SAMHIA) no
se versiona: es un registro de la UCC que aportó el director.
"""

import csv
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[3] / "backend"))

from metis.core.pipeline.pipeline_etapa1 import ejecutar_etapa1  # noqa: E402
from metis.core.validacion.parser import parse_file  # noqa: E402

RES = AQUI.parent / "resultados"


def main(ruta: str, col_x: str, col_y: str) -> None:
    contenido = Path(ruta).read_bytes()
    datos = parse_file(contenido, Path(ruta).name, col_x, col_y)
    filas = []
    for mes in (6, 7):
        r1 = ejecutar_etapa1(
            datos.serie,
            "caudal_precipitacion",
            datos.resolucion_temporal,
            datos.timestamps,
            mes_inicio_anio=mes,
        )
        pruebas = {t.prueba: t for g in ("independencia", "homogeneidad", "tendencia", "atipicos") for t in getattr(r1, g)}
        filas.append(
            {
                "archivo": Path(ruta).name,
                "variable": col_y,
                "resolucion_inferida": datos.resolucion_temporal,
                "mes_inicio_anio": mes,
                "n_carga": len(datos.serie),
                "n_analizado": len(r1.serie_efectiva),
                "bloqueo": r1.contract.codigo_error or "",
                "warnings": ";".join(w.codigo for w in r1.warnings),
                **{f"{k}_veredicto": v.veredicto for k, v in pruebas.items()},
                "anderson_lags_fuera": pruebas["anderson"].explicacion.terminos["lags_fuera"] if pruebas.get("anderson") and pruebas["anderson"].explicacion else "",
                "nivel_independencia": r1.nivel_independencia,
                "nivel_homogeneidad": r1.nivel_homogeneidad,
                "nivel_confianza": r1.nivel_confianza,
            }
        )
    with open(RES / "metis_mensual.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(filas)
    for f in filas:
        print(f)


if __name__ == "__main__":
    main(*sys.argv[1:4])
