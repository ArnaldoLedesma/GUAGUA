from tkinter import *
from tkinter import ttk, messagebox


class Login:
    """Ventana de inicio de sesión del sistema GUAGUA."""

    def __init__(self, base_datos):

        # Guardamos la conexión con la base de datos para validar el usuario.
        self.base_datos = base_datos

        # Indica si el usuario inició sesión correctamente.
        self.acceso_permitido = False

        # Creamos la ventana principal del login.
        self.ventana = Tk()

        # Título que aparecerá en la barra superior de Windows.
        self.ventana.title("GUAGUA - Inicio de sesión")

        # Tamaño inicial de la ventana.
        self.ventana.geometry("500x600")

        # Evitamos que el usuario cambie manualmente el tamaño.
        self.ventana.resizable(False, False)

        # Colores principales utilizados en el sistema GUAGUA.
        self.color_fondo = "#F4F5F2"
        self.color_tarjeta = "#FFFFFF"
        self.color_azul = "#002852"
        self.color_verde = "#00C180"
        self.color_texto = "#1F2933"

        # Aplicamos el color de fondo.
        self.ventana.configure(bg=self.color_fondo)

        # Centramos la ventana en la pantalla.
        self.centrar_ventana() #metodo
        # Creamos todos los elementos visuales del login.
        
        self.crear_interfaz()

    def crear_interfaz(self):
        """Crea los elementos visuales de la pantalla de inicio de sesión."""

        # Título principal del negocio.
        Label(
            self.ventana,
            text="GUAGUA",
            font=("Segoe UI", 30, "bold"),
            bg=self.color_fondo,
            fg=self.color_azul
        ).pack(pady=(45, 0))

        Label(
            self.ventana,
            text="PAÑALERA",
            font=("Segoe UI", 12, "bold"),
            bg=self.color_fondo,
            fg=self.color_verde
        ).pack(pady=(0, 25))

        # Tarjeta blanca que contiene el formulario.
        tarjeta = Frame(
            self.ventana,
            bg=self.color_tarjeta,
            padx=40,
            pady=30
        )
        tarjeta.pack(fill=X, padx=50)

        Label(
            tarjeta,
            text="INICIAR SESIÓN",
            font=("Segoe UI", 17, "bold"),
            bg=self.color_tarjeta,
            fg=self.color_azul
        ).pack(pady=(0, 25))

        # Campo para ingresar el nombre de usuario.
        Label(
            tarjeta,
            text="Usuario",
            font=("Segoe UI", 10, "bold"),
            bg=self.color_tarjeta,
            fg=self.color_texto
        ).pack(anchor=W)

        self.entry_usuario = ttk.Entry(
            tarjeta,
            font=("Segoe UI", 11)
        )
        self.entry_usuario.pack(fill=X, ipady=6, pady=(5, 18))

        # Campo para ingresar la contraseña.
        Label(
            tarjeta,
            text="Contraseña",
            font=("Segoe UI", 10, "bold"),
            bg=self.color_tarjeta,
            fg=self.color_texto
        ).pack(anchor=W)

        self.entry_contrasena = ttk.Entry(
            tarjeta,
            font=("Segoe UI", 11),
            show="●"
        )
        self.entry_contrasena.pack(fill=X, ipady=6, pady=(5, 8))

        # Casilla que permite visualizar u ocultar la contraseña ingresada.
        self.mostrar_contrasena = BooleanVar(value=False)

        Checkbutton(
            tarjeta,
            text="Mostrar contraseña",
            variable=self.mostrar_contrasena,
            command=self.alternar_contrasena,
            bg=self.color_tarjeta,
            fg=self.color_texto,
            activebackground=self.color_tarjeta,
            font=("Segoe UI", 9),
            cursor="hand2"
        ).pack(anchor=W, pady=(0, 18))

        # Botón principal del inicio de sesión.
        self.boton_ingresar = Button(
            tarjeta,
            text="INICIAR SESIÓN",
            font=("Segoe UI", 11, "bold"),
            bg=self.color_verde,
            fg="white",
            activebackground=self.color_azul,
            activeforeground="white",
            relief=FLAT,
            cursor="hand2",
            pady=10,
            command=self.validar_login
        )
        self.boton_ingresar.pack(fill=X)

        # Dejamos el cursor listo en el campo Usuario.
        self.entry_usuario.focus_set()  

        # Permite iniciar sesión presionando Enter desde la contraseña.
        self.entry_contrasena.bind(
            "<Return>",
            lambda event: self.validar_login()
        )

    def alternar_contrasena(self):
        """Permite mostrar u ocultar la contraseña ingresada."""

        if self.mostrar_contrasena.get():
            # Mostramos los caracteres reales.
            self.entry_contrasena.config(show="")
        else:
            # Volvemos a ocultar la contraseña.
            self.entry_contrasena.config(show="●")    


    def validar_login(self):
        """Comprueba el usuario y la contraseña utilizando la base de datos."""

        # Obtenemos los datos ingresados por la usuaria.
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get()

        # Consultamos la tabla usuarios de SQLite.
        if self.base_datos.validar_usuario(usuario, contrasena):

            # Marcamos que el inicio de sesión fue correcto.
            self.acceso_permitido = True

            messagebox.showinfo(
                "Inicio de sesión",
                "Acceso correcto. Bienvenida a GUAGUA."
            )

            # Cerramos el login y permitimos continuar hacia el sistema.
            self.ventana.destroy()

        else:
            messagebox.showerror(
                "Acceso denegado",
                "Usuario o contraseña incorrectos."
            )

            # Borramos la contraseña para permitir un nuevo intento.
            self.entry_contrasena.delete(0, END)
            self.entry_contrasena.focus_set() 


    def centrar_ventana(self):
        """Centra la ventana de login en la pantalla."""

        self.ventana.update_idletasks()

        ancho = 500
        alto = 600

        pantalla_ancho = self.ventana.winfo_screenwidth()
        pantalla_alto = self.ventana.winfo_screenheight()

        posicion_x = (pantalla_ancho - ancho) // 2
        posicion_y = (pantalla_alto - alto) // 2

        self.ventana.geometry(
            f"{ancho}x{alto}+{posicion_x}+{posicion_y}"
        )

    # Permite iniciar y mantener visible la ventana del login.
    def iniciar(self):
        self.ventana.mainloop() 

  