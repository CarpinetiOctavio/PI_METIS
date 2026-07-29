# DECISIÓN 036 — Partición de Cramer personalizada inalcanzable por el endpoint multipart
**Fecha:** 29 de Julio de 2026
**Estado:** DOCUMENTADO — no implementado en esta pasada, requerimiento funcional caído

### Contexto
`api-contracts.md` y `statistical-pipeline.md` documentan `cramer_particion` como
`"default" | {n1_pct, n2_pct}`, configurable por el usuario en CU-01/CU-02
(`formulas-etapa1.md` §6, nota de arquitectura: "Aunque el usuario personalice los
tamaños de los bloques (...), el principio de Cramer exige que se extraigan los
últimos datos del registro"). La sesión de implementación de Fase 2 del frontend
(`ConfigPage.tsx`) encontró que el botón "Personalizada" no se podía cablear contra
el backend real y lo dejó `disabled` con un `title` improvisado — sin escalar el
hallazgo a `docs/decisiones/`.

### Diagnóstico confirmado
Verificado directamente contra el código en esta pasada, no solo contra lo que decía
el `title` del botón:

- `backend/metis/api/v1/analysis.py:27` — `cramer_particion: str = Form("default")`.
  Un campo `multipart/form-data` siempre llega como `str` al handler de FastAPI; no
  hay forma de que un objeto JSON llegue tipado como `dict` por esta vía.
- `backend/metis/core/etapa1/homogeneity.py:97-112` — `calcular_cramer(serie,
  particion: dict | str = "default")`. La rama `if particion == "default":` cubre el
  caso por defecto; la rama `else` asume `dict` e indexa `particion["n1_pct"]` /
  `particion["n2_pct"]` directamente.
- Consecuencia: cualquier valor de `cramer_particion` distinto del string literal
  `"default"` entra a la rama `else` como `str` y la indexación `"algo"["n1_pct"]`
  lanza `TypeError: string indices must be integers` — no una respuesta 400
  controlada, un error 500 no manejado.
- `frontend/src/routes/config/ConfigPage.tsx:42` confirma que hoy el frontend nunca
  intenta enviar otra cosa: `cramer_particion: "default"` está hardcodeado en el
  `AnalysisStreamForm`, y el botón "Personalizada" está deshabilitado. No hay ningún
  camino de punta a punta, ni de frontend ni de un cliente HTTP directo, por el que
  la partición personalizada llegue a `calcular_cramer` sin crashear.

### Por qué importa
Contradice tres documentos vigentes a la vez:
- `.claude/rules/architecture/api-contracts.md` — contrato documentado de
  `POST /api/v1/analysis/stream`, campo `cramer_particion`.
- `.claude/rules/core/statistical-pipeline.md` — *"Partición configurable: default =
  últimos 60% y últimos 30%. CU-01/CU-02: usuario configura partición desde la
  interfaz."*
- `.claude/rules/core/formulas-etapa1.md` §6 — nota de arquitectura sobre
  personalización de bloques de Cramer.

### Opciones evaluadas
1. **Recibir `cramer_particion` como JSON string en el `Form` y parsearlo con
   `CramerParticionCustom.model_validate_json()` en la capa `api/`.** Reutiliza el
   modelo Pydantic que ya existe en `schemas/analysis.py` (ver
   [DECISIÓN 037](decision037.md) — ese modelo hoy no lo importa ninguna ruta). No
   requiere cambiar el contrato multipart declarado (`cramer_particion` sigue siendo
   un único campo string desde el punto de vista del cliente HTTP), solo cambia qué
   hace `api/` con el string antes de llamar a `services/`. Riesgo: hay que validar
   explícitamente el JSON malformado con un 400 `CONTRACT`-style, no dejar que
   Pydantic tire un 422 críptico para un campo que hoy es opcional/default.
2. **Recibir dos campos `Form` separados (`cramer_n1_pct`, `cramer_n2_pct`,
   opcionales) y armar el dict en `api/`.** Más simple de validar (dos floats
   opcionales, sin parseo de JSON), pero cambia la forma del contrato documentado en
   `api-contracts.md` (dos campos nuevos en vez de un objeto anidado) — requeriría
   actualizar el contrato, no solo la implementación.
3. **Dejar la partición fija en `"default"` para V1.0 y bajar el requerimiento
   explícitamente.** No requiere tocar `core/` ni `api/`. Bajaría un RF documentado
   sin que quede registrado en ningún lado más que en este archivo, salvo que se
   actualice también `constraints.md`/`sprint.md` con el recorte de alcance.

### Decisión
**No se implementa ninguna opción en esta pasada** — alcance explícito de
`plan-mejora-frontend-pasada2.md`: los hallazgos de backend de esta pasada se
documentan, no se implementan. Queda como pendiente agendado para quien retome
`backend/metis/api/v1/analysis.py` y `core/etapa1/homogeneity.py`. Sin una
recomendación cerrada entre las tres opciones — depende de si Kevin/Octavio quieren
mantener el contrato anidado (`opción 1`, más fiel a lo ya documentado) o simplificar
el contrato (`opción 2`). La `opción 3` solo debería tomarse si se decide
explícitamente recortar el alcance de V1.0, no como default por inacción.

Mientras tanto: el botón "Personalizada" sigue deshabilitado en `ConfigPage.tsx`,
pero su `title` deja de decir "rota en el backend actual" (lenguaje de debugging, no
apto para un usuario final) y pasa a referenciar esta decisión.

### Criterio de hecho
- `decision036.md` existe y está indexado en `docs/decisiones/README.md` con
  título/fecha/estado.
- Referenciada desde `.claude/rules/sprint.md` (pendiente agendado).
- Referenciada desde `.claude/rules/architecture/api-contracts.md` (nota de que el
  contrato documentado no está implementado tal cual para partición personalizada).
- Referenciada desde `frontend/src/routes/config/ConfigPage.tsx` (reemplaza el
  `title` improvisado).

**Ver también:** [DECISIÓN 037](decision037.md) — el modelo Pydantic
`CramerParticionCustom` que la opción 1 reutilizaría ya existe pero no está cableado
al endpoint por un motivo relacionado, no idéntico.
