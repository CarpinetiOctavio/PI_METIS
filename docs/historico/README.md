# Histórico

`reimplementacion-etapa2.md` — documento de contexto para la reimplementación de fórmulas de Etapa 2 (junio 2026). Superado por `.claude/rules/core/core-etapa2-implementation.md`; se conserva como registro histórico. Movido acá el 16/07/2026.

`oauth-descartado.md` — flujo de autenticación Google OAuth tal como se había diseñado originalmente, antes de ser descartado por `DECISIÓN 001` (`docs/decisiones/decision001.md`) — el servidor no puede recibir el callback entrante de Google desde la intranet de la UCC. Reemplazado por usuario/contraseña + JWT, documentado en `architecture.md`, sección "Autenticación — flujo vigente". Movido desde `architecture.md` el 17/07/2026.

`2026-07-22-frontend-fase0-scaffold.md` — plan de implementación de la Fase 0 del frontend (scaffold de Vite + React + TS, tokens del tema "Instrumento", 8 rutas stub, conectividad verificada contra el backend). Ya ejecutado y mergeado. Es el único registro de por qué el scaffold quedó como quedó (puerto 5173 atado a `FRONTEND_ORIGIN`, theming por CSS custom properties sin runtime CSS-in-JS, proxy del dev server en vez de CORS real). Reemplazado como plan activo por `docs/frontend/frontend-implementation-plan.md` y el informe de Fases 1-6. Movido desde `docs/superpowers/plans/` el 09/08/2026 — ese directorio (una herramienta de planificación que el proyecto ya no usa) se eliminó en el mismo commit.
