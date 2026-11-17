"""Verifica que backend/requirements.lock esté al día con backend/requirements.txt (DECISIÓN 082).

requirements.txt lista las dependencias directas con `==`; requirements.lock las fija junto con las transitivas y
sus hashes, y es lo que instalan CI y la imagen Docker (`--require-hashes`). Si alguien cambia una versión en
requirements.txt y no regenera el lock, la imagen seguiría instalando la versión vieja sin avisar. Este chequeo
falla en ese caso: toda dependencia directa tiene que estar en el lock con la misma versión.

Uso: python scripts/check_requirements_lock.py   (sale con 1 y lista las diferencias si no coinciden)
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent / "backend"
PIN = re.compile(r"^([A-Za-z0-9._-]+)(?:\[[^\]]*\])?==([^\s;\\]+)")


def normalizar(nombre: str) -> str:
    """Nombre de paquete normalizado según PEP 503 (minúsculas, `-` en lugar de `_` y `.`)."""
    return re.sub(r"[-_.]+", "-", nombre).lower()


def pines(ruta: Path) -> dict[str, str]:
    resultado = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        m = PIN.match(linea.strip())
        if m:
            resultado[normalizar(m.group(1))] = m.group(2)
    return resultado


def main() -> int:
    directas = pines(RAIZ / "requirements.txt")
    bloqueadas = pines(RAIZ / "requirements.lock")
    diferencias = [
        f"{nombre}: requirements.txt pide {version}, requirements.lock tiene {bloqueadas.get(nombre, 'nada')}"
        for nombre, version in sorted(directas.items())
        if bloqueadas.get(nombre) != version
    ]
    if diferencias:
        print("requirements.lock no está al día con requirements.txt. Regeneralo (ver su encabezado):")
        print("\n".join(f"  - {d}" for d in diferencias))
        return 1
    print(f"requirements.lock al día: {len(directas)} dependencias directas, {len(bloqueadas)} en total.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
