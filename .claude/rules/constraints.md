# Restricciones y Comportamientos No Negociables

## Lo que NUNCA se cambia sin consultar a Octavio

### Stack
- Python en backend — no agregar otros lenguajes de backend
- PostgreSQL — no reemplazar por SQLite ni ninguna otra BD
- React + TypeScript — no JavaScript puro ni otro framework

### Seguridad
- JWT en HttpOnly Cookie — nunca en localStorage ni sessionStorage
- API Keys almacenadas como hash bcrypt — nunca texto plano en BD
- Variables de entorno en .env — nunca credenciales en código
- .env nunca se commitea — está en .gitignore desde el inicio
> auth/ implementado: usuario/contraseña + bcrypt + JWT HttpOnly Cookie con verificación @ucc.edu.ar. Ver decisions-log.md — DECISIÓN 001.
> Parte 2 (envío real de mail con aiosmtplib) pendiente de credenciales SMTP de IT.

### Lógica de negocio
- α = 5% fijo — no es configurable por el usuario en V1.0
- El pipeline siempre arranca por Etapa 1 — nunca se puede ejecutar Etapa 2 directamente
- METIS no sugiere distribución ganadora — presenta el ranking, el usuario decide
- METIS no corrige datos — detecta, advierte, y continúa (excepto CU-03 con auto_clean=true)
- Chow aplica sobre logaritmos — si hay ceros en caudal_precipitacion, marcar como no_ejecutada

### CU-03
- CU-03 expone solo Etapa 1 — nunca Etapa 2
- CU-03 es completamente stateless — ningún estado entre llamadas
- CU-03 no tiene endpoint outlier-decision ni design-events

---

## Comportamientos específicos que se implementan tal como están

### Wald-Wolfowitz con n ≤ 40
NO omitir. NO bloquear. Ejecutar CON advertencia explícita `TEST_WARNING_SMALL_SAMPLE`.
Fuente: Facundo — reunión 14/04.

### Anderson acepta, Wald-Wolfowitz rechaza
Resultado final = INDEPENDIENTE. Incluir nota del resultado de Wald en el output.
Anderson manda en independencia.

### Cramer rechaza homogeneidad
→ nivel = `homogeneidad_critica` → warning CRÍTICO.
No importa si Helmert o t de Student aprobaron.

### Chow detecta atípico — CU-01/CU-02
Stream pausa. Se emite evento `outlier_detected`. El pipeline NO continúa hasta recibir
decisión del usuario via POST /analysis/outlier-decision.

### Gráficos con eje temporal
Siempre dos versiones: calendario (ene-dic) e hidrológico (jul-jun).
Ambas son obligatorias. Aplica a: serie temporal, boxplot mensual, gráfico Chow, gráfico ajuste, eventos de diseño.

### PDF de exportación — CU-01
Se genera on-demand, no se almacena en disco.
Contenido varía según lo ejecutado (solo Etapa 1 vs pipeline completo) y el modo (paso a paso vs experto).
En modo paso a paso: incluir fórmulas con valores sustituidos.
En modo experto: resultados directos, sin fórmulas ni explicaciones.

---

## Pendientes que afectan implementación — no asumir

### Con Facundo (distribuciones ante ceros)
Las siguientes distribuciones ante series con ceros en caudal_precipitacion están pendientes de confirmación.
**No asumir comportamiento — preguntar a Octavio antes de implementar:**
- Gamma 3 parámetros
- Exponencial x₀ y β
- Generalizada de Pareto
- Log-Normal 3 parámetros
- Generalizada Exponencial

### Con área de sistemas UCC (deploy)
El CD (deploy automático a producción) está bloqueado hasta confirmar:
- Docker disponible en servidores UCC
- Acceso SSH desde GitHub Actions
- Restricciones de red/firewall

### Datos de fixtures de testing
Los datos de las 9 estaciones de la tesis de Facundo para los tests de regresión matemática
están pendientes de confirmación en formato digital.

---

## Scope V1.0 — lo que NO entra

- Bandas de confianza (RF-GEN-O-11): feature candidata, no prioritaria
- Exportación a Google Drive institucional: feature candidata
- Análisis raster: fuera del alcance
- Tests de carga o performance
- Tests end-to-end de UI automatizados (Selenium/Playwright)
- CD automático a producción (bloqueado por infraestructura UCC)

---

## GitHub Flow — branching

```
main           → producción, siempre estable, nunca commit directo
staging        → integración, nunca commit directo
feature/xxx    → funcionalidad nueva, sale de staging, PR hacia staging
fix/xxx        → corrección, sale de staging, PR hacia staging
```

Flujo de tres niveles:
  feature/xxx → staging  (PR, revisión, CI)
  staging → main         (PR, solo cuando staging está estable)

Nunca merge directo de feature a main.
CI corre en cada PR antes del merge. No mergear sin que CI pase.
