"""Reproduce el hallazgo de Generalizada de Pareto (01/10/2026).

Correr desde la raíz del repo, con numpy/scipy/pandas instalados:
    python docs/auditoria/hallazgos/scripts/analisis_gen_pareto.py
No modifica nada: solo lee core/ y las series de docs/.
Secciones:
  A. Recuperación de parámetros en muestras simuladas (semilla fija).
  B. IV-153 (Mínimos Cuadrados): raíces vs. ajuste de mínimos cuadrados común.
  C. Las 9 estaciones + la serie con negativos: EEA actual vs. coherente.
  D. Puesto en el ranking actual y eventos de diseño T=100/500 (Momentos).
"""
import glob
import re
import sys

import numpy as np

sys.path.insert(0, "backend")
from metis.core.etapa2.distributions import gen_pareto as gp  # noqa: E402
from metis.core.etapa2.empirical import probabilidades_weibull  # noqa: E402
from metis.core.pipeline.pipeline_etapa2 import ejecutar_etapa2  # noqa: E402


# Cuantil tal como lo imprime la tesis (IV-174), convención "xi" (Coles):
def q_iv174(F, mu, sigma, eps):
    return ((1.0 / (1.0 - F)) ** eps - 1.0) * sigma / eps + mu


# Cuantil coherente con los estimadores de la tesis, convención "k" (Hosking):
def q_hosking(F, mu, sigma, eps):
    return mu + sigma / eps * (1.0 - (1.0 - F) ** eps)


def muestra_hosking(rng, k, mu, sigma, n):
    u = rng.uniform(size=n)
    return q_hosking(u, mu, sigma, k)


def mpp_eps(x, signo):
    """IV-167 con el signo del segundo término del numerador como parámetro:
    signo=+1 es la tesis impresa, signo=-1 es lo que se despeja de IV-168..171."""
    n = len(x)
    xi = np.sort(x)
    x1 = xi[0]
    Pi = (np.arange(1, n + 1) - 0.35) / n  # IV-173
    M0 = x.mean()  # IV-172, k=0
    M1 = np.mean((1 - Pi) * xi)  # IV-172, k=1
    I1, I2 = M0 - x1, M0 - 2 * M1  # IV-170, IV-171
    eps = (n * I1 + signo * 2 * I2 * (n - 1)) / (I2 * (n - 1) - I1)
    sigma = (1 + eps) * (2 + eps) * I2  # IV-168
    mu = x1 - sigma / (n + eps)  # IV-169
    return {"mu": mu, "sigma": sigma, "epsilon": eps}


def eea(x, q, p):
    so, _, P = probabilidades_weibull(x)
    est = np.array([q(F, p["mu"], p["sigma"], p["epsilon"]) for F in P])
    return float(np.sqrt(np.sum((est - so) ** 2) / (len(x) - 3)))


def series():
    out = {}
    for f in sorted(glob.glob("docs/auditoria/regresion/regresion-pipeline/est_0*-pipeline.md")):
        txt = open(f, encoding="utf-8").read()
        m = re.search(r"^serie\s*=\s*\[(.*?)^\]", txt, re.S | re.M)
        vals = re.findall(r"-?\d+(?:\.\d+)?", re.sub(r"#.*", "", m.group(1)))
        out[f.replace("\\", "/").split("/")[-1][:6]] = np.array([float(v) for v in vals])
    out["negativos"] = np.loadtxt(
        "docs/series prueba/serie_con_negativos_otro.csv", delimiter=",", skiprows=1
    )[:, 1]
    return out


print("A. Recuperación de parámetros (400 muestras de n=40, mu=50, sigma=30, semilla 1)")
rng = np.random.default_rng(1)
print(f"{'k real':>7} | {'MPP tesis(+)':>12} | {'MPP (-)':>8} | {'Momentos':>9} | {'MC':>6}")
for k in (-0.2, 0.1, 0.4):
    a, b, mo, mc = [], [], [], []
    for _ in range(400):
        x = muestra_hosking(rng, k, 50, 30, 40)
        a.append(mpp_eps(x, +1)["epsilon"])
        b.append(mpp_eps(x, -1)["epsilon"])
        r = gp.ajustar(x, "momentos")
        if r.status == "ok":
            mo.append(r.parametros["epsilon"])
        r = gp.ajustar(x, "mc")
        if r.status == "ok":
            mc.append(r.parametros["epsilon"])
    print(f"{k:+7.1f} | {np.median(a):12.2f} | {np.median(b):8.2f} | {np.median(mo):9.2f} | {np.median(mc):6.2f}")

print("\nB. IV-153 sobre una muestra con k=0.1 (semilla 2)")
rng = np.random.default_rng(2)
x = muestra_hosking(rng, 0.1, 50, 30, 40)
n = len(x)
xs = np.sort(x)
fi = (np.arange(1, n + 1) - 0.4) / (n + 0.2)
yi = np.log(1 - fi)


def iv153(e):
    zi = (1 - fi) ** e
    z1, zb, z2 = zi[0], zi.mean(), np.mean(zi**2)
    xz, zy, z2y, xyz = np.mean(xs * zi), np.mean(zi * yi), np.mean(zi**2 * yi), np.mean(xs * yi * zi)
    xb, x1 = xs.mean(), xs[0]
    A = xb*z1*zy - xb*z2y - xz*z1*zy + xz*z2y - zb*x1*z2y + x1*z2y + z2*x1*zy - zb*x1*zy
    B = z2 - zb - z1*zb + z1
    return e**2 * A - xyz * B


es = np.linspace(-0.49, 3, 500)
v = np.array([iv153(e) for e in es])
raices = [(es[i] + es[i + 1]) / 2 for i in range(len(es) - 1) if np.sign(v[i]) != np.sign(v[i + 1])]


def sse(e):
    Z = np.c_[np.ones(n), (1 - fi) ** e]
    c, *_ = np.linalg.lstsq(Z, xs, rcond=None)
    return np.sum((xs - Z @ c) ** 2)


es2 = np.linspace(-0.45, 1.5, 400)
print("  raíces de IV-153:", np.round(raices, 3), "| eps de mínimos cuadrados común:",
      round(float(es2[np.argmin([sse(e) for e in es2])]), 3), "| k real: 0.1")

print("\nC. EEA por serie (mejor otra = menor EEA de las 12 distribuciones restantes)")
print(f"{'serie':10s} {'n':>3} {'mejor otra':>10} | {'MC actual':>10} {'MC coher.':>9} | "
      f"{'MPP actual':>10} {'MPP corr.+coher.':>16} {'eps corr.':>9}")
datos = series()
for nombre, x in datos.items():
    e2 = ejecutar_etapa2(x)
    best = min(d.mejor_eea for d in e2.ranking if d.mejor_eea is not None and d.distribucion != "gen_pareto")
    r = gp.ajustar(x, "mc")
    mc = (eea(x, q_iv174, r.parametros), eea(x, q_hosking, r.parametros)) if r.status == "ok" else (np.nan, np.nan)
    r = gp.ajustar(x, "mpp")
    mpp_act = eea(x, q_iv174, r.parametros) if r.status == "ok" else np.nan
    pf = mpp_eps(x, -1)
    mpp_fix = eea(x, q_hosking, pf) if pf["sigma"] > 0 else np.nan
    print(f"{nombre:10s} {len(x):3d} {best:10.3f} | {mc[0]:10.3g} {mc[1]:9.3f} | "
          f"{mpp_act:10.3g} {mpp_fix:16.3f} {pf['epsilon']:9.3f}")

print("\nD. Puesto actual de gen_pareto y Momentos con los dos cuantiles")
for nombre, x in datos.items():
    e2 = ejecutar_etapa2(x)
    nombres = [d.distribucion for d in e2.ranking]
    puesto = nombres.index("gen_pareto") + 1
    r = gp.ajustar(x, "momentos")
    if r.status != "ok":
        print(f"{nombre:10s} puesto {puesto:2d}/13 | Momentos: {r.status}")
        continue
    p = r.parametros
    t = [(q_iv174(F, **{"mu": p["mu"], "sigma": p["sigma"], "eps": p["epsilon"]}),
          q_hosking(F, p["mu"], p["sigma"], p["epsilon"])) for F in (0.99, 0.998)]
    print(f"{nombre:10s} puesto {puesto:2d}/13 | Momentos eps={p['epsilon']:.3f} "
          f"EEA actual={eea(x, q_iv174, p):.2f} coherente={eea(x, q_hosking, p):.2f} | "
          f"T100 {t[0][0]:.1f} vs {t[0][1]:.1f} | T500 {t[1][0]:.1f} vs {t[1][1]:.1f}")
