# Implementaciones de referencia en R para las mismas 9 series.
# Paquetes: stats (base R), randtests, Kendall, trend, lmom (Hosking).
# Correr desde la raíz del repo:
#   Rscript docs/auditoria/comparacion-herramientas/scripts/referencia_r.R
# Lee resultados/series.csv (lo escribe correr_metis.py).

suppressPackageStartupMessages({
  library(randtests); library(Kendall); library(trend); library(lmom)
})
res <- "docs/auditoria/comparacion-herramientas/resultados"
datos <- read.csv(file.path(res, "series.csv"))
periodos <- c(2, 5, 10, 20, 25, 50, 100, 200, 500)

e1 <- list(); q <- list()
for (est in unique(datos$estacion)) {
  x <- datos$valor[datos$estacion == est]
  n <- length(x)
  # Anderson: autocorrelación serial con stats::acf (mismo estimador que III-1:
  # media global y denominador sum((x - media)^2)); bandas de III-3.
  kmax <- ceiling(n / 3)
  r <- acf(x, lag.max = kmax, plot = FALSE, demean = TRUE)$acf[-1]
  k <- seq_len(kmax)
  sup <- (-1 + 1.96 * sqrt(n - k - 1)) / (n - k)
  inf <- (-1 - 1.96 * sqrt(n - k - 1)) / (n - k)
  fuera <- sum(r > sup | r < inf)
  # Wald-Wolfowitz: randtests::runs.test con umbral en la media.
  ww <- runs.test(x, threshold = mean(x), alternative = "two.sided")
  # t de Student (mitades, varianzas iguales): stats::t.test.
  n1 <- n %/% 2
  tt <- t.test(x[1:n1], x[(n1 + 1):n], var.equal = TRUE)
  # Mann-Kendall: Kendall::MannKendall (S y Var(S) con corrección por empates)
  # y trend::mk.test (z).
  mk <- MannKendall(x)
  mkz <- (mk$S - sign(mk$S)) / sqrt(mk$varS)
  mk2 <- mk.test(x)
  # Kolmogorov-Smirnov entre mitades: stats::ks.test, tipificado con A.57.
  ks <- suppressWarnings(ks.test(x[1:n1], x[(n1 + 1):n]))
  ksz <- unname(ks$statistic) * sqrt(n1 * (n - n1) / n)
  e1[[est]] <- data.frame(
    estacion = est, n = n, anderson_r1 = r[1], anderson_lags_fuera = fuera,
    ww_rachas = unname(ww$runs), ww_z = unname(ww$statistic), ww_p = ww$p.value,
    t_student = unname(tt$statistic), t_student_p = tt$p.value,
    mk_z = mkz, mk_z_trend = unname(mk2$statistic), mk_p = mk2$p.value,
    ks_z = ksz, ks_p = ks$p.value
  )
  # Etapa 2: ajuste por momentos-L con lmom (Hosking) y cuantiles exactos.
  if (n >= 10) {
    lm <- samlmu(x)
    F <- 1 - 1 / periodos
    ajustes <- list(
      c("normal", "ml", "nor"), c("gumbel", "ml", "gum"), c("gve", "ml", "gev"),
      c("gamma2p", "ml", "gam"), c("lognormal3p", "ml", "ln3"),
      c("logpearson3", "ml", "pe3"), c("exponencial_x0_beta", "ml", "exp")
    )
    for (a in ajustes) {
      par <- tryCatch(do.call(paste0("pel", a[3]), list(lm)), error = function(e) NULL)
      if (is.null(par)) next
      v <- tryCatch(do.call(paste0("qua", a[3]), list(F, par)), error = function(e) rep(NA, length(F)))
      q[[paste(est, a[3])]] <- data.frame(
        estacion = est, distribucion = a[1], metodo = a[2], familia_lmom = a[3],
        T = periodos, r_lmom = v
      )
    }
  }
}
write.csv(do.call(rbind, e1), file.path(res, "r_etapa1.csv"), row.names = FALSE)
write.csv(do.call(rbind, q), file.path(res, "r_lmom_cuantiles.csv"), row.names = FALSE)
cat("r_etapa1.csv y r_lmom_cuantiles.csv escritos\n")
cat(R.version.string, "| randtests", as.character(packageVersion("randtests")),
    "| Kendall", as.character(packageVersion("Kendall")),
    "| trend", as.character(packageVersion("trend")),
    "| lmom", as.character(packageVersion("lmom")), "\n")
