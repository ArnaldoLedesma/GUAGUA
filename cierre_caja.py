import os
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime


class CierreCaja:
    def __init__(self, contenedor, base_datos, colores):
        self.contenedor = contenedor
        self.base_datos = base_datos
        self.colores = colores

        self._crear_interfaz()
        self.actualizar_resumen()

    def _crear_interfaz(self):
        """Crea la pantalla visual del cierre de caja."""

        self.contenedor.configure(bg=self.colores["fondo"])

        titulo = Label(
            self.contenedor,
            text="Cierre de Caja",
            bg=self.colores["fondo"],
            fg=self.colores["texto"],
            font=("Segoe UI", 20, "bold")
        )
        titulo.pack(pady=(20, 10))

        subtitulo = Label(
            self.contenedor,
            text=f"Resumen de ventas del día — {datetime.now().strftime('%d/%m/%Y')}",
            bg=self.colores["fondo"],
            fg=self.colores["texto"],
            font=("Segoe UI", 10, "bold")
        )
        subtitulo.pack(pady=(0, 20))

        # Contenedor principal de los resultados
        panel = Frame(
            self.contenedor,
            bg="#E1F4EC",  # Verde muy suave para destacar el resumen de caja
            highlightbackground=self.colores["borde"],
            highlightthickness=1
        )
        panel.pack(fill=X, padx=40, pady=10)

        self.label_cantidad = self._crear_fila(
            panel,
            "Cantidad de ventas:",
            0
        )

        self.label_efectivo = self._crear_fila(
            panel,
            "Efectivo:",
            "$ 0"
        )

        self.label_transferencia = self._crear_fila(
            panel,
            "Transferencia:",
            "$ 0"
        )

        self.label_debito = self._crear_fila(
            panel,
            "Débito:",
            "$ 0"
        )

        self.label_credito = self._crear_fila(
            panel,
            "Crédito:",
            "$ 0"
        )

        Label(
            panel,
            text="-" * 45,
            bg="#E1F4EC",
            fg=self.colores["borde"]
        ).pack(pady=5)

        self.label_total = self._crear_fila(
            panel,
            "TOTAL DEL DÍA:",
            "$ 0",
            destacado=True
        )

        # Contenedor para los botones del cierre de caja.
        frame_botones = Frame(
            self.contenedor,
            bg=self.colores["fondo"]
        )
        frame_botones.pack(pady=(20, 8))

        ttk.Button(
            frame_botones,
            text="🔄 Actualizar",
            command=self.actualizar_resumen
        ).pack(side=LEFT, padx=5)

                # Permite imprimir el resumen actual del cierre de caja.
        ttk.Button(
            frame_botones,
            text="🖨 Imprimir cierre",
            command=self.imprimir_cierre
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            frame_botones,
            text="Cerrar",
            command=self.contenedor.destroy
        ).pack(side=LEFT, padx=5)

        self.label_actualizacion = Label(
            self.contenedor,
            text="",
            bg=self.colores["fondo"],
            fg=self.colores["texto"],
            font=("Segoe UI", 9, "bold")
        )
        self.label_actualizacion.pack(pady=(0, 10))

    def _crear_fila(self, padre, texto, valor, destacado=False):
        """Crea una fila del resumen de caja."""

        fila = Frame(padre, bg="#E1F4EC")
        fila.pack(fill=X, padx=25, pady=8)

        fuente = ("Segoe UI", 12, "bold") if destacado else ("Segoe UI", 11)

        Label(
            fila,
            text=texto,
            bg="#E1F4EC",
            fg=self.colores["texto"],
            font=fuente
        ).pack(side=LEFT)

        label_valor = Label(
            fila,
            text=valor,
            bg="#E1F4EC",
            fg=self.colores["secundario"],
            font=fuente
        )
        label_valor.pack(side=RIGHT)

        return label_valor

    def actualizar_resumen(self): # def=funciones 
        """Consulta la base de datos y muestra el cierre del día."""

        resumen = self.base_datos.obtener_cierre_caja_hoy()

        self.label_cantidad.config(
            text=str(resumen["cantidad_ventas"])
        )

        self.label_efectivo.config(
            text=self._formatear_moneda(resumen["efectivo"])
        )

        self.label_transferencia.config(
            text=self._formatear_moneda(resumen["transferencia"])
        )

        self.label_debito.config(
            text=self._formatear_moneda(resumen["debito"])
        )

        self.label_credito.config(
            text=self._formatear_moneda(resumen["credito"])
        )

        self.label_total.config(
            text=self._formatear_moneda(resumen["total_general"])
        )

        # Indicamos al usuario que los datos fueron consultados nuevamente.
        if hasattr(self, "label_actualizacion"):
            self.label_actualizacion.config(
                text=f"Actualizado: {datetime.now().strftime('%H:%M:%S')}"
            )

    def imprimir_cierre(self):
        """Genera un archivo TXT con el cierre de caja actual."""

        # Obtenemos los datos actuales del cierre directamente desde la base de datos.
        resumen = self.base_datos.obtener_cierre_caja_hoy()

        # Guardamos la fecha y hora exactas en las que se genera el cierre.
        fecha_actual = datetime.now()

        # Creamos una carpeta exclusiva para guardar los cierres de caja.
        carpeta_cierres = "cierres"
        os.makedirs(carpeta_cierres, exist_ok=True)

        # Creamos un nombre único utilizando la fecha y la hora.
        nombre_archivo = fecha_actual.strftime("cierre_%d-%m-%Y_%H-%M-%S.txt")
        ruta_cierre = os.path.join(carpeta_cierres, nombre_archivo)

        # Ancho preparado para un ticket térmico de 58 mm.
        ancho = 32

        # Generamos el comprobante de cierre de caja.
        with open(ruta_cierre, "w", encoding="utf-8") as cierre:

            cierre.write("=" * ancho + "\n")
            cierre.write("GUAGUA".center(ancho) + "\n")
            cierre.write("PAÑALERA".center(ancho) + "\n")
            cierre.write("=" * ancho + "\n")

            cierre.write("CIERRE DE CAJA".center(ancho) + "\n")
            cierre.write("=" * ancho + "\n")

            cierre.write(
                f"Fecha: {fecha_actual.strftime('%d/%m/%Y')}\n"
            )
            cierre.write(
                f"Hora: {fecha_actual.strftime('%H:%M:%S')}\n"
            )

            cierre.write("-" * ancho + "\n")

            cierre.write(
                f"Cantidad de ventas: {resumen['cantidad_ventas']}\n"
            )

            cierre.write("-" * ancho + "\n")

            cierre.write(
                f"Efectivo: {self._formatear_moneda(resumen['efectivo'])}\n"
            )
            cierre.write(
                f"Transferencia: {self._formatear_moneda(resumen['transferencia'])}\n"
            )
            cierre.write(
                f"Débito: {self._formatear_moneda(resumen['debito'])}\n"
            )
            cierre.write(
                f"Crédito: {self._formatear_moneda(resumen['credito'])}\n"
            )

            cierre.write("-" * ancho + "\n")

            cierre.write(
                f"TOTAL DEL DÍA: {self._formatear_moneda(resumen['total_general'])}\n"
            )

            cierre.write("=" * ancho + "\n")

                # Enviamos el cierre de caja a la impresora predeterminada de Windows.
        try:
            os.startfile(ruta_cierre, "print")

            messagebox.showinfo(
                "Impresión",
                "El cierre de caja fue enviado a la impresora."
            )

        except Exception as error:
            messagebox.showerror(
                "Error de impresión",
                f"No se pudo imprimir el cierre de caja:\n{error}"
            )

    @staticmethod
    def _formatear_moneda(valor):
        """Convierte 15000 en $ 15.000."""
        return f"$ {int(valor):,}".replace(",", ".")