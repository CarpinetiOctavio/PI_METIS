// Prueba de concepto (paso 3 de docs/calidad/herramienta-carga.md): el mismo escenario que
// locustfile.py. 10 usuarios durante 60 s; cada iteración es el recorrido completo de CU-02.
import { sleep } from "k6";
import { previewColumns, simulateExclusion, streamEtapa1 } from "../k6/metis.js";

export const options = {
  vus: 10,
  duration: "60s",
  // Umbral nativo: si se supera, k6 termina con código 99 y el job falla.
  thresholds: { http_req_failed: ["rate<0.01"] },
};

export default function () {
  previewColumns();
  streamEtapa1();
  simulateExclusion();
  sleep(1);
}
