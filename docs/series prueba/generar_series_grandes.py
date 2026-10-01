"""Regenera las tres series de prueba grandes que no se versionan (ver README.md).

Uso, desde esta carpeta:  python generar_series_grandes.py
Necesita pandas, numpy y openpyxl (los mismos del backend).

- bajo_limite.csv / sobre_limite.csv: relleno de "x" de 9 MiB y 11 MiB, sin
  salto de línea. Prueban el tope de subida de 10 MB (DECISIÓN 050): el primero
  pasa el tope y falla en el parseo; el segundo responde 400 PARSE_FILE_TOO_LARGE.
- serie_horaria_40anios.xlsx: 40 años de caudal horario aleatorio. Prueba que una
  serie sub-diaria se rechace con CONTRACT_NO_TEMPORAL_RESOLUTION. Los valores no
  son los mismos que los del archivo original (también eran aleatorios); lo que
  importa es la resolución horaria.
"""

import numpy as np
import pandas as pd

MIB = 1024 * 1024

for nombre, mib in (("bajo_limite.csv", 9), ("sobre_limite.csv", 11)):
    with open(nombre, "w", encoding="ascii", newline="") as fh:
        fh.write("x" * (mib * MIB))

rng = np.random.default_rng(20261001)
fechas = pd.date_range("1980-01-01", periods=40 * 365 * 24, freq="h")
caudal = rng.gamma(shape=4.0, scale=30.0, size=len(fechas))
pd.DataFrame({"fecha": fechas, "caudal": caudal}).to_excel(
    "serie_horaria_40anios.xlsx", index=False
)
print("Listo: bajo_limite.csv, sobre_limite.csv, serie_horaria_40anios.xlsx")
