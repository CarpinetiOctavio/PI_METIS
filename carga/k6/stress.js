// Stress (B7 del plan del TP de Calidad, DECISIÓN 077). Dos perfiles, elegidos con PERFIL:
//
//   quiebre  rampa de 10 a 120 usuarios, un minuto por escalón, para encontrar el punto donde el
//            backend deja de responder dentro de lo aceptable. Exploratorio: sus umbrales son
//            informativos (carga.sh ignora el código de salida) y el análisis por escalón lo hace
//            carga/analizar.py sobre la salida CSV.
//   ci       carga fija por debajo del quiebre, con los umbrales congelados (carga/umbrales.json):
//            si se superan, k6 sale con código 99 y el job falla. Es el que corre en el pipeline.
import { sleep } from "k6";
import { previewColumns, simulateExclusion, streamEtapa1 } from "./metis.js";

const PERFIL = __ENV.PERFIL || "ci";
const UMBRALES = JSON.parse(open("../umbrales.json"));

const ESCENARIOS = {
  quiebre: {
    executor: "ramping-vus",
    startVUs: 0,
    stages: [10, 20, 40, 60, 80, 120].map((target) => ({ duration: "1m", target })).concat([
      { duration: "20s", target: 0 },
    ]),
    gracefulRampDown: "30s",
  },
  ci: {
    executor: "ramping-vus",
    startVUs: 0,
    stages: [
      { duration: "30s", target: UMBRALES.ci.usuarios },
      { duration: "2m", target: UMBRALES.ci.usuarios },
      { duration: "15s", target: 0 },
    ],
    gracefulRampDown: "30s",
  },
};

// Los mismos umbrales en los dos perfiles: así el resumen muestra cada endpoint. En quiebre se
// esperan cruzados (es el objetivo), y carga.sh no toma su código de salida como falla.
function umbrales(limites) {
  const t = {
    http_req_failed: [`rate<${limites.tasa_error}`],
    checks: [`rate>${1 - limites.tasa_error}`],
  };
  for (const [endpoint, p95] of Object.entries(limites.p95_ms)) {
    t[`http_req_duration{endpoint:${endpoint}}`] = [`p(95)<${p95}`];
  }
  return t;
}

export const options = {
  scenarios: { carga: ESCENARIOS[PERFIL] },
  thresholds: umbrales(UMBRALES.ci),
  summaryTrendStats: ["avg", "med", "p(90)", "p(95)", "max"],
};

export default function () {
  previewColumns();
  streamEtapa1();
  simulateExclusion();
  sleep(1);
}
