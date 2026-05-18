# Pipeline Estadístico — Lógica de Negocio

## IMPORTANTE: Esta lógica vive en core/ — no en api/ ni services/

El motor estadístico no sabe que existe HTTP. Recibe datos Python, devuelve resultados Python.
Services/ orquesta el pipeline y emite eventos SSE. Core/ solo calcula.

---

## Etapa 1 — Pipeline de validación estadística

### Orden de ejecución (fijo, no configurable)

```
1. Validación del contrato de datos        ← primera barrera, puede ser bloqueante
2. Estadística descriptiva                 ← automática, siempre, antes de cualquier prueba
3. Independencia: Anderson + Wald-Wolfowitz
4. Homogeneidad: Helmert + t de Student + Cramer
5. Tendencia: Mann-Kendall + Kolmogorov-Smirnov
6. Atípicos: Chow                          ← pausa para decisión del usuario en CU-01/CU-02
```

**α = 5% fijo en toda la V1.0. No es configurable.**

### Contrato de datos — validaciones en orden

```python
# BLOQUEANTE — detiene el pipeline completamente
if len(serie) < 10:
    emit("contract_error", {"codigo": "CONTRACT_SERIES_TOO_SHORT", "datos": len(serie), "minimo": 10})
    return  # nada más se ejecuta

if resolución_temporal is None:
    emit("contract_error", {"codigo": "CONTRACT_NO_TEMPORAL_RESOLUTION"})
    return

# NO BLOQUEANTES — el pipeline continúa con warning
if len(serie) < 30:
    emit("contract_warning", {"codigo": "CONTRACT_LENGTH_WARNING", "datos": len(serie)})

if tipo_variable == "caudal_precipitacion" and any(v < 0 for v in serie):
    emit("contract_warning", {"codigo": "CONTRACT_NEGATIVE_VALUES"})

# ... resto de validaciones (faltantes, duplicados, orden, espaciado, no numéricos)
```

### Pruebas de independencia

**Anderson (principal)**
- Calcula coeficiente de autocorrelación serial para k = 1, 2, ..., n/3
- Valor crítico: fórmula analítica de la tesis de Facundo (no tabla)
- Si Anderson acepta → serie es independiente aunque Wald-Wolfowitz rechace
- Produce correlograma como output gráfico

**Wald-Wolfowitz (verificación)**
- Para n > 40: valor crítico de distribución normal estándar (Z = ±1.96 para α=5%)
- Para n ≤ 40: ejecutar CON advertencia explícita `TEST_WARNING_SMALL_SAMPLE` — no omitir
- Si Anderson acepta y Wald-Wolfowitz rechaza: resultado = INDEPENDIENTE con nota de Wald

**Jerarquía:** Anderson manda. Wald-Wolfowitz es verificación, no co-decisor.

### Pruebas de homogeneidad

**Helmert**
- Resultado directo, sin tabla

**t de Student**
- Tabla con ν = n₁ + n₂ − 2 grados de libertad, α = 5%

**Cramer (principal de homogeneidad)**
- Distribución t de Student
- El resultado SIEMPRE incluye n₁ y n₂ empleados en la partición
- Partición configurable: default = últimos 60% y últimos 30%
- CU-01/CU-02: usuario configura partición desde la interfaz
- CU-03: partición viene de configuración del client_id

**Niveles de homogeneidad:**
```
homogeneidad_ok       → todas aprobaron
homogeneidad_warning  → Cramer aprobó pero Helmert o t de Student rechazaron
homogeneidad_critica  → Cramer rechazó → WARNING CRÍTICO
```

### Pruebas de tendencia

**Mann-Kendall**
- n > 10: fórmula analítica A.55 del apéndice de Carlos
- n ≤ 10: Tabla A.4

**Kolmogorov-Smirnov (tendencia)**
- Z_crit = 1.358 para α = 0.05 (Tabla A.5)

### Detección de atípicos: Chow

- Aplica sobre **logaritmos** de la serie — CRÍTICO
- Si hay ceros en caudal_precipitacion: marcar como `TEST_NOT_EXECUTED_ZEROS`, continuar
- Fuente primaria: Escalante Sandoval & Reyes Chávez (2005)
- Chow **nunca** genera warning Crítico — siempre es warning normal
- Si detecta atípico: emitir `TEST_WARNING_OUTLIER_DETECTED` y pausar stream
  - CU-01/CU-02: esperar decisión del usuario via POST /analysis/outlier-decision
  - CU-03: registrar warning y continuar automáticamente (sin pausa)

### Distribuciones deshabilitadas ante ceros en caudal_precipitacion

```python
DISABLED_WITH_ZEROS = [
    "log_normal_2p",
    "log_pearson_3",
    "gamma_2p",
    "exponencial_beta",
    # "chow" ya manejado arriba
]
# Pendiente confirmar con Facundo: gamma_3p, exponencial_x0_beta,
# generalizada_pareto, log_normal_3p, generalizada_exponencial
```

### Niveles de warning

```
CRÍTICO:
  - Anderson rechaza independencia
  - Cramer rechaza homogeneidad (homogeneidad_critica)

NORMAL:
  - Tendencia detectada (Mann-Kendall o KS)
  - Chow detecta atípico
  - Wald-Wolfowitz rechaza
  - Helmert o t de Student rechazan
  - Cualquier problema del contrato no bloqueante
  - Wald-Wolfowitz con n ≤ 40
```

---

## Estado de confianza global del resultado

```python
# Se determina al finalizar el pipeline completo
if len(serie) < 10 or serie_vacía:
    nivel = "rechazado"        # único estado que detiene el pipeline
elif any(warning.nivel == "critico" for warning in warnings):
    nivel = "con_warnings"     # advertencia prominente en UI
elif len(warnings) > 0:
    nivel = "con_warnings"     # advertencia estándar
else:
    nivel = "validado"
```

---

## Eventos SSE del stream — estructura

Todos los eventos siguen este esquema:

```python
# Formato de cada evento SSE
f"event: {tipo}\ndata: {json.dumps(payload)}\n\n"

# Tipos de eventos:
"contract_error"          # bloqueante, stream termina
"contract_warning"        # no bloqueante, stream continúa
"descriptive_stats"       # estadística descriptiva calculada
"progress"                # avance del pipeline
"test_result"             # resultado de una prueba individual
"outlier_detected"        # pausa para decisión del usuario (CU-01/CU-02)
"result_etapa1"           # resultados completos de Etapa 1
"result_etapa2_ranking"   # ranking EEA completo (pausa para selección)
"complete"                # pipeline terminado
"error"                   # error interno inesperado
```

Payload mínimo de `progress`:
```json
{"paso": "anderson", "etapa": 1, "completado": 2, "total": 8}
```

Payload de `test_result`:
```json
{
  "prueba": "anderson",
  "estadistico": 0.23,
  "valor_critico": 0.37,
  "veredicto": "aprobada",
  "warning_codigo": null,
  "warning_nivel": null,
  "n1": null,
  "n2": null
}
```

---

## Etapa 2 — Motor de análisis de frecuencia

### Solo se ejecuta si Etapa 1 fue completada primero — siempre

### 13 distribuciones con hasta 6 métodos de estimación

El ajuste es **automático y exhaustivo** — sin intervención del usuario.

| Distribución | Métodos aplicables |
|---|---|
| Uniforme | Momentos, MV |
| Normal | Momentos, MV, ML |
| Gumbel | Momentos, MV, ML, ME |
| GVE | Momentos, MV, ML |
| Log-Normal 2p | Momentos, MV |
| Log-Normal 3p | Momentos, MV |
| Log-Pearson III | Momentos (directo e indirecto), MV |
| Gamma 2p | Momentos, MV, ML |
| Gamma 3p | Momentos, MV |
| Exponencial (β) | Momentos, MV |
| Exponencial (x₀, β) | Momentos, MV |
| Generalizada de Pareto | Momentos, MV, MC |
| Generalizada Exponencial | Momentos, MV, ML |

> **Nota sobre Pearson III:** no existe como distribución independiente en la tesis
> de Facundo — no tiene sección propia ni fórmulas propias. La distribución Gamma 3p
> (β, α, x₀) es matemáticamente equivalente a Pearson III en escala original.
> Log-Pearson III aplica la misma lógica sobre yi = ln(xi).
> Fuente: confirmado por Octavio — Tesis Facundo Cap. IV.

> **Nota sobre métodos ME y MC:** ME = Máxima Entropía, MC = Mínimos Cuadrados.
> Confirmados solo para las distribuciones donde aparecen en la tabla.
> Pendiente confirmar con Facundo si aplican a otras distribuciones.
> Fuente: formulas-etapa2.md — Gumbel IV-190/IV-198, Gen. Pareto IV-153/IV-155.

**GVE con Momentos-L:** usar aproximación de Hosking (1985) para estimar κ (IV-234 a IV-242).

### Casos especiales de Etapa 2

```python
"no_converge"    # método iterativo no encontró solución estable → registrar, continuar
"no_aplicable"   # combinación sin sentido matemático para esos datos → registrar, continuar
"high_eea"       # EEA > 5% de la media → warning DIST_HIGH_EEA
"disabled_zeros" # distribución deshabilitada por ceros → registrar, continuar
```

**Ningún caso especial detiene el pipeline de Etapa 2.**

### Criterio de rankeo: EEA (Error Estándar de Ajuste)

- Menor EEA → mejor ajuste → posición 1 en el ranking
- **METIS no sugiere ganadora** — presenta el ranking y el usuario decide
- Fórmula de Weibull para períodos de retorno empíricos: T = (n+1)/m

### Selección de distribución

- CU-01 y CU-02: el usuario selecciona manualmente desde la tabla rankeada
- CU-03: selección automática por EEA (la de menor EEA)
- Después de la selección → calcular eventos de diseño via POST /analysis/design-events

### Año hidrológico

Todo gráfico con eje temporal produce **dos versiones**:
- Año calendario: 1 enero → 31 diciembre
- Año hidrológico: 1 julio → 30 junio del año siguiente

Ambas versiones son **obligatorias**, no opcionales. Aplica a: gráfico de Chow, gráfico de ajuste, gráfico de eventos de diseño, serie temporal, boxplot mensual.
