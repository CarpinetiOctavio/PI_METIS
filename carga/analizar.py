"""Análisis de las corridas de carga (B7). Solo librería estándar: corre en el runner sin instalar nada.

    python carga/analizar.py escalones <k6.csv>            p95 y tasa de error por minuto (quiebre)
    python carga/analizar.py memoria <memoria.csv> <MB/h>   pendiente de memoria del backend (sostenido)

`escalones` lee la salida `--out csv` de k6 (comprimida con gzip o no). `memoria` lee las muestras de scripts/carga.sh
(`epoch,mib`), descarta los primeros 5 minutos de calentamiento, ajusta una recta por mínimos
cuadrados y sale con código 1 si la pendiente supera el umbral en MB por hora.
"""

import csv
import gzip
import math
import sys
from collections import defaultdict

CALENTAMIENTO_S = 300


def _p95(valores: list[float]) -> float:
    ordenados = sorted(valores)
    return ordenados[min(len(ordenados) - 1, math.ceil(0.95 * len(ordenados)) - 1)]


def _endpoint(extra_tags: str) -> str | None:
    for par in extra_tags.split("&"):
        clave, _, valor = par.partition("=")
        if clave == "endpoint":
            return valor
    return None


def escalones(ruta: str) -> None:
    duraciones: dict[int, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    fallas: dict[int, list[float]] = defaultdict(list)
    usuarios: dict[int, float] = defaultdict(float)
    inicio = None
    abrir = gzip.open if ruta.endswith(".gz") else open
    with abrir(ruta, "rt", newline="") as f:
        for fila in csv.DictReader(f):
            t = int(fila["timestamp"])
            inicio = t if inicio is None else min(inicio, t)
            minuto = (t - inicio) // 60
            valor = float(fila["metric_value"])
            if fila["metric_name"] == "http_req_duration":
                duraciones[minuto][_endpoint(fila.get("extra_tags", "")) or "?"].append(valor)
            elif fila["metric_name"] == "http_req_failed":
                fallas[minuto].append(valor)
            elif fila["metric_name"] == "vus":
                usuarios[minuto] = max(usuarios[minuto], valor)

    endpoints = sorted({e for m in duraciones.values() for e in m})
    print("| Minuto | Usuarios | Req | Error | " + " | ".join(f"p95 {e} (ms)" for e in endpoints) + " |")
    print("|---" * (4 + len(endpoints)) + "|")
    for minuto in sorted(duraciones):
        total = sum(len(v) for v in duraciones[minuto].values())
        error = 100 * sum(fallas[minuto]) / len(fallas[minuto]) if fallas[minuto] else 0.0
        p95s = [f"{_p95(duraciones[minuto][e]):.0f}" if duraciones[minuto][e] else "—" for e in endpoints]
        print(f"| {minuto + 1} | {usuarios[minuto]:.0f} | {total} | {error:.1f} % | " + " | ".join(p95s) + " |")


def memoria(ruta: str, umbral_mb_h: float) -> int:
    with open(ruta, newline="") as f:
        muestras = [(float(t), float(m)) for t, m in csv.reader(f)]
    t0 = muestras[0][0]
    puntos = [((t - t0) / 3600, m) for t, m in muestras if t - t0 >= CALENTAMIENTO_S]
    if len(puntos) < 3:
        print(f"Muy pocas muestras después del calentamiento ({len(puntos)}): no se puede ajustar una recta.")
        return 1
    n = len(puntos)
    mx = sum(x for x, _ in puntos) / n
    my = sum(y for _, y in puntos) / n
    pendiente = sum((x - mx) * (y - my) for x, y in puntos) / sum((x - mx) ** 2 for x, _ in puntos)
    print(f"Muestras: {len(muestras)} ({n} después de {CALENTAMIENTO_S // 60} min de calentamiento)")
    print(
        f"Memoria del backend: mínimo {min(m for _, m in muestras):.1f} MiB, máximo {max(m for _, m in muestras):.1f} MiB"
    )
    print(f"Pendiente: {pendiente:+.1f} MB/h (umbral {umbral_mb_h:.0f} MB/h)")
    if pendiente > umbral_mb_h:
        print("FALLA: la memoria crece por encima del umbral.")
        return 1
    print("OK: sin crecimiento sostenido por encima del umbral.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "escalones":
        escalones(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "memoria":
        sys.exit(memoria(sys.argv[2], float(sys.argv[3])))
    else:
        print(__doc__)
        sys.exit(2)
