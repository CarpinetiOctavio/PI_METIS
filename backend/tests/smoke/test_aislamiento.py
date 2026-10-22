"""Smoke de aislamiento entre perfiles (bloque K de docs/historico/planes/plan-revision-manual-21-10-2026.md).

Dos usuarios sembrados por `scripts/deploy-local.sh`. El usuario 1 corre un análisis con
Etapas 1 y 2 y guarda una exclusión de puntos; el usuario 2 no lo ve en su historial y recibe
404 en todo lo que lo nombra por su id, también en la dirección directa. Los tests de integración
ya cubren la pertenencia contra la base; este lo verifica sobre el sistema desplegado detrás de
nginx, que es lo que se muestra en la defensa.
"""

import httpx
import pytest

from tests.smoke.conftest import BASE_URL, EMAIL, EMAIL_2, PASSWORD
from tests.smoke.test_despliegue import NOMBRE_ARCHIVO, SERIE, _eventos_sse

pytestmark = pytest.mark.smoke

_SELECCION = {
    "distribucion": "gumbel",
    "metodo": "momentos",
    "periodos_retorno": [2, 10, 100],
}


def _login(c: httpx.Client, email: str) -> None:
    r = c.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert r.status_code == 200, f"login de {email}: {r.text}"


def _analisis_con_etapa2(c: httpx.Client) -> str:
    """Corre Etapas 1 y 2. La pausa de la distribución se resuelve desde otro cliente
    (`distribution-decision` no pide sesión, como en CU-02) mientras el stream espera."""
    datos = {
        "columna_x": "anio",
        "columna_y": "caudal",
        "tipo_variable": "caudal_precipitacion",
        "etapas": "1,2",
        "modo": "experto",
    }
    analysis_id = None
    with SERIE.open("rb") as f, httpx.Client(base_url=BASE_URL, timeout=30.0) as aparte:
        with c.stream(
            "POST",
            "/api/v1/analysis/stream",
            data=datos,
            files={"archivo": (NOMBRE_ARCHIVO, f)},
            timeout=120.0,
        ) as r:
            assert r.status_code == 200
            for tipo, data in _eventos_sse(r):
                assert tipo != "error", data
                if tipo == "result_etapa2_ranking":
                    d = aparte.post(
                        "/api/v1/analysis/distribution-decision",
                        json={"session_id": data["session_id"], **_SELECCION},
                    )
                    assert d.status_code == 200, d.text
                elif tipo == "complete":
                    analysis_id = data["analysis_id"]
    assert analysis_id, "el stream terminó sin analysis_id"
    return analysis_id


@pytest.fixture(scope="module")
def dos_usuarios(cliente):
    # `cliente` (conftest) decide si hay stack: sin él, saltea o falla según METIS_REQUIRE_SMOKE.
    with (
        httpx.Client(base_url=BASE_URL, timeout=30.0) as uno,
        httpx.Client(base_url=BASE_URL, timeout=30.0) as dos,
    ):
        _login(uno, EMAIL)
        _login(dos, EMAIL_2)
        analysis_id = _analisis_con_etapa2(uno)
        r = uno.post(
            f"/api/v1/history/{analysis_id}/exclusiones",
            json={"indices_excluidos": [3]},
        )
        assert r.status_code == 200, r.text
        yield uno, dos, analysis_id, r.json()["id"]


def test_el_duenio_ve_su_analisis(dos_usuarios):
    uno, _, analysis_id, _ = dos_usuarios

    assert analysis_id in [i["id"] for i in uno.get("/api/v1/history/").json()]
    detalle = uno.get(f"/api/v1/history/{analysis_id}")
    assert detalle.status_code == 200
    assert len(detalle.json()["exclusiones"]) == 1
    assert uno.get(f"/api/v1/export/{analysis_id}").status_code == 200
    eventos = uno.post(f"/api/v1/analysis/{analysis_id}/design-events", json=_SELECCION)
    assert eventos.status_code == 200, eventos.text


def test_otro_usuario_no_lo_ve_en_su_historial(dos_usuarios):
    _, dos, analysis_id, _ = dos_usuarios

    r = dos.get("/api/v1/history/", params={"archivados": "true"})
    assert r.status_code == 200
    assert analysis_id not in [i["id"] for i in r.json()]


@pytest.mark.parametrize(
    ("metodo", "ruta", "cuerpo"),
    [
        ("GET", "/api/v1/history/{id}", None),
        ("GET", "/api/v1/export/{id}", None),
        ("POST", "/api/v1/analysis/{id}/design-events", _SELECCION),
        ("POST", "/api/v1/history/{id}/archive", None),
        ("POST", "/api/v1/history/{id}/exclusiones", {"indices_excluidos": [4]}),
        ("DELETE", "/api/v1/history/{id}/exclusiones/{exclusion}", None),
    ],
    ids=[
        "detalle",
        "pdf",
        "design-events",
        "archivar",
        "guardar exclusión",
        "quitar exclusión",
    ],
)
def test_otro_usuario_recibe_404_por_la_direccion_directa(
    dos_usuarios, metodo, ruta, cuerpo
):
    _, dos, analysis_id, exclusion_id = dos_usuarios

    r = dos.request(
        metodo, ruta.format(id=analysis_id, exclusion=exclusion_id), json=cuerpo
    )

    assert r.status_code == 404, r.text
