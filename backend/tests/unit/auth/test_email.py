"""
Tests unitarios de metis.auth.email — aislados de router.py y de BD.

Patrón de mocking — precedente de repo, status pendiente de confirmar como
vinculante fuera de auth (ver decisions-log.md): mockear en el borde de la
unidad bajo test, no un nivel más abajo. Acá la unidad es send_verification_email,
así que se mockea aiosmtplib.send en el punto de uso
(metis.auth.email.aiosmtplib.send) con unittest.mock.patch + AsyncMock
(stdlib, sin dependencias nuevas) — nunca se conecta a un servidor SMTP real.
"""

from unittest.mock import AsyncMock, patch

import aiosmtplib
import pytest

from metis.auth import email as email_module


def _set_config(monkeypatch, host="smtp.example.com", port=587,
                 user="metis", password="app-password",
                 from_address="metis-noreply@ucc.edu.ar"):
    # user y from_address quedan con valores DISTINTOS a propósito (reflejan
    # el caso real: SMTP_USER es la identidad de autenticación del relay,
    # SMTP_FROM_ADDRESS es la dirección del remitente — ver DECISIÓN 034,
    # Bug 2). Si el código volviera a usar SMTP_USER como From, cualquier
    # test que compare message["From"] contra from_address fallaría.
    monkeypatch.setattr(email_module, "_SMTP_HOST", host)
    monkeypatch.setattr(email_module, "_SMTP_PORT", port)
    monkeypatch.setattr(email_module, "_SMTP_USER", user)
    monkeypatch.setattr(email_module, "_SMTP_PASSWORD", password)
    monkeypatch.setattr(email_module, "_SMTP_FROM_ADDRESS", from_address)
    monkeypatch.setattr(email_module, "_FRONTEND_URL", "http://localhost:5173")


@pytest.mark.unit
async def test_send_verification_email_llama_aiosmtplib_send_con_parametros_correctos(monkeypatch):
    _set_config(monkeypatch)

    with patch(
        "metis.auth.email.aiosmtplib.send", new_callable=AsyncMock
    ) as mock_send:
        await email_module.send_verification_email("legajo@ucc.edu.ar", "tok123")

    mock_send.assert_awaited_once()
    _, kwargs = mock_send.call_args
    assert kwargs["hostname"] == "smtp.example.com"
    assert kwargs["port"] == 587
    assert kwargs["username"] == "metis"
    assert kwargs["password"] == "app-password"
    assert kwargs["start_tls"] is True


@pytest.mark.unit
async def test_send_verification_email_arma_el_mensaje_con_link_correcto(monkeypatch):
    _set_config(monkeypatch)

    with patch(
        "metis.auth.email.aiosmtplib.send", new_callable=AsyncMock
    ) as mock_send:
        await email_module.send_verification_email("legajo@ucc.edu.ar", "tok123")

    message = mock_send.call_args[0][0]
    assert message["From"] == "metis-noreply@ucc.edu.ar"
    assert message["To"] == "legajo@ucc.edu.ar"
    assert "http://localhost:5173/auth/verify?token=tok123" in message.get_content()


@pytest.mark.unit
async def test_send_verification_email_sin_config_lanza_runtimeerror_sin_llamar_aiosmtplib(monkeypatch):
    _set_config(monkeypatch, host=None, user=None, password=None)

    with patch(
        "metis.auth.email.aiosmtplib.send", new_callable=AsyncMock
    ) as mock_send:
        with pytest.raises(RuntimeError):
            await email_module.send_verification_email("legajo@ucc.edu.ar", "tok123")

    mock_send.assert_not_awaited()


@pytest.mark.unit
async def test_send_verification_email_from_es_independiente_de_smtp_user(monkeypatch):
    """
    DECISIÓN 034, Bug 2: SMTP_USER es la identidad de autenticación del
    relay, no una dirección de mail válida para el remitente — el From
    real viene de SMTP_FROM_ADDRESS. Este test usa valores deliberadamente
    distintos para las dos variables y confirma que el mensaje usa la
    segunda, no la primera — protege contra que se vuelvan a mezclar sin
    querer, no solo confirma el valor actual (a diferencia del test de
    arriba, que ya lo hace de forma incidental gracias a los defaults de
    _set_config, pero no deja explícito qué regresión previene).
    """
    _set_config(
        monkeypatch,
        user="usuario-de-autenticacion-sin-arroba",
        from_address="remitente-real@ucc.edu.ar",
    )

    with patch(
        "metis.auth.email.aiosmtplib.send", new_callable=AsyncMock
    ) as mock_send:
        await email_module.send_verification_email("legajo@ucc.edu.ar", "tok123")

    message = mock_send.call_args[0][0]
    assert message["From"] == "remitente-real@ucc.edu.ar"
    assert message["From"] != "usuario-de-autenticacion-sin-arroba"
    # SMTP_USER se sigue usando para autenticación, no para el From.
    assert mock_send.call_args.kwargs["username"] == "usuario-de-autenticacion-sin-arroba"


@pytest.mark.unit
async def test_send_verification_email_sin_from_address_lanza_runtimeerror_sin_llamar_aiosmtplib(monkeypatch):
    _set_config(monkeypatch, from_address=None)

    with patch(
        "metis.auth.email.aiosmtplib.send", new_callable=AsyncMock
    ) as mock_send:
        with pytest.raises(RuntimeError):
            await email_module.send_verification_email("legajo@ucc.edu.ar", "tok123")

    mock_send.assert_not_awaited()


@pytest.mark.unit
async def test_send_verification_email_propaga_smtpexception_sin_capturarla(monkeypatch):
    _set_config(monkeypatch)

    with patch(
        "metis.auth.email.aiosmtplib.send",
        new_callable=AsyncMock,
        side_effect=aiosmtplib.SMTPConnectError("conexión rechazada"),
    ):
        with pytest.raises(aiosmtplib.SMTPException):
            await email_module.send_verification_email("legajo@ucc.edu.ar", "tok123")
