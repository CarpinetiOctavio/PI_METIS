"""
Utilidades compartidas del motor de Etapa 2.

_ut(p) — aproximación racional del cuantil estándar normal (IV-102 a IV-105).
Usada por: Normal (IV-101), Log-Normal 2p (IV-109),
           Log-Normal 3p (IV-120), Log-Pearson III (IV-260).
"""

import numpy as np

# Coeficientes de la aproximación racional — IV-102 a IV-104
_B0, _B1, _B2 = 2.515517, 0.802853, 0.010328
_B3, _B4, _B5 = 1.432788, 0.189269, 0.001308


def _ut(p: float) -> float:
    """
    Aproximación racional del cuantil estándar normal — IV-102 a IV-105.

    Para p ≤ 0.5: aplica la fórmula a p y niega el resultado (cuantil negativo).
    Para p > 0.5: aplica la fórmula a 1-p y mantiene el resultado positivo.
    """
    if p <= 0.5:
        q, signo = p, -1.0
    else:
        q, signo = 1.0 - p, 1.0
    V = np.sqrt(np.log(1.0 / q**2))
    ut_abs = V - (_B0 + _B1 * V + _B2 * V**2) / (
        1.0 + _B3 * V + _B4 * V**2 + _B5 * V**3
    )
    return signo * ut_abs
