# Plantillas de caso de prueba y de defecto

TP integrador de Calidad de Software, bloque B9. Las dos plantillas con las que se documenta una prueba y un
defecto, y cómo se enlazan entre sí y con el requisito.

| Versión | Fecha | Cambios |
|---|---|---|
| 1.0 | 09/10/2026 | Primera versión |

## 1. Caso de prueba

Un caso nuevo se agrega como una fila de `casos-de-prueba.md`, en la tabla de su técnica. Si el caso es complejo
(varios pasos, un flujo de pantalla), se escribe completo con este formato:

```markdown
### <ID> — <título corto en forma de comportamiento esperado>

| Campo | Valor |
|---|---|
| ID | VL-nn / CE-nn / TD-nn / E2E-n (el prefijo es la técnica o el nivel) |
| Requisito | RF-… del Manual de Requerimientos, o la regla del repo (decisión, documento) de la que sale |
| Técnica | Valores límite / clase de equivalencia / tabla de decisión / flujo E2E / oráculo externo |
| Nivel | Unidad / integración / sistema |
| Precondiciones | Estado necesario antes de ejecutar (usuario sembrado, base migrada, serie cargada…) |
| Entrada | Datos concretos (la serie, el archivo, el parámetro) |
| Pasos | Solo si hay más de una acción |
| Resultado esperado | Con su fuente: valor de la tesis, código del catálogo de errores, columna de la tabla de decisión |
| Fecha del esperado | Cuándo se fijó, anterior a la primera ejecución |
| Test que lo implementa | `ruta::nombre[id de parametrize]` |
| Resultado de la última ejecución | Pasa / falla, corrida de CI o commit |
| Defectos | D-nn, si el caso encontró alguno |
```

**Reglas.**
- El resultado esperado se escribe **antes** de ejecutar el test y sale de una fuente, no de la salida actual del
  código.
- El ID va también en el id de `parametrize` (o en el nombre del test), para que el caso se encuentre en la salida
  de pytest.
- Un caso que ya cubre otro test apunta a ese test y no se duplica.

## 2. Defecto

Se registra como issue de GitHub con el formulario **Defecto** (`.github/ISSUE_TEMPLATE/defecto.yml`), que pide:

| Campo | Para qué |
|---|---|
| Pasos para reproducir | Que cualquiera pueda verlo fallar |
| Resultado esperado | Con su fuente: contrato, ecuación de la tesis o decisión |
| Resultado obtenido | Lo que pasa en realidad, con la salida o el mensaje exacto |
| Severidad | Impacto en el usuario o en el resultado (`sev:critica` a `sev:baja`) |
| Prioridad | Cuándo se corrige (`prio:alta` a `prio:baja`) |
| Fase de detección | Dónde se encontró (`fase:auditoria`, `desarrollo`, `revision`, `ci`, `uso-real`): alimenta la métrica de defectos por fase |
| Ambiente | Desarrollo, despliegue local, CI, navegador |
| Commit o versión | Dónde se detectó |
| Caso de prueba relacionado | ID de `casos-de-prueba.md` o E2E, si lo hay |
| Test de regresión | `ruta::nombre` del test que lo reproduce |

Criterios de severidad y prioridad, y el ciclo de vida completo (rojo antes del fix, verde después, cierre con el
test nombrado): `registro-defectos.md`.

## 3. Cómo se enlazan

```
Requisito (RF-…) ──► Caso (VL/CE/TD/E2E) ──► Test (ruta::nombre) ──► Defecto (D-nn, issue #…)
       ▲                                                                       │
       └──────────────────────── trazabilidad.md ◄─────────────────────────────┘
```

- El **caso** nombra su requisito y su test.
- El **defecto** nombra su caso y su test de regresión.
- `trazabilidad.md` reúne las tres columnas por requisito, y se actualiza en el mismo PR que agrega un caso o cierra
  un defecto.
