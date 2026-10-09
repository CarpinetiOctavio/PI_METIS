// Esfuerzo sostenido (B7 del plan del TP de Calidad, DECISIÓN 077): carga moderada y constante
// durante DURACION (default 30 min). Mientras corre, scripts/carga.sh muestrea la memoria del
// backend: lo que interesa es si crece sin parar (sesiones del stream en memoria, DECISIÓN 053).
// Los umbrales de latencia y error son los mismos del stress de CI.
import { sleep } from "k6";
import { previewColumns, simulateExclusion, streamEtapa1 } from "./metis.js";

const UMBRALES = JSON.parse(open("../umbrales.json"));

const thresholds = {
  http_req_failed: [`rate<${UMBRALES.ci.tasa_error}`],
  checks: [`rate>${1 - UMBRALES.ci.tasa_error}`],
};
for (const [endpoint, p95] of Object.entries(UMBRALES.ci.p95_ms)) {
  thresholds[`http_req_duration{endpoint:${endpoint}}`] = [`p(95)<${p95}`];
}

export const options = {
  scenarios: {
    sostenido: {
      executor: "constant-vus",
      vus: UMBRALES.sostenido.usuarios,
      duration: __ENV.DURACION || "30m",
    },
  },
  thresholds,
  summaryTrendStats: ["avg", "med", "p(90)", "p(95)", "max"],
};

export default function () {
  previewColumns();
  streamEtapa1();
  simulateExclusion();
  sleep(1);
}
