# DECISIÓN 082: las dependencias del backend se instalan desde un lock con hashes y solo como wheels

**Fecha:** 22 de octubre de 2026
**Estado:** Decidida y aplicada (CI + imagen Docker del backend).
**Decide:** Kevin, a partir del análisis de SonarCloud sobre `staging` del 22/10/2026.
**Depende de:** DECISIÓN 077 (SonarCloud por CI). Cierra la acción "requirements con hashes" de
`docs/calidad/metricas.md` §6.

### Problema

SonarCloud marcaba sobre `staging` (código total) **5 vulnerabilidades de severidad media**, y con ellas el Security
rating en **C**. Las cinco son de la cadena de suministro de dependencias, ninguna está en el código de METIS:

| Regla | Dónde | Qué señala |
|---|---|---|
| `githubactions:S8541` | `ci.yml`, instalación de ruff en el job `lint` | `pip install` sin `--only-binary :all:`: un paquete distribuido como código fuente ejecuta su `setup.py` al instalarse |
| `githubactions:S8541` | `ci.yml`, instalación de dependencias en el job `test` | Ídem |
| `githubactions:S8544` | Ídem | Dependencias sin versiones resueltas bloqueadas |
| `docker:S8541` | `backend/Dockerfile`, instalación de dependencias | Ídem S8541, en la imagen que se despliega |
| `docker:S8544` | Ídem | Ídem S8544 |

`requirements.txt` fija con `==` las 23 dependencias directas, pero no las transitivas (unas 57 más) ni sus hashes.
Dos instalaciones en días distintos pueden traer versiones transitivas distintas, y un paquete reemplazado en el
índice con el mismo número de versión se instala sin que nada lo note.

### La decisión

1. **`backend/requirements.lock`**: las 80 dependencias (directas y transitivas) con versión y hash SHA-256,
   generado desde `requirements.txt` con `uv pip compile --generate-hashes`, para Python 3.11 en Linux x86-64 (la
   plataforma del runner y de la imagen `python:3.11-slim`) y solo wheels. El comando exacto está en el encabezado
   del archivo.
2. **CI y la imagen instalan desde el lock** con `pip install --only-binary :all: --require-hashes -r
   requirements.lock`. Con `--require-hashes`, pip rechaza cualquier archivo cuyo hash no coincida; con
   `--only-binary :all:`, ningún paquete ejecuta código al instalarse.
3. **`requirements.txt` sigue siendo la fuente** de las dependencias directas y lo que se usa en un `venv` de
   desarrollo. El lock se regenera en el mismo commit que cambie `requirements.txt`.
4. **`scripts/check_requirements_lock.py`**, en el job `lint`, falla si alguna dependencia directa de
   `requirements.txt` no está en el lock con la misma versión. Sin este chequeo, cambiar una versión en
   `requirements.txt` sin regenerar el lock pasaría inadvertido: la imagen seguiría instalando la vieja.
5. La instalación de ruff en el job `lint` suma `--only-binary :all:` (la versión ya estaba fijada).

### Alternativas descartadas

- **Marcar las cinco como "aceptadas" en SonarCloud.** El riesgo es real aunque bajo, la corrección no toca código de
  METIS y cuesta un archivo generado. Aceptarlas habría dejado el rating en C sin una razón técnica para hacerlo.
- **Fijar los hashes dentro de `requirements.txt`.** Un archivo de dependencias directas con unos 2.000 hashes deja de
  ser legible y de editarse a mano. Separar fuente y lock es el patrón habitual de `pip-tools` y `uv`.
- **Migrar a otro gestor (Poetry, `uv sync` con `pyproject.toml`).** Cambia cómo se instala el backend en todos los
  entornos a cuatro días de la entrega del TP de Calidad, sin beneficio adicional para este problema.

### Verificación

- Instalación limpia en Python 3.11 con `pip install --only-binary :all: --require-hashes -r requirements.lock`:
  todas las dependencias tienen wheel; las versiones directas instaladas son las de `requirements.txt`.
- Con esas dependencias, `pytest -m "unit or integration"` da 961 pasan y 23 se saltean (los de PostgreSQL y
  Mailpit, sin servicios en la máquina local); en CI corren todos. `ruff check` y `ruff format --check` limpios.
- La imagen del backend se construye con el lock en el job `despliegue` (smoke y E2E sobre ella).

### Consecuencias

- Agregar o actualizar una dependencia del backend son dos archivos: `requirements.txt` y el lock regenerado.
  Regla escrita en `CLAUDE.md`.
- Las versiones transitivas quedan congeladas hasta la próxima regeneración. Una actualización de seguridad de una
  transitiva no entra sola: hay que regenerar el lock a propósito.
- Una dependencia nueva que solo se publique como código fuente no se puede instalar con esta configuración; habría
  que justificar la excepción en un addendum.
