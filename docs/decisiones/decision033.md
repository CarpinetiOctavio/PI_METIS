# DECISIÓN 033 — Bump de FastAPI/Starlette diferido, con criterios explícitos de habilitación
**Fecha:** 19 de Julio de 2026
**Estado:** DIFERIDO — condicionado a dos criterios explícitos, no abierto sin fecha

### Contexto
Los tests nuevos de auth (ver [DECISIÓN 032](decision032.md)) son los primeros en `tests/unit/` que importan FastAPI. Expusieron un `PendingDeprecationWarning` en `starlette/formparsers.py`: `python-multipart` instalado (`0.0.28`) deprecó el import legacy `import multipart`, y la versión de Starlette que trae `fastapi==0.111.0` (mediados de 2024) todavía usa ese import internamente.

### Diagnóstico confirmado
Verificado contra el changelog oficial de Starlette: el cambio de import (a `python_multipart`) ya está resuelto en una versión posterior de Starlette. El bump de FastAPI resolvería el problema en la raíz — no es una supresión disfrazada, es diferir un fix real ya identificado.

### Opciones evaluadas
- Pinnear `python-multipart` a una versión anterior al deprecation: descartado. Retroceder una dependencia a propósito para silenciar un aviso es peor que documentarlo.
- Bump de FastAPI/Starlette ahora: descartado para esta sesión. Cambio de superficie amplia (toda la app, no sólo auth), sin testear, salto probablemente grande dado que `fastapi==0.111.0` lleva más de un año sin actualizar.
- Suprimir el warning puntual, documentado, y diferir el bump con condiciones explícitas: elegida.

### Decisión
Se suprime en `pytest.ini`: `ignore::PendingDeprecationWarning:starlette.formparsers`, con comentario citando este motivo.

El bump queda diferido hasta que se cumplan ambas condiciones (deliberadamente no se usa "cuando el proyecto esté estable" como criterio — es impreciso y puede no llegar a cumplirse nunca en un proyecto en desarrollo activo):
1. Cobertura de tests suficiente sobre toda la superficie HTTP de la API (los tres casos de uso, no sólo auth) para correr la suite completa post-bump con confianza razonable. Hoy no alcanza: solo auth (10 tests) y Etapa 2 (motores puros, no pasan por FastAPI/Starlette) tienen cobertura.
2. Margen suficiente de tiempo antes de la exposición ante el tribunal para absorber y corregir cualquier ruptura que el bump introduzca. No se ejecuta cerca de la fecha de defensa.

### Riesgo de acoplamiento con Pydantic — verificado, bajo
`pydantic==2.7.1`, ya por encima del mínimo que FastAPI empezó a exigir en versiones recientes al discontinuar soporte de Pydantic v1 (`>=2.7.0`). El bump de FastAPI, al momento de ejecutarse, no debería arrastrar una migración de Pydantic v1→v2 — ya está en v2. Igual, confirmar contra la versión objetivo específica de FastAPI al momento de ejecutar el bump, no asumir que se mantiene válido indefinidamente.

**Ver también:** [DECISIÓN 032](decision032.md) — primeros tests de auth que expusieron este warning.