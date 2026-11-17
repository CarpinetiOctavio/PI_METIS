"""Resumen de calidad del pipeline (DECISIÓN 077, B1a del plan del TP de Calidad).

Lee los reportes que dejan los jobs de CI y escribe:
- un resumen en Markdown por stdout (el job lo agrega a $GITHUB_STEP_SUMMARY);
- con `--json`, los mismos números para `metricas.json`, que sube como artefacto: los números del informe del TP salen de
  acá, no de corridas locales.

Solo biblioteca estándar: corre en el runner sin instalar nada.

    python scripts/ci_resumen.py          > resumen en Markdown (desde la raíz del repo)
    python scripts/ci_resumen.py --json   > los mismos números en JSON

Lee siempre de `reportes/`, donde el job descargó los artefactos de los otros jobs (sin
rutas por línea de comandos: no hay nada que validar):
    backend/coverage.xml, backend/junit-backend.xml,
    frontend/coverage/coverage-summary.json, frontend/junit-frontend.xml,
    jscpd/jscpd-report.json, diff-cover-backend.md, diff-cover-frontend.md (los dos últimos solo en PR),
    radon/cc.json, radon/mi.json, radon/raw.json (complejidad del backend, B11).
El job guarda la salida --json como reportes/metricas.json.
"""

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

UMBRAL_COBERTURA = 80.0
UMBRAL_DUPLICACION = 5.0
# radon: CC de 1 a 10 es rango A o B ("simple" a "bien estructurada"); desde 11, C en adelante.
UMBRAL_CC = 10
FUNCIONES_MAS_COMPLEJAS = 5


def _junit(ruta: Path) -> dict | None:
    if not ruta.is_file():
        return None
    raiz = ET.parse(ruta).getroot()
    suites = [raiz] if raiz.tag == "testsuite" else list(raiz.iter("testsuite"))
    total = sum(int(s.get("tests", 0)) for s in suites)
    fallas = sum(int(s.get("failures", 0)) + int(s.get("errors", 0)) for s in suites)
    omitidos = sum(int(s.get("skipped", 0)) for s in suites)
    return {"total": total, "fallas": fallas, "omitidos": omitidos}


def _cobertura_backend(ruta: Path) -> dict | None:
    if not ruta.is_file():
        return None
    raiz = ET.parse(ruta).getroot()
    return {
        "sentencias": [int(raiz.get("lines-covered")), int(raiz.get("lines-valid"))],
        "ramas": [int(raiz.get("branches-covered")), int(raiz.get("branches-valid"))],
    }


def _cobertura_frontend(ruta: Path) -> dict | None:
    if not ruta.is_file():
        return None
    total = json.loads(ruta.read_text(encoding="utf-8"))["total"]
    return {
        "sentencias": [total["statements"]["covered"], total["statements"]["total"]],
        "ramas": [total["branches"]["covered"], total["branches"]["total"]],
    }


def _duplicacion(ruta: Path) -> dict | None:
    if not ruta.is_file():
        return None
    total = json.loads(ruta.read_text(encoding="utf-8"))["statistics"]["total"]
    return {
        "porcentaje_lineas": total["percentage"],
        "lineas_duplicadas": total["duplicatedLines"],
        "lineas": total["lines"],
        "clones": total["clones"],
    }


def _bloques_cc(cc: dict) -> list[dict]:
    """Funciones y métodos, con el archivo. radon lista cada método también dentro de su clase, y la
    clase con una complejidad propia: se saltean las clases para no contar dos veces."""
    return [
        {**b, "archivo": archivo}
        for archivo, items in cc.items()
        if isinstance(items, list)  # radon informa un error de parseo como dict
        for b in items
        if b["type"] != "class"
    ]


def _complejidad(carpeta: Path) -> dict | None:
    rutas = {n: carpeta / f"{n}.json" for n in ("cc", "mi", "raw")}
    if not all(r.is_file() for r in rutas.values()):
        return None
    cc, mi, raw = (json.loads(r.read_text(encoding="utf-8")) for r in rutas.values())

    bloques = _bloques_cc(cc)
    por_rango_cc: dict[str, int] = {}
    for b in bloques:
        por_rango_cc[b["rank"]] = por_rango_cc.get(b["rank"], 0) + 1
    mas_complejas = sorted(bloques, key=lambda b: b["complexity"], reverse=True)

    por_rango_mi: dict[str, int] = {}
    for v in mi.values():
        por_rango_mi[v["rank"]] = por_rango_mi.get(v["rank"], 0) + 1
    menor_mi = min(mi.items(), key=lambda kv: kv[1]["mi"])

    totales = {
        k: sum(v[k] for v in raw.values()) for k in ("loc", "sloc", "comments", "multi")
    }
    return {
        "funciones": len(bloques),
        "cc_promedio": round(sum(b["complexity"] for b in bloques) / len(bloques), 2)
        if bloques
        else 0.0,
        "cc_por_rango": dict(sorted(por_rango_cc.items())),
        "cc_mayor_a_umbral": sum(1 for b in bloques if b["complexity"] > UMBRAL_CC),
        "mas_complejas": [
            {"funcion": f"{b['archivo']}::{b['name']}", "cc": b["complexity"]}
            for b in mas_complejas[:FUNCIONES_MAS_COMPLEJAS]
        ],
        "archivos": len(mi),
        "mi_por_rango": dict(sorted(por_rango_mi.items())),
        "mi_menor": {"archivo": menor_mi[0], "mi": round(menor_mi[1]["mi"], 2)},
        "loc": totales["loc"],
        "sloc": totales["sloc"],
        "lineas_comentario": totales["comments"] + totales["multi"],
    }


def _pct(par: list[int]) -> float:
    cubiertas, total = par
    return round(100.0 * cubiertas / total, 2) if total else 100.0


def _estado(ok: bool) -> str:
    return "✅" if ok else "❌"


def construir(reportes: Path) -> tuple[dict, str]:
    metricas = {
        "tests_backend": _junit(reportes / "backend" / "junit-backend.xml"),
        "tests_frontend": _junit(reportes / "frontend" / "junit-frontend.xml"),
        "cobertura_backend": _cobertura_backend(reportes / "backend" / "coverage.xml"),
        "cobertura_frontend": _cobertura_frontend(
            reportes / "frontend" / "coverage" / "coverage-summary.json"
        ),
        "duplicacion": _duplicacion(reportes / "jscpd" / "jscpd-report.json"),
        "complejidad_backend": _complejidad(reportes / "radon"),
    }

    lineas = ["## Calidad del pipeline", ""]

    lineas += [
        "### Tests",
        "",
        "| Suite | Total | Fallas | Omitidos |",
        "|---|---|---|---|",
    ]
    for nombre, clave in (
        ("Backend (pytest)", "tests_backend"),
        ("Frontend (Vitest)", "tests_frontend"),
    ):
        t = metricas[clave]
        lineas.append(
            f"| {nombre} | {t['total']} | {t['fallas']} | {t['omitidos']} |"
            if t
            else f"| {nombre} | sin reporte | | |"
        )

    lineas += [
        "",
        "### Cobertura del código existente",
        "",
        f"Meta: {UMBRAL_COBERTURA:.0f} % (Nivel 3).",
        "",
        "| | Sentencias | Decisiones (ramas) |",
        "|---|---|---|",
    ]
    for nombre, clave in (
        ("Backend", "cobertura_backend"),
        ("Frontend", "cobertura_frontend"),
    ):
        c = metricas[clave]
        if not c:
            lineas.append(f"| {nombre} | sin reporte | |")
            continue
        s, r = _pct(c["sentencias"]), _pct(c["ramas"])
        lineas.append(
            f"| {nombre} | {_estado(s >= UMBRAL_COBERTURA)} {s} % "
            f"({c['sentencias'][0]}/{c['sentencias'][1]}) "
            f"| {_estado(r >= UMBRAL_COBERTURA)} {r} % ({c['ramas'][0]}/{c['ramas'][1]}) |"
        )

    d = metricas["duplicacion"]
    lineas += ["", "### Duplicación (jscpd)", ""]
    if d:
        lineas.append(
            f"{_estado(d['porcentaje_lineas'] <= UMBRAL_DUPLICACION)} {d['porcentaje_lineas']} % de "
            f"líneas duplicadas ({d['lineas_duplicadas']}/{d['lineas']}, {d['clones']} clones). "
            f"Umbral: {UMBRAL_DUPLICACION:.0f} %."
        )
    else:
        lineas.append("sin reporte")

    k = metricas["complejidad_backend"]
    lineas += ["", "### Complejidad del backend (radon, informativo)", ""]
    if k:
        rangos_cc = ", ".join(f"{r}: {n}" for r, n in k["cc_por_rango"].items())
        rangos_mi = ", ".join(f"{r}: {n}" for r, n in k["mi_por_rango"].items())
        lineas += [
            f"- {k['sloc']} líneas de código ({k['loc']} en total, {k['lineas_comentario']} de comentarios).",
            f"- Complejidad ciclomática: {k['funciones']} funciones, promedio {k['cc_promedio']}; "
            f"por rango {rangos_cc}. Con CC > {UMBRAL_CC}: {k['cc_mayor_a_umbral']}.",
            f"- Índice de mantenibilidad: {k['archivos']} archivos; por rango {rangos_mi}. "
            f"El menor: `{k['mi_menor']['archivo']}` ({k['mi_menor']['mi']}).",
            "",
            "| Función más compleja | CC |",
            "|---|---|",
        ]
        lineas += [f"| `{f['funcion']}` | {f['cc']} |" for f in k["mas_complejas"]]
    else:
        lineas.append("sin reporte")

    for lado in ("backend", "frontend"):
        md = reportes / f"diff-cover-{lado}.md"
        if md.is_file():
            lineas += ["", f"### Cobertura del código nuevo ({lado}, diff-cover)", ""]
            lineas.append(md.read_text(encoding="utf-8").strip())

    return metricas, "\n".join(lineas) + "\n"


def main() -> int:
    metricas, markdown = construir(Path("reportes"))
    # Sin escritura de archivos: el job redirige la salida (resumen o, con --json, metricas.json).
    salida = (
        json.dumps(metricas, indent=2, ensure_ascii=False) + "\n"
        if "--json" in sys.argv[1:]
        else markdown
    )
    # UTF-8 explícito: la consola de Windows (cp1252) no codifica los íconos del resumen.
    sys.stdout.buffer.write(salida.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
