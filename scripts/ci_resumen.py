"""Resumen de calidad del pipeline (DECISIÓN 077, B1a del plan del TP de Calidad).

Lee los reportes que dejan los jobs de CI y escribe:
- un resumen en Markdown por stdout (el job lo agrega a $GITHUB_STEP_SUMMARY);
- `metricas.json` con los mismos números, como artefacto: los números del informe del TP salen de
  acá, no de corridas locales.

Solo biblioteca estándar: corre en el runner sin instalar nada.

    python scripts/ci_resumen.py --reportes <dir> [--salida-json metricas.json]

<dir> es donde el job descargó los artefactos de los otros jobs:
    backend/coverage.xml, backend/junit-backend.xml,
    frontend/coverage/coverage-summary.json, frontend/junit-frontend.xml,
    jscpd/jscpd-report.json, diff-cover-backend.md, diff-cover-frontend.md (los dos últimos solo en PR).
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

UMBRAL_COBERTURA = 80.0
UMBRAL_DUPLICACION = 5.0


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

    for lado in ("backend", "frontend"):
        md = reportes / f"diff-cover-{lado}.md"
        if md.is_file():
            lineas += ["", f"### Cobertura del código nuevo ({lado}, diff-cover)", ""]
            lineas.append(md.read_text(encoding="utf-8").strip())

    return metricas, "\n".join(lineas) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--reportes", type=Path, required=True)
    parser.add_argument("--salida-json", type=Path)
    args = parser.parse_args()

    metricas, markdown = construir(args.reportes)
    # UTF-8 explícito: la consola de Windows (cp1252) no codifica los íconos del resumen.
    sys.stdout.buffer.write(markdown.encode("utf-8"))
    if args.salida_json:
        args.salida_json.write_text(
            json.dumps(metricas, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
