
import os
import sys
from pathlib import Path


def obtener_carpeta_datos():
    """Devuelve la carpeta donde GUAGUA guarda los datos del negocio."""

    if getattr(sys, "frozen", False):
        # En el ejecutable, GUAGUA_DATOS estará junto a GUAGUA_APP.
        carpeta_app = Path(sys.executable).resolve().parent
        carpeta_datos = carpeta_app.parent / "GUAGUA_DATOS"
    else:
        # Durante el desarrollo, seguimos usando la base original
        # para no modificar todavía el funcionamiento de VS Code.
        carpeta_datos = Path(__file__).resolve().parent

    return carpeta_datos


def obtener_ruta_db():
    """Devuelve la ubicación de la base de datos."""
    return obtener_carpeta_datos() / "basededatos.db" 