import { expect, type APIRequestContext } from "@playwright/test";

// API de Mailpit v1.20 (axllent/mailpit, la imagen fijada en docker-compose.yml):
//   GET /api/v1/search?query=to:"<email>"  → { messages: [{ ID, ... }] }
//   GET /api/v1/message/{ID}               → { Text, HTML, ... }
const MAILPIT_URL = process.env.MAILPIT_URL ?? "http://localhost:8025";

/** Espera el mail de verificación que el backend le mandó a `email` y devuelve el link que trae. */
export async function linkDeVerificacion(request: APIRequestContext, email: string): Promise<string> {
  let id: string | undefined;
  await expect
    .poll(
      async () => {
        const r = await request.get(`${MAILPIT_URL}/api/v1/search`, {
          params: { query: `to:"${email}"` },
        });
        const cuerpo = (await r.json()) as { messages: { ID: string }[] };
        id = cuerpo.messages[0]?.ID;
        return id;
      },
      { message: `mail de verificación para ${email} en Mailpit`, timeout: 30_000 },
    )
    .toBeTruthy();

  const r = await request.get(`${MAILPIT_URL}/api/v1/message/${id}`);
  const { Text } = (await r.json()) as { Text: string };
  const link = /https?:\/\/\S+\/auth\/verify\?token=\S+/.exec(Text)?.[0];
  expect(link, `link de verificación en el cuerpo del mail:\n${Text}`).toBeTruthy();
  return link!;
}
