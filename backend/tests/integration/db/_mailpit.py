"""Lectura de mails en Mailpit (DECISIÓN 049), compartida por los tests de integración con SMTP real."""

import asyncio

import httpx


async def esperar_mail(mailpit: httpx.AsyncClient, destinatario: str) -> str:
    """Texto del mail que le llegó a `destinatario`; reintenta mientras Mailpit lo indexa."""
    for _ in range(20):
        busqueda = await mailpit.get(
            "/api/v1/search", params={"query": f'to:"{destinatario}"'}
        )
        busqueda.raise_for_status()
        mensajes = busqueda.json()["messages"]
        if mensajes:
            mensaje = await mailpit.get(f"/api/v1/message/{mensajes[0]['ID']}")
            mensaje.raise_for_status()
            return mensaje.json()["Text"]
        await asyncio.sleep(0.25)
    raise AssertionError(f"Mailpit no recibió ningún mail para {destinatario}")
