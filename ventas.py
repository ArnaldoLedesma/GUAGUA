"""
Módulo de Gestión de Ventas - GUAGUA
------------------------------------
Contiene la interfaz y la lógica visual del carrito de compras.
No ejecuta SQL directamente: toda operación con SQLite se delega a BaseDatos.
"""

import os
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox
from cierre_caja import CierreCaja
from historial_ventas import HistorialVentas
# Configuración del ancho del ticket térmico.
TAMANO_TICKET = "58mm"

if TAMANO_TICKET == "58mm":
    ANCHO_TICKET = 32
else:
    ANCHO_TICKET = 46

class GestionVentas:
    def __init__(self, contenedor, base_datos, colores):
        self.contenedor = contenedor
        self.base_datos = base_datos
        self.colores = colores

        # El carrito se guarda temporalmente en memoria hasta confirmar la venta.
        # La clave es el código del producto, para evitar duplicados en el carrito.
        self.carrito = {}

        self._crear_interfaz()
        self.cargar_productos()

    # ------------------------------------------------------------------
    # CONSTRUCCIÓN DE LA INTERFAZ
    # ------------------------------------------------------------------
    def _crear_interfaz(self):
        self.contenedor.configure(bg=self.colores["fondo"])

        titulo = Frame(self.contenedor, bg=self.colores["fondo"])
        titulo.pack(fill=X, pady=(0, 12))

        Label(
            titulo,
            text="Gestión de ventas",
            bg=self.colores["fondo"],
            fg=self.colores["texto"],
            font=("Segoe UI", 19, "bold")
        ).pack(side=LEFT)

        Label(
            titulo,
            text="Buscar productos, agregarlos al carrito y confirmar la venta",
            bg=self.colores["fondo"],
            fg=self.colores["texto_suave"],
            font=("Segoe UI", 10)
        ).pack(side=LEFT, padx=(14, 0), pady=(7, 0))

                # Botón para consultar todas las ventas realizadas y sus productos.
        Button(
                titulo,
                text="Historial de ventas",
                command=self.abrir_historial_ventas,
                bg=self.colores["primario"],
                fg="white",
                font=("Segoe UI", 10, "bold"),
                relief=FLAT,
                cursor="hand2",
                padx=15,
                pady=7
            ).pack(side=RIGHT, padx=(0, 8))

        # Botón para consultar el resumen de ventas y medios de pago del día.
        Button(
                titulo,
                text="Cierre de caja",
                command=self.abrir_cierre_caja,
                bg=self.colores["secundario"],
                fg="white",
                font=("Segoe UI", 10, "bold"),
                relief=FLAT,
                cursor="hand2",
                padx=15,
                pady=7
            ).pack(side=RIGHT)

        cuerpo = Frame(self.contenedor, bg=self.colores["fondo"])
        cuerpo.pack(fill=BOTH, expand=True)

        # Panel izquierdo: búsqueda y listado de productos disponibles.
        panel_productos = Frame(
            cuerpo,
            bg=self.colores["tarjeta"],
            highlightbackground=self.colores["borde"],
            highlightthickness=1
        )
        panel_productos.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        # Panel derecho: carrito de compra y total de la operación.
        panel_carrito = Frame(
            cuerpo,
            bg=self.colores["tarjeta"],
            highlightbackground=self.colores["borde"],
            highlightthickness=1
        )
        panel_carrito.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 0))

        self._crear_panel_productos(panel_productos)
        self._crear_panel_carrito(panel_carrito)

    def _crear_panel_productos(self, panel):
        encabezado = Frame(panel, bg=self.colores["tarjeta"])
        encabezado.pack(fill=X, padx=16, pady=(16, 8))

        Label(
            encabezado,
            text="PRODUCTOS",
            bg=self.colores["tarjeta"],
            fg=self.colores["secundario"],
            font=("Segoe UI", 11, "bold")
        ).pack(side=LEFT)

        buscador = Frame(panel, bg=self.colores["tarjeta"])
        buscador.pack(fill=X, padx=16, pady=(0, 12))

        self.entry_buscar = ttk.Entry(buscador, style="Campo.TEntry", font=("Segoe UI", 11))
        self.entry_buscar.pack(side=LEFT, fill=X, expand=True)
        # Al presionar Enter intentamos procesar el texto como un código de barras.
        # Esto permite trabajar directamente con un lector USB.
        self.entry_buscar.bind(
            "<Return>",
            self.procesar_codigo_barras
)

       # Mientras el usuario escribe, actualizamos automáticamente la búsqueda.
        self.entry_buscar.bind("<KeyRelease>", self.programar_busqueda_venta)

        ttk.Button(
            buscador,
            text="Buscar",
            style="Secundario.TButton",
            command=self.buscar_producto
        ).pack(side=LEFT, padx=(8, 0))

        ttk.Button(
            buscador,
            text="Todos",
            style="Neutro.TButton",
            command=self.cargar_productos
        ).pack(side=LEFT, padx=(8, 0))

        columnas = ("codigo", "nombre", "precio", "stock")
        self.tabla_productos = ttk.Treeview(
            panel,
            columns=columnas,
            show="headings",
            style="Tabla.Treeview",
            height=9
        )

        self.tabla_productos.heading("codigo", text="Código")
        self.tabla_productos.heading("nombre", text="Producto")
        self.tabla_productos.heading("precio", text="Precio")
        self.tabla_productos.heading("stock", text="Stock")

        self.tabla_productos.column("codigo", width=70, anchor=CENTER)
        self.tabla_productos.column("nombre", width=250)
        self.tabla_productos.column("precio", width=100, anchor=E)
        self.tabla_productos.column("stock", width=70, anchor=CENTER)

        scroll = ttk.Scrollbar(panel, orient=VERTICAL, command=self.tabla_productos.yview)
        self.tabla_productos.configure(yscrollcommand=scroll.set)
        self.tabla_productos.pack(side=LEFT, fill=BOTH, expand=True, padx=(16, 0), pady=(0, 16))
        scroll.pack(side=LEFT, fill=Y, pady=(0, 16))

        acciones = Frame(panel, bg=self.colores["tarjeta"])
        acciones.pack(side=BOTTOM, fill=X, padx=16, pady=(0, 16))

        Label(
            acciones,
            text="Cantidad:",
            bg=self.colores["tarjeta"],
            fg=self.colores["texto"],
            font=("Segoe UI", 10, "bold")
        ).pack(side=LEFT)

        self.spin_cantidad = Spinbox(
            acciones,
            from_=1,
            to=999,
            width=5,
            font=("Segoe UI", 10),
            justify=CENTER
        )
        self.spin_cantidad.pack(side=LEFT, padx=(7, 12))

        ttk.Button(
            acciones,
            text="Agregar al carrito",
            style="Primario.TButton",
            command=self.agregar_al_carrito
        ).pack(side=LEFT)

        # Doble clic = agregar una unidad. Es cómodo cuando se usa rápido en mostrador.
        self.tabla_productos.bind("<Double-1>", lambda evento: self.agregar_al_carrito())

    def _crear_panel_carrito(self, panel):
        encabezado = Frame(panel, bg=self.colores["tarjeta"])
        encabezado.pack(fill=X, padx=16, pady=(16, 12))

        Label(
            encabezado,
            text="CARRITO DE COMPRA",
            bg=self.colores["tarjeta"],
            fg=self.colores["secundario"],
            font=("Segoe UI", 11, "bold")
        ).pack(side=LEFT)

        columnas = ("codigo", "nombre", "cantidad", "precio", "subtotal")
        self.tabla_carrito = ttk.Treeview(
            panel,
            columns=columnas,
            show="headings",
            style="Tabla.Treeview",
            height=7
        )

        self.tabla_carrito.heading("codigo", text="Código")
        self.tabla_carrito.heading("nombre", text="Producto")
        self.tabla_carrito.heading("cantidad", text="Cant.")
        self.tabla_carrito.heading("precio", text="Precio")
        self.tabla_carrito.heading("subtotal", text="Subtotal")

        # Distribuimos el ancho para que todas las columnas entren dentro del carrito.
        self.tabla_carrito.column("codigo", width=65, anchor=CENTER)
        self.tabla_carrito.column("nombre", width=125, anchor=CENTER)
        self.tabla_carrito.column("cantidad", width=60, anchor=CENTER)
        self.tabla_carrito.column("precio", width=85, anchor=CENTER)
        self.tabla_carrito.column("subtotal", width=95, anchor=CENTER)

        scroll = ttk.Scrollbar(panel, orient=VERTICAL, command=self.tabla_carrito.yview)
        self.tabla_carrito.configure(yscrollcommand=scroll.set)
        self.tabla_carrito.pack(fill=BOTH, expand=True, padx=16, pady=(0, 10))

        botones = Frame(panel, bg=self.colores["tarjeta"])
        botones.pack(fill=X, padx=16, pady=(0, 12))

        ttk.Button(
            botones,
            text="Quitar producto",
            style="Peligro.TButton",
            command=self.quitar_del_carrito
        ).pack(side=LEFT)

        ttk.Button(
            botones,
            text="Vaciar carrito",
            style="Neutro.TButton",
            command=self.vaciar_carrito
        ).pack(side=LEFT, padx=(8, 0))

        # Selector del medio de pago que usará el cliente.
        frame_pago = Frame(panel, bg=self.colores["tarjeta"])
        frame_pago.pack(fill=X, padx=16, pady=(0, 10))

        Label(
            frame_pago,
            text="Medio de pago:",
            bg=self.colores["tarjeta"],
            fg=self.colores["texto"],
            font=("Segoe UI", 10, "bold")
        ).pack(side=LEFT)

        self.medio_pago = ttk.Combobox(
            frame_pago,
            values=["Efectivo", "Transferencia", "Débito", "Crédito"],
            state="readonly",
            width=18
        )

        # Dejamos Efectivo seleccionado por defecto.
        self.medio_pago.set("Efectivo")
        self.medio_pago.pack(side=LEFT, padx=(10, 0))

        pie = Frame(panel, bg=self.colores["tarjeta"])
        pie.pack(fill=X, padx=16, pady=(4, 8))

        self.label_total = Label(
            pie,
            text="TOTAL: $ 0",
            bg=self.colores["tarjeta"],
            fg=self.colores["secundario"],
            font=("Segoe UI", 22, "bold")
        )
        self.label_total.pack(side=LEFT)

        ttk.Button(
            pie,
            text="FINALIZAR VENTA",
            style="Primario.TButton",
            command=self.finalizar_venta
        ).pack(side=RIGHT, ipadx=10, ipady=4)

    # ------------------------------------------------------------------
    # PRODUCTOS Y BÚSQUEDA
    # ------------------------------------------------------------------
    def cargar_productos(self):
        self._mostrar_productos(self.base_datos.obtener_todos())

    def programar_busqueda_venta(self, event=None):
        """Espera un instante antes de buscar mientras el usuario escribe."""

        # Si había una búsqueda pendiente, la cancelamos.
        if hasattr(self, "_busqueda_venta_pendiente"):
            self.entry_buscar.after_cancel(
                self._busqueda_venta_pendiente
            )

        # Esperamos 400 milisegundos desde la última tecla.
        self._busqueda_venta_pendiente = self.entry_buscar.after(
            400,
            self.buscar_producto
        )
        # Esperamos 400 milisegundos desde la última tecla.
        self._busqueda_venta_pendiente = self.entry_buscar.after(
            400,
            self.buscar_producto
    ) 

    def buscar_producto(self):
        texto = self.entry_buscar.get().strip()
        if texto == "":
            self.cargar_productos()
            return

        resultados = []

        # Un código de barras suele ser largo. Primero lo buscamos como código de barras
        # y, si no existe, permitimos igualmente buscar por código interno del producto.
        # Si el usuario escribe números, buscamos tanto por código interno

        #como por código de barras, incluso mientras está escribiendo.
        if texto.isdigit():
            resultados = self.base_datos.buscar_por_codigo_o_barra(texto)

        else:
            # Si contiene letras, buscamos por nombre parcial.
            resultados = self.base_datos.buscar_por_nombre_parcial(texto)

        self._mostrar_productos(resultados)

        # En la búsqueda automática simplemente dejamos la tabla vacía
        # si todavía no existe una coincidencia.
        if not resultados:
            return

    def _mostrar_productos(self, productos):
        for fila in self.tabla_productos.get_children():
            self.tabla_productos.delete(fila)

        for producto in productos:
            codigo, nombre, tipo, categoria, temporada, precio, stock, codigo_barras = producto

            fila = self.tabla_productos.insert(
                "",
                END,
                values=(codigo, nombre, self._formatear_moneda(precio), stock or 0)
            )

            # Si la búsqueda encontró un solo producto, lo seleccionamos automáticamente.
            if len(productos) == 1:
                self.tabla_productos.selection_set(fila)
                self.tabla_productos.focus(fila)

    # ------------------------------------------------------------------
    # CARRITO
    # ------------------------------------------------------------------

    def procesar_codigo_barras(self, event=None):
        """Agrega al carrito el producto encontrado mediante código de barras."""

        codigo_barras = self.entry_buscar.get().strip()

        # Si el campo está vacío, no hacemos nada.
        if codigo_barras == "":
            return

        # Verificamos que exista exactamente ese código de barras.
        resultados = self.base_datos.buscar_por_codigo_barras(codigo_barras)

        if not resultados:
            messagebox.showwarning(
                "Código de barras",
                "No se encontró ningún producto con ese código de barras."
            )
            return

        # Mostramos únicamente el producto encontrado.
        # _mostrar_productos() ya lo selecciona automáticamente si es el único resultado.
        self._mostrar_productos(resultados)

        # El lector agrega siempre una unidad por cada escaneo.
        self.spin_cantidad.delete(0, END)
        self.spin_cantidad.insert(0, "1")

        # Utilizamos la función normal del carrito, que ya controla stock y cantidades.
        self.agregar_al_carrito()

        # Limpiamos el buscador y volvemos a mostrar todos los productos.
        self.entry_buscar.delete(0, END)
        self.cargar_productos()

        # Dejamos el cursor preparado para el próximo escaneo.
        self.entry_buscar.focus_set()    

    def agregar_al_carrito(self):
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            messagebox.showwarning("Producto", "Seleccioná un producto para agregar al carrito.")
            return

        valores = self.tabla_productos.item(seleccion[0], "values")
        codigo = int(valores[0])

        try:
            cantidad = int(self.spin_cantidad.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Cantidad", "Ingresá una cantidad válida mayor a cero.")
            return

        resultado = self.base_datos.buscar_por_codigo(codigo)
        if not resultado:
            messagebox.showerror("Producto", "El producto ya no existe en la base de datos.")
            return

        producto = resultado[0]
        stock_disponible = int(producto[6] or 0)
        cantidad_actual = self.carrito.get(codigo, {}).get("cantidad", 0)

        # Se controla el stock sumando lo que ya existe en el carrito más lo nuevo.
        # Así evitamos vender más unidades de las disponibles antes de confirmar.
        if cantidad_actual + cantidad > stock_disponible:
            messagebox.showwarning(
                "Stock insuficiente",
                f"Stock disponible: {stock_disponible}\n"
                f"Ya tenés en el carrito: {cantidad_actual}"
            )
            return

        precio = self._precio_a_numero(producto[5])

        if codigo in self.carrito:
            self.carrito[codigo]["cantidad"] += cantidad
        else:
            self.carrito[codigo] = {
                "codigo": codigo,
                "nombre": producto[1],
                "cantidad": cantidad,
                "precio": precio
            }

        self._refrescar_carrito()

    def quitar_del_carrito(self):
        seleccion = self.tabla_carrito.selection()
        if not seleccion:
            messagebox.showwarning("Carrito", "Seleccioná un producto del carrito para quitarlo.")
            return

        valores = self.tabla_carrito.item(seleccion[0], "values")
        codigo = int(valores[0])
        self.carrito.pop(codigo, None)
        self._refrescar_carrito()

    def vaciar_carrito(self, pedir_confirmacion=True):
        if not self.carrito:
            return

        if pedir_confirmacion:
            confirmar = messagebox.askyesno("Vaciar carrito", "¿Querés quitar todos los productos?")
            if not confirmar:
                return

        self.carrito.clear()
        self._refrescar_carrito()

    def _refrescar_carrito(self):
        for fila in self.tabla_carrito.get_children():
            self.tabla_carrito.delete(fila)

        total = 0
        for item in self.carrito.values():
            subtotal = item["cantidad"] * item["precio"]
            total += subtotal

            self.tabla_carrito.insert(
                "",
                END,
                values=(
                    item["codigo"],
                    item["nombre"],
                    item["cantidad"],
                    self._formatear_moneda(item["precio"]),
                    self._formatear_moneda(subtotal)
                )
            )

        self.label_total.config(text=f"TOTAL: {self._formatear_moneda(total)}")

    # ------------------------------------------------------------------
    # FINALIZACIÓN DE LA VENTA
    # ------------------------------------------------------------------
    def finalizar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Venta", "El carrito está vacío.")
            return

        total = sum(item["cantidad"] * item["precio"] for item in self.carrito.values())

        # Abrimos una ventana personalizada para confirmar la venta.
        confirmar = self.confirmar_venta_personalizada(total)

        # Si el usuario cancela, detenemos la operación.
        if not confirmar:
            return

        items = list(self.carrito.values())

        try:
            # BaseDatos vuelve a comprobar stock y ejecuta toda la operación
            # dentro de una transacción: venta + detalle + descuento de stock.
            # Obtenemos el medio de pago seleccionado por el usuario.
            medio_pago = self.medio_pago.get()

            # Registramos la venta junto con el medio de pago elegido.
            id_venta = self.base_datos.registrar_venta(
                items,
                total,
                medio_pago
            )

            ruta_ticket = self._generar_ticket(id_venta, items, total, medio_pago)

            # Mostramos el comprobante directamente dentro del sistema.
            
               
        
        except ValueError as error:
            messagebox.showwarning("No se pudo realizar la venta", str(error))
            self.cargar_productos()
            return
        except Exception as error:
            messagebox.showerror("Error", f"Ocurrió un error al registrar la venta:\n{error}")
            return

        messagebox.showinfo(
            "Venta realizada",
            f"Venta N.º {id_venta} registrada correctamente.\n\n"
            f"Ticket generado en:\n{ruta_ticket}"
        )

        self._mostrar_ticket(id_venta, items, total, medio_pago, ruta_ticket)

        self.vaciar_carrito(pedir_confirmacion=False)
        self.cargar_productos()  # Refleja inmediatamente el nuevo stock en pantalla.
        self.entry_buscar.delete(0, END)

    def confirmar_venta_personalizada(self, total):
        """Muestra una ventana personalizada para confirmar la venta."""

        respuesta = {"confirmar": False}

        ventana = Toplevel(self.contenedor)
        ventana.title("Confirmar venta")
        ventana.geometry("420x260")
        ventana.resizable(False, False)
        # Centramos la ventana de confirmación en la pantalla.
        ventana.update_idletasks()

        ancho = 420
        alto = 260

        posicion_x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        posicion_y = (ventana.winfo_screenheight() // 2) - (alto // 2)

        ventana.geometry(
            f"{ancho}x{alto}+{posicion_x}+{posicion_y}"
)

        # La dejamos centrada respecto de la ventana principal.
        ventana.transient(self.contenedor.winfo_toplevel())
        ventana.grab_set()

        Frame(
            ventana,
            bg=self.colores["secundario"],
            height=45
        ).pack(fill=X)

        Label(
            ventana,
            text="CONFIRMAR VENTA",
            bg=self.colores["secundario"],
            fg="white",
            font=("Segoe UI", 14, "bold")
        ).place(relx=0.5, y=23, anchor=CENTER)

        Label(
            ventana,
            text="Total de la venta",
            font=("Segoe UI", 11)
        ).pack(pady=(28, 5))

        Label(
            ventana,
            text=self._formatear_moneda(total),
            fg=self.colores["secundario"],
            font=("Segoe UI", 22, "bold")
        ).pack()

        Label(
            ventana,
            text="¿Confirmar la operación?",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(15, 18))

        frame_botones = Frame(ventana)
        frame_botones.pack()

        def confirmar():
            respuesta["confirmar"] = True
            ventana.destroy()

        Button(
            frame_botones,
            text="CONFIRMAR",
            command=confirmar,
            bg=self.colores["primario"],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=FLAT,
            width=13,
            pady=7,
            cursor="hand2"
        ).pack(side=LEFT, padx=8)

        Button(
            frame_botones,
            text="CANCELAR",
            command=ventana.destroy,
            bg=self.colores["peligro"],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=FLAT,
            width=13,
            pady=7,
            cursor="hand2"
        ).pack(side=LEFT, padx=8)

        # Esperamos hasta que el usuario confirme o cierre la ventana.
        ventana.wait_window()

        return respuesta["confirmar"]


    def _generar_ticket(self, id_venta, items, total, medio_pago):
        """Genera el comprobante de venta en formato TXT."""

        carpeta_tickets = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "tickets"
        )
        os.makedirs(carpeta_tickets, exist_ok=True)

        fecha = datetime.now()

        nombre_archivo = (
            f"ticket_{id_venta}_{fecha.strftime('%Y%m%d_%H%M%S')}.txt"
        )

        ruta = os.path.join(carpeta_tickets, nombre_archivo)

        with open(ruta, "w", encoding="utf-8") as ticket:

            ticket.write("=" * ANCHO_TICKET + "\n")
            # Centramos automáticamente los datos del comercio
            # según el ancho configurado del ticket.
            ticket.write("GUAGUA".center(ANCHO_TICKET) + "\n")
            ticket.write("PAÑALERA".center(ANCHO_TICKET) + "\n")
            ticket.write("Liniers 920 - Rivadavia".center(ANCHO_TICKET) + "\n")
            ticket.write("Mendoza".center(ANCHO_TICKET) + "\n")
            ticket.write("Tel: 2634777200".center(ANCHO_TICKET) + "\n")
            ticket.write("=" * ANCHO_TICKET + "\n")

            ticket.write(
                "COMPROBANTE DE VENTA - NO FISCAL".center(ANCHO_TICKET) + "\n"
            )
            # Indicamos que la venta está destinada a consumidor final.
            ticket.write("CONSUMIDOR FINAL".center(ANCHO_TICKET) + "\n")

            ticket.write("=" * ANCHO_TICKET + "\n")

            ticket.write(f"Venta N.º: {id_venta}\n")
            # Fecha y hora separadas para respetar el ancho de una térmica de 58 mm.
            ticket.write(f"Fecha: {fecha.strftime('%d/%m/%Y')}\n")
            ticket.write(f"Hora: {fecha.strftime('%H:%M:%S')}\n")
            ticket.write(f"Medio de pago: {medio_pago}\n")

            ticket.write("=" * ANCHO_TICKET + "\n")

            for item in items:
                subtotal = item["cantidad"] * item["precio"]

                ticket.write(f"{item['nombre']}\n")

                ticket.write(
                    f"  {item['cantidad']} x "
                    f"{self._formatear_moneda(item['precio'])}"
                    f" = {self._formatear_moneda(subtotal)}\n"
                )
                # Indicamos que el precio final del producto ya incluye el IVA.
                ticket.write("  (IVA 21% incluido)\n")

            ticket.write("-" * ANCHO_TICKET + "\n")

            # Alineamos el total a la derecha según el ancho del ticket.
            texto_total = f"TOTAL: {self._formatear_moneda(total)}"
            ticket.write(texto_total.rjust(ANCHO_TICKET) + "\n")

            ticket.write("=" * ANCHO_TICKET + "\n")
            ticket.write("Gracias por su compra".center(ANCHO_TICKET) + "\n")
            ticket.write("¡Te esperamos!".center(ANCHO_TICKET) + "\n")
            ticket.write("=" * ANCHO_TICKET + "\n")

        return ruta

    # ------------------------------------------------------------------
    # UTILIDADES
    # ------------------------------------------------------------------
    

    def _mostrar_ticket(self, id_venta, items, total, medio_pago, ruta_ticket):
        """Muestra una vista previa del ticket con el mismo formato de impresión."""

        ventana_ticket = Toplevel(self.contenedor)

        ventana_ticket.transient(
            self.contenedor.winfo_toplevel()
        )

        ventana_ticket.lift()
        ventana_ticket.focus_force()

        ventana_ticket.title(
            f"Ticket - Venta N.º {id_venta}"
        )

        # Ventana más angosta para representar mejor un ticket térmico.
        ventana_ticket.geometry("400x600")
        ventana_ticket.resizable(False, False)

        fecha = datetime.now()

        texto_ticket = Text(
            ventana_ticket,
            font=("Consolas", 10),
            padx=20,
            pady=15,
            borderwidth=0
        )

        texto_ticket.pack(
            fill=BOTH,
            expand=True,
            padx=10,
            pady=(10, 0)
        )

        # Encabezado adaptado al ancho configurado del ticket.
        texto_ticket.insert(END, "=" * ANCHO_TICKET + "\n")
        texto_ticket.insert(END, "GUAGUA".center(ANCHO_TICKET) + "\n")
        texto_ticket.insert(END, "PAÑALERA".center(ANCHO_TICKET) + "\n")
        texto_ticket.insert(
            END,
            "Liniers 920 - Rivadavia".center(ANCHO_TICKET) + "\n"
        )
        texto_ticket.insert(END, "Mendoza".center(ANCHO_TICKET) + "\n")
        texto_ticket.insert(
            END,
            "Tel: 2634777200".center(ANCHO_TICKET) + "\n"
        )
        texto_ticket.insert(END, "=" * ANCHO_TICKET + "\n")

        texto_ticket.insert(
            END,
            "COMPROBANTE DE VENTA - NO FISCAL".center(ANCHO_TICKET) + "\n"
        )

        texto_ticket.insert(END, "=" * ANCHO_TICKET + "\n")

        # Datos de la venta.
        texto_ticket.insert(
            END,
            f"Venta N.º: {id_venta}\n"
        )

        # Fecha y hora separadas para respetar el ancho de 58 mm.
        texto_ticket.insert(
            END,
            f"Fecha: {fecha.strftime('%d/%m/%Y')}\n"
        )

        texto_ticket.insert(
            END,
            f"Hora: {fecha.strftime('%H:%M:%S')}\n"
        )

        texto_ticket.insert(
            END,
            f"Medio de pago: {medio_pago}\n"
        )

        texto_ticket.insert(END, "-" * ANCHO_TICKET + "\n")

        # Detalle de los productos vendidos.
        for item in items:
            subtotal = item["cantidad"] * item["precio"]

            texto_ticket.insert(
                END,
                f"{item['nombre']}\n"
            )

            texto_ticket.insert(
                END,
                f"  {item['cantidad']} x "
                f"{self._formatear_moneda(item['precio'])}"
                f" = {self._formatear_moneda(subtotal)}\n"
            )
            texto_ticket.insert(END, "  (IVA 21% incluido)\n")

        texto_ticket.insert(END, "-" * ANCHO_TICKET + "\n")

        # Total alineado a la derecha.
        texto_total = f"TOTAL: {self._formatear_moneda(total)}"

        texto_ticket.insert(
            END,
            texto_total.rjust(ANCHO_TICKET) + "\n"
        )

        texto_ticket.insert(END, "=" * ANCHO_TICKET + "\n")

        # Mensaje final centrado.
        texto_ticket.insert(
            END,
            "Gracias por su compra".center(ANCHO_TICKET) + "\n"
        )

        texto_ticket.insert(
            END,
            "¡Te esperamos!".center(ANCHO_TICKET) + "\n"
        )

        texto_ticket.insert(END, "=" * ANCHO_TICKET + "\n")

        # El ticket es solo de lectura.
        texto_ticket.config(state=DISABLED)

        botones_ticket = Frame(ventana_ticket)
        botones_ticket.pack(pady=12)

        ttk.Button(
            botones_ticket,
            text="🖨 Imprimir ticket",
            command=lambda: self._imprimir_ticket(ruta_ticket)
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            botones_ticket,
            text="Cerrar",
            command=ventana_ticket.destroy
        ).pack(side=LEFT, padx=5)

    

    def _imprimir_ticket(self, ruta_ticket):

        """Envía el ticket a la impresora predeterminada de Windows."""

        try:
            # Windows abre el archivo y lo envía a la impresora predeterminada.
            os.startfile(ruta_ticket, "print")

            messagebox.showinfo(
                "Impresión",
                "El ticket fue enviado a la impresora."
            )

        except Exception as error:
            messagebox.showerror(
                "Error de impresión",
                f"No se pudo imprimir el ticket:\n{error}"
            )  
    @staticmethod 

    def _precio_a_numero(precio):
        # Los precios actuales de tu tabla productos están guardados como TEXT.
        # Limpiamos $, puntos y otros caracteres antes de convertirlos a número.
        solo_numeros = "".join(caracter for caracter in str(precio) if caracter.isdigit())
        return int(solo_numeros) if solo_numeros else 0

    @staticmethod
    
    def _formatear_moneda(valor):
        try:
            numero = int(float(valor))
        except (ValueError, TypeError):
            numero = 0
        return f"$ {numero:,}".replace(",", ".")

    def abrir_cierre_caja(self):
        """Abre una ventana con el resumen del cierre de caja del día."""

        ventana_cierre = Toplevel(self.contenedor)
        ventana_cierre.title("Cierre de caja")
        ventana_cierre.geometry("600x550")
        ventana_cierre.resizable(False, False)

        # Centramos la ventana de Cierre de Caja en la pantalla.
        ventana_cierre.update_idletasks()

        ancho = 600
        alto = 550

        posicion_x = (ventana_cierre.winfo_screenwidth() // 2) - (ancho // 2)
        posicion_y = (ventana_cierre.winfo_screenheight() // 2) - (alto // 2)

        ventana_cierre.geometry(
            f"{ancho}x{alto}+{posicion_x}+{posicion_y}"
        )

        # Mantiene la ventana del cierre por encima de la ventana principal.
        ventana_cierre.transient(
            self.contenedor.winfo_toplevel()
        )

        # Creamos el módulo de cierre de caja dentro de esta nueva ventana.
        CierreCaja(
            ventana_cierre,
            self.base_datos,
            self.colores
        )

    def abrir_historial_ventas(self):
        """Abre una ventana para consultar el historial de ventas."""

        # Creamos una nueva ventana independiente para el historial.
        ventana_historial = Toplevel(self.contenedor)

        # Abrimos el módulo HistorialVentas dentro de la nueva ventana.
        HistorialVentas(
            ventana_historial,
            self.base_datos,
            self.colores
        )
