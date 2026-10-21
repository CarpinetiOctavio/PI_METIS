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

// Bloque G (revisión manual 21/10/2026). Un año que arranca en julio de 1994
// corre hasta junio de 1995: "1994-95". Con enero es el año calendario: "1994".
// Solo vale si METIS agregó la serie (carga mensual o diaria): con carga anual
// los años los fijó el usuario y mes_inicio_anio no se aplicó.
export function rotuloAnio(anio: number, mesInicio: number | undefined): string {
  if (mesInicio === undefined || mesInicio === 1) return String(anio);
  return `${anio}-${String((anio + 1) % 100).padStart(2, "0")}`;
}

// La diferencia entre "Configurado" y "Calendario" no es un error de cálculo:
// cada vista toma el máximo de una ventana de doce meses distinta.
export const NOTA_VISTAS_CRITERIO_ANIO =
  "Cada vista toma el máximo de doce meses distintos, así que un mismo año puede tener valores distintos en una y otra.";
