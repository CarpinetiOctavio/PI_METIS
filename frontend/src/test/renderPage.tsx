import { StrictMode, type ReactElement } from "react";
import { render, type RenderResult } from "@testing-library/react";

// Capa 1 de testing (docs/frontend/plan-arreglo-ui-rota.md §4.1): todo test
// que renderiza una PÁGINA lo hace bajo StrictMode. Cierra §5.2 del informe
// de diagnóstico — F1 solo era visible bajo StrictMode (el modo en el que la
// app corre de verdad en desarrollo), y ningún test lo usaba antes de esto.
//
// Deliberadamente no arma MemoryRouter/AuthProvider acá adentro: cada test de
// página ya construye su propio árbol (rutas destino falsas para observar un
// navigate(), con o sin AuthProvider según si la página lo necesita). Esta
// función solo agrega la envoltura de StrictMode alrededor de ESE árbol —
// así ningún test tiene que acordarse de hacerlo por su cuenta.
export function renderPage(tree: ReactElement): RenderResult {
  return render(<StrictMode>{tree}</StrictMode>);
}
