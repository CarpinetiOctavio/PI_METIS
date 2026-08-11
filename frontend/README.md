# METIS — Frontend

Aplicación Vite + React + TypeScript. Implementa las pantallas de CU-01/CU-02
(entrada, configuración, stream, resultados, historial, verificación de
mail) con routing, layout común y el tema visual fijo "Instrumento"
(claro/oscuro). **No es scaffold** — Auth, Config + stream de Etapa 1 y
Etapa 2, Resultados e Historial están integrados de verdad contra el backend
real (verificado contra Docker). Etapa 2 (ranking de distribuciones, eventos
de diseño) dejó de ser mock el 09/08/2026 (Bloque B del plan de
implementación de Etapa 2): se resuelve inline dentro de `StreamPage`
mientras el stream está pausado — no hay rutas `/ranking` ni
`/design-events` (retiradas, ver `docs/decisiones/decision042.md` para el
mock original y su addendum de cierre). Detalle completo en
`docs/frontend/frontend-implementation-plan.md` §10 y
`docs/frontend/informe-implementacion-frontend-fase1-6.md`.

## Estructura de `src/`

```
src/
├── routes/       # una carpeta por pantalla (entry, config, stream, results,
│                 # history, auth-verify), cada una con su .tsx + .css
│                 # co-locado + .test.tsx. routes/results/ también tiene
│                 # Etapa2RankingView.tsx/Etapa2EventosView.tsx — presentación
│                 # de Etapa 2, reusada por StreamPage (interactiva),
│                 # ResultsPage e HistoryDetailPage (solo lectura)
├── api/          # cliente fetch tipado: client.ts, auth.ts, analysis.ts,
│                 # history.ts, sse.ts (hook useAnalysisStream,
│                 # SSE-sobre-fetch — ver docs/decisiones/decision040.md)
├── auth/         # AuthProvider (context + fetch/useState, sin TanStack
│                 # Query — ver docs/decisiones/decision041.md), guards.tsx
├── theme/        # tokens.ts + tokens.instrumento.css (deben mantenerse en
│                 # paridad, verificado por tokenParity.test.ts), ThemeProvider
├── i18n/         # errors.es.ts — diccionario código→texto en español
└── components/   # UI compartida (RootLayout, TopBar)
```

## Testing

Vitest + React Testing Library. Un solo mecanismo de mock de red en toda la
suite: `vi.stubGlobal("fetch", ...)` — MSW salió del proyecto por completo
(Bloque B5 del plan de Etapa 2, 09/08/2026), no queda ninguna dependencia
`msw` en `package.json`. El hook `useAnalysisStream` mockea el módulo
`@microsoft/fetch-event-source` directamente, con secuencias de eventos
sintéticas armadas a mano según los shapes reales de
`docs/frontend/frontend-integration.md`, no una grabación de sesión real.

## Comandos

```bash
npm install       # instalar dependencias
npm run dev       # servidor de desarrollo (Vite), http://localhost:5173
npm run build     # type-check (tsc -b) + build de producción a dist/
npm run lint      # ESLint
npm test          # tests unitarios (Vitest + Testing Library)
```

## Desarrollo — proxy al backend

En desarrollo, `/api` y `/ping` se redirigen (proxy de Vite) hacia
`http://localhost:8000`, donde se espera el backend de FastAPI corriendo
localmente. Esto evita configurar CORS real durante el desarrollo — es un
bypass exclusivo de este entorno, no válido en producción. El manejo de
CORS real para producción queda pendiente (ver
`docs/frontend/frontend-implementation-plan.md`).

## `.claude/launch.json`

No es convención de VS Code ni archivo inerte — es la configuración que lee
la herramienta de preview de navegador de Claude Code (`preview_start` con
`{name: "frontend-dev"}`) para levantar `npm run dev` y abrir una pestaña de
preview apuntando a `http://localhost:5173`. Entró sin mención explícita en
el commit de Fase 1 porque Claude Code lo generó solo, la primera vez que
una sesión necesitó previsualizar el frontend en el navegador integrado — no
hace falta tocarlo a mano.

## Tema

El tema visual está fijo a "Instrumento" — no es seleccionable por el
usuario. Sí es alternable entre modo claro y oscuro, con la preferencia
persistida en `localStorage` y detección inicial de
`prefers-color-scheme`.
