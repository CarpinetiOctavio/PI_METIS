# PENDIENTE — respuesta de Facundo: tolerancia de Anderson ante α

**Abierto desde el 19/10/2026.** Cuando Facundo responda, aplicar lo que corresponda según la sección "Qué hacer
con la respuesta" y **borrar este archivo** en el mismo PR. No bloquea nada: hoy la tolerancia queda fija en el 10 %, y
con α = 5 % el resultado no debería cambiar con ninguna respuesta (si cambiara, ver el punto 4 de la opción B).

Origen: [DECISIÓN 078](decisiones/decision078.md), "Lo que no depende de α y queda fijo". La misma pregunta está
registrada en [`auditoria/pendientes/pendientes-facundo.md`](auditoria/pendientes/pendientes-facundo.md), sección
"Nivel de significancia configurable (18/10/2026)".

## El problema en dos líneas

Desde la DECISIÓN 078, α se elige entre 1 %, 5 % y 10 %. En Anderson eso mueve las **bandas** de cada rezago
(Ec. III-3), pero la **tolerancia** del veredicto, `⌈0,10 · k_max⌉` rezagos fuera de banda (DECISIONES 012 y 016),
quedó fija. No sabemos si ese 10 % es una regla propia de la prueba o si está atado al nivel de significancia.

## Mensaje enviado a Facundo (19/10/2026)

> Hola Facundo, una consulta sobre la prueba de independencia de Anderson, a raíz de lo que me respondiste del nivel
> de significancia.
>
> Siguiendo tu sugerencia, METIS ahora deja elegir α entre 1 %, 5 % (por defecto) y 10 % para toda la Etapa 1.
>
> En Anderson calculamos el coeficiente de autocorrelación r_k para cada rezago k = 1 hasta n/3, y cada uno se
> compara contra sus bandas de confianza (Ec. III-3 de tu tesis). Esas bandas dependen de α, así que ahora se
> ensanchan o se angostan según el nivel elegido.
>
> Después, para dar el veredicto, METIS acepta la independencia si la cantidad de rezagos que caen fuera de las bandas
> no supera el 10 % del total de rezagos calculados. Por ejemplo, con n = 40 se calculan 14 rezagos y se toleran hasta
> 2 fuera de banda. Ese 10 % lo dejamos fijo: no cambia con α.
>
> Mi pregunta es: ese 10 % de rezagos fuera de banda, ¿es una regla propia de la prueba, que se mantiene igual con
> cualquier nivel de significancia? ¿O debería cambiar junto con α? En ese caso, ¿con qué regla?
>
> Con α = 5 % no cambia nada en ningún caso; es solo para que 1 % y 10 % queden bien aplicados. Gracias!

## Qué hacer con la respuesta

### A. "Queda fijo" (el 10 % es de la prueba)

Solo documentación, sin código:

1. Revisión fechada en `docs/decisiones/decision078.md`: la tolerancia queda fija, confirmado por Facundo (fecha y
   cita). Actualizar la fila 078 de `docs/decisiones/README.md` si cambia el estado.
2. Marcar la pregunta como respondida en `docs/auditoria/pendientes/pendientes-facundo.md`.
3. Borrar este archivo.

### B. "Cambia con α" (con la regla que indique)

1. **Código:** `backend/metis/core/etapa1/independence.py`, la línea `tolerancia = math.ceil(k_max * 0.10)`, pasa a
   depender de `alfa` según la regla de Facundo. La regla va con su referencia en
   `.claude/rules/core/formulas-etapa1.md` §2 ("Veredicto"), que hoy dice `tolerancia = ceil(0.10 · k_max)`.
2. **Textos que hoy dicen que la tolerancia no depende de α** (hay que cambiarlos):
   - `backend/metis/reportes/pdf.py`, nota sobre las tablas de pruebas: "Helmert y la tolerancia de rezagos de
     Anderson no dependen de él".
   - `frontend/src/i18n/explicaciones.ts`, interpretación de Anderson: "la tolerancia del 10%".
   - `.claude/rules/core/formulas-etapa1.md` (encabezado) y `.claude/rules/architecture/constraints.md` (α configurable).
3. **Tests:** uno por nivel de α en `backend/tests/unit/core/etapa1/` con la tolerancia esperada, y revisar
   `test_significancia.py`.
4. **No regresión:** si con α = 5 % la regla nueva da un número distinto de `⌈0,10 · k_max⌉`, va a fallar
   `backend/tests/unit/core/pipeline/test_no_regresion_alfa.py`. **No regenerar la referencia sin más:** cambia
   resultados ya auditados contra la tesis, así que hay que confirmarlo con Facundo y dejarlo explícito en la
   decisión.
5. Revisión fechada de la DECISIÓN 078 (y de la 012 si corresponde), con la cita de Facundo. Caso nuevo en
   `docs/calidad/casos-de-prueba.md` si la regla agrega un borde.
6. Marcar la pregunta como respondida en `pendientes-facundo.md` y borrar este archivo.
