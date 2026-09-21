from tkinter import *
from tkinter import ttk
from datetime import datetime # selecciona automaticamnete el año actual 


class HistorialVentas:
    """Ventana que permite consultar las ventas realizadas."""

    def __init__(self, contenedor, base_datos, colores):

        # Guardamos las referencias que necesitaremos en todo el módulo.
        self.contenedor = contenedor
        self.base_datos = base_datos
        self.colores = colores

        # Configuramos la ventana del historial.
        self.contenedor.title("Historial de Ventas - GUAGUA")
        self.contenedor.geometry("900x600")
        self.contenedor.resizable(False, False)

        self._crear_interfaz()
        self.cargar_ventas()

    def _crear_interfaz(self):
        """Crea la interfaz visual del historial de ventas."""

        # Título principal de la ventana.
        Label(
            self.contenedor,
            text="HISTORIAL DE VENTAS",
            font=("Segoe UI", 18, "bold"),
            bg=self.colores["fondo"],
            fg=self.colores["secundario"]
        ).pack(pady=(20, 10))

               # Contenedor para los filtros del historial de ventas.
        frame_filtro = Frame(
            self.contenedor,
            bg=self.colores["fondo"]
        )
        frame_filtro.pack(pady=(0, 8))

        # Filtro por año.
        Label(
            frame_filtro,
            text="Año:",
            bg=self.colores["fondo"],
            fg=self.colores["texto"],
            font=("Segoe UI", 10, "bold")
        ).pack(side=LEFT, padx=(0, 5))

        self.combo_anio = ttk.Combobox(
            frame_filtro,
            state="readonly",
            width=8,
            values=("2026", "2027", "2028", "2029", "2030")
        )
        self.combo_anio.pack(side=LEFT, padx=(0, 15))

        # Filtro por mes.
        Label(
            frame_filtro,
            text="Mes:",
            bg=self.colores["fondo"],
            fg=self.colores["texto"],
            font=("Segoe UI", 10, "bold")
        ).pack(side=LEFT, padx=(0, 5))

        self.combo_mes = ttk.Combobox(
            frame_filtro,
            state="readonly",
            width=14,
            values=(
                "Todos",
                "Enero",
                "Febrero",
                "Marzo",
                "Abril",
                "Mayo",
                "Junio",
                "Julio",
                "Agosto",
                "Septiembre",
                "Octubre",
                "Noviembre",
                "Diciembre"
            )
        )
        self.combo_mes.pack(side=LEFT)

        # Al abrir el historial mostramos el año actual y todos sus meses.
        self.combo_anio.set(str(datetime.now().year))
        self.combo_mes.set("Todos")

                # Al cambiar el año o el mes, actualizamos automáticamente el historial.
        self.combo_anio.bind("<<ComboboxSelected>>", self.filtrar_ventas)
        self.combo_mes.bind("<<ComboboxSelected>>", self.filtrar_ventas)

        
        # Tabla donde se mostrarán todas las ventas registradas.
        self.tabla_ventas = ttk.Treeview(
            self.contenedor,
            columns=("venta", "fecha", "medio_pago", "total"),
            show="headings",
            height=10,
            style="Historial.Treeview"
        )

        # Títulos de las columnas.
        self.tabla_ventas.heading("venta", text="Venta N.º")
        self.tabla_ventas.heading("fecha", text="Fecha y hora")
        self.tabla_ventas.heading("medio_pago", text="Medio de pago")
        self.tabla_ventas.heading("total", text="Total")

        # Tamaño y alineación de cada columna.
        self.tabla_ventas.column("venta", width=100, anchor=CENTER)
        self.tabla_ventas.column("fecha", width=220, anchor=CENTER)
        self.tabla_ventas.column("medio_pago", width=180, anchor=CENTER)
        self.tabla_ventas.column("total", width=150, anchor=CENTER)

                # Estilo visual de las tablas del historial.
        estilo = ttk.Style()

        estilo.configure(
            "Historial.Treeview",
            background="#E1F4EC",
            fieldbackground="#E1F4EC",
            foreground=self.colores["texto"],
            rowheight=24
        )

        self.tabla_ventas.pack(
            padx=30,
            pady=10,
            fill=X
        )
                # Título de la sección donde veremos los productos de la venta seleccionada.
        self.label_detalle = Label(
            self.contenedor,
            text="DETALLE DE LA VENTA",
            font=("Segoe UI", 13, "bold"),
            bg=self.colores["fondo"],
            fg=self.colores["secundario"]
        )
        self.label_detalle.pack(pady=(15, 5))

        # Tabla que mostrará los productos pertenecientes a la venta seleccionada.
        self.tabla_detalle = ttk.Treeview(
            self.contenedor,
            columns=("producto", "cantidad", "precio", "subtotal"),
            show="headings",
            height=7,
            style="Historial.Treeview"
        )

        self.tabla_detalle.heading("producto", text="Producto")
        self.tabla_detalle.heading("cantidad", text="Cantidad")
        self.tabla_detalle.heading("precio", text="Precio unitario")
        self.tabla_detalle.heading("subtotal", text="Subtotal")

        self.tabla_detalle.column("producto", width=300, anchor=W)
        self.tabla_detalle.column("cantidad", width=100, anchor=CENTER)
        self.tabla_detalle.column("precio", width=150, anchor=CENTER)
        self.tabla_detalle.column("subtotal", width=150, anchor=CENTER)

        self.tabla_detalle.pack(
            padx=30,
            pady=(5, 15),
            fill=X
        )


                # Cuando seleccionamos una venta, mostramos automáticamente sus productos.
        self.tabla_ventas.bind(
            "<<TreeviewSelect>>",
            self.mostrar_detalle_venta
        )

    def mostrar_detalle_venta(self, event=None):
        """Muestra los productos de la venta seleccionada."""

        # Obtenemos la fila seleccionada en la tabla de ventas.
        seleccion = self.tabla_ventas.selection()

        if not seleccion:
            return

        # Obtenemos los datos de la venta seleccionada.
        datos_venta = self.tabla_ventas.item(seleccion[0], "values")

        # La primera columna contiene el número de venta.
        id_venta = datos_venta[0]

        # Actualizamos el título indicando qué venta estamos consultando.
        self.label_detalle.config(
            text=f"DETALLE DE LA VENTA N.º {id_venta}"
        )

        # Limpiamos el detalle anterior.
        for fila in self.tabla_detalle.get_children():
            self.tabla_detalle.delete(fila)

        # Consultamos en SQLite los productos pertenecientes a esa venta.
        productos = self.base_datos.obtener_detalle_venta(id_venta)

        # Mostramos cada producto en la tabla inferior.
        for producto in productos:
            codigo, nombre, cantidad, precio, subtotal = producto

            self.tabla_detalle.insert(
                "",
                END,
                values=(
                    nombre,
                    cantidad,
                    self._formatear_moneda(precio),
                    self._formatear_moneda(subtotal)
                )
            )    

    def filtrar_ventas(self, event=None):
        """Filtra las ventas según el año y el mes seleccionados."""

        anio_seleccionado = self.combo_anio.get()
        mes_seleccionado = self.combo_mes.get()

        # Relacionamos el nombre del mes con su número.
        meses = {
            "Enero": 1,
            "Febrero": 2,
            "Marzo": 3,
            "Abril": 4,
            "Mayo": 5,
            "Junio": 6,
            "Julio": 7,
            "Agosto": 8,
            "Septiembre": 9,
            "Octubre": 10,
            "Noviembre": 11,
            "Diciembre": 12
        }

        # Obtenemos todas las ventas guardadas.
        ventas = self.base_datos.obtener_historial_ventas()

        # Limpiamos la tabla antes de mostrar el resultado del filtro.
        for fila in self.tabla_ventas.get_children():
            self.tabla_ventas.delete(fila)

        for venta in ventas:
            id_venta, fecha, medio_pago, total = venta

            # Convertimos la fecha guardada en SQLite a una fecha de Python.
            fecha_venta = datetime.strptime(
                fecha,
                "%Y-%m-%d %H:%M:%S"
            )

            # Primero comprobamos el año.
            if fecha_venta.year != int(anio_seleccionado):
                continue

            # Si se eligió un mes específico, también lo comprobamos.
            if mes_seleccionado != "Todos":
                if fecha_venta.month != meses[mes_seleccionado]:
                    continue

            # Si cumple el filtro, mostramos la venta.
            self.tabla_ventas.insert(
                "",
                END,
                values=(
                    id_venta,
                    fecha,
                    medio_pago,
                    self._formatear_moneda(total)
                )
            )

    def cargar_ventas(self):
        """Carga en la tabla todas las ventas guardadas en la base de datos."""

        # Limpiamos la tabla antes de cargar los datos.
        for fila in self.tabla_ventas.get_children():
            self.tabla_ventas.delete(fila)

        # Consultamos el historial de ventas en la base de datos.
        ventas = self.base_datos.obtener_historial_ventas()

        # Recorremos cada venta y la mostramos en la tabla.
        for venta in ventas:
            id_venta, fecha, medio_pago, total = venta

            self.tabla_ventas.insert(
                "",
                END,
                values=(
                    id_venta,
                    fecha,
                    medio_pago,
                    self._formatear_moneda(total)
                )
            )
    @staticmethod
    def _formatear_moneda(valor):
        """Convierte 15000 en $ 15.000."""
        return f"$ {int(valor):,}".replace(",", ".")