"""
Punto de entrada del programa.
Aca se crean los dos objetos principales (BaseDatos y VentanaPrincipal)
y se conectan entre si. Este archivo es intencionalmente muy corto:
toda la logica real vive dentro de cada clase.
"""

from base_datos import BaseDatos
from ventana_principal import VentanaPrincipal, recurso_path

if __name__ == "__main__":
    base_datos = BaseDatos(recurso_path("basededatos.db"))
    app = VentanaPrincipal(base_datos)
    app.iniciar()
    base_datos.cerrar()
