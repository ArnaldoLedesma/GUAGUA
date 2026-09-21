from tkinter import *
from tkinter import messagebox


class CambiarContrasena:
    """Ventana que permite a la usuaria cambiar su contraseña."""

    def __init__(self, ventana_padre, base_datos):
        # Guardamos la conexión con SQLite.
        self.base_datos = base_datos

        # Creamos una ventana secundaria dentro de GUAGUA.
        self.ventana = Toplevel(ventana_padre)
        self.ventana.title("GUAGUA - Cambiar contraseña")
        self.ventana.geometry("450x550")
        self.ventana.resizable(False, False)

        # Colores utilizados en el sistema.
        self.color_fondo = "#F4F5F2"
        self.color_tarjeta = "#FFFFFF"
        self.color_azul = "#002852"
        self.color_verde = "#00C180"
        self.color_texto = "#1F2933"

        self.ventana.configure(bg=self.color_fondo)

        # Hace que esta ventana quede asociada a la ventana principal.
        self.ventana.transient(ventana_padre)
        self.ventana.grab_set()

        self.crear_interfaz()


    def crear_interfaz(self):
        """Crea los campos necesarios para cambiar la contraseña."""

        Label(
            self.ventana,
            text="CAMBIAR CONTRASEÑA",
            font=("Segoe UI", 18, "bold"),
            bg=self.color_fondo,
            fg=self.color_azul
        ).pack(pady=(30, 20))

        tarjeta = Frame(
            self.ventana,
            bg=self.color_tarjeta,
            padx=35,
            pady=25
        )
        tarjeta.pack(fill=X, padx=40)

        # Contraseña que utiliza actualmente la usuaria.
        Label(
            tarjeta,
            text="Contraseña actual",
            font=("Segoe UI", 10, "bold"),
            bg=self.color_tarjeta,
            fg=self.color_texto
        ).pack(anchor=W)

        self.entry_actual = Entry(
            tarjeta,
            font=("Segoe UI", 11),
            show="●"
        )
        self.entry_actual.pack(fill=X, ipady=5, pady=(5, 15))

        # Nueva contraseña elegida por la usuaria.
        Label(
            tarjeta,
            text="Nueva contraseña",
            font=("Segoe UI", 10, "bold"),
            bg=self.color_tarjeta,
            fg=self.color_texto
        ).pack(anchor=W)

        self.entry_nueva = Entry(
            tarjeta,
            font=("Segoe UI", 11),
            show="●"
        )
        self.entry_nueva.pack(fill=X, ipady=5, pady=(5, 15))

        # Se solicita nuevamente para evitar errores al escribirla.
        Label(
            tarjeta,
            text="Repetir nueva contraseña",
            font=("Segoe UI", 10, "bold"),
            bg=self.color_tarjeta,
            fg=self.color_texto
        ).pack(anchor=W)

        self.entry_repetir = Entry(
            tarjeta,
            font=("Segoe UI", 11),
            show="●"
        )
        self.entry_repetir.pack(fill=X, ipady=5, pady=(5, 8))
        # Permite mostrar u ocultar las tres contraseñas.
        self.mostrar_contrasena = BooleanVar(value=False)

        Checkbutton(
            tarjeta,
            text="Mostrar contraseñas",
            variable=self.mostrar_contrasena,
            command=self.alternar_contrasenas,
            bg=self.color_tarjeta,
            fg=self.color_texto,
            activebackground=self.color_tarjeta,
            font=("Segoe UI", 9),
            cursor="hand2"
        ).pack(anchor=W, pady=(0, 18))

        Button(
            tarjeta,
            text="CAMBIAR CONTRASEÑA",
            font=("Segoe UI", 10, "bold"),
            bg=self.color_verde,
            fg="white",
            activebackground=self.color_azul,
            activeforeground="white",
            relief=FLAT,
            cursor="hand2",
            pady=9,
            command=self.cambiar
        ).pack(fill=X)

        # Dejamos el cursor preparado en el primer campo.
        self.entry_actual.focus_set()

    def alternar_contrasenas(self):
        """Permite mostrar u ocultar las tres contraseñas."""

        if self.mostrar_contrasena.get():
            # Mostramos los caracteres de los tres campos.
            self.entry_actual.config(show="")
            self.entry_nueva.config(show="")
            self.entry_repetir.config(show="")
        else:
            # Volvemos a ocultar los caracteres.
            self.entry_actual.config(show="●")
            self.entry_nueva.config(show="●")
            self.entry_repetir.config(show="●")    

    def cambiar(self):
        """Valida los datos y actualiza la contraseña de la usuaria."""

        # Obtenemos las tres contraseñas ingresadas.
        contrasena_actual = self.entry_actual.get()
        nueva_contrasena = self.entry_nueva.get()
        repetir_contrasena = self.entry_repetir.get()

        # Verificamos que ningún campo esté vacío.
        if not contrasena_actual or not nueva_contrasena or not repetir_contrasena:
            messagebox.showwarning(
                "Datos incompletos",
                "Completá todos los campos."
            )
            return

        # Comprobamos que la contraseña actual sea correcta.
        if not self.base_datos.validar_usuario("admin", contrasena_actual):
            messagebox.showerror(
                "Contraseña incorrecta",
                "La contraseña actual no es correcta."
            )
            return

        # Comprobamos que las dos nuevas contraseñas sean iguales.
        if nueva_contrasena != repetir_contrasena:
            messagebox.showwarning(
                "Contraseñas diferentes",
                "Las nuevas contraseñas no coinciden."
            )
            return

        # Evitamos una contraseña demasiado corta.
        if len(nueva_contrasena) < 6:
            messagebox.showwarning(
                "Contraseña muy corta",
                "La nueva contraseña debe tener al menos 6 caracteres."
            )
            return

        # Guardamos la nueva contraseña mediante su hash.
        if self.base_datos.cambiar_contrasena("admin", nueva_contrasena):
            messagebox.showinfo(
                "Contraseña actualizada",
                "La contraseña fue modificada correctamente."
            )

            # Cerramos la ventana una vez realizado el cambio.
            self.ventana.destroy()    