"""
Clase VentanaPrincipal
-----------------------
Se encarga EXCLUSIVAMENTE de la interfaz visual: crear labels, entries,
botones y la tabla de productos.

Cuando necesita guardar, buscar, modificar o eliminar algo, le pide
el trabajo a un objeto BaseDatos (recibido por parámetro). Esta clase
nunca escribe SQL directamente: solo llama a métodos como
self.base_datos.insertar_producto(...).
"""

import sys
import os
from ventas import GestionVentas
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from cambiar_contrasena import CambiarContrasena


def recurso_path(nombre_archivo):
    """Devuelve la ruta correcta de un archivo, tanto si el programa
    corre como script .py como si corre empaquetado como .exe (PyInstaller)."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, nombre_archivo)


class VentanaPrincipal:
    def __init__(self, base_datos):
        self.base_datos = base_datos

        # ---------------------------------------------------------------
        # Paleta de colores, extraída del logo GUAGUA (amarillo, verde,
        # naranja, azul marino). Se usan como ACENTOS sobre una base
        # neutra clara, en vez de pintar toda la ventana de color:
        # así se ve prolijo y profesional sin perder identidad de marca.
        # Si el día de mañana querés retocar algo, es acá.
        # ---------------------------------------------------------------
        self.COLOR_FONDO = "#F4F5F2"          # gris muy claro, fondo general
        self.COLOR_TARJETA = "#FFFFFF"        # blanco, paneles/tarjetas
        self.COLOR_HEADER = "#002852"         # azul marino del logo
        self.COLOR_HEADER_TEXTO = "#FFDA01"   # amarillo del logo (título)
        self.COLOR_HEADER_SUBTEXTO = "#B8C4D6"
        self.COLOR_TEXTO = "#1F2933"          # gris oscuro para texto general
        self.COLOR_TEXTO_SUAVE = "#6B7280"    # gris medio, para labels
        self.COLOR_BORDE = "#E1E4E0"

        self.COLOR_PRIMARIO = "#00C180"       # verde del logo -> acción principal
        self.COLOR_PRIMARIO_HOVER = "#00A06A"
        self.COLOR_SECUNDARIO = "#002852"     # azul marino -> acciones neutras
        self.COLOR_PELIGRO = "#FB7400"        # naranja del logo -> eliminar
        self.COLOR_PELIGRO_HOVER = "#D96300"

        self.ventana = Tk()
        self.ventana.geometry("1250x700")
        self.ventana.minsize(1000, 550)
        self.ventana.title("GUAGUA - sistema de gestion")
        self.ventana.config(bg=self.COLOR_FONDO)
        # Arranca maximizada, para aprovechar toda la pantalla disponible
        # sin importar la resolución (en Windows, 'zoomed' maximiza).
        try:
            self.ventana.state("zoomed")
        except TclError:
            pass

        self._configurar_estilos_ttk()
        self._crear_encabezado()
        self._crear_layout_principal()
        self._crear_pantalla_inicio()
        self._crear_panel_formulario()
        self._crear_panel_listado()
        self._configurar_atajos_teclado()

        self.cargar_todos_los_productos()
        self.contenedor_inicio.pack(fill=BOTH, expand=True)

    def abrir_cambiar_contrasena(self):
        """Abre la ventana para modificar la contraseña del usuario."""

        CambiarContrasena(
            self.ventana,
            self.base_datos
        )    

    # ---------- Construcción de la interfaz ----------

    def _configurar_estilos_ttk(self):
        """Define estilos reutilizables para los widgets ttk (botones,
        tabla, campos), así todos los componentes se ven consistentes
        entre sí en vez de cada uno con su propio look."""
        estilo = ttk.Style()
        estilo.theme_use("clam")  # tema que permite personalizar colores a fondo

        # --- Botones ---
        estilo.configure("Primario.TButton",
                          background=self.COLOR_PRIMARIO, foreground="white",
                          font=("Segoe UI", 11, "bold"), padding=10, borderwidth=0)
        estilo.map("Primario.TButton",
                    background=[("active", self.COLOR_PRIMARIO_HOVER)])
        estilo.configure("InicioPrimario.TButton",
                          background=self.COLOR_PRIMARIO, foreground="white",
                          font=("Segoe UI", 14, "bold"), padding=16, borderwidth=0)
        estilo.map("InicioPrimario.TButton",
                    background=[("active", self.COLOR_PRIMARIO_HOVER)])

        estilo.configure("InicioSecundario.TButton",
                          background=self.COLOR_PELIGRO, foreground="white",
                          font=("Segoe UI", 14, "bold"), padding=16, borderwidth=0)
        estilo.map("InicioSecundario.TButton",
                    background=[("active", self.COLOR_PELIGRO_HOVER)])

        estilo.configure("Secundario.TButton",
                          background=self.COLOR_SECUNDARIO, foreground="white",
                          font=("Segoe UI", 10, "bold"), padding=9, borderwidth=0)
        estilo.map("Secundario.TButton",
                    background=[("active", "#001B38")])

        estilo.configure("Peligro.TButton",
                          background=self.COLOR_PELIGRO, foreground="white",
                          font=("Segoe UI", 10, "bold"), padding=9, borderwidth=0)
        estilo.map("Peligro.TButton",
                    background=[("active", self.COLOR_PELIGRO_HOVER)])

        estilo.configure("Neutro.TButton",
                          background="#E5E7EB", foreground=self.COLOR_TEXTO,
                          font=("Segoe UI", 10), padding=9, borderwidth=0)
        estilo.map("Neutro.TButton",
                    background=[("active", "#D1D5DB")])

        # --- Campos de texto ---
        estilo.configure("Campo.TEntry",
                          fieldbackground="white", padding=8,
                          bordercolor=self.COLOR_BORDE, lightcolor=self.COLOR_BORDE,
                          darkcolor=self.COLOR_BORDE, borderwidth=1, relief="solid")

        # --- Tabla (Treeview) ---
        estilo.configure("Tabla.Treeview",
                          background="white", fieldbackground="white",
                          foreground=self.COLOR_TEXTO, rowheight=30,
                          font=("Segoe UI", 10), borderwidth=0)
        
        estilo.configure("Tabla.Treeview.Heading",
                          background=self.COLOR_SECUNDARIO, foreground="white",
                          font=("Segoe UI", 10, "bold"), padding=8, relief="flat")
        estilo.map("Tabla.Treeview.Heading",
                    background=[("active", self.COLOR_SECUNDARIO)])
        estilo.map("Tabla.Treeview",
                    background=[("selected", self.COLOR_PRIMARIO)],
                    foreground=[("selected", "white")])

    def _crear_encabezado(self):
        """Franja superior tipo cartel de negocio, con el nombre y los
        atajos de teclado disponibles."""
        franja = Frame(self.ventana, bg=self.COLOR_HEADER, height=70)
        franja.pack(side=TOP, fill=X)
        franja.pack_propagate(False)

        contenedor = Frame(franja, bg=self.COLOR_HEADER)
        contenedor.pack(expand=True, fill=BOTH, padx=25)

        self.label_volver_inicio = Label(contenedor, text="‹ Volver al inicio",
              bg=self.COLOR_HEADER, fg="white",
              font=("Segoe UI", 12), cursor="hand2")
        self.label_volver_inicio.bind("<Button-1>", self.nav_inicio)

        def _resaltar_volver_inicio(evento):
            self.label_volver_inicio.config(bg="#166BAF")#0A3D68

        def _quitar_resaltado_volver_inicio(evento):
            self.label_volver_inicio.config(bg=self.COLOR_HEADER)

        self.label_volver_inicio.bind("<Enter>", _resaltar_volver_inicio)
        self.label_volver_inicio.bind("<Leave>", _quitar_resaltado_volver_inicio)

        # Permite a la usuaria cambiar su contraseña desde el sistema.
        Button(
            contenedor,
            text="🔑 Cambiar contraseña",
            command=self.abrir_cambiar_contrasena,
            bg=self.COLOR_HEADER,
            fg="white",
            activebackground="#166BAF",
            activeforeground="white",
            font=("Segoe UI", 9),
            relief=FLAT,
            cursor="hand2",
            borderwidth=0
        ).pack(side=RIGHT, padx=(15, 5), pady=10)

        Label(contenedor,text= "Rivadavia-Mendoza    Direccion: Liniers 920   Telefono: 2634777200 ",
              bg=self.COLOR_HEADER, fg=self.COLOR_HEADER_SUBTEXTO,
              font=("Segoe UI", 9)).pack(side=RIGHT, pady=10)
    def sacar_frames(self):
        self.contenedor_inicio.pack_forget()
        self.contenedor_principal.pack_forget()
        self.contenedor_principal2.pack_forget()
    def nav_gestion(self,evento=None):
        self.sacar_frames()
        self.contenedor_principal.pack(fill=BOTH, expand=True, padx=20, pady=20)
        self.label_volver_inicio.pack(side=LEFT, pady=10)
    def nav_ventas(self,evento=None):
        self.sacar_frames()
        self.contenedor_principal2.pack(fill=BOTH, expand=True, padx=20, pady=20)
        self.label_volver_inicio.pack(side=LEFT, pady=10)
    def nav_inicio(self, evento=None):
        self.sacar_frames()
        self.label_volver_inicio.pack_forget()
        self.contenedor_inicio.pack(fill=BOTH, expand=True)
    def _crear_layout_principal(self):
        """Contenedor general debajo del encabezado, dividido en dos
        columnas: formulario a la izquierda, listado a la derecha."""
        self.contenedor_inicio = Frame(self.ventana, bg=self.COLOR_HEADER)
        self.contenedor_principal = Frame(self.ventana, bg=self.COLOR_FONDO)
        #self.contenedor_principal.pack(fill=BOTH, expand=True, padx=20, pady=20)
        self.contenedor_principal2 = Frame(self.ventana, bg=self.COLOR_FONDO)

        # Creamos el módulo de Gestión de Ventas dentro del contenedor correspondiente.
        self.modulo_ventas = GestionVentas(
        self.contenedor_principal2,
        self.base_datos,
        {
        "fondo": self.COLOR_FONDO,
        "tarjeta": self.COLOR_TARJETA,
        "texto": self.COLOR_TEXTO,
        "texto_suave": self.COLOR_TEXTO_SUAVE,
        "borde": self.COLOR_BORDE,
        "primario": self.COLOR_PRIMARIO,
        "secundario": self.COLOR_SECUNDARIO,
        "peligro": self.COLOR_PELIGRO,
        }
    )       
        self.panel_izquierdo = Frame(self.contenedor_principal, bg=self.COLOR_TARJETA,
                                      width=320, highlightbackground=self.COLOR_BORDE,
                                      highlightthickness=1)
        self.panel_izquierdo.pack(side=LEFT, fill=Y, padx=(0, 20))
        self.panel_izquierdo.pack_propagate(False)

        # --- Canvas con scroll, para que el formulario NUNCA quede
        # cortado, sin importar la altura de la pantalla del usuario. ---
        self._canvas_formulario = Canvas(self.panel_izquierdo, bg=self.COLOR_TARJETA,
                                          highlightthickness=0)
        barra_scroll_form = ttk.Scrollbar(self.panel_izquierdo, orient=VERTICAL,
                                           command=self._canvas_formulario.yview)
        self._canvas_formulario.configure(yscrollcommand=barra_scroll_form.set)

        self._canvas_formulario.pack(side=LEFT, fill=BOTH, expand=True)
        barra_scroll_form.pack(side=RIGHT, fill=Y)

        self.frame_formulario = Frame(self._canvas_formulario, bg=self.COLOR_TARJETA)
        self._ventana_canvas = self._canvas_formulario.create_window(
            (0, 0), window=self.frame_formulario, anchor="nw"
        )

        def _actualizar_scrollregion(evento):
            self._canvas_formulario.configure(
                scrollregion=self._canvas_formulario.bbox("all")
            )

        def _ajustar_ancho_interior(evento):
            self._canvas_formulario.itemconfig(self._ventana_canvas, width=evento.width)

        self.frame_formulario.bind("<Configure>", _actualizar_scrollregion)
        self._canvas_formulario.bind("<Configure>", _ajustar_ancho_interior)

        # Rueda del mouse: solo activa cuando el cursor está sobre este panel
        def _scroll_con_mouse(evento):
            self._canvas_formulario.yview_scroll(int(-1 * (evento.delta / 120)), "units")

        self._canvas_formulario.bind(
            "<Enter>", lambda e: self._canvas_formulario.bind_all("<MouseWheel>", _scroll_con_mouse)
        )
        self._canvas_formulario.bind(
            "<Leave>", lambda e: self._canvas_formulario.unbind_all("<MouseWheel>")
        )

        self.panel_derecho = Frame(self.contenedor_principal, bg=self.COLOR_TARJETA,
                                    highlightbackground=self.COLOR_BORDE,
                                    highlightthickness=1)
        self.panel_derecho.pack(side=RIGHT, fill=BOTH, expand=True)
    def _crear_pantalla_inicio(self):
        """Pantalla de bienvenida: logo grande y los 2 botones para
        elegir entre Gestión de productos y Gestión de ventas.
        El fondo tiene un patrón sutil de líneas diagonales finas."""
        canvas_fondo = Canvas(self.contenedor_inicio, bg=self.COLOR_HEADER, highlightthickness=0)
        canvas_fondo.pack(fill=BOTH, expand=True)

        color_lineas = "#0A3D68"  # un toque más claro que el fondo, para que se note apenas

        def _dibujar_puntos(evento=None):
            canvas_fondo.delete("punto_fondo")
            ancho = canvas_fondo.winfo_width()
            alto = canvas_fondo.winfo_height()
            espacio = 28  # separación entre puntos, en píxeles
            radio = 1.3   # tamaño de cada punto
            for y in range(0, alto, espacio):
                for x in range(0, ancho, espacio):
                    canvas_fondo.create_oval(x - radio, y - radio, x + radio, y + radio,
                                              fill=color_lineas, outline="", tags="punto_fondo")

        canvas_fondo.bind("<Configure>", _dibujar_puntos)

        contenido = Frame(canvas_fondo, bg=self.COLOR_HEADER)
        canvas_fondo.create_window(0, 0, window=contenido, anchor="center", tags="contenido_inicio")

        def _centrar_contenido(evento):
            canvas_fondo.coords("contenido_inicio", evento.width // 2, evento.height // 2)

        canvas_fondo.bind("<Configure>", _centrar_contenido, add="+")

        imagen_png = Image.open(recurso_path("guagua_circulo.png"))
        proporcion = 380 / imagen_png.width
        imagen_inicio = imagen_png.resize((380, int(imagen_png.height * proporcion)))
        self.imagen_inicio_tk = ImageTk.PhotoImage(imagen_inicio)
        Label(contenido, image=self.imagen_inicio_tk, bg=self.COLOR_HEADER).pack(pady=(0, 40))

        

        ttk.Button(contenido, text="📦  Gestión de productos", style="InicioPrimario.TButton",
                   width=22, command=self.nav_gestion).pack(ipady=6, pady=(0, 14))

        ttk.Button(contenido, text="🛒  Gestión de ventas", style="InicioSecundario.TButton",
                   width=22, command=self.nav_ventas).pack(ipady=6)

    def _crear_panel_formulario(self):
        """Panel izquierdo: logo, campos del producto y botones de acción.
        Vive DENTRO del canvas con scroll creado en _crear_layout_principal."""
        contenido = Frame(self.frame_formulario, bg=self.COLOR_TARJETA)
        contenido.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # Logo dentro de una placa negra, más grande, con contraste
        imagen_png = Image.open(recurso_path("guagua_circulo.png"))
        proporcion = 240 / imagen_png.width
        imagen = imagen_png.resize((240, int(imagen_png.height * proporcion)))
        self.imagen_tk = ImageTk.PhotoImage(imagen)

        placa_logo = Frame(contenido, bg="black")
        placa_logo.pack(pady=(0, 12))
        Label(placa_logo, image=self.imagen_tk, bg="black").pack(padx=15, pady=15)

        # Código: solo lectura, se genera solo
        self._crear_etiqueta(contenido, "Código (automático)")
        self.entry_codigo = ttk.Entry(contenido, style="Campo.TEntry",
                                       font=("Segoe UI", 11), state="readonly")
        self.entry_codigo.pack(fill=X, pady=(0, 10))

        self.entry_nombre = self._crear_campo(contenido, "Nombre")
        self.entry_tipo = self._crear_campo(contenido, "Tipo")
        self.entry_categoria = self._crear_campo(contenido, "Categoria")
        self.entry_temporada = self._crear_campo(contenido, "Temporada")
        self.entry_precio = self._crear_campo(contenido, "Precio")
        self.entry_stock = self._crear_campo(contenido, "Stock")
        self.entry_codigo_barras = self._crear_campo(contenido, "Código de barras", ultimo=True)

        self._crear_botones(contenido)

    def _crear_etiqueta(self, contenedor, texto):
        Label(contenedor, text=texto.upper(),
              bg=self.COLOR_TARJETA, fg=self.COLOR_TEXTO_SUAVE,
              font=("Segoe UI", 8, "bold")).pack(anchor=W)

    def _crear_campo(self, contenedor, texto_label, ultimo=False):
        self._crear_etiqueta(contenedor, texto_label)
        entry = ttk.Entry(contenedor, style="Campo.TEntry", font=("Segoe UI", 11))
        entry.pack(fill=X, pady=(0, 3 if ultimo else 10))
        return entry

    def _crear_botones(self, contenedor):
        """Botones de acción, ordenados según el flujo natural de uso:
        primero la acción principal (Guardar), después las de edición
        (Modificar / Eliminar), y por último las utilitarias (Limpiar)."""
        espacio = Frame(contenedor, bg=self.COLOR_TARJETA, height=8)
        espacio.pack(fill=X)

        ttk.Button(contenedor, text="Guardar producto (F5)",
                   style="Primario.TButton",
                   command=self.guardar).pack(fill=X, pady=(10, 6))

        fila_editar = Frame(contenedor, bg=self.COLOR_TARJETA)
        fila_editar.pack(fill=X, pady=(0, 6))
        ttk.Button(fila_editar, text="Modificar (F8)", style="Secundario.TButton",
                   command=self.modificar).pack(side=LEFT, fill=X, expand=True, padx=(0, 4))
        ttk.Button(fila_editar, text="Eliminar (F9)", style="Peligro.TButton",
                   command=self.eliminar).pack(side=LEFT, fill=X, expand=True, padx=(4, 0))

        ttk.Button(contenedor, text="Limpiar campos (F12)", style="Neutro.TButton",
                   command=self.limpiar_campos).pack(fill=X)
        ttk.Button(contenedor, text="Actualizar precios", style="Secundario.TButton",
           command=self.abrir_ventana_actualizar_precios).pack(fill=X, pady=(10, 0))

    def _crear_panel_listado(self):
        """Panel derecho: buscador arriba y tabla de productos abajo."""
        contenido = Frame(self.panel_derecho, bg=self.COLOR_TARJETA)
        contenido.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # --- Buscador ---
        Label(contenido, text="BUSCAR PRODUCTO (por código,nombre o código de barra)",
              bg=self.COLOR_TARJETA, fg=self.COLOR_TEXTO_SUAVE,
              font=("Segoe UI", 8, "bold")).pack(anchor=W)

        fila_busqueda = Frame(contenido, bg=self.COLOR_TARJETA)
        fila_busqueda.pack(fill=X, pady=(2, 15))

        self.entry_buscador = ttk.Entry(fila_busqueda, style="Campo.TEntry",
                                         font=("Segoe UI", 11))
        self.entry_buscador.pack(side=LEFT, fill=X, expand=True, ipady=2)
        # Permite buscar automáticamente cuando el lector envía Enter.
        # Espera a que el usuario termine de escribir antes de realizar la búsqueda.
        self.entry_buscador.bind("<KeyRelease>", self.programar_busqueda)

        ttk.Button(fila_busqueda, text="Buscar (F1)", style="Secundario.TButton",
                   command=self.buscar).pack(side=LEFT, padx=(8, 0))
        ttk.Button(fila_busqueda, text="Ver todos", style="Neutro.TButton",
                   command=self.cargar_todos_los_productos).pack(side=LEFT, padx=(8, 0))

        # --- Título de la tabla ---
        fila_titulo = Frame(contenido, bg=self.COLOR_TARJETA)
        fila_titulo.pack(fill=X)
        Label(fila_titulo, text="Listado de productos",
              bg=self.COLOR_TARJETA, fg=self.COLOR_TEXTO,
              font=("Segoe UI", 12, "bold")).pack(side=LEFT)
        self.label_contador = Label(fila_titulo, text="",
                                     bg=self.COLOR_TARJETA, fg=self.COLOR_TEXTO_SUAVE,
                                     font=("Segoe UI", 9))
        self.label_contador.pack(side=RIGHT)

        # --- Tabla ---
        marco_tabla = Frame(contenido, bg=self.COLOR_BORDE, highlightthickness=1,
                             highlightbackground=self.COLOR_BORDE)
        marco_tabla.pack(fill=BOTH, expand=True, pady=(8, 0))

        columnas = ("codigo", "nombre", "tipo", "categoria", "temporada", "precio", "stock", "codigo_barras")
        nombres_columnas = ("Código", "Nombre", "Tipo", "Categoría", "Temporada", "Precio","stock", "codigo_barras")

        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings",
                                   style="Tabla.Treeview")
        anchos = (60, 220, 95, 95, 110, 85, 65, 120)
        for col, nombre_col, ancho in zip(columnas, nombres_columnas, anchos):
            self.tabla.heading(col, text=nombre_col, anchor=W)
            self.tabla.column(col, width=ancho, anchor=W)#
        self.tabla.heading("precio", anchor=E)
        self.tabla.heading("stock", anchor=CENTER)
        self.tabla.column("precio", anchor=E)
        self.tabla.column("stock", anchor=CENTER)

        # Filas alternadas (cebra) para que sea más fácil de leer
        self.tabla.tag_configure("par", background="#FAFBFA")
        self.tabla.tag_configure("impar", background="white")

        barra_scroll_v = ttk.Scrollbar(marco_tabla, orient=VERTICAL, command=self.tabla.yview)
        barra_scroll_h = ttk.Scrollbar(contenido, orient=HORIZONTAL, command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=barra_scroll_v.set, xscrollcommand=barra_scroll_h.set)

        self.tabla.pack(side=LEFT, fill=BOTH, expand=True)
        barra_scroll_v.pack(side=RIGHT, fill=Y)
        barra_scroll_h.pack(side=BOTTOM, fill=X)

        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar_fila)

    def _configurar_atajos_teclado(self):
        """Conecta las teclas de función mostradas en el encabezado
        con las acciones reales, para que no sean solo decorativas."""
        self.ventana.bind("<F1>", lambda evento: self.entry_buscador.focus_set())
        self.ventana.bind("<F5>", lambda evento: self.guardar())
        self.ventana.bind("<F8>", lambda evento: self.modificar())
        self.ventana.bind("<F9>", lambda evento: self.eliminar())
        self.ventana.bind("<F12>", lambda evento: self.limpiar_campos())
        self.entry_buscador.bind("<Return>", lambda evento: self.buscar()) 
        

    # ---------- Métodos auxiliares ----------
    def abrir_ventana_actualizar_precios(self):
        """Abre una ventanita aparte donde el cliente elige una categoría
        (o todas) y un porcentaje, para aumentar o disminuir precios
        en forma masiva."""
        ventana_emergente = Toplevel(self.ventana)
        ventana_emergente.title("Actualizar precios")
        ventana_emergente.geometry("380x260")
        ventana_emergente.config(bg=self.COLOR_TARJETA)
        ventana_emergente.resizable(False, False)

        contenido = Frame(ventana_emergente, bg=self.COLOR_TARJETA)
        contenido.pack(fill=BOTH, expand=True, padx=20, pady=20)

        Label(contenido, text="Aplicar a tipo de producto:",
              bg=self.COLOR_TARJETA, fg=self.COLOR_TEXTO,
              font=("Segoe UI", 10, "bold")).pack(anchor=W)

        tipos = ["Todos los tipos"] + self.base_datos.obtener_tipos()
        variable_tipo = StringVar(value=tipos[0])
        combo_tipo = ttk.Combobox(contenido, textvariable=variable_tipo,
                                   values=tipos, state="readonly",
                                   font=("Segoe UI", 10))
        combo_tipo.pack(fill=X, pady=(4, 15))

        Label(contenido, text="Porcentaje (ej: 15 para +15%, -10 para -10%):",
              bg=self.COLOR_TARJETA, fg=self.COLOR_TEXTO,
              font=("Segoe UI", 10, "bold")).pack(anchor=W)

        entry_porcentaje = ttk.Entry(contenido, style="Campo.TEntry", font=("Segoe UI", 11))
        entry_porcentaje.pack(fill=X, pady=(4, 20))

        def confirmar():
            self._confirmar_actualizacion_precios(
                variable_tipo.get(), entry_porcentaje.get(), ventana_emergente
            )

        ttk.Button(contenido, text="Aplicar aumento", style="Primario.TButton",
                   command=confirmar).pack(fill=X)
        
    def _confirmar_actualizacion_precios(self, categoria_elegida, porcentaje_texto, ventana_emergente):
        """Valida lo que escribió el cliente en la ventanita, y si está
        todo bien, aplica el aumento/descuento a la base de datos."""
        porcentaje_texto = porcentaje_texto.strip().replace(",", ".")

        try:
            porcentaje = float(porcentaje_texto)
        except ValueError:
            messagebox.showwarning(
                title="Porcentaje inválido",
                message="Escribí un número válido, por ejemplo 15 o -10."
            )
            return

        if categoria_elegida == "Todas las categorías":
            categoria_para_filtrar = None
        else:
            categoria_para_filtrar = categoria_elegida

        cantidad = self.base_datos.aplicar_aumento_precio(porcentaje, categoria_para_filtrar)

        ventana_emergente.destroy()
        messagebox.showinfo(
            title="Precios actualizados",
            message=f"Se actualizó el precio de {cantidad} producto(s) "
                    f"con un {porcentaje}% de {'aumento' if porcentaje >= 0 else 'descuento'}."
        )
        self.cargar_todos_los_productos()
        

    def limpiar_campos(self):
        self.entry_codigo.config(state="normal")
        self.entry_codigo.delete(0, END)
        self.entry_codigo.config(state="readonly")
        for entry in (self.entry_nombre, self.entry_tipo, self.entry_categoria,
                      self.entry_temporada, self.entry_precio, self.entry_stock, self.entry_codigo_barras):
            entry.delete(0, END)
    def formatear_precio(self, precio_texto):
        """Recibe el precio tal como está guardado (por ejemplo '15000')
        y devuelve siempre el mismo formato con signo $ y puntos de miles.
        Ejemplo: '15000' -> '$ 15.000'"""
        solo_numeros = "".join(caracter for caracter in str(precio_texto) if caracter.isdigit())
        if solo_numeros == "":
            return precio_texto
        numero = int(solo_numeros)
        return f"$ {numero:,}".replace(",", ".")

    def cargar_fila_en_campos(self, fila):
        """fila = (codigo, nombre, tipo, categoria, temporada, precio)"""
        ...

    def cargar_fila_en_campos(self, fila):
        """fila = (codigo, nombre, tipo, categoria, temporada, precio)"""
        self.limpiar_campos()
        self.entry_codigo.config(state="normal")
        self.entry_codigo.insert(END, fila[0])
        self.entry_codigo.config(state="readonly")
        self.entry_nombre.insert(END, fila[1])
        self.entry_tipo.insert(END, fila[2])
        self.entry_categoria.insert(END, fila[3])
        self.entry_temporada.insert(END, fila[4])
        precio_limpio = "".join(caracter for caracter in str(fila[5]) if caracter.isdigit())# de esta forma el precio no me larga preceio sin el $ y no me da error
        self.entry_precio.insert(END, precio_limpio)
        self.entry_stock.insert(END,fila[6] if fila [6] is not None else "") # ME LARGABA UN ERROR EN LA VENTANA AL NO TENER LA DB CON STOCK
        self.entry_codigo_barras.insert(END, fila[7] if fila[7] is not None else "")
        
    def refrescar_tabla(self, productos):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for indice, producto in enumerate(productos):
            etiqueta = "par" if indice % 2 == 0 else "impar"
            codigo, nombre, tipo, categoria, temporada, precio, stock, codigo_barras = producto
            precio_formateado = self.formatear_precio(precio)
            codigo_barras_mostrar = f"   {codigo_barras}" if codigo_barras is not None else ""
            fila_para_mostrar = (codigo, nombre, tipo, categoria, temporada, precio_formateado, stock, codigo_barras_mostrar)
            self.tabla.insert("", END, values=fila_para_mostrar, tags=(etiqueta,))

        cantidad = len(productos)
        texto = "1 producto" if cantidad == 1 else f"{cantidad} productos"
        self.label_contador.config(text=texto)
        
    def al_seleccionar_fila(self, evento):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        valores = self.tabla.item(seleccion[0], "values")
        self.cargar_fila_en_campos(valores)

    def validar_campos_obligatorios(self):
        """Devuelve True si todos los campos obligatorios están completos.
        Si falta alguno, avisa con un messagebox y devuelve False."""
        campos = {
            "Nombre": self.entry_nombre.get().strip(),
            "Tipo": self.entry_tipo.get().strip(),
            "Categoría": self.entry_categoria.get().strip(),
            "Temporada": self.entry_temporada.get().strip(),
            "Precio": self.entry_precio.get().strip(),
            "Stock": self.entry_stock.get().strip(),
            "codigo_barras": self.entry_codigo_barras.get().strip(),
        }
        faltantes = [nombre_campo for nombre_campo, valor in campos.items() if valor == ""]
        if faltantes:
            messagebox.showwarning(
                title="Campos incompletos",
                message="Completá los siguientes campos antes de continuar:\n\n"
                        + "\n".join(f"- {campo}" for campo in faltantes)
            )
            return False

        # Validación extra: el precio debe ser un número
        try:
            float(campos["Precio"].replace(",", "."))
        except ValueError:
            messagebox.showwarning(
                title="Precio inválido",
                message="El precio debe ser un valor numérico (ejemplo: 15000 o 15000.50)."
            )
            return False

        return True

    # ---------- Acciones de los botones ----------

    def buscar(self):
        texto = self.entry_buscador.get().strip()

        # Si el buscador está vacío, mostramos todos los productos.
        if texto == "":
            self.cargar_todos_los_productos()
            return

        resultados = []

        # Si es numérico, primero buscamos por código de barras.
        if texto.isdigit():
            # Busca por código interno exacto o por el inicio del código de barras.
            resultados = self.base_datos.buscar_por_codigo_o_barra(texto)

            # Si no encontró por código de barras,
            # recién ahí buscamos por código interno.
            if not resultados:
                resultados = self.base_datos.buscar_por_codigo(int(texto))

        else:
            # Si tiene letras, buscamos por nombre parcial.
            resultados = self.base_datos.buscar_por_nombre_parcial(texto)

        # Actualizamos la tabla con lo encontrado.
        self.refrescar_tabla(resultados)

        # Si encontramos un solo producto,
        # cargamos sus datos automáticamente en el formulario.
        if len(resultados) == 1:
            # Guardamos lo que el usuario está escribiendo en el buscador.
            texto_buscado = self.entry_buscador.get()

            # Cargamos el producto encontrado en el CRUD.
            self.cargar_fila_en_campos(resultados[0])

            # Restauramos el texto por si limpiar_campos() modificó el buscador.
            self.entry_buscador.delete(0, END)
            self.entry_buscador.insert(0, texto_buscado)

            # Dejamos nuevamente el cursor en el buscador para poder seguir escribiendo.
            self.entry_buscador.icursor(END)
            self.entry_buscador.focus_set()

    def programar_busqueda(self, event=None):
        """Espera un instante antes de buscar para evitar búsquedas por cada tecla."""

        # Si ya había una búsqueda pendiente, la cancelamos.
        if hasattr(self, "_busqueda_pendiente"):
            self.entry_buscador.after_cancel(self._busqueda_pendiente)

        # Esperamos 400 milisegundos desde la última tecla.
        self._busqueda_pendiente = self.entry_buscador.after(
            400,
            self.buscar
        )

    def guardar(self):
        if not self.validar_campos_obligatorios():
            return

        self.base_datos.insertar_producto(
            self.entry_nombre.get().strip(),
            self.entry_tipo.get().strip(),
            self.entry_categoria.get().strip(),
            self.entry_temporada.get().strip(),
            self.entry_precio.get().strip(),
            self.entry_stock.get().strip(),
            self.entry_codigo_barras.get().strip()
            
        )
        messagebox.showinfo(title="GUAGUA", message="Producto guardado correctamente")
        self.limpiar_campos()
        self.cargar_todos_los_productos()

    def modificar(self):
        codigo = self.entry_codigo.get().strip()
        if codigo == "":
            messagebox.showwarning(
                title="Falta seleccionar producto",
                message="Primero buscá o seleccioná de la tabla el producto que querés modificar."
            )
            return

        if not self.validar_campos_obligatorios():
            return

        filas_afectadas = self.base_datos.modificar_producto(
            int(codigo),
            self.entry_nombre.get().strip(),
            self.entry_tipo.get().strip(),
            self.entry_categoria.get().strip(),
            self.entry_temporada.get().strip(),
            self.entry_precio.get().strip(),
            self.entry_stock.get().strip(),
            self.entry_codigo_barras.get().strip()
        )
        if filas_afectadas == 0:
            messagebox.showerror(title="Error", message="No se encontró ese código para modificar.")
            return

        messagebox.showinfo(title="GUAGUA", message="Producto modificado correctamente")
        self.limpiar_campos()
        self.cargar_todos_los_productos()

    def eliminar(self):
        codigo = self.entry_codigo.get().strip()
        if codigo == "":
            messagebox.showwarning(
                title="Falta seleccionar producto",
                message="Primero buscá o seleccioná de la tabla el producto que querés eliminar."
            )
            return

        confirmar = messagebox.askyesno(
            title="Confirmar eliminación",
            message=f"¿Seguro que querés eliminar el producto con código {codigo}?"
        )
        if not confirmar:
            return

        filas_afectadas = self.base_datos.eliminar_producto(int(codigo))
        if filas_afectadas == 0:
            messagebox.showerror(title="Error", message="No se encontró ese código para eliminar.")
            return

        messagebox.showinfo(title="GUAGUA", message="Producto eliminado correctamente")
        self.limpiar_campos()
        self.cargar_todos_los_productos()

    def cargar_todos_los_productos(self):
        productos = self.base_datos.obtener_todos()
        self.refrescar_tabla(productos)

    # ---------- Arranque ----------

    def iniciar(self):
        self.ventana.mainloop()
