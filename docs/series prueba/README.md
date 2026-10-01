# Series de prueba

Archivos para probar METIS a mano en el navegador o desde un smoke test. **Ninguno es un dato hidrológico real**:
son series armadas para forzar un comportamiento puntual del pipeline. Las series reales de referencia (las 9
estaciones de la tesis de Facundo) están en `docs/auditoria/regresion/`, no acá.

| Archivo | Qué es | Qué prueba |
|---|---|---|
| `mini_serie.csv` | 15 años (`anio,caudal`), valores de 90 a 104 | Serie corta: `CONTRACT_LENGTH_WARNING` (entre 10 y 29 datos), sin bloquear |
| `serie_con_atipico.csv` | 40 años (`anio,caudal`, 1980–2019), valores de 83 a 156 y un valor forzado de 950 | Chow detecta el atípico y el stream pausa; exclusión de puntos y "Recalcular" |
| `serie_con_negativos_otro.csv` | 40 años (`anio,nivel_m`, 1980–2019). **Sintética:** normal con media 0,6 y desvío 0,9, semilla `20261001`, redondeo a 2 decimales. Simula el nivel máximo anual de un río referido al cero de escala. 5 negativos (1989, 2005, 2006, 2015, 2019), ningún cero, mínimo -0,74, máximo 2,88 | Tipo de variable "Otro" con negativos: Chow no se ejecuta y cinco distribuciones de Etapa 2 quedan sin ajuste. Columna X `anio`, columna Y `nivel_m` |
| `serie_anual_40anios.xlsx` | 40 años (`fecha,caudal`, una fecha por año), valores aleatorios entre ~58 y ~294 | Carga anual desde Excel |
| `serie_diaria_40anios.csv` / `.xlsx` | 14.600 días (`fecha,caudal`, 1980-01-01 a 2019-12-21), valores aleatorios entre 50 y 300 | Resolución diaria: agregación a máximos anuales y recorte de años parciales (DECISIÓN 065). Con `mes_inicio_anio=7` quedan 39 años |

## Las que no se versionan

Pesan demasiado para el repositorio y se regeneran con `python generar_series_grandes.py` (desde esta carpeta).
Están en `.gitignore`.

| Archivo | Qué prueba |
|---|---|
| `bajo_limite.csv` | 9 MiB de relleno: pasa el tope de subida de 10 MB (DECISIÓN 050) y falla en el parseo |
| `sobre_limite.csv` | 11 MiB de relleno: 400 `PARSE_FILE_TOO_LARGE`, antes de abrir el stream |
| `serie_horaria_40anios.xlsx` | 40 años de caudal horario: una serie sub-diaria se rechaza con `CONTRACT_NO_TEMPORAL_RESOLUTION` |

`UCC-DAT-ESR-AH-001-26-00.xlsx` tampoco se versiona hasta confirmar que se puede publicar en el repositorio.
