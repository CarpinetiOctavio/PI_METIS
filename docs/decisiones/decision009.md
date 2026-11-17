# DECISIÓN 009 — Convención de nombres de distribuciones en el pipeline
**Fecha:** 17 de Mayo de 2026
**Estado:** IMPLEMENTADO

Las claves que identifican distribuciones en `DISABLED_WITH_ZEROS` y
`PENDING_ZEROS_CONFIRMATION` deben coincidir exactamente con los nombres
de módulo en `distributions/` (sin guiones entre palabras, todo minúsculas):
`lognormal2p`, `logpearson3`, `gamma2p`, `exponencial_beta`, etc.

### Bug encontrado durante smoke test de Fase 1
`DISABLED_WITH_ZEROS` usaba `log_normal_2p` con guiones bajos entre palabras,
pero el pipeline usa `lognormal2p`. El lookup `nombre in DISABLED_WITH_ZEROS`
fallaba silenciosamente — las distribuciones afectadas no quedaban deshabilitadas
ante series con ceros. Detectado al verificar el output del smoke test con
`tiene_ceros=True`. Corregido antes de commitear.

### Regla
Cualquier cambio en nombres de módulo de distribuciones requiere verificar
consistencia con estas constantes en `distributions/__init__.py`.
