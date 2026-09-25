"""
Punto de entrada del programa.
Aca se crean los dos objetos principales (BaseDatos y VentanaPrincipal)
y se conectan entre si. Este archivo es intencionalmente muy corto:
toda la logica real vive dentro de cada clase.
"""

from base_datos import BaseDatos
from ventana_principal import VentanaPrincipal
from rutas import obtener_ruta_db
from login import Login

if __name__ == "__main__":

    # Abrimos la base de datos antes del login porque las credenciales
    # Localizamos la base de datos según estemos en desarrollo o en el ejecutable.
    base_datos = BaseDatos(str(obtener_ruta_db()))

    # Mostramos la pantalla de inicio de sesión.
    login = Login(base_datos)
    login.iniciar()

    # El sistema principal solamente se abre si el login fue correcto.
    if login.acceso_permitido:
        app = VentanaPrincipal(base_datos)
        app.iniciar()

    # Cerramos correctamente SQLite al finalizar el programa.
    base_datos.cerrar()