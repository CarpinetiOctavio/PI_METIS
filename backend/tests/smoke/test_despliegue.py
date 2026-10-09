"""Smoke del despliegue: lo mínimo para decir que el stack levantó y atiende de punta a punta.

Cada test recorre una capa distinta detrás de nginx: la SPA estática, el backend, el parser y el
motor estadístico, la base de datos con las migraciones aplicadas y la sesión por cookie.
"""

import json
from pathlib import Path

import pytest

from tests.smoke.conftest import EMAIL, PASSWORD

pytestmark = pytest.mark.smoke

# serie_con_atipico.csv de docs/series prueba/ con el 950 del año 2000 reemplazado por 118,4: sin
# atípico, el stream con etapas=1 no se pausa y termina solo en `complete`.
SERIE = Path(__file__).with_name("serie_smoke.csv")
NOMBRE_ARCHIVO = "smoke.csv"


def _eventos_sse(respuesta):
    """Itera `(tipo, data)` de un `text/event-stream` (formato de services/analysis_service.py)."""
    tipo = None
    for linea in respuesta.iter_lines():
        # httpx 0.27 (el de requirements.txt) deja el salto de línea al final de cada línea.
        linea = linea.rstrip("\r\n")
        if linea.startswith("event: "):
            tipo = linea.removeprefix("event: ")
        elif linea.startswith("data: ") and tipo is not None:
            yield tipo, json.loads(linea.removeprefix("data: "))
            tipo = None


@pytest.fixture(scope="session")
def sesion(cliente):
    r = cliente.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert r.status_code == 200, r.text
    assert "access_token" in cliente.cookies
    return cliente


def test_spa_servida_por_nginx(cliente):
    r = cliente.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert '<div id="root">' in r.text


def test_spa_resuelve_rutas_del_cliente(cliente):
    # try_files de frontend/nginx.conf: recargar en /config sirve la SPA, no un 404.
    r = cliente.get("/config")
    assert r.status_code == 200
    assert '<div id="root">' in r.text


def test_ping_llega_al_backend(cliente):
    r = cliente.get("/ping")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_preview_columns(cliente):
    with SERIE.open("rb") as f:
        r = cliente.post(
            "/api/v1/analysis/preview-columns", files={"archivo": (NOMBRE_ARCHIVO, f)}
        )
    assert r.status_code == 200, r.text
    cuerpo = r.json()
    assert [c["nombre"] for c in cuerpo["columnas"]] == ["anio", "caudal"]
    assert cuerpo["filas"] == 40


def test_login_y_me(sesion):
    r = sesion.get("/api/v1/auth/me")
    assert r.status_code == 200, r.text
    assert r.json()["email"] == EMAIL


def test_stream_etapa1_hasta_complete(sesion):
    datos = {
        "columna_x": "anio",
        "columna_y": "caudal",
        "tipo_variable": "caudal_precipitacion",
        "etapas": "1",
        "modo": "experto",
    }
    with SERIE.open("rb") as f:
        with sesion.stream(
            "POST",
            "/api/v1/analysis/stream",
            data=datos,
            files={"archivo": (NOMBRE_ARCHIVO, f)},
            timeout=120.0,
        ) as r:
            assert r.status_code == 200
            assert r.headers["content-type"].startswith("text/event-stream")
            eventos = dict(_eventos_sse(r))

    assert "error" not in eventos, eventos.get("error")
    assert "outlier_detected" not in eventos
    assert eventos["result_etapa1"]["nivel_confianza"] != "rechazado"
    assert "complete" in eventos


def test_historial_registra_el_analisis(sesion):
    # Depende del stream de arriba (mismo usuario): CU-01 persiste en la base del despliegue.
    r = sesion.get("/api/v1/history/")
    assert r.status_code == 200, r.text
    assert NOMBRE_ARCHIVO in [item["nombre_archivo"] for item in r.json()]
