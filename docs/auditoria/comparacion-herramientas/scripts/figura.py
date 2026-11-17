"""Figura del hallazgo de la U_T de la planilla (est_02 y est_05, Log-Normal 3p MV)."""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RES = Path(__file__).resolve().parent.parent / "resultados"
filas = list(csv.DictReader(open(RES / "comparacion_tesis_autoconsistencia.csv", encoding="utf-8")))

fig, ejes = plt.subplots(1, 2, figsize=(10, 3.8), sharex=True)
for ax, (clave, titulo) in zip(ejes, [("est_02", "Vado de Río Seco"), ("est_05", "Piedra Blanca")]):
    sel = [f for f in filas if f["estacion"] == clave]
    T = [float(f["T"]) for f in sel]
    ax.plot(T, [float(f["metis"]) for f in sel], "-", color="#2f5f8a", lw=2, label="METIS")
    ax.plot(T, [float(f["tesis_recalculado_con_sus_parametros"]) for f in sel], "--", color="#8a96a3", lw=1.4,
            label="Parámetros de la tesis, inversa exacta (scipy)")
    ax.plot(T, [float(f["tesis_impreso"]) for f in sel], "o", color="#b4443c", ms=6, label="Cuantil impreso en la tesis")
    ax.plot(T, [float(f["tesis_recalculado_con_UT_de_la_planilla"]) for f in sel], "x", color="#1f2933", ms=7,
            label="Parámetros de la tesis, U_T con F en vez de 1 − F")
    ax.set_xscale("log")
    ax.set_title(f"{titulo}: Log-Normal 3p, Máx. Verosimilitud", fontsize=9)
    ax.set_xlabel("Período de retorno T [años]", fontsize=8)
    ax.set_ylabel("Caudal [m³/s]", fontsize=8)
    ax.tick_params(labelsize=8)
    ax.grid(True, color="#e3e7eb", lw=0.6)
ejes[0].legend(fontsize=7, frameon=False, loc="upper left")
fig.tight_layout()
fig.savefig(RES / "figura_ut_planilla.png", dpi=180)
print("figura_ut_planilla.png")
