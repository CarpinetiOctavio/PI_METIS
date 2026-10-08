# Corre SAMHIA (SAMHIA_EST_v16.R, Dr. Ing. Carlos G. Catalini) sobre las mismas
# series y captura sus estadísticos en un CSV, sin modificar el archivo original.
#
# SAMHIA no se versiona en este repo (es código del director). Se le pasa la ruta:
#   Rscript correr_samhia.R ruta/a/SAMHIA_EST_v16.R salida.csv entrada1.xlsx [entrada2.xlsx ...]
# Conviene correrlo desde una carpeta de trabajo: SAMHIA escribe sus propios
# PDF y PNG en ./SAMHIA_Resultados_Est.
#
# Qué hace: lee el texto del script, (1) reemplaza la lista de archivos de
# entrada por los que se pasan acá, (2) agrega UNA instrucción al final de la
# sección D de analizar_variable_samhia() (justo antes de "E. GENERACIÓN DEL
# PDF") que copia a una tabla los estadísticos que SAMHIA ya calculó. Todo lo
# demás (limpieza, pruebas, gráficos y el PDF propio de SAMHIA) corre tal cual.

args <- commandArgs(trailingOnly = TRUE)
fuente <- args[1]
salida <- args[2]
entradas <- args[-(1:2)]

codigo <- readLines(fuente, encoding = "UTF-8", warn = FALSE)
i_pdf <- grep("E. GENERACI", codigo, fixed = TRUE)[1]
stopifnot(!is.na(i_pdf))
captura <- '
  .num <- function(v) if (is.null(v) || length(v) == 0) NA_real_ else as.numeric(v)[1]
  .SAMHIA_RES[[length(.SAMHIA_RES) + 1]] <<- data.frame(
    archivo = nombre_embalse, variable = nombre_variable, n = N,
    media = media_val, desvio = sd_val, asimetria = asymmetry, curtosis = kurt,
    kn = Kn, limite_superior = limite_superior, limite_inferior = limite_inferior,
    atipicos = nrow(datos_atipicos_df),
    anderson_t = .num(result_anderson$statistic), anderson_p = .num(result_anderson$p.value),
    ww_z = .num(test_ww$statistic), ww_p = .num(test_ww$p.value),
    spearman_rho = .num(test_spearman$estimate), spearman_p = .num(test_spearman$p.value),
    mw_w = .num(test_mann_whitney$statistic), mw_p = .num(test_mann_whitney$p.value),
    mood_z = .num(test_mood$statistic), mood_p = .num(test_mood$p.value),
    mk_tau = .num(mk_tau_val), mk_p = .num(mk_trend$p.value),
    dw = .num(dw_stat_val), dw_p = .num(dw_p_val),
    ljung_box = .num(lb_stat_val), ljung_box_p = .num(lb_p_val)
  )
'
codigo <- c(codigo[1:(i_pdf - 2)], captura, codigo[(i_pdf - 1):length(codigo)])
i_lista <- grep("^lista_archivos <- c\\(", codigo)
i_fin <- i_lista + which(codigo[(i_lista + 1):length(codigo)] == ")")[1]
codigo <- c(codigo[1:(i_lista - 1)],
            sprintf("lista_archivos <- c(%s)", paste(sprintf('"%s"', entradas), collapse = ", ")),
            codigo[(i_fin + 1):length(codigo)])

.SAMHIA_RES <- list()
options(repos = c(CRAN = "https://cloud.r-project.org"))
eval(parse(text = codigo, encoding = "UTF-8"), envir = globalenv())
write.csv(do.call(rbind, .SAMHIA_RES), salida, row.names = FALSE)
cat("\nCapturados", length(.SAMHIA_RES), "análisis en", salida, "\n")
