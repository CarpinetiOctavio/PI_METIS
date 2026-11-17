"""Métricas de proceso y de SonarCloud (B11 del plan del TP de Calidad).

A diferencia de ci_resumen.py, que lee los reportes de una corrida, esto mira la historia del repo:
- tasa de fallo del workflow CI (API de GitHub Actions);
- lead time de los PR mergeados (de abiertos a mergeados);
- defectos por fase de detección y por severidad (issues con label `defecto`);
- las medidas de SonarCloud sobre `staging` (API pública, sin token).

Necesita `gh` autenticado con acceso al repo. Solo biblioteca estándar.

    python scripts/metricas_proceso.py          > resumen en Markdown (desde la raíz del repo)
    python scripts/metricas_proceso.py --json   > los mismos números en JSON
"""

import json
import statistics
import subprocess
import sys
import urllib.request
from datetime import datetime

# Inicio del pipeline con cobertura y gate (PR #111, B1a): separa la tasa de fallo de antes y después.
INICIO_GATE = "2026-10-08T00:00:00Z"
SONAR_PROYECTO = "CarpinetiOctavio_PI_METIS"
SONAR_RAMA = "staging"
SONAR_METRICAS = (
    "ncloc,complexity,cognitive_complexity,bugs,vulnerabilities,code_smells,"
    "security_hotspots,sqale_index,sqale_debt_ratio,reliability_rating,security_rating,"
    "sqale_rating,duplicated_lines_density"
)
RATINGS = {"1.0": "A", "2.0": "B", "3.0": "C", "4.0": "D", "5.0": "E"}


def _gh(*args: str) -> list | dict:
    salida = subprocess.run(
        ["gh", *args], capture_output=True, text=True, check=True
    ).stdout
    return json.loads(salida)


def _gh_lineas(*args: str) -> list:
    """gh --paginate con un --jq que emite un objeto por elemento imprime un JSON por línea."""
    salida = subprocess.run(
        ["gh", *args], capture_output=True, text=True, check=True
    ).stdout
    return [json.loads(linea) for linea in salida.splitlines() if linea.strip()]


def _fecha(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def _tasa(corridas: list[dict]) -> dict:
    fallas = sum(1 for c in corridas if c["conclusion"] == "failure")
    exitos = sum(1 for c in corridas if c["conclusion"] == "success")
    terminadas = fallas + exitos
    return {
        "corridas": len(corridas),
        "exitosas": exitos,
        "fallidas": fallas,
        "otras": len(corridas) - terminadas,  # canceladas, en curso
        "tasa_fallo_pct": round(100.0 * fallas / terminadas, 1) if terminadas else 0.0,
    }


def ci() -> dict:
    corridas = _gh_lineas(
        "api",
        "--paginate",
        "repos/{owner}/{repo}/actions/workflows/ci.yml/runs?per_page=100",
        "--jq",
        ".workflow_runs[] | {conclusion, event, created_at, head_branch}",
    )
    antes = [c for c in corridas if c["created_at"] < INICIO_GATE]
    despues = [c for c in corridas if c["created_at"] >= INICIO_GATE]
    return {
        "total": _tasa(corridas),
        "antes_del_gate": _tasa(antes),
        "desde_el_gate": _tasa(despues),
    }


def _resumen_horas(horas: list[float]) -> dict:
    horas = sorted(horas)
    p90 = horas[min(len(horas) - 1, int(round(0.9 * (len(horas) - 1))))]
    return {
        "mediana_h": round(statistics.median(horas), 1),
        "promedio_h": round(statistics.mean(horas), 1),
        "p90_h": round(p90, 1),
        "menos_de_24h_pct": round(
            100.0 * sum(1 for h in horas if h < 24) / len(horas), 1
        ),
    }


def lead_time() -> dict:
    """Dos medidas por PR hacia staging: de abierto a mergeado (espera en la cola de merge) y del
    primer commit de la rama a mergeado (lo más cercano al lead time de cambio de DORA)."""
    # API REST: la de GraphQL (gh pr list --json commits) excede su límite de nodos con todo el historial.
    prs = _gh_lineas(
        "api", "--paginate", "repos/{owner}/{repo}/pulls?state=closed&base=staging&per_page=100",
        "--jq", ".[] | select(.merged_at != null) | {number, created_at, merged_at}",
    )  # fmt: skip
    if not prs:
        return {"prs": 0}
    abierto, commit = [], []
    for p in prs:
        mergeado = _fecha(p["merged_at"])
        abierto.append((mergeado - _fecha(p["created_at"])).total_seconds() / 3600)
        # Los commits de un PR vienen del más viejo al más nuevo: el primero alcanza.
        primero = _gh(
            "api", f"repos/{{owner}}/{{repo}}/pulls/{p['number']}/commits?per_page=1",
            "--jq", "{fecha: .[0].commit.author.date}",  # un string suelto saldría sin comillas
        )["fecha"]  # fmt: skip
        if primero:
            commit.append((mergeado - _fecha(primero)).total_seconds() / 3600)
    return {
        "prs": len(prs),
        "desde_abierto": _resumen_horas(abierto),
        "desde_primer_commit": _resumen_horas(commit),
    }


def defectos() -> dict:
    issues = _gh(
        "issue",
        "list",
        "--label",
        "defecto",
        "--state",
        "all",
        "--limit",
        "500",
        "--json",
        "number,state,labels",
    )
    por_fase: dict[str, int] = {}
    por_severidad: dict[str, int] = {}
    abiertos = 0
    for i in issues:
        nombres = [label["name"] for label in i["labels"]]
        for n in nombres:
            if n.startswith("fase:"):
                por_fase[n[5:]] = por_fase.get(n[5:], 0) + 1
            if n.startswith("sev:"):
                por_severidad[n[4:]] = por_severidad.get(n[4:], 0) + 1
        abiertos += i["state"] == "OPEN"
    return {
        "total": len(issues),
        "abiertos": abiertos,
        "por_fase": dict(sorted(por_fase.items())),
        "por_severidad": dict(sorted(por_severidad.items())),
    }


def sonar() -> dict:
    url = (
        "https://sonarcloud.io/api/measures/component"
        f"?component={SONAR_PROYECTO}&branch={SONAR_RAMA}&metricKeys={SONAR_METRICAS}"
    )
    with urllib.request.urlopen(url, timeout=30) as r:  # noqa: S310 — URL fija, https
        medidas = json.load(r)["component"]["measures"]
    valores = {m["metric"]: m.get("value") for m in medidas}
    for clave in ("reliability_rating", "security_rating", "sqale_rating"):
        valores[clave] = RATINGS.get(valores.get(clave), valores.get(clave))
    return valores


def construir() -> tuple[dict, str]:
    m = {"ci": ci(), "lead_time": lead_time(), "defectos": defectos(), "sonar": sonar()}

    lineas = [
        "## Métricas de proceso",
        "",
        "### Tasa de fallo del CI (workflow `ci.yml`)",
        "",
    ]
    lineas += [
        "| Período | Corridas | Exitosas | Fallidas | Otras | Tasa de fallo |",
        "|---|---|---|---|---|---|",
    ]
    for nombre, clave in (
        ("Total", "total"),
        ("Antes del gate (< 08/10)", "antes_del_gate"),
        ("Desde el gate", "desde_el_gate"),
    ):
        t = m["ci"][clave]
        lineas.append(
            f"| {nombre} | {t['corridas']} | {t['exitosas']} | {t['fallidas']} | {t['otras']} | {t['tasa_fallo_pct']} % |"
        )

    lt = m["lead_time"]
    lineas += ["", "### Lead time de PR hacia `staging`", ""]
    if lt["prs"]:
        lineas += [
            f"{lt['prs']} PR mergeados.",
            "",
            "| Desde | Mediana | Promedio | p90 | < 24 h |",
            "|---|---|---|---|---|",
        ]
        for nombre, clave in (
            ("Apertura del PR", "desde_abierto"),
            ("Primer commit de la rama", "desde_primer_commit"),
        ):
            r = lt[clave]
            lineas.append(
                f"| {nombre} | {r['mediana_h']} h | {r['promedio_h']} h | {r['p90_h']} h | {r['menos_de_24h_pct']} % |"
            )

    d = m["defectos"]
    lineas += [
        "",
        "### Defectos registrados",
        "",
        f"{d['total']} en total, {d['abiertos']} abiertos.",
        "",
    ]
    lineas += ["| Fase de detección | Defectos |", "|---|---|"]
    lineas += [f"| {f} | {n} |" for f, n in d["por_fase"].items()]
    lineas += ["", "| Severidad | Defectos |", "|---|---|"]
    lineas += [f"| {s} | {n} |" for s, n in d["por_severidad"].items()]

    s = m["sonar"]
    lineas += ["", f"### SonarCloud (`{SONAR_RAMA}`, código total)", ""]
    lineas += ["| Medida | Valor |", "|---|---|"]
    lineas += [f"| {k} | {v} |" for k, v in s.items()]

    return m, "\n".join(lineas) + "\n"


def main() -> int:
    metricas, markdown = construir()
    salida = (
        json.dumps(metricas, indent=2, ensure_ascii=False) + "\n"
        if "--json" in sys.argv[1:]
        else markdown
    )
    sys.stdout.buffer.write(salida.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
