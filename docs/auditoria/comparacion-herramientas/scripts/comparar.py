"""Cruza los resultados de METIS con la tesis (planilla de Facundo), con las
librerías de referencia (R y scipy) y escribe las tablas de comparación.

Orden de ejecución (desde la raíz del repo):
    python  .../scripts/correr_metis.py
    Rscript .../scripts/referencia_r.R
    python  .../scripts/comparar.py
"""

import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from series import estaciones  # noqa: E402

RES = AQUI.parent / "resultados"


def leer(nombre):
    with open(RES / nombre, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def f(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def rel(a, b):
    if a is None or b is None or b == 0:
        return None
    return 100.0 * (a - b) / abs(b)


def escribir(nombre, filas):
    claves = list(dict.fromkeys(k for fila in filas for k in fila))
    with open(RES / nombre, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=claves, lineterminator="\n")
        w.writeheader()
        w.writerows(filas)


def parametros(texto):
    return {k: float(v) for k, v in (p.split("=") for p in texto.split(";") if p)}


def main():
    est = {e["clave"]: e for e in estaciones()}
    m1 = {r["estacion"]: r for r in leer("metis_etapa1.csv")}
    r1 = {r["estacion"]: r for r in leer("r_etapa1.csv")}
    resumen = {}

    # ── A. Etapa 1: tesis vs METIS vs R ───────────────────────────────────
    pruebas = [
        ("helmert_s_menos_c", "Helmert S-C", 0.0, False),
        ("t_student", "t de Student", 0.01, True),
        ("cramer_tw1", "Cramer t_w1", 0.0001, False),
        ("cramer_tw2", "Cramer t_w2", 0.0001, False),
        ("anderson_lags_fuera", "Anderson, lags fuera de banda", 0.0, True),
        ("ww_rachas", "Wald-Wolfowitz, rachas", 0.0, True),
        ("ww_z", "Wald-Wolfowitz Z", 0.01, True),
        ("mk_z", "Mann-Kendall Z", 0.0001, None),
        ("ks_z", "Kolmogorov-Smirnov Z", 0.0001, None),
    ]
    filas_a = []
    for clave, e in est.items():
        for campo, rotulo, tol, en_r in pruebas:
            tesis = e["tesis_etapa1"].get(campo)
            metis = f(m1[clave].get(campo))
            r = f(r1[clave].get(campo)) if en_r is not False else None
            filas_a.append(
                {
                    "estacion": clave,
                    "prueba": rotulo,
                    "tesis": tesis,
                    "metis": metis,
                    "r": r,
                    "metis_vs_tesis": None if tesis is None or metis is None else round(metis - tesis, 5),
                    "metis_vs_r": None if r is None or metis is None else round(metis - r, 6),
                    "bloqueo_contrato_metis": m1[clave]["bloqueo_contrato"],
                }
            )
    escribir("comparacion_etapa1.csv", filas_a)

    # ── B. Cuantiles del modelo elegido en la tesis vs METIS ──────────────
    mq = defaultdict(dict)
    for r in leer("metis_cuantiles.csv"):
        mq[(r["estacion"], r["distribucion"], r["metodo"])][float(r["T"])] = f(r["metis"])
    filas_b = []
    for clave, e in est.items():
        for c in e["tesis_cuantiles"]:
            modelo = c["modelo"]
            metis = mq.get((clave, *modelo), {}).get(c["T"]) if modelo else None
            filas_b.append(
                {
                    "estacion": clave,
                    "modelo_tesis": c["columna_tesis"],
                    "distribucion_metis": modelo[0] if modelo else "(sin equivalente)",
                    "metodo_metis": modelo[1] if modelo else "",
                    "T": c["T"],
                    "tesis": c["tesis"],
                    "metis": metis,
                    "dif_pct": None if rel(metis, c["tesis"]) is None else round(rel(metis, c["tesis"]), 3),
                }
            )
    escribir("comparacion_cuantiles_tesis.csv", filas_b)

    # ── C. METIS (momentos-L) vs lmom de R ────────────────────────────────
    filas_c = []
    for r in leer("r_lmom_cuantiles.csv"):
        clave = (r["estacion"], r["distribucion"], r["metodo"])
        if clave not in mq:
            continue
        metis = mq[clave].get(float(r["T"]))
        ref = f(r["r_lmom"])
        filas_c.append(
            {
                "estacion": r["estacion"],
                "distribucion": r["distribucion"],
                "metodo": r["metodo"],
                "T": float(r["T"]),
                "metis": metis,
                "r_lmom": ref,
                "dif_pct": None if rel(metis, ref) is None else round(rel(metis, ref), 4),
            }
        )
    escribir("comparacion_lmom.csv", filas_c)

    # ── D. METIS (Máxima Verosimilitud) vs scipy.stats.fit (MLE exacto) ──
    filas_d = []
    T = np.array([2, 5, 10, 20, 25, 50, 100, 200, 500], dtype=float)
    F = 1 - 1 / T
    for clave, e in est.items():
        x = np.array(e["serie"])
        if len(x) < 10:
            continue
        ajustes = {
            ("gumbel", "mv"): stats.gumbel_r.ppf(F, *stats.gumbel_r.fit(x)),
            ("gve", "mv"): stats.genextreme.ppf(F, *stats.genextreme.fit(x)),
            ("gamma2p", "mv"): stats.gamma.ppf(F, *stats.gamma.fit(x, floc=0)),
            ("exponencial_beta", "mv"): stats.expon.ppf(F, *stats.expon.fit(x, floc=0)),
            ("normal", "mv"): stats.norm.ppf(F, *stats.norm.fit(x)),
        }
        for (dist, met), ref in ajustes.items():
            for t, v in zip(T, ref):
                metis = mq.get((clave, dist, met), {}).get(t)
                filas_d.append(
                    {
                        "estacion": clave,
                        "distribucion": dist,
                        "metodo": met,
                        "T": t,
                        "metis": metis,
                        "scipy_mle": float(v),
                        "dif_pct": None if rel(metis, float(v)) is None else round(rel(metis, float(v)), 4),
                    }
                )
    escribir("comparacion_scipy_mle.csv", filas_d)

    # ── E. Aproximaciones de cuantil de la tesis vs inversa exacta ───────
    # Mismos parámetros de METIS; solo cambia UT (aprox. racional IV-102) o
    # Wilson-Hilferty (IV-135/144/260) por la inversa exacta de scipy.
    def exacto(dist, p, P):
        if dist == "normal":
            return p["mu"] + p["sigma"] * stats.norm.ppf(P)
        if dist == "lognormal2p":
            return np.exp(p["mu_y"] + p["sigma_y"] * stats.norm.ppf(P))
        if dist == "lognormal3p":
            return p["x0"] + np.exp(p["mu_y"] + p["sigma_y"] * stats.norm.ppf(P))
        if dist == "gamma2p":
            return p["alpha"] * stats.gamma.ppf(P, p["beta"])
        if dist == "gamma3p":
            return p["x0"] + p["alpha"] * stats.gamma.ppf(P, p["beta"])
        if dist == "logpearson3":
            return np.exp(p["y0"] + p["alpha"] * stats.gamma.ppf(P, p["beta"]))
        return None

    filas_e = []
    for r in leer("metis_parametros.csv"):
        if r["status"] != "ok" or r["distribucion"] not in (
            "normal", "lognormal2p", "lognormal3p", "gamma2p", "gamma3p", "logpearson3"
        ):
            continue
        p = parametros(r["parametros"])
        clave = (r["estacion"], r["distribucion"], r["metodo"])
        for t in T:
            try:
                ex = float(exacto(r["distribucion"], p, 1 - 1 / t))
            except (KeyError, ValueError, OverflowError):
                continue
            metis = mq.get(clave, {}).get(t)
            filas_e.append(
                {
                    "estacion": r["estacion"],
                    "distribucion": r["distribucion"],
                    "metodo": r["metodo"],
                    "beta_forma": p.get("beta"),
                    "T": t,
                    "metis_formula_tesis": metis,
                    "inversa_exacta": ex,
                    "dif_pct": None if rel(metis, ex) is None else round(rel(metis, ex), 4),
                }
            )
    escribir("comparacion_aproximaciones.csv", filas_e)

    # ── F. Hoja de cálculo con funciones nativas (Excel / LibreOffice) ────
    hc = defaultdict(dict)
    for r in leer("hoja_calculo.csv"):
        hc[r["estacion"]][r["magnitud"]] = f(r["hoja_calculo"])
    filas_f = []
    for clave, h in hc.items():
        m, td = m1[clave], est[clave]["tesis_descriptiva"]
        comparables = [
            ("Media", h["media"], f(m["media"]), td["media"]),
            ("Desvío (n-1)", h["desvio_s"], f(m["desvio"]), td["desvio"]),
            ("Asimetría: SKEW vs g de IV-5", h["asimetria_skew"], f(m["asimetria_g"]), td["asimetria_g"]),
            ("Curtosis: KURT vs k de IV-7", h["curtosis_kurt"], f(m["curtosis_k"]), td["curtosis_k"]),
            ("Autocorrelación lag 1: CORREL vs r1 de III-1", h["correl_lag1"], f(m["anderson_r1"]), None),
            ("p-valor t de mitades: T.TEST vs R", h["ttest_p"], f(r1[clave]["t_student_p"]), None),
        ]
        for nombre, hoja, metis, tesis in comparables:
            filas_f.append({"estacion": clave, "magnitud": nombre, "hoja_calculo": hoja, "metis": metis, "tesis": tesis,
                            "dif_pct_hoja_vs_metis": None if rel(hoja, metis) is None else round(rel(hoja, metis), 3)})
        for dist in ("normal", "lognormal2p", "gamma2p", "gumbel"):
            for t in (2, 10, 100):
                hoja = h.get(f"{dist}_T{t}")
                metis = mq.get((clave, dist, "momentos"), {}).get(float(t))
                filas_f.append({"estacion": clave, "magnitud": f"Cuantil {dist} (momentos) T={t}", "hoja_calculo": hoja,
                                "metis": metis, "tesis": None,
                                "dif_pct_hoja_vs_metis": None if rel(hoja, metis) is None else round(rel(hoja, metis), 4)})
    escribir("comparacion_hoja_calculo.csv", filas_f)

    # ── G. SAMHIA vs METIS vs tesis: veredictos ────────────────────────────
    sam = {r["archivo"]: r for r in leer("samhia_resultados.csv")}
    filas_g = []
    for clave in est:
        s_ = sam.get(clave)
        m = m1[clave]
        t_ = est[clave]["tesis_etapa1"]
        def rech(p):
            v = f(p)
            return None if v is None else ("rechaza" if v < 0.05 else "no rechaza")
        filas_g.append({
            "estacion": clave,
            "n": m["n"],
            "metis_bloqueo": m["bloqueo_contrato"],
            "indep_metis_anderson": m.get("anderson_veredicto"),
            "indep_tesis_anderson_lags_fuera": t_["anderson_lags_fuera"],
            "indep_samhia_anderson_pearson_lag1": rech(s_["anderson_p"]) if s_ else "no corre (n<12)",
            "indep_samhia_ww": rech(s_["ww_p"]) if s_ else "",
            "indep_metis_ww": m.get("ww_veredicto"),
            "homog_metis_nivel": m.get("nivel_homogeneidad"),
            "homog_samhia_mann_whitney": rech(s_["mw_p"]) if s_ else "",
            "homog_samhia_mood": rech(s_["mood_p"]) if s_ else "",
            "tend_metis_mk": m.get("mk_veredicto"),
            "tend_samhia_mk": rech(s_["mk_p"]) if s_ else "",
            "atip_metis_chow": m.get("chow_veredicto"),
            "atip_samhia_kn": s_["atipicos"] if s_ else "",
            "samhia_anderson_p": f(s_["anderson_p"]) if s_ else None,
            "samhia_ljung_box_p": f(s_["ljung_box_p"]) if s_ else None,
        })
    escribir("comparacion_samhia.csv", filas_g)

    # ── H. Cuantiles de la tesis recalculados con los PARÁMETROS de la tesis ─
    # Parámetros copiados de la tabla "Etapa 2 — Parámetros (Sheet 3)" de cada
    # ficha. Se evalúan con las ecuaciones de cuantil de la propia tesis, con
    # la inversa normal/gamma exacta (las aproximaciones IV-102 y Wilson-
    # Hilferty mueven el resultado menos de 0,1 % y 1 %, ver sección E).
    tesis_param = [
        ("est_01", "Gamma 2p (Momentos L) [m³/s]", "gamma2p", {"alpha": 109.64, "beta": 1.32}),
        ("est_02", "Log Normal 3p MV [m³/s]", "lognormal3p", {"x0": 38.47, "mu_y": 4.0031, "sigma_y": 1.2927}),
        ("est_03", "Log Pearson III MMI [m³/s]", "logpearson3", {"alpha": 0.260, "beta": 16.252, "y0": -0.588}),
        ("est_05", "Log Normal 3p MV [m³/s]", "lognormal3p", {"x0": -2.15, "mu_y": 3.3323, "sigma_y": 1.1137}),
        ("est_07", "Log Normal 2 parámetros (Momentos y M. Verosimilitud) [m³/s]", "lognormal2p", {"mu_y": 3.82, "sigma_y": 0.578}),
        ("est_09", "Normal (Momentos L) [m³/s]", "normal", {"mu": 27.6, "sigma": 9.877}),
    ]
    # Hipótesis verificada abajo: la planilla evalúa la aproximación racional
    # IV-102 (Abramowitz y Stegun 26.2.23, válida solo para 0 < p <= 0,5) con
    # V = sqrt(ln(1/F^2)) usando F aun cuando F > 0,5, y le cambia el signo;
    # IV-105 indica usar 1 - F en V en ese tramo, que es lo que hace METIS.
    b = (2.515517, 0.802853, 0.010328, 1.432788, 0.189269, 0.001308)

    def ut_planilla(F):
        v = math.sqrt(math.log(1 / F**2))
        return -(v - (b[0] + b[1] * v + b[2] * v * v) / (1 + b[3] * v + b[4] * v * v + b[5] * v**3))

    def con_ut(dist, p, F):
        u = ut_planilla(F)
        wh = lambda beta: (1 - 1 / (9 * beta) + u * math.sqrt(1 / (9 * beta))) ** 3  # noqa: E731
        if dist == "normal":
            return p["mu"] + p["sigma"] * u
        if dist == "lognormal2p":
            return math.exp(p["mu_y"] + p["sigma_y"] * u)
        if dist == "lognormal3p":
            return p["x0"] + math.exp(p["mu_y"] + p["sigma_y"] * u)
        if dist == "gamma2p":
            return p["alpha"] * p["beta"] * wh(p["beta"])
        if dist == "logpearson3":
            return math.exp(p["y0"] + p["alpha"] * p["beta"] * wh(p["beta"]))
        raise ValueError(dist)

    filas_h = []
    for clave, col, dist, p in tesis_param:
        tabla = {c["T"]: c["tesis"] for c in est[clave]["tesis_cuantiles"] if c["columna_tesis"] == col}
        modelo = next(c["modelo"] for c in est[clave]["tesis_cuantiles"] if c["columna_tesis"] == col)
        for t, impreso in sorted(tabla.items()):
            recalculado = float(exacto(dist, p, 1 - 1 / t))
            metis = mq.get((clave, *modelo), {}).get(t)
            filas_h.append({
                "estacion": clave, "modelo_tesis": col, "T": t,
                "tesis_impreso": impreso,
                "tesis_recalculado_con_sus_parametros": round(recalculado, 3),
                "tesis_recalculado_con_UT_de_la_planilla": round(con_ut(dist, p, 1 - 1 / t), 3),
                "metis": metis,
                "impreso_vs_recalculado_pct": round(rel(impreso, recalculado), 3),
                "impreso_vs_UT_planilla_pct": round(rel(impreso, con_ut(dist, p, 1 - 1 / t)), 3),
                "metis_vs_recalculado_pct": None if rel(metis, recalculado) is None else round(rel(metis, recalculado), 3),
            })
    escribir("comparacion_tesis_autoconsistencia.csv", filas_h)

    # ── I. EEA de la tesis con la misma U_T de la planilla ────────────────
    # EEA = sqrt(sum((Q_est(F_i) - Q_i)^2) / (n - mp)), F_i de Weibull (IV-263).
    eea_tesis = {  # tabla "EEA esperados (Sheet 3)" de cada ficha
        ("est_02", "lognormal3p"): 20.7985,
        ("est_05", "lognormal3p"): 5.7842,
        ("est_07", "lognormal2p"): 3.9748,
        ("est_09", "normal"): 2.9141,
    }

    def eea(x, q, mp):
        xs = np.sort(x)[::-1]
        n = len(xs)
        Fw = 1 - 1 / ((n + 1) / np.arange(1, n + 1))
        return math.sqrt(sum((q(F) - o) ** 2 for F, o in zip(Fw, xs)) / (n - mp))

    filas_i = []
    for clave, col, dist, p in tesis_param:
        if (clave, dist) not in eea_tesis:
            continue
        x = np.array(est[clave]["serie"])
        mp = len(p)
        filas_i.append({
            "estacion": clave, "distribucion": dist, "eea_tesis": eea_tesis[(clave, dist)],
            "eea_con_UT_planilla": round(eea(x, lambda F: con_ut(dist, p, F), mp), 4),
            "eea_con_inversa_exacta": round(eea(x, lambda F: float(exacto(dist, p, F)), mp), 4),
        })
    escribir("comparacion_tesis_eea.csv", filas_i)

    # ── Resumen ────────────────────────────────────────────────────────────
    def maxabs(filas, cond=lambda r: True):
        vals = [abs(r["dif_pct"]) for r in filas if r["dif_pct"] is not None and cond(r)]
        return (round(max(vals), 4), len(vals)) if vals else (None, 0)

    resumen["lmom_por_familia"] = {
        d: maxabs(filas_c, lambda r, d=d: r["distribucion"] == d)
        for d in sorted({r["distribucion"] for r in filas_c})
    }
    resumen["scipy_por_familia"] = {
        d: maxabs(filas_d, lambda r, d=d: r["distribucion"] == d)
        for d in sorted({r["distribucion"] for r in filas_d})
    }
    resumen["aprox_por_familia_T100"] = {
        d: maxabs(filas_e, lambda r, d=d: r["distribucion"] == d and r["T"] == 100)
        for d in sorted({r["distribucion"] for r in filas_e})
    }
    resumen["cuantiles_tesis_por_estacion"] = {
        k: maxabs(filas_b, lambda r, k=k: r["estacion"] == k) for k in est
    }
    resumen["etapa1_metis_vs_r_max"] = {
        p[1]: max(
            (abs(r["metis_vs_r"]) for r in filas_a if r["prueba"] == p[1] and r["metis_vs_r"] is not None),
            default=None,
        )
        for p in pruebas
        if p[3] is not False
    }
    with open(RES / "resumen.json", "w", encoding="utf-8") as fh:
        json.dump(resumen, fh, ensure_ascii=False, indent=2)
    print(json.dumps(resumen, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
