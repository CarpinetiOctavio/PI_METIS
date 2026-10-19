import numpy as np
from scipy.stats import t as t_dist

from metis.core.etapa1.significancia import ALFA_DEFECTO, validar_alfa
from metis.core.types import Explicacion, TestResult

# Chow usa el mismo α que el resto de la Etapa 1, aplicado a CADA extremo
# (DECISIÓN 078; respuesta de Facundo del 18/10/2026 a la DECISIÓN 018: 5 %,
# el estándar en hidrología). Antes se escribía como α = 0,10 repartido en las
# dos colas, t_{1−0,10/(2n)}: es el mismo cuantil que t_{1−0,05/n}.


def calcular_chow(
    serie: list[float], tipo_variable: str, alfa: float = ALFA_DEFECTO
) -> TestResult:
    validar_alfa(alfa)
    arr = np.array(serie, dtype=float)

    # Negativos → no ejecutar, con motivo propio (DECISIÓN 073). Va primero,
    # con la misma precedencia que en Etapa 2: es el motivo más fuerte, y antes
    # se perdía dentro de TEST_NOT_EXECUTED_CONDITION. Depende de los datos,
    # no de tipo_variable (con Caudal/Precip. ya se advierte aparte,
    # CONTRACT_NEGATIVE_VALUES).
    if np.any(arr < 0):
        return TestResult(
            prueba="chow",
            estadistico=None,
            valor_critico=None,
            veredicto="no_ejecutada",
            warning_codigo="TEST_NOT_EXECUTED_NEGATIVES",
            warning_nivel="normal",
        )

    # Ceros en caudal_precipitacion → no ejecutar
    if tipo_variable == "caudal_precipitacion" and np.any(arr == 0):
        return TestResult(
            prueba="chow",
            estadistico=None,
            valor_critico=None,
            veredicto="no_ejecutada",
            warning_codigo="TEST_NOT_EXECUTED_ZEROS",
            warning_nivel="normal",
        )

    # Ceros con tipo "otro" → log no definido
    if np.any(arr <= 0):
        return TestResult(
            prueba="chow",
            estadistico=None,
            valor_critico=None,
            veredicto="no_ejecutada",
            warning_codigo="TEST_NOT_EXECUTED_CONDITION",
            warning_nivel="normal",
        )

    # Chow aplica sobre logaritmos
    log_serie = np.log(arr)
    n = len(log_serie)
    media = np.mean(log_serie)
    s = np.std(log_serie, ddof=1)

    # z con signo: positivo por encima de la media de los logaritmos.
    z_con_signo = (log_serie - media) / s if s != 0 else np.zeros(n)
    z_scores = np.abs(z_con_signo)
    estadistico = float(np.max(z_scores))

    # Valor crítico K_N — Grubbs-Beck, Bulletin 17B Apéndice 4 (DECISIÓN 018).
    # El estadístico (desvío estandarizado máximo) es el de Grubbs; K_N
    # requiere la transformación geométrica completa, no el cuantil t crudo:
    #   K_N = (n-1)/√n · √(t² / (n-2+t²)),  t = t_{n-2, 1-α/n}
    # (Bonferroni por las n comparaciones, α en cada extremo — DECISIÓN 078)
    nu = n - 2
    t_val = t_dist.ppf(1 - alfa / n, df=nu)
    valor_critico = float(
        ((n - 1) / np.sqrt(n)) * np.sqrt(t_val**2 / (n - 2 + t_val**2))
    )

    # DECISIÓN 079 — Bulletin 17B: umbral alto ȳ + K_N·S y bajo ȳ − K_N·S sobre
    # los logaritmos, cada lado como prueba de un extremo, y TODO valor más allá
    # de su umbral es atípico, no solo el más extremo. Una sola pasada: ȳ, S y
    # K_N se calculan sobre la serie completa (el enmascaramiento queda
    # declarado en la decisión). Que la lista no esté vacía equivale a
    # max|z| > K_N, el criterio anterior.
    valores_atipicos = sorted(
        (
            {
                "indice": i,
                "valor": float(arr[i]),
                "z": float(z_con_signo[i]),
                "lado": "alto" if z_con_signo[i] > 0 else "bajo",
            }
            for i in range(n)
            if z_con_signo[i] > valor_critico or z_con_signo[i] < -valor_critico
        ),
        key=lambda a: -abs(a["z"]),
    )
    # Umbrales en la escala original: el gráfico de Chow dibuja exactamente estos.
    limite_inferior = float(np.exp(media - valor_critico * s))
    limite_superior = float(np.exp(media + valor_critico * s))

    atipico_detectado = bool(valores_atipicos)
    veredicto = "rechazada" if atipico_detectado else "aprobada"

    # Chow nunca genera warning crítico — siempre normal
    warning_codigo = "TEST_WARNING_OUTLIER_DETECTED" if atipico_detectado else None
    warning_nivel = "normal" if atipico_detectado else None

    # Valor e índice originales de la serie (no el log) correspondientes al
    # z-score máximo — el índice es necesario para remover el dato correcto
    # en caso de que la serie tenga valores duplicados (ver analysis_service.py)
    valor_atipico: float | None = None
    indice_atipico: int | None = None
    if atipico_detectado:
        idx = int(np.argmax(z_scores))
        valor_atipico = float(arr[idx])
        indice_atipico = idx

    explicacion = Explicacion(
        ecuacion="Bulletin 17B, Apéndice 4 (Grubbs-Beck) — DECISIÓN 018",
        terminos={
            "n": n,
            "media_log": float(media),
            "s_log": float(s),
            "nu": nu,
            "t_bonferroni": float(t_val),
            "alfa": alfa,
            "limite_inferior": limite_inferior,
            "limite_superior": limite_superior,
        },
        # Addendum 01/10/2026 a la DECISIÓN 064 — una fila por observación, con
        # los z que ya se calcularon para el estadístico (max(z_i)). `i` es la
        # posición 1..n en la serie analizada.
        desglose=[
            {
                "i": i + 1,
                "x_i": float(arr[i]),
                "ln_x_i": float(log_serie[i]),
                "z_i": float(z_scores[i]),
                # DECISIÓN 079 — la observación está fuera de los umbrales.
                "fuera": bool(z_scores[i] > valor_critico),
            }
            for i in range(n)
        ],
    )

    return TestResult(
        prueba="chow",
        estadistico=estadistico,
        valor_critico=valor_critico,
        veredicto=veredicto,
        warning_codigo=warning_codigo,
        warning_nivel=warning_nivel,
        valor_atipico=valor_atipico,
        indice_atipico=indice_atipico,
        explicacion=explicacion,
        valores_atipicos=valores_atipicos,
    )
