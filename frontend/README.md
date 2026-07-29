# METIS — Frontend

Aplicación Vite + React + TypeScript. Implementa el scaffold de las 8
pantallas de CU-01/CU-02 (entrada, configuración, stream, resultados,
ranking, eventos de diseño, historial, verificación de mail) con routing,
layout común y el tema visual fijo "Instrumento" (claro/oscuro).

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

## Tema

El tema visual está fijo a "Instrumento" — no es seleccionable por el
usuario. Sí es alternable entre modo claro y oscuro, con la preferencia
persistida en `localStorage` y detección inicial de
`prefers-color-scheme`.
