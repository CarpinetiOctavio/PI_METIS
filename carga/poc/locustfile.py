"""Prueba de concepto con Locust (paso 3 de docs/calidad/herramienta-carga.md).

El mismo escenario que k6-poc.js: cada usuario hace el recorrido completo de CU-02 y espera 1 s.

    locust -f locustfile.py --headless -u 10 -r 10 -t 60s --host http://nginx --html poc.html
"""

import json
from pathlib import Path

from locust import HttpUser, constant, events, task

CSV = (Path(__file__).parent.parent / "datos" / "serie_carga.csv").read_text()
FILAS = [linea.split(",") for linea in CSV.strip().splitlines()[1:]]
SIMULACION = {
    "serie": [float(f[1]) for f in FILAS],
    "anios": [int(f[0]) for f in FILAS],
    "tipo_variable": "caudal_precipitacion",
    "cramer_particion": "default",
    "indices_excluidos": [20],
    "etapas": [1, 2],
}


class UsuarioAnonimo(HttpUser):
    wait_time = constant(1)

    @task
    def recorrido(self):
        archivo = {"archivo": ("carga.csv", CSV, "text/csv")}
        self.client.post("/api/v1/analysis/preview-columns", files=archivo, name="preview-columns")

        datos = {
            "columna_x": "anio",
            "columna_y": "caudal",
            "tipo_variable": "caudal_precipitacion",
            "etapas": "1",
            "modo": "experto",
        }
        with self.client.post(
            "/api/v1/analysis/stream", data=datos, files=archivo, name="stream", catch_response=True, timeout=120
        ) as r:
            if r.status_code != 200 or "event: complete" not in r.text:
                r.failure("el stream no terminó en complete")

        with self.client.post(
            "/api/v1/analysis/simulate-exclusion",
            data=json.dumps(SIMULACION),
            headers={"Content-Type": "application/json"},
            name="simulate-exclusion",
            catch_response=True,
            timeout=120,
        ) as r:
            if r.status_code != 200 or r.json().get("etapa2") is None:
                r.failure("simulate-exclusion sin Etapa 2")


# Locust no trae umbrales que corten el proceso: hay que programarlos. Este hook replica el
# umbral de k6-poc.js (tasa de error < 1 %) poniendo el código de salida a mano.
@events.quitting.add_listener
def _umbral(environment, **_kwargs):
    if environment.stats.total.fail_ratio >= 0.01:
        environment.process_exit_code = 1
