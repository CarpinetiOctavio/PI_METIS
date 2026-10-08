"""Informe PDF de un análisis persistido de CU-01 — DECISIÓN 075.

Recibe el dict de `services/analysis_service.py::get_analysis_by_id()` (el mismo
payload que `GET /history/{id}`) y devuelve los bytes del PDF. Es presentación
pura: no importa nada de `api/`, `services/`, `db/` ni `core/`, no recalcula
ningún estadístico y no toca la BD. Todo lo que dibuja ya se calculó en `core/`
y quedó persistido en `analysis_results`.

Siempre en formato Experto (`constraints.md`, "PDF de exportación — CU-01"):
resultados directos, sin fórmulas ni explicaciones, sea cual sea el modo con
que se corrió el análisis. Tampoco marca una distribución ganadora: el ranking
se presenta ordenado por EEA y la única distribución resaltada es la que eligió
el usuario.
"""

import io
import math
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# DejaVu Sans viene con matplotlib: cubre α, β, ≤, subíndices y acentos, que las
# fuentes estándar de PDF (Helvetica, WinAnsi) no tienen. Así no se suma ningún
# archivo de fuente al repo.
_DIR_FUENTES = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
_FUENTE = "DejaVuSans"
_FUENTE_NEGRITA = "DejaVuSans-Bold"


def _registrar_fuentes() -> None:
    if _FUENTE in pdfmetrics.getRegisteredFontNames():
        return
    pdfmetrics.registerFont(TTFont(_FUENTE, str(_DIR_FUENTES / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(
        TTFont(_FUENTE_NEGRITA, str(_DIR_FUENTES / "DejaVuSans-Bold.ttf"))
    )


# ---------------------------------------------------------------------------
# Rótulos
# ---------------------------------------------------------------------------

_PRUEBAS = {
    "anderson": "Anderson",
    "wald_wolfowitz": "Wald-Wolfowitz",
    "helmert": "Helmert",
    "t_student": "t de Student",
    "cramer": "Cramer",
    "mann_kendall": "Mann-Kendall",
    "kolmogorov_smirnov": "Kolmogorov-Smirnov",
    "chow": "Chow",
}

_DISTRIBUCIONES = {
    "uniforme": "Uniforme",
    "normal": "Normal",
    "gumbel": "Gumbel",
    "gve": "GVE",
    "lognormal2p": "Log-Normal 2p",
    "lognormal3p": "Log-Normal 3p",
    "logpearson3": "Log-Pearson III",
    "gamma2p": "Gamma 2p",
    "gamma3p": "Gamma 3p",
    "exponencial_beta": "Exponencial (β)",
    "exponencial_x0_beta": "Exponencial (x₀, β)",
    "gen_pareto": "Generalizada de Pareto",
    "gen_exponencial": "Generalizada Exponencial",
}

_METODOS = {
    "momentos": "Momentos",
    "momentos_directo": "Momentos (directo)",
    "momentos_indirecto": "Momentos (indirecto)",
    "mv": "Máxima verosimilitud",
    "ml": "Momentos-L",
    "me": "Máxima entropía",
    "mc": "Mínimos cuadrados",
    "mpp": "Momentos de probabilidad pesada",
}

_STATUS_METODO = {
    "no_converge": "no converge",
    "no_aplicable": "no aplicable",
    "disabled_zeros": "deshabilitada por ceros",
    "disabled_negatives": "deshabilitada por negativos",
}

_VEREDICTOS = {
    "aprobada": "Aprobada",
    "rechazada": "Rechazada",
    "no_ejecutada": "No ejecutada",
}

_NIVELES = {
    "independiente": "Independiente",
    "dependiente": "Dependiente (crítico)",
    "homogeneidad_ok": "Homogénea",
    "homogeneidad_warning": "Homogénea con advertencias",
    "homogeneidad_critica": "No homogénea (crítico)",
    "validado": "Validado",
    "con_warnings": "Con advertencias",
    "rechazado": "Rechazado",
}

_NOTAS_PRUEBA = {
    "TEST_WARNING_SMALL_SAMPLE": "Muestra chica",
    "TEST_NOT_EXECUTED_ZEROS": "Serie con ceros",
    "TEST_NOT_EXECUTED_NEGATIVES": "Serie con valores negativos",
    "TEST_NOT_EXECUTED_CONDITION": "Condición de la prueba no cumplida",
    "TEST_NOT_EXECUTED_MIN_SAMPLES": "Menos de 10 datos",
}

_TIPOS_VARIABLE = {
    "caudal_precipitacion": "Caudal / precipitación",
    "otro": "Otro",
}

_RESOLUCIONES = {"anual": "Anual", "mensual": "Mensual", "diaria": "Diaria"}

_MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]  # fmt: skip


# ---------------------------------------------------------------------------
# Período de retorno: rótulos según la serie que se ajustó (DECISIÓN 076)
# ---------------------------------------------------------------------------
# METIS ajusta siempre la serie de máximos anuales (DECISIÓN 066): con carga
# mensual o diaria, el paso 0 la agrega a un máximo por año antes de Etapa 1.
# T = 1 / (1 - F) se mide en el intervalo de muestreo de la serie ajustada, así
# que está en años para las tres resoluciones. Lo que cambia con la carga es
# qué representa el valor de diseño y qué año se usó para agregar, y eso es lo
# que estos rótulos dejan explícito. Mismo texto que
# frontend/src/i18n/periodoRetorno.ts: si se cambia uno, cambiar el otro.

_MAXIMO_AGREGADO = {
    ("mensual", None): "valor mensual máximo",
    ("diaria", "pico"): "pico diario máximo",
    ("diaria", "media"): "media diaria máxima",
}

_MAXIMO_CON_ARTICULO = {
    ("mensual", None): "el valor mensual máximo",
    ("diaria", "pico"): "el pico diario máximo",
    ("diaria", "media"): "la media diaria máxima",
}

_CARGA_AGREGADA = {
    ("mensual", None): "una serie mensual",
    ("diaria", "pico"): "una serie de picos diarios",
    ("diaria", "media"): "una serie de medias diarias",
}


def _contexto_serie(detalle: dict) -> tuple[str | None, int | None, str | None]:
    """(resolución de la carga, mes de inicio del año, variable diaria)."""
    config = detalle.get("configuracion") or {}
    datos = (detalle.get("etapa1") or {}).get("datos") or {}
    resolucion = datos.get("resolucion_original")
    mes = config.get("mes_inicio_anio")
    if not (isinstance(mes, int) and 1 <= mes <= 12):
        mes = None
    variable = None
    if resolucion == "diaria":
        variable = "media" if config.get("variable_diaria") == "media" else "pico"
    return resolucion, mes, variable


def _rango_anio(mes: int) -> str:
    fin = 12 if mes == 1 else mes - 1
    return f"de {_MESES[mes - 1]} a {_MESES[fin - 1]}"


def _clave_agregada(detalle: dict) -> tuple[str, str | None] | None:
    resolucion, _, variable = _contexto_serie(detalle)
    clave = (resolucion, variable)
    return clave if clave in _MAXIMO_AGREGADO else None


def _unidad_periodo_retorno(detalle: dict) -> str:
    """'años', o 'años, de julio a junio' cuando la serie se agregó."""
    _, mes, _ = _contexto_serie(detalle)
    if _clave_agregada(detalle) is None or mes is None:
        return "años"
    return f"años, {_rango_anio(mes)}"


def _rotulo_eje_periodo_retorno(detalle: dict) -> str:
    return f"Período de retorno T [{_unidad_periodo_retorno(detalle)}]"


def _rotulo_valor_diseno(detalle: dict) -> str:
    clave = _clave_agregada(detalle)
    if clave is None:
        return "Valor de diseño"
    return f"Valor de diseño ({_MAXIMO_AGREGADO[clave]} del año)"


def _nota_periodo_retorno(detalle: dict) -> str:
    promedio = (
        "el valor de diseño de T años es el que se espera igualar o superar, en "
        "promedio, una vez cada T años (probabilidad 1/T de ser superado en un año "
        "cualquiera)."
    )
    clave = _clave_agregada(detalle)
    if clave is None:
        return (
            "La distribución se ajustó a la serie de máximos anuales, por eso T se "
            "mide en años: " + promedio
        )
    _, mes, _ = _contexto_serie(detalle)
    anio = f"de cada año ({_rango_anio(mes)})" if mes is not None else "de cada año"
    unidad_carga = "meses" if clave[0] == "mensual" else "días"
    return (
        f"Se cargó {_CARGA_AGREGADA[clave]}. METIS no ajusta la distribución a esos "
        f"valores: toma {_MAXIMO_CON_ARTICULO[clave]} {anio} y ajusta la serie de "
        f"esos máximos anuales. Por eso T se mide en años y no en {unidad_carga}: "
        + promedio
    )


def _rotulo(tabla: dict, clave: str | None) -> str:
    if clave is None:
        return "—"
    return tabla.get(clave, clave.replace("_", " ").capitalize())


def _num(valor, decimales: int = 4) -> str:
    if valor is None or isinstance(valor, bool):
        return "—"
    if isinstance(valor, int):
        return str(valor)
    if not math.isfinite(valor):
        return "—"
    return f"{valor:.{decimales}f}"


# ---------------------------------------------------------------------------
# Estilos y piezas de maquetado
# ---------------------------------------------------------------------------

_TINTA = colors.HexColor("#1f2933")
_TENUE = colors.HexColor("#5f6b76")
_LINEA = colors.HexColor("#c9d1d9")
_FONDO_CABECERA = colors.HexColor("#eef2f5")
_ACENTO = colors.HexColor("#2f5f8a")


def _estilos() -> dict[str, ParagraphStyle]:
    base = ParagraphStyle(
        "base", fontName=_FUENTE, fontSize=9, leading=12, textColor=_TINTA
    )
    return {
        "base": base,
        "titulo": ParagraphStyle(
            "titulo", parent=base, fontName=_FUENTE_NEGRITA, fontSize=17, leading=21
        ),
        "subtitulo": ParagraphStyle(
            "subtitulo", parent=base, textColor=_TENUE, spaceAfter=10
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base,
            fontName=_FUENTE_NEGRITA,
            fontSize=13,
            leading=16,
            spaceBefore=14,
            spaceAfter=6,
            textColor=_ACENTO,
            keepWithNext=1,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base,
            fontName=_FUENTE_NEGRITA,
            fontSize=10.5,
            leading=14,
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=1,
        ),
        "celda": ParagraphStyle("celda", parent=base, fontSize=8, leading=10),
        "celda_negrita": ParagraphStyle(
            "celda_negrita",
            parent=base,
            fontName=_FUENTE_NEGRITA,
            fontSize=8,
            leading=10,
        ),
        "nota": ParagraphStyle(
            "nota", parent=base, fontSize=8, leading=10.5, textColor=_TENUE
        ),
        # Nota que presenta lo que sigue (tabla o gráfico): no queda sola al pie.
        "nota_previa": ParagraphStyle(
            "nota_previa",
            parent=base,
            fontSize=8,
            leading=10.5,
            textColor=_TENUE,
            keepWithNext=1,
        ),
        "aviso": ParagraphStyle(
            "aviso",
            parent=base,
            backColor=colors.HexColor("#fff4e5"),
            borderColor=colors.HexColor("#e0a458"),
            borderWidth=0.5,
            borderPadding=5,
            spaceBefore=4,
            spaceAfter=8,
        ),
    }


def _p(texto: str, estilo: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(texto), estilo)


def _tabla(
    filas: list[list[str]],
    anchos: list[float],
    est: dict[str, ParagraphStyle],
    *,
    cabecera: bool = True,
    filas_resaltadas: tuple[int, ...] = (),
) -> Table:
    celdas = [
        [
            _p(texto, est["celda_negrita"] if cabecera and i == 0 else est["celda"])
            for texto in fila
        ]
        for i, fila in enumerate(filas)
    ]
    tabla = Table(celdas, colWidths=anchos, repeatRows=1 if cabecera else 0)
    estilo = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, _LINEA),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if cabecera:
        estilo.append(("BACKGROUND", (0, 0), (-1, 0), _FONDO_CABECERA))
    for fila in filas_resaltadas:
        estilo.append(("BACKGROUND", (0, fila), (-1, fila), colors.HexColor("#e6eef6")))
    tabla.setStyle(TableStyle(estilo))
    return tabla


def _figura_a_imagen(fig: Figure, ancho: float) -> Image:
    FigureCanvasAgg(fig)
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=200, bbox_inches="tight")
    buffer.seek(0)
    ancho_px, alto_px = fig.get_size_inches()
    return Image(buffer, width=ancho, height=ancho * alto_px / ancho_px)


def _figura(alto_pulgadas: float = 2.8) -> tuple[Figure, object]:
    fig = Figure(figsize=(7.2, alto_pulgadas))
    ax = fig.add_subplot(1, 1, 1)
    ax.grid(True, color="#e3e7eb", linewidth=0.6)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(labelsize=8)
    return fig, ax


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------


def _grafico_serie(etapa1: dict) -> Figure | None:
    datos = etapa1.get("datos") or {}
    serie = datos.get("serie_efectiva")
    if not serie:
        return None
    timestamps = datos.get("timestamps_efectivos")
    x = (
        [t["anio"] for t in timestamps]
        if timestamps and len(timestamps) == len(serie)
        else list(range(1, len(serie) + 1))
    )
    fig, ax = _figura()
    ax.plot(x, serie, color="#2f5f8a", linewidth=1.2, marker="o", markersize=3)
    media = (etapa1.get("descriptive") or {}).get("media")
    if media is not None:
        ax.axhline(media, color="#8a96a3", linewidth=0.8, linestyle="--", label="Media")
    chow = next(iter(etapa1.get("atipicos") or []), None)
    indice = datos.get("indice_atipico")
    if (
        chow is not None
        and chow.get("veredicto") == "rechazada"
        and indice is not None
        and 0 <= indice < len(serie)
    ):
        ax.plot(
            [x[indice]],
            [serie[indice]],
            linestyle="none",
            marker="o",
            markersize=8,
            markerfacecolor="none",
            markeredgecolor="#b4443c",
            markeredgewidth=1.5,
            label="Atípico detectado (Chow)",
        )
    ax.set_xlabel("Año" if timestamps else "Orden", fontsize=8)
    ax.set_ylabel("Valor", fontsize=8)
    if ax.get_legend_handles_labels()[0]:
        ax.legend(fontsize=7, frameon=False)
    return fig


def _grafico_correlograma(anderson: dict) -> Figure | None:
    desglose = (anderson.get("explicacion") or {}).get("desglose")
    if not desglose:
        return None
    k = [fila["k"] for fila in desglose]
    fig, ax = _figura(2.4)
    colores = ["#b4443c" if fila.get("fuera") else "#2f5f8a" for fila in desglose]
    ax.bar(k, [fila["r_k"] for fila in desglose], color=colores, width=0.6)
    ax.plot(k, [fila["banda_sup"] for fila in desglose], color="#8a96a3", linewidth=0.9)
    ax.plot(
        k,
        [fila["banda_inf"] for fila in desglose],
        color="#8a96a3",
        linewidth=0.9,
        label="Límites de confianza (95 %)",
    )
    ax.axhline(0, color="#5f6b76", linewidth=0.6)
    ax.set_xlabel("Rezago k", fontsize=8)
    ax.set_ylabel("r_k", fontsize=8)
    ax.legend(fontsize=7, frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0))
    return fig


def _grafico_ajuste(
    seleccion: dict, puntos: list[dict], rotulo_t: str
) -> Figure | None:
    curva = [
        c for c in seleccion.get("curva_ajuste") or [] if c.get("valor") is not None
    ]
    if not curva and not puntos:
        return None
    fig, ax = _figura(3.0)
    if puntos:
        ax.plot(
            [p["periodo_retorno"] for p in puntos],
            [p["valor"] for p in puntos],
            linestyle="none",
            marker="o",
            markersize=3.5,
            color="#1f2933",
            label="Datos observados (Weibull)",
        )
    if curva:
        ax.plot(
            [c["periodo_retorno"] for c in curva],
            [c["valor"] for c in curva],
            color="#2f5f8a",
            linewidth=1.4,
            label="Distribución ajustada",
        )
    eventos = [
        e for e in seleccion.get("eventos_diseno") or [] if e.get("valor") is not None
    ]
    if eventos:
        ax.plot(
            [e["periodo_retorno"] for e in eventos],
            [e["valor"] for e in eventos],
            linestyle="none",
            marker="D",
            markersize=4.5,
            color="#c07a2c",
            label="Eventos de diseño",
        )
    ax.set_xscale("log")
    ax.set_xlabel(rotulo_t, fontsize=8)
    ax.set_ylabel("Valor", fontsize=8)
    ax.legend(fontsize=7, frameon=False)
    return fig


def _grafico_serie_excluidos(etapa1: dict, excluidos: list[dict]) -> Figure | None:
    """Serie analizada con los puntos excluidos de la simulación marcados."""
    datos = etapa1.get("datos") or {}
    serie = datos.get("serie_efectiva")
    timestamps = datos.get("timestamps_efectivos")
    if not serie or not timestamps or len(timestamps) != len(serie):
        return None
    x = [t["anio"] for t in timestamps]
    fig, ax = _figura()
    ax.plot(x, serie, color="#2f5f8a", linewidth=1.2, marker="o", markersize=3)
    indices = [e["indice"] for e in excluidos if 0 <= e["indice"] < len(serie)]
    if indices:
        ax.plot(
            [x[i] for i in indices],
            [serie[i] for i in indices],
            linestyle="none",
            marker="X",
            markersize=8,
            color="#b4443c",
            label="Excluido en la simulación",
        )
        ax.legend(fontsize=7, frameon=False)
    ax.set_xlabel("Año", fontsize=8)
    ax.set_ylabel("Valor", fontsize=8)
    return fig


def _grafico_ajuste_comparado(
    original: dict,
    puntos_original: list[dict],
    simulada: dict,
    puntos_simulada: list[dict],
    rotulo_t: str,
) -> Figure | None:
    """Misma distribución+método ajustada con y sin los puntos excluidos."""

    def curva(seleccion: dict) -> list[dict]:
        return [
            c for c in seleccion.get("curva_ajuste") or [] if c.get("valor") is not None
        ]

    curva_original, curva_simulada = curva(original), curva(simulada)
    if not curva_original and not curva_simulada:
        return None
    fig, ax = _figura(3.0)
    if puntos_original:
        ax.plot(
            [p["periodo_retorno"] for p in puntos_original],
            [p["valor"] for p in puntos_original],
            linestyle="none",
            marker="o",
            markersize=4,
            markerfacecolor="none",
            markeredgecolor="#8a96a3",
            label="Datos — original",
        )
    if puntos_simulada:
        ax.plot(
            [p["periodo_retorno"] for p in puntos_simulada],
            [p["valor"] for p in puntos_simulada],
            linestyle="none",
            marker="o",
            markersize=3,
            color="#1f2933",
            label="Datos — sin los puntos",
        )
    if curva_original:
        ax.plot(
            [c["periodo_retorno"] for c in curva_original],
            [c["valor"] for c in curva_original],
            color="#8a96a3",
            linewidth=1.3,
            linestyle="--",
            label="Ajuste — original",
        )
    if curva_simulada:
        ax.plot(
            [c["periodo_retorno"] for c in curva_simulada],
            [c["valor"] for c in curva_simulada],
            color="#2f5f8a",
            linewidth=1.4,
            label="Ajuste — sin los puntos",
        )
    ax.set_xscale("log")
    ax.set_xlabel(rotulo_t, fontsize=8)
    ax.set_ylabel("Valor", fontsize=8)
    ax.legend(fontsize=7, frameon=False)
    return fig


# ---------------------------------------------------------------------------
# Secciones
# ---------------------------------------------------------------------------

_ANCHO_UTIL = A4[0] - 4 * cm


def _texto_particion(particion) -> str:
    if isinstance(particion, dict):
        return (
            f"Personalizada ({particion.get('n1_pct')} % / {particion.get('n2_pct')} %)"
        )
    return "Por defecto (60 % / 30 %)"


def _seccion_datos(detalle: dict, autor: str | None, est) -> list:
    config = detalle.get("configuracion") or {}
    etapa1 = detalle.get("etapa1") or {}
    resolucion = (etapa1.get("datos") or {}).get("resolucion_original")
    etapas = detalle.get("etapas") or []
    filas = [
        ["Archivo", config.get("nombre_archivo") or "—"],
        ["Fecha del análisis", _fecha(detalle.get("created_at"))],
    ]
    if autor:
        filas.append(["Usuario", autor])
    filas += [
        ["Tipo de variable", _rotulo(_TIPOS_VARIABLE, detalle.get("tipo_variable"))],
        ["Etapas ejecutadas", "Etapa 1 y Etapa 2" if "2" in etapas else "Etapa 1"],
        ["Resolución de la carga", _rotulo(_RESOLUCIONES, resolucion)],
    ]
    mes = config.get("mes_inicio_anio")
    if isinstance(mes, int) and 1 <= mes <= 12:
        filas.append(["Inicio del año", _MESES[mes - 1].capitalize()])
    if resolucion == "diaria" and config.get("variable_diaria"):
        filas.append(
            [
                "Valores diarios",
                "Medias diarias"
                if config["variable_diaria"] == "media"
                else "Picos diarios",
            ]
        )
    if "cramer_particion" in config:
        filas.append(
            ["Partición de Cramer", _texto_particion(config["cramer_particion"])]
        )
    filas.append(
        ["Nivel de confianza", _rotulo(_NIVELES, etapa1.get("nivel_confianza"))]
    )
    return [
        _p("Datos del análisis", est["h1"]),
        _tabla(filas, [4.5 * cm, _ANCHO_UTIL - 4.5 * cm], est, cabecera=False),
    ]


def _advertencias(warnings: list[dict], est) -> list:
    if not warnings:
        return [_p("Sin advertencias.", est["nota"])]
    filas = [["Nivel", "Advertencia"]]
    for w in warnings:
        nivel = "Crítica" if w.get("nivel") == "critico" else "Normal"
        filas.append([nivel, w.get("descripcion") or w.get("codigo") or "—"])
    return [_tabla(filas, [2.2 * cm, _ANCHO_UTIL - 2.2 * cm], est)]


def _sin_duplicados(*listas: list[dict]) -> list[dict]:
    vistas = set()
    resultado = []
    for lista in listas:
        for w in lista or []:
            clave = (w.get("codigo"), w.get("descripcion"))
            if clave not in vistas:
                vistas.add(clave)
                resultado.append(w)
    return resultado


def _nota_prueba(tr: dict) -> str:
    notas = []
    if tr.get("prueba") == "cramer" and tr.get("n1") is not None:
        notas.append(f"n₁ = {tr['n1']}, n₂ = {tr['n2']}")
    if tr.get("prueba") == "chow" and tr.get("veredicto") == "rechazada":
        notas.append(f"Atípico: {_num(tr.get('valor_atipico'))}")
    codigo = tr.get("warning_codigo")
    if codigo in _NOTAS_PRUEBA:
        notas.append(_NOTAS_PRUEBA[codigo])
    return " · ".join(notas)


def _tabla_pruebas(pruebas: list[dict], est) -> Table:
    filas = [["Prueba", "Estadístico", "Valor crítico", "Veredicto", "Observaciones"]]
    for tr in pruebas:
        filas.append(
            [
                _rotulo(_PRUEBAS, tr.get("prueba")),
                _num(tr.get("estadistico")),
                _num(tr.get("valor_critico")),
                _rotulo(_VEREDICTOS, tr.get("veredicto")),
                _nota_prueba(tr),
            ]
        )
    anchos = [3.4 * cm, 2.4 * cm, 2.4 * cm, 2.3 * cm]
    return _tabla(filas, anchos + [_ANCHO_UTIL - sum(anchos)], est)


def _seccion_etapa1(detalle: dict, est) -> list:
    etapa1 = detalle.get("etapa1")
    story: list = [_p("Etapa 1 — Validación estadística", est["h1"])]
    if not etapa1:
        return story + [
            _p(
                "Este análisis no tiene resultados de Etapa 1 registrados.",
                est["aviso"],
            )
        ]

    contract = etapa1.get("contract") or {}
    warnings = _sin_duplicados(contract.get("warnings"), etapa1.get("warnings"))
    if contract.get("bloqueante"):
        story.append(
            _p(
                "La serie no cumple el contrato de datos y el análisis se detuvo "
                f"({contract.get('codigo_error') or 'sin código'}).",
                est["aviso"],
            )
        )
        story += [_p("Advertencias", est["h2"])] + _advertencias(warnings, est)
        return story

    story += [_p("Advertencias", est["h2"])] + _advertencias(warnings, est)

    descriptiva = etapa1.get("descriptive")
    if descriptiva:
        filas = [
            ["n", _num(descriptiva.get("n")), "Media", _num(descriptiva.get("media"))],
            [
                "Mediana",
                _num(descriptiva.get("mediana")),
                "Desvío estándar",
                _num(descriptiva.get("desvio_estandar")),
            ],
            [
                "Coef. de variación",
                _num(descriptiva.get("coef_variacion")),
                "Coef. de asimetría",
                _num(descriptiva.get("coef_asimetria")),
            ],
            [
                "Mínimo",
                _num(descriptiva.get("minimo")),
                "Máximo",
                _num(descriptiva.get("maximo")),
            ],
        ]
        col = _ANCHO_UTIL / 4
        story += [
            _p("Estadística descriptiva", est["h2"]),
            _tabla(filas, [col] * 4, est, cabecera=False),
        ]

    fig = _grafico_serie(etapa1)
    if fig is not None:
        story.append(
            KeepTogether(
                [_p("Serie analizada", est["h2"]), _figura_a_imagen(fig, _ANCHO_UTIL)]
            )
        )

    grupos = [
        ("Independencia", "independencia", etapa1.get("nivel_independencia")),
        ("Homogeneidad", "homogeneidad", etapa1.get("nivel_homogeneidad")),
        ("Tendencia", "tendencia", None),
        ("Atípicos", "atipicos", None),
    ]
    for titulo, clave, nivel in grupos:
        pruebas = etapa1.get(clave) or []
        if not pruebas:
            continue
        encabezado = f"{titulo} — {_rotulo(_NIVELES, nivel)}" if nivel else titulo
        story += [_p(encabezado, est["h2"]), _tabla_pruebas(pruebas, est)]
        if clave == "independencia":
            anderson = next((t for t in pruebas if t.get("prueba") == "anderson"), None)
            fig = _grafico_correlograma(anderson) if anderson else None
            if fig is not None:
                story += [
                    Spacer(1, 4),
                    KeepTogether(
                        [
                            _p("Correlograma de Anderson", est["nota_previa"]),
                            _figura_a_imagen(fig, _ANCHO_UTIL * 0.85),
                        ]
                    ),
                ]

    chow = (detalle.get("decisiones") or {}).get("chow")
    if chow:
        accion = (
            "rechazó el dato atípico y se excluyó del análisis. Los resultados de "
            "este informe corresponden a la serie sin ese dato"
            if chow.get("accion") == "rechazar"
            else "aceptó el dato atípico como parte de la población"
        )
        anio = _anio_del_dato(detalle, chow.get("dato"))
        dato = f"{_num(chow.get('dato'))} ({anio})" if anio else _num(chow.get("dato"))
        story += [
            _p("Decisión ante el atípico", est["h2"]),
            _p(f"Dato {dato}: el usuario {accion}.", est["base"]),
        ]
    return story


def _anio_del_dato(detalle: dict, dato) -> int | None:
    """Año del atípico de Chow. Solo con carga anual: ahí la serie subida
    (`analyses.serie`) es la que se analizó, y tras un rechazo es la única que
    todavía conserva el dato. Con carga mensual o diaria el valor es un máximo
    anual agregado y no se ubica en un único registro de la serie subida."""
    datos = (detalle.get("etapa1") or {}).get("datos") or {}
    serie, timestamps = detalle.get("serie"), detalle.get("timestamps")
    if datos.get("resolucion_original") != "anual" or dato is None:
        return None
    if not serie or not timestamps or len(serie) != len(timestamps):
        return None
    for valor, ts in zip(serie, timestamps):
        if isinstance(valor, (int, float)) and math.isclose(valor, dato):
            return ts.get("anio")
    return None


def _texto_parametros(parametros: dict | None) -> str:
    if not parametros:
        return "—"
    return ", ".join(f"{clave} = {_num(valor)}" for clave, valor in parametros.items())


def _tabla_ranking(
    etapa2: dict, media: float | None, seleccion: dict | None, est
) -> Table:
    filas = [
        [
            "#",
            "Distribución",
            "Parám.",
            "Mejor método",
            "EEA",
            "EEA / media",
            "Observación",
        ]
    ]
    resaltadas = []
    for i, dist in enumerate(etapa2.get("ranking") or [], start=1):
        eea = dist.get("mejor_eea")
        notas = []
        if dist.get("pendiente_validacion"):
            notas.append("Pendiente de validación, no elegible")
        if eea is None:
            notas.append("Sin ajuste válido")
        if seleccion and seleccion.get("distribucion") == dist.get("distribucion"):
            notas.append("Elegida por el usuario")
            resaltadas.append(i)
        filas.append(
            [
                str(i),
                _rotulo(_DISTRIBUCIONES, dist.get("distribucion")),
                str(dist.get("n_parametros") or "—"),
                _rotulo(_METODOS, dist.get("mejor_metodo")) if eea is not None else "—",
                _num(eea),
                f"{100 * eea / media:.2f} %" if eea is not None and media else "—",
                " · ".join(notas),
            ]
        )
    anchos = [0.8 * cm, 3.4 * cm, 1.7 * cm, 3.0 * cm, 1.9 * cm, 1.9 * cm]
    return _tabla(
        filas,
        anchos + [_ANCHO_UTIL - sum(anchos)],
        est,
        filas_resaltadas=tuple(resaltadas),
    )


def _seccion_etapa2(detalle: dict, est) -> list:
    etapa2 = detalle.get("etapa2")
    etapas = detalle.get("etapas") or []
    if etapa2 is None:
        if "2" in etapas:
            return [
                _p("Etapa 2 — Análisis de frecuencia", est["h1"]),
                _p("Etapa 2 no se ejecutó: Etapa 1 quedó rechazada.", est["aviso"]),
            ]
        return []

    story: list = [_p("Etapa 2 — Análisis de frecuencia", est["h1"])]
    story += [_p("Advertencias", est["h2"])] + _advertencias(
        etapa2.get("warnings"), est
    )

    seleccion = etapa2.get("seleccion")
    media = ((detalle.get("etapa1") or {}).get("descriptive") or {}).get("media")
    story += [
        _p("Ranking de distribuciones", est["h2"]),
        _p(
            "Ordenado por Error Estándar de Ajuste (EEA), de menor a mayor. METIS no "
            "sugiere una distribución: la elección es del usuario.",
            est["nota_previa"],
        ),
        _tabla_ranking(etapa2, media, seleccion, est),
    ]

    story.append(_p("Distribución elegida y eventos de diseño", est["h2"]))
    if not seleccion:
        story.append(
            _p(
                "No quedó registrada ninguna distribución elegida para este análisis.",
                est["aviso"],
            )
        )
        return story

    dist = next(
        (
            d
            for d in etapa2.get("ranking") or []
            if d.get("distribucion") == seleccion.get("distribucion")
        ),
        {},
    )
    metodo = next(
        (
            m
            for m in dist.get("metodos") or []
            if m.get("metodo") == seleccion.get("metodo")
        ),
        {},
    )
    resumen = [
        ["Distribución", _rotulo(_DISTRIBUCIONES, seleccion.get("distribucion"))],
        ["Método de estimación", _rotulo(_METODOS, seleccion.get("metodo"))],
        ["Parámetros", _texto_parametros(metodo.get("parametros"))],
        ["EEA", _num(metodo.get("eea"))],
    ]
    if metodo.get("status") and metodo["status"] != "ok":
        resumen.append(["Estado del ajuste", _rotulo(_STATUS_METODO, metodo["status"])])
    story.append(
        _tabla(resumen, [4.5 * cm, _ANCHO_UTIL - 4.5 * cm], est, cabecera=False)
    )

    eventos = [
        [
            _rotulo_eje_periodo_retorno(detalle),
            "Prob. de no excedencia",
            _rotulo_valor_diseno(detalle),
        ]
    ]
    for e in seleccion.get("eventos_diseno") or []:
        t = e.get("periodo_retorno")
        eventos.append(
            [
                _num(t, 0) if isinstance(t, float) and t.is_integer() else _num(t),
                _num(1 - 1 / t) if t else "—",
                _num(e.get("valor")) if e.get("valor") is not None else "Sin cuantil",
            ]
        )
    story += [
        Spacer(1, 6),
        _tabla(eventos, [_ANCHO_UTIL / 3] * 3, est),
        Spacer(1, 3),
        _p(_nota_periodo_retorno(detalle), est["nota"]),
    ]

    fig = _grafico_ajuste(
        seleccion,
        etapa2.get("puntos_empiricos") or [],
        _rotulo_eje_periodo_retorno(detalle),
    )
    if fig is not None:
        story.append(
            KeepTogether(
                [
                    _p("Ajuste de la distribución elegida", est["h2"]),
                    _figura_a_imagen(fig, _ANCHO_UTIL),
                ]
            )
        )
    return story


_GRUPOS = [
    ("independencia", "Independencia"),
    ("homogeneidad", "Homogeneidad"),
    ("tendencia", "Tendencia"),
    ("atipicos", "Atípicos"),
]

_NIVELES_COMPARADOS = [
    ("Independencia", "nivel_independencia"),
    ("Homogeneidad", "nivel_homogeneidad"),
    ("Nivel de confianza", "nivel_confianza"),
]


def _celda_prueba(tr: dict | None) -> str:
    if tr is None:
        return "No se ejecutó"
    veredicto = _rotulo(_VEREDICTOS, tr.get("veredicto"))
    if tr.get("estadistico") is None:
        return veredicto
    return f"{veredicto} ({_num(tr['estadistico'])})"


def _comparar_pruebas(original: dict, simulado: dict) -> list[tuple]:
    """Una fila por prueba, alineada por nombre — la misma lógica que
    `frontend/src/routes/results/comparacionEtapa1.ts::compararPruebas`: una
    prueba que existe en una sola corrida aparece igual, con None del otro lado."""
    filas = []
    for clave, grupo in _GRUPOS:
        antes, despues = original.get(clave) or [], simulado.get(clave) or []
        for nombre in dict.fromkeys(t.get("prueba") for t in antes + despues):
            o = next((t for t in antes if t.get("prueba") == nombre), None)
            d = next((t for t in despues if t.get("prueba") == nombre), None)
            filas.append((grupo, nombre, o, d))
    return filas


def _tabla_comparacion_pruebas(original: dict, simulado: dict, est) -> list:
    filas = [["Prueba", "Grupo", "Original", "Sin los puntos", ""]]
    cambiadas = []
    for i, (grupo, nombre, o, d) in enumerate(
        _comparar_pruebas(original, simulado), start=1
    ):
        cambio = (o or {}).get("veredicto") != (d or {}).get("veredicto")
        if cambio:
            cambiadas.append(i)
        filas.append(
            [
                _rotulo(_PRUEBAS, nombre),
                grupo,
                _celda_prueba(o),
                _celda_prueba(d),
                "Cambió" if cambio else "",
            ]
        )
    if not cambiadas:
        resumen = "Ningún veredicto cambia al quitar esos puntos."
    elif len(cambiadas) == 1:
        resumen = "1 veredicto cambia al quitar esos puntos."
    else:
        resumen = f"{len(cambiadas)} veredictos cambian al quitar esos puntos."
    anchos = [3.4 * cm, 2.6 * cm, 4.2 * cm, 4.2 * cm]
    return [
        _p("Pruebas de Etapa 1", est["h2"]),
        _tabla(
            filas,
            anchos + [_ANCHO_UTIL - sum(anchos)],
            est,
            filas_resaltadas=tuple(cambiadas),
        ),
        _p(resumen, est["nota"]),
    ]


def _tabla_comparacion_niveles(original: dict, simulado: dict, est) -> list:
    filas = [["Nivel", "Original", "Sin los puntos"]]
    cambiadas = []
    for i, (etiqueta, clave) in enumerate(_NIVELES_COMPARADOS, start=1):
        if original.get(clave) != simulado.get(clave):
            cambiadas.append(i)
        filas.append(
            [
                etiqueta,
                _rotulo(_NIVELES, original.get(clave)),
                _rotulo(_NIVELES, simulado.get(clave)),
            ]
        )
    resto = (_ANCHO_UTIL - 4.5 * cm) / 2
    return [
        _p("Niveles", est["h2"]),
        _tabla(filas, [4.5 * cm, resto, resto], est, filas_resaltadas=tuple(cambiadas)),
    ]


def _eventos_comparados(
    sel_original: dict, sel_simulada: dict, rotulo_t: str, est
) -> Table:
    originales = {
        e.get("periodo_retorno"): e.get("valor")
        for e in sel_original.get("eventos_diseno") or []
    }
    filas = [[rotulo_t, "Original", "Sin los puntos", "Diferencia"]]
    for e in sel_simulada.get("eventos_diseno") or []:
        t = e.get("periodo_retorno")
        antes, despues = originales.get(t), e.get("valor")
        if antes is not None and despues is not None and antes != 0:
            diferencia = f"{100 * (despues - antes) / antes:+.2f} %"
        else:
            diferencia = "—"
        filas.append(
            [
                _num(t, 0) if isinstance(t, float) and t.is_integer() else _num(t),
                _num(antes) if antes is not None else "Sin cuantil",
                _num(despues) if despues is not None else "Sin cuantil",
                diferencia,
            ]
        )
    return _tabla(filas, [_ANCHO_UTIL / 4] * 4, est)


def _seccion_simulacion(detalle: dict, simulacion: dict, est) -> list:
    """Resultados con y sin los puntos excluidos (DECISIÓN 071), lo mismo que
    muestra la vista comparativa de Resultados. La simulación no se guarda ni
    cambia el análisis registrado: va después de él, en una sección rotulada."""
    original = detalle.get("etapa1") or {}
    simulado = simulacion.get("etapa1") or {}
    excluidos = simulacion.get("excluidos") or []

    quitados = ", ".join(
        f"{e['periodo']} ({_num(e['valor_original'])})" for e in excluidos
    )
    resumen = f"Se {'quitó' if len(excluidos) == 1 else 'quitaron'}: {quitados}."
    n_antes = (original.get("descriptive") or {}).get("n")
    n_despues = (simulado.get("descriptive") or {}).get("n")
    if n_antes is not None and n_despues is not None:
        resumen += f" Datos: {n_antes} → {n_despues}."

    story: list = [
        PageBreak(),
        _p("Resultados sin los puntos excluidos", est["h1"]),
        _p(
            "Simulación: recalcula Etapa 1 y Etapa 2 sin los puntos excluidos para "
            "compararlas con el análisis registrado. No cambia ese análisis ni la "
            "distribución elegida, y no queda guardada.",
            est["nota"],
        ),
        Spacer(1, 4),
        _p(resumen, est["base"]),
    ]
    fig = _grafico_serie_excluidos(original, excluidos)
    if fig is not None:
        story.append(_figura_a_imagen(fig, _ANCHO_UTIL))

    contract = simulado.get("contract") or {}
    if contract.get("bloqueante"):
        story.append(
            _p(
                "Sin esos puntos la serie no cumple el contrato de datos "
                f"({contract.get('codigo_error') or 'sin código'}): no hay resultados "
                "que comparar.",
                est["aviso"],
            )
        )
        return story

    story += _tabla_comparacion_pruebas(original, simulado, est)
    story += _tabla_comparacion_niveles(original, simulado, est)

    chow = next(
        (t for t in simulado.get("atipicos") or [] if t.get("prueba") == "chow"), None
    )
    if chow and chow.get("veredicto") == "rechazada":
        indice = (simulado.get("datos") or {}).get("indice_atipico")
        anios = simulacion.get("anios") or []
        anio = (
            f" ({anios[indice]})"
            if indice is not None and 0 <= indice < len(anios)
            else ""
        )
        story.append(
            _p(
                f"Sin esos puntos, Chow marca otro dato como atípico{anio}: "
                f"{_num(chow.get('valor_atipico'))}. En la simulación no se frena nada.",
                est["base"],
            )
        )

    previos = {w.get("codigo") for w in original.get("warnings") or []}
    nuevos = [
        w for w in simulado.get("warnings") or [] if w.get("codigo") not in previos
    ]
    if nuevos:
        story += [_p("Advertencias nuevas", est["h2"])] + _advertencias(nuevos, est)

    etapa2_original = detalle.get("etapa2") or {}
    etapa2_simulada = simulacion.get("etapa2")
    if etapa2_simulada is None:
        if detalle.get("etapa2") is not None:
            story.append(
                _p(
                    "Sin esos puntos Etapa 1 queda rechazada: no hay Etapa 2 que "
                    "recalcular.",
                    est["aviso"],
                )
            )
        return story

    sel_original = etapa2_original.get("seleccion")
    sel_simulada = etapa2_simulada.get("seleccion")
    story += [
        _p("Ranking de distribuciones sin esos puntos", est["h2"]),
        _tabla_ranking(
            etapa2_simulada,
            (simulado.get("descriptive") or {}).get("media"),
            sel_simulada,
            est,
        ),
    ]
    if not (sel_original and sel_simulada):
        return story

    story += [
        _p("Eventos de diseño con y sin los puntos", est["h2"]),
        _p(
            f"{_rotulo(_DISTRIBUCIONES, sel_simulada.get('distribucion'))} · "
            f"{_rotulo(_METODOS, sel_simulada.get('metodo'))} — la distribución "
            "elegida, reajustada sin los puntos excluidos.",
            est["nota_previa"],
        ),
        _eventos_comparados(
            sel_original, sel_simulada, _rotulo_eje_periodo_retorno(detalle), est
        ),
    ]
    fig = _grafico_ajuste_comparado(
        sel_original,
        etapa2_original.get("puntos_empiricos") or [],
        sel_simulada,
        etapa2_simulada.get("puntos_empiricos") or [],
        _rotulo_eje_periodo_retorno(detalle),
    )
    if fig is not None:
        story.append(
            KeepTogether(
                [
                    _p("Ajuste con y sin los puntos", est["h2"]),
                    _figura_a_imagen(fig, _ANCHO_UTIL),
                ]
            )
        )
    return story


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------


def _fecha(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        return datetime.fromisoformat(iso).strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return iso


def _canvas_con_pie(texto_pie: str):
    """Canvas que difiere el dibujo del pie hasta conocer el total de páginas
    ("Página X de Y")."""

    class _CanvasNumerado(Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._paginas: list[dict] = []

        def showPage(self):  # noqa: N802 — API de ReportLab
            self._paginas.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._paginas)
            for estado in self._paginas:
                self.__dict__.update(estado)
                self._pie(total)
                super().showPage()
            super().save()

        def _pie(self, total: int) -> None:
            self.saveState()
            self.setFont(_FUENTE, 7.5)
            self.setFillColor(_TENUE)
            self.drawString(2 * cm, 1.2 * cm, texto_pie)
            self.drawRightString(
                A4[0] - 2 * cm, 1.2 * cm, f"Página {self._pageNumber} de {total}"
            )
            self.setStrokeColor(_LINEA)
            self.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
            self.restoreState()

    return _CanvasNumerado


def generar_pdf_analisis(
    detalle: dict,
    autor: str | None = None,
    generado_en: datetime | None = None,
    simulacion: dict | None = None,
) -> bytes:
    """`detalle` es el dict de `get_analysis_by_id()`. Con `simulacion` (lo que
    devuelve `simular_exclusion()`), agrega al final los resultados sin los
    puntos excluidos, comparados con el análisis registrado. Devuelve el PDF en
    bytes."""
    _registrar_fuentes()
    est = _estilos()
    generado_en = generado_en or datetime.now()

    subtitulo = (
        "Formato experto: resultados directos, sin fórmulas ni explicaciones. "
        "Nivel de significancia α = 5 %."
    )
    if simulacion is not None:
        cantidad = len(simulacion.get("excluidos") or [])
        subtitulo += (
            " Incluye, al final, los resultados sin el punto excluido."
            if cantidad == 1
            else f" Incluye, al final, los resultados sin los {cantidad} puntos excluidos."
        )
    story: list = [
        _p("Informe de análisis — METIS", est["titulo"]),
        _p(subtitulo, est["subtitulo"]),
    ]
    story += _seccion_datos(detalle, autor, est)
    story += _seccion_etapa1(detalle, est)
    story += _seccion_etapa2(detalle, est)
    if simulacion is not None:
        story += _seccion_simulacion(detalle, simulacion, est)

    buffer = io.BytesIO()
    nombre = (detalle.get("configuracion") or {}).get("nombre_archivo") or "análisis"
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=2 * cm,
        title=f"METIS — {nombre}",
        author=autor or "METIS",
        creator="METIS",
    )
    pie = f"METIS · {nombre} · generado el {generado_en.strftime('%d/%m/%Y %H:%M')}"
    doc.build(story, canvasmaker=_canvas_con_pie(pie))
    return buffer.getvalue()


def nombre_archivo_pdf(detalle: dict, simulacion: bool = False) -> str:
    """`metis_<archivo>_<fecha>[_simulacion].pdf`, en ASCII para el header
    Content-Disposition."""
    original = (detalle.get("configuracion") or {}).get("nombre_archivo") or "analisis"
    base = unicodedata.normalize("NFKD", Path(original).stem)
    base = base.encode("ascii", "ignore").decode("ascii")
    base = re.sub(r"[^A-Za-z0-9_-]+", "_", base).strip("_") or "analisis"
    fecha = (detalle.get("created_at") or "")[:10] or "sin_fecha"
    sufijo = "_simulacion" if simulacion else ""
    return f"metis_{base}_{fecha}{sufijo}.pdf"
