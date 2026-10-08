"""Lectura de las 9 series de la tesis y de los valores que publica la tesis
(planilla Excel de Facundo Ganancias), desde las fichas de regresión del repo.

Fuente: docs/auditoria/regresion/regresion-pipeline/est_0X_*-pipeline.md, que
transcriben las tablas de la tesis (Sheet 1 a 3). No se usa ningún resultado
de METIS de esas fichas: solo la serie y los valores "esperados" de la tesis.
"""

import glob
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
FICHAS = RAIZ / "docs/auditoria/regresion/regresion-pipeline"

NOMBRES = {
    "est_01": "Alpa Corral - Río Barrancas",
    "est_02": "Vado de Río Seco - Río Barrancas",
    "est_03": "La Tapa - Río Las Cañitas",
    "est_04": "Las Tapias - Río Las Tapias",
    "est_05": "Piedra Blanca - Río Piedra Blanca",
    "est_06": "Las Tapias - Río San Bartolomé",
    "est_07": "Tincunaco - Río Chocancharagua",
    "est_08": "Ume Pay - Río Grande",
    "est_09": "La Suela - Río La Suela",
}

# Columnas de la tabla "Cuantiles esperados" de cada ficha -> (distribución,
# método) de METIS. None: la combinación no existe en METIS (Gamma 3p por
# Momentos de Probabilidad Pesada: la tesis no desarrolla sus ecuaciones,
# pendiente de Facundo).
MODELOS_TESIS = {
    "est_01": [None, ("gamma2p", "ml")],
    "est_02": [("exponencial_beta", "momentos"), ("lognormal3p", "mv")],
    "est_03": [("logpearson3", "momentos_indirecto"), ("gve", "mv")],
    "est_04": [("logpearson3", "momentos_indirecto"), ("gve", "mv")],
    "est_05": [("lognormal3p", "mv"), ("gve", "mv")],
    "est_06": [("exponencial_x0_beta", "mv"), None],
    "est_07": [("lognormal2p", "momentos"), ("gumbel", "ml")],
    "est_08": [("gumbel", "ml"), None],
    "est_09": [("uniforme", "momentos"), ("normal", "ml")],
}


def _num(texto: str) -> float | None:
    m = re.search(r"-?\d+(?:[.,]\d+)?", texto.replace("±", ""))
    return float(m.group(0).replace(",", ".")) if m else None


def _seccion(txt: str, titulo: str) -> str:
    i = txt.find(titulo)
    if i < 0:
        return ""
    j = txt.find("\n### ", i + len(titulo))
    return txt[i : j if j > 0 else len(txt)]


def _fila(seccion: str, rotulo: str) -> float | None:
    for linea in seccion.splitlines():
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) >= 2 and celdas[0].startswith(rotulo):
            return _num(celdas[1])
    return None


def leer_estacion(ruta: str) -> dict:
    txt = open(ruta, encoding="utf-8").read()
    clave = Path(ruta).name[:6]
    m = re.search(r"^serie\s*=\s*\[(.*?)^\]", txt, re.S | re.M)
    valores = re.findall(r"-?\d+(?:\.\d+)?", re.sub(r"#.*", "", m.group(1)))
    serie = [float(v) for v in valores]

    homog = _seccion(txt, "### Etapa 1 — Homogeneidad (Sheet 2)")
    indep = _seccion(txt, "### Etapa 1 — Independencia (Sheet 2)")
    cramer = homog[homog.find("#### Cramer") :]
    tesis_e1 = {
        "helmert_s_menos_c": _fila(homog, "Estadístico (S-C)"),
        "t_student": _fila(homog, "Estadístico t"),
        "cramer_tw1": _fila(cramer, "t calculado sg. 1"),
        "cramer_tw2": _fila(cramer, "t calculado sg. 2"),
        "anderson_lags_fuera": _fila(indep, "N° puntos fuera de bandas"),
        "ww_rachas": _fila(indep, "R (rachas observadas)"),
        "ww_z": _fila(indep, "Estadístico Z"),
    }

    desc = _seccion(txt, "### Estadística descriptiva esperada")
    tesis_desc = {
        "media": _fila(desc, "Media"),
        "desvio": _fila(desc, "Desvío"),
        "asimetria_g": _fila(desc, "Asimetría No Sesgada"),
        "curtosis_k": _fila(desc, "Curtosis No Sesgada"),
    }

    cuant = _seccion(txt, "### Etapa 2 — Cuantiles esperados")
    filas = [
        [c.strip() for c in l.strip().strip("|").split("|")]
        for l in cuant.splitlines()
        if l.strip().startswith("|") and not set(l.strip()) <= set("|-: ")
    ]
    encabezado, datos = filas[0], filas[1:]
    columnas = encabezado[1:3]
    cuantiles = []
    for fila in datos:
        t = _num(fila[0])
        for j, col in enumerate(columnas):
            v = _num(fila[1 + j]) if len(fila) > 1 + j else None
            cuantiles.append({"T": t, "columna_tesis": col, "modelo": MODELOS_TESIS[clave][j], "tesis": v})
    return {
        "clave": clave,
        "nombre": NOMBRES[clave],
        "serie": serie,
        "tesis_etapa1": tesis_e1,
        "tesis_descriptiva": tesis_desc,
        "tesis_cuantiles": cuantiles,
    }


def estaciones() -> list[dict]:
    return [leer_estacion(f) for f in sorted(glob.glob(str(FICHAS / "est_0*-pipeline.md")))]


if __name__ == "__main__":
    for e in estaciones():
        print(e["clave"], len(e["serie"]), e["tesis_etapa1"], len(e["tesis_cuantiles"]))
