// Requests de METIS para las pruebas de carga (B7 del plan del TP de Calidad, DECISIÓN 077).
// Cada función es un paso del recorrido de un usuario anónimo (CU-02): subir el archivo, correr
// Etapa 1 y simular la exclusión de un punto, que dispara Etapa 2 completa (13 distribuciones).
// Cada request lleva el tag `endpoint`, así los umbrales y el resumen se leen por endpoint.
import http from "k6/http";
import { check } from "k6";

export const BASE_URL = (__ENV.BASE_URL || "http://localhost").replace(/\/$/, "");

// serie_smoke.csv del smoke del backend: 40 años sin atípico, así el stream con etapas=1 no se
// pausa en Chow y termina solo en `complete` (k6 no habla SSE; lee la respuesta entera).
const CSV = open("../datos/serie_carga.csv");
const FILAS = CSV.trim()
  .split("\n")
  .slice(1)
  .map((linea) => linea.split(","));

const SIMULACION = JSON.stringify({
  serie: FILAS.map((f) => Number(f[1])),
  anios: FILAS.map((f) => Number(f[0])),
  tipo_variable: "caudal_precipitacion",
  cramer_particion: "default",
  indices_excluidos: [20],
  etapas: [1, 2],
});

const archivo = () => http.file(CSV, "carga.csv", "text/csv");

export function previewColumns() {
  const r = http.post(
    `${BASE_URL}/api/v1/analysis/preview-columns`,
    { archivo: archivo() },
    { tags: { endpoint: "preview-columns" } },
  );
  check(r, { "preview-columns 200": (res) => res.status === 200 }, { endpoint: "preview-columns" });
}

export function streamEtapa1() {
  const r = http.post(
    `${BASE_URL}/api/v1/analysis/stream`,
    {
      archivo: archivo(),
      columna_x: "anio",
      columna_y: "caudal",
      tipo_variable: "caudal_precipitacion",
      etapas: "1",
      modo: "experto",
    },
    { tags: { endpoint: "stream" }, timeout: "120s" },
  );
  check(
    r,
    {
      "stream 200": (res) => res.status === 200,
      "stream termina en complete": (res) => typeof res.body === "string" && res.body.includes("event: complete"),
    },
    { endpoint: "stream" },
  );
}

export function simulateExclusion() {
  const r = http.post(`${BASE_URL}/api/v1/analysis/simulate-exclusion`, SIMULACION, {
    headers: { "Content-Type": "application/json" },
    tags: { endpoint: "simulate-exclusion" },
    timeout: "120s",
  });
  check(
    r,
    {
      "simulate-exclusion 200": (res) => res.status === 200,
      "simulate-exclusion trae Etapa 2": (res) => res.status === 200 && res.json("etapa2") !== null,
    },
    { endpoint: "simulate-exclusion" },
  );
}
