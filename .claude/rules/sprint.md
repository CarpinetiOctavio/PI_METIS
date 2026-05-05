# Estado del Sprint Actual

## Sprint 1 — Etapa 1 completa

### Estrategia de ramas
Una rama por funcionalidad. Flujo de tres niveles: feature/xxx → staging → main.
Nunca merge directo de feature a main.

### Orden de implementación
1. feature/db-models     — modelos SQLAlchemy + sesión  ✓ mergeado a staging
2. feature/schemas       — modelos Pydantic de request/response  ✓ completado
3. feature/auth          — OAuth Google + JWT en HttpOnly Cookie  ← EN CURSO
4. feature/core-etapa1   — motor estadístico Etapa 1 completo
5. feature/api-etapa1    — endpoints de Etapa 1 + auth
6. feature/services-sse  — orquestación stream SSE hasta resultado Etapa 1

### Fuera de alcance en este sprint
- Etapa 2 (distribuciones, ranking EEA, eventos de diseño)
- Frontend React + TypeScript
- Exportación PDF
- Endpoint /export/
- Endpoint /analysis/design-events
- Endpoint /api/v1/validate/ (CU-03) — sprint posterior

### Completado
- Scaffolding inicial (feature/project-scaffolding — en GitHub, inactiva)
- feature/db-models — mergeado a staging