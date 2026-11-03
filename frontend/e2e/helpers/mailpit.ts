import { expect, type APIRequestContext } from "@playwright/test";

// API de Mailpit v1.20 (axllent/mailpit, la imagen fijada en docker-compose.yml):
//   GET /api/v1/search?query=to:"<email>"  → { messages: [{ ID, ... }] }  (más nuevo primero)
//   GET /api/v1/message/{ID}               → { Text, HTML, ... }
const MAILPIT_URL = process.env.MAILPIT_URL ?? "http://localhost:8025";

/** Espera un mail para `email` cuyo cuerpo contenga un link que cumpla `patron` y devuelve ese link.
 *  Una misma casilla puede recibir varios mails (verificación, reseteo): se elige por el link. */
async function linkEnMail(
  request: APIRequestContext,
  email: string,
  patron: RegExp,
  descripcion: string,
): Promise<string> {
  let link: string | undefined;
  await expect
    .poll(
      async () => {
        const r = await request.get(`${MAILPIT_URL}/api/v1/search`, {
          params: { query: `to:"${email}"` },
        });
        const cuerpo = (await r.json()) as { messages: { ID: string }[] };
        for (const { ID } of cuerpo.messages) {
          const m = await request.get(`${MAILPIT_URL}/api/v1/message/${ID}`);
          const { Text } = (await m.json()) as { Text: string };
          link = patron.exec(Text)?.[0];
          if (link) break;
        }
        return link;
      },
      { message: `${descripcion} para ${email} en Mailpit`, timeout: 30_000 },
    )
    .toBeTruthy();
  return link!;
}

/** Espera el mail de verificación que el backend le mandó a `email` y devuelve el link que trae. */
export function linkDeVerificacion(request: APIRequestContext, email: string): Promise<string> {
  return linkEnMail(request, email, /https?:\/\/\S+\/auth\/verify\?token=\S+/, "mail de verificación");
}

/** Espera el mail de recuperación de contraseña (DECISIÓN 085) y devuelve el link que trae. */
export function linkDeReseteo(request: APIRequestContext, email: string): Promise<string> {
  return linkEnMail(
    request,
    email,
    /https?:\/\/\S+\/auth\/reset-password\?token=\S+/,
    "mail de recuperación de contraseña",
  );
}
