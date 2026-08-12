// Nombres de mes y rótulo del criterio de año (mes_inicio_anio, DECISIÓN 057)
// — compartido entre ConfigPage (selector) y Etapa1ResultView (nota en
// resultados) para que ambos textos digan exactamente lo mismo.
const MESES = [
  "enero",
  "febrero",
  "marzo",
  "abril",
  "mayo",
  "junio",
  "julio",
  "agosto",
  "septiembre",
  "octubre",
  "noviembre",
  "diciembre",
];

function nombreMes(mes: number): string {
  return MESES[mes - 1];
}

function capitalizar(texto: string): string {
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

// mes=7 (julio) -> "de julio a junio". mes=1 (enero) -> "de enero a
// diciembre" — degenera en el año calendario (DECISIÓN 057).
function formatRangoAnio(mes: number): string {
  const mesFin = mes === 1 ? 12 : mes - 1;
  return `de ${nombreMes(mes)} a ${nombreMes(mesFin)}`;
}

// Texto de cada <option> del selector de ConfigPage.
export function etiquetaSelectorMes(mes: number): string {
  return `${capitalizar(nombreMes(mes))} — el año va ${formatRangoAnio(mes)}`;
}

// Nota junto a la estadística descriptiva en resultados (Etapa1ResultView).
export function notaCriterioAnio(mes: number): string {
  return `Criterio de año: ${nombreMes(mes)} — el año va ${formatRangoAnio(mes)}.`;
}
