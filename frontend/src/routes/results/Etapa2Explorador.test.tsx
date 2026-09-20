import { describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";
import { makeEtapa2 } from "../../test/etapa2Fixtures";
import { renderPage } from "../../test/renderPage";
import { Etapa2Explorador } from "./Etapa2Explorador";

const RECALCULO = {
  eventos_diseno: [{ periodo_retorno: 2, valor: 108.4 }],
  curva_ajuste: [{ periodo_retorno: 1.05, valor: 55.0 }],
};

const BOTON = { name: "Explorar este ajuste" };

function montar(explorar: ReturnType<typeof vi.fn>) {
  renderPage(<Etapa2Explorador etapa2={makeEtapa2()} explorar={explorar} />);
  return userEvent.setup();
}

describe("Etapa2Explorador", () => {
  it("no explora nada hasta que el usuario lo pide, y aclara que no cambia la elección registrada", () => {
    const explorar = vi.fn();
    montar(explorar);

    expect(screen.getByText(/no cambia la elección registrada/)).toBeInTheDocument();
    expect(screen.queryByText(/No es la elección registrada/)).not.toBeInTheDocument();
    expect(explorar).not.toHaveBeenCalled();
  });

  it("al explorar llama a `explorar` con la distribución y el método elegidos y muestra el resultado como exploración", async () => {
    const explorar = vi.fn().mockResolvedValue(RECALCULO);
    const user = montar(explorar);

    // "gve" es la segunda card del ranking
    await user.click((await screen.findAllByRole("button", BOTON))[1]);

    expect(await screen.findByText(/No es la elección registrada/)).toBeInTheDocument();
    expect(explorar).toHaveBeenCalledTimes(1);
    expect(explorar).toHaveBeenCalledWith("gve", "ml", expect.any(Array));
  });

  it.each([
    ["un ApiError con código propio", new ApiError(400, "DIST_METHOD_NOT_FITTED", "x"), "DIST_METHOD_NOT_FITTED"],
    ["un error cualquiera (red caída, etc.)", new Error("boom"), ""],
  ])("si explorar falla con %s, muestra el texto legible del catálogo", async (_caso, falla, codigo) => {
    const user = montar(vi.fn().mockRejectedValue(falla));

    await user.click((await screen.findAllByRole("button", BOTON))[0]);

    expect(await screen.findByRole("alert")).toHaveTextContent(errorText(codigo));
    expect(screen.queryByText(/No es la elección registrada/)).not.toBeInTheDocument();
  });

  it("una exploración exitosa limpia el error de la anterior", async () => {
    const explorar = vi
      .fn()
      .mockRejectedValueOnce(new ApiError(400, "DIST_METHOD_NOT_FITTED", "x"))
      .mockResolvedValueOnce(RECALCULO);
    const user = montar(explorar);

    await user.click((await screen.findAllByRole("button", BOTON))[0]);
    expect(await screen.findByRole("alert")).toBeInTheDocument();

    await user.click((await screen.findAllByRole("button", BOTON))[0]);
    expect(await screen.findByText(/No es la elección registrada/)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
