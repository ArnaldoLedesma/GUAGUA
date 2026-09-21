"""
Clase BaseDatos
----------------
Se encarga EXCLUSIVAMENTE de hablar con SQLite: conectar, insertar,
buscar, actualizar y eliminar productos.

No sabe nada de Tkinter, ventanas ni botones. Si mañana cambiamos
la interfaz gráfica (por ejemplo, pasamos de Tkinter a otra librería),
esta clase no necesita modificarse en absoluto.
"""

import sqlite3
import hashlib # lo utilizamos para el recupero de la contraseña dentro de nuestro sistema


class BaseDatos:
    def __init__(self, ruta_db):
        # La conexión se abre una sola vez, al crear el objeto.
        self.conexion = sqlite3.connect(ruta_db)

        self.crear_tabla_si_no_existe()
        self.crear_tablas_ventas_si_no_existen()

        # Primero creamos la tabla de usuarios.
        self.crear_tabla_usuarios_si_no_existe()

        # Después creamos el usuario administrador inicial.
        self.crear_usuario_inicial()

    def crear_tabla_si_no_existe(self):
        """Si alguien corre el programa con una base de datos vacía,
        esto crea la tabla productos con la misma estructura que ya
        tenías, para que el programa no se rompa."""
        cursor = self.conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                codigo INTEGER PRIMARY KEY,
                nombre TEXT,
                tipo TEXT,
                categoria TEXT,
                temporada TEXT,
                precio TEXT,
                stock INTEGER,
                codigo_barras TEXT
            )
        """)
        self.conexion.commit()
        cursor.close()

    def crear_tabla_usuarios_si_no_existe(self):
        """Crea la tabla donde se guardan los usuarios del sistema."""

        cursor = self.conexion.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                contrasena_hash TEXT NOT NULL
            )
        """)

        self.conexion.commit()
        cursor.close()   

    def crear_tablas_ventas_si_no_existen(self):
        """Crea las tablas necesarias para guardar la venta
        y el detalle de los productos vendidos."""
    
        cursor = self.conexion.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            total INTEGER NOT NULL,
            medio_pago TEXT
         )
        """)
        # Si la tabla ventas ya existía, agregamos la columna medio_pago.
        try:
            cursor.execute("ALTER TABLE ventas ADD COLUMN medio_pago TEXT")
        except sqlite3.OperationalError:
            # Si la columna ya existe, simplemente continuamos.
            pass

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta INTEGER NOT NULL,
            codigo_producto INTEGER NOT NULL,
            nombre_producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario INTEGER NOT NULL,
            subtotal INTEGER NOT NULL,
            FOREIGN KEY (id_venta) REFERENCES ventas(id_venta)
        )
        """)

        self.conexion.commit()
        cursor.close()

    def crear_usuario_inicial(self):
        """Crea el usuario administrador solamente si todavía no existe."""

        usuario = "admin"
        contrasena = "guagua123"

        # Convertimos la contraseña en una huella digital (hash).
        contrasena_hash = hashlib.sha256(
            contrasena.encode("utf-8")
        ).hexdigest()

        cursor = self.conexion.cursor()

        # INSERT OR IGNORE evita crear nuevamente el usuario si ya existe.
        cursor.execute(
            """
            INSERT OR IGNORE INTO usuarios (usuario, contrasena_hash)
            VALUES (?, ?)
            """,
            (usuario, contrasena_hash)
        )

        self.conexion.commit()
        cursor.close()

    

    def registrar_venta(self, items, total, medio_pago):
        """Guarda la venta completa y descuenta el stock."""

        from datetime import datetime

        cursor = self.conexion.cursor()

        try:
            # Iniciamos una transacción:
            # si algo falla, ningún cambio queda guardado a medias.
            cursor.execute("BEGIN")

            # Verificamos nuevamente el stock real antes de vender.
            for item in items:
                cursor.execute(
                    "SELECT nombre, stock FROM productos WHERE codigo = ?",
                    (item["codigo"],)
                )

                producto = cursor.fetchone()

                if producto is None:
                    raise ValueError(
                        f"El producto código {item['codigo']} ya no existe."
                    )

                nombre, stock_actual = producto
                stock_actual = int(stock_actual or 0)

                if item["cantidad"] > stock_actual:
                    raise ValueError(
                        f"Stock insuficiente para {nombre}. "
                        f"Disponible: {stock_actual}."
                    )

            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                "INSERT INTO ventas (fecha, total, medio_pago) VALUES (?, ?, ?)",
                (fecha, int(total), medio_pago)
            )

            # lastrowid obtiene el número de la venta recién creada.
            id_venta = cursor.lastrowid

            for item in items:

                subtotal = item["cantidad"] * item["precio"]

                cursor.execute(
                    """
                    INSERT INTO detalle_ventas
                    (id_venta, codigo_producto, nombre_producto,
                    cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        id_venta,
                        item["codigo"],
                        item["nombre"],
                        item["cantidad"],
                        item["precio"],
                        subtotal
                    )
                )

                # Restamos del inventario la cantidad vendida.
                cursor.execute(
                    "UPDATE productos SET stock = stock - ? WHERE codigo = ?",
                    (item["cantidad"], item["codigo"])
                )

            # Confirmamos venta + detalle + descuento de stock.
            self.conexion.commit()

            return id_venta

        except Exception:
            # Si ocurre un error, SQLite vuelve todo al estado anterior.
            self.conexion.rollback()
            raise

        finally:
            cursor.close()

    def insertar_producto(self, nombre, tipo, categoria, temporada, precio, stock, codigo_barras):
        cursor = self.conexion.cursor()
        cursor.execute(
            "INSERT INTO productos (nombre, tipo, categoria, temporada, precio, stock, codigo_barras) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (nombre, tipo, categoria, temporada, precio, stock, codigo_barras)
        )
        self.conexion.commit()
        cursor.close()

    def buscar_por_codigo(self, codigo):
        """Búsqueda exacta por código (como funcionaba antes)."""
        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM productos WHERE codigo = ?", (codigo,))
        resultado = cursor.fetchall()
        cursor.close()
        return resultado
    def buscar_por_codigo_barras(self, codigo_barras):
        """Busca un producto por código de barras exacto."""

        cursor = self.conexion.cursor()

        cursor.execute(
            "SELECT * FROM productos WHERE TRIM(codigo_barras) = ?",
            (str(codigo_barras).strip(),)
        )

        resultados = cursor.fetchall()

       

        cursor.close()

        return resultados

    def buscar_por_codigo_o_barra(self, texto):
        """Busca por código interno exacto o por el inicio del código de barras."""

        cursor = self.conexion.cursor()

        cursor.execute(
                """
                SELECT *
                FROM productos
                WHERE CAST(codigo AS TEXT) = ?
                OR codigo_barras LIKE ?
                """,
                (texto, texto + "%")
            )

        resultados = cursor.fetchall()
        cursor.close()

        return resultados



    def buscar_por_nombre_parcial(self, texto_busqueda):
        """Búsqueda parcial por nombre: si buscás 'pañal', encuentra
        cualquier producto cuyo nombre CONTENGA esa palabra, sin
        importar mayúsculas/minúsculas."""
        cursor = self.conexion.cursor()
        patron = f"%{texto_busqueda}%"
        cursor.execute(
            "SELECT * FROM productos WHERE nombre LIKE ? COLLATE NOCASE",
            (patron,)
        )
        resultado = cursor.fetchall()
        cursor.close()
        return resultado

    def obtener_todos(self):
        """Trae todos los productos, para mostrarlos en la tabla."""
        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM productos ORDER BY codigo")
        resultado = cursor.fetchall()
        cursor.close()
        return resultado
    
    def obtener_tipos(self):
        """Devuelve la lista de tipos distintos que ya existen entre los
        productos cargados (ROPA, PAÑALES, ACCESORIO...), para armar el
        desplegable de actualización de precios."""
        cursor = self.conexion.cursor()
        cursor.execute("SELECT DISTINCT tipo FROM productos WHERE tipo != '' ORDER BY tipo")
        resultado = [fila[0] for fila in cursor.fetchall()]
        cursor.close()
        return resultado

    def aplicar_aumento_precio(self, porcentaje, tipo=None):
        """Aumenta (o disminuye, si porcentaje es negativo) el precio de
        los productos en el porcentaje indicado. Si categoria es None,
        se aplica a TODOS los productos. Si se pasa una categoría puntual,
        solo se aplica a los productos de esa categoría.
        Devuelve la cantidad de productos que se modificaron."""
        cursor = self.conexion.cursor()

        if tipo is None:
            cursor.execute("SELECT codigo, precio FROM productos")
        else:
            cursor.execute("SELECT codigo, precio FROM productos WHERE tipo = ?", (tipo,))

        productos = cursor.fetchall()

        for codigo, precio_actual in productos:
            solo_numeros = "".join(c for c in str(precio_actual) if c.isdigit())
            if solo_numeros == "":
                continue  # si el precio está vacío o roto, lo salteamos

            precio_numero = int(solo_numeros)
            precio_nuevo = round(precio_numero * (1 + porcentaje / 100))
            cursor.execute(
                "UPDATE productos SET precio = ? WHERE codigo = ?",
                (str(precio_nuevo), codigo)
            )

        self.conexion.commit()
        cursor.close()
        return len(productos)

    def modificar_producto(self, codigo, nombre, tipo, categoria, temporada, precio, stock, codigo_barras):
        cursor = self.conexion.cursor()
        cursor.execute(
            "UPDATE productos SET nombre=?, tipo=?, categoria=?, temporada=?, precio=? , stock=?, codigo_barras=? "
            "WHERE codigo=?",
            (nombre, tipo, categoria, temporada, precio, stock, codigo_barras, codigo)
        )
        self.conexion.commit()
        filas_afectadas = cursor.rowcount
        cursor.close()
        return filas_afectadas

    def eliminar_producto(self, codigo):
        cursor = self.conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE codigo=?", (codigo,))
        self.conexion.commit()
        filas_afectadas = cursor.rowcount
        cursor.close()
        return filas_afectadas

    def cerrar(self):
        self.conexion.close()

    def obtener_cierre_caja_hoy(self):
        """Devuelve el resumen de ventas realizadas en el día actual."""

        cursor = self.conexion.cursor()

        # Tomamos solo la fecha YYYY-MM-DD guardada al inicio del campo fecha.
        cursor.execute("""
            SELECT
                COUNT(*),
                COALESCE(SUM(total), 0),
                COALESCE(SUM(CASE WHEN medio_pago = 'Efectivo' THEN total ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN medio_pago = 'Transferencia' THEN total ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN medio_pago = 'Débito' THEN total ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN medio_pago = 'Crédito' THEN total ELSE 0 END), 0)
            FROM ventas
            WHERE DATE(fecha) = DATE('now', 'localtime')
        """)

        resultado = cursor.fetchone()
        cursor.close()

        return {
            "cantidad_ventas": resultado[0],
            "total_general": resultado[1],
            "efectivo": resultado[2],
            "transferencia": resultado[3],
            "debito": resultado[4],
            "credito": resultado[5]
        }

    def obtener_historial_ventas(self):
        """Devuelve todas las ventas registradas, mostrando primero las más recientes."""

        cursor = self.conexion.cursor()

        cursor.execute("""
            SELECT id_venta, fecha, medio_pago, total
            FROM ventas
            ORDER BY id_venta DESC
        """)

        ventas = cursor.fetchall()
        cursor.close()

        return ventas
    def obtener_detalle_venta(self, id_venta):
        """Devuelve los productos correspondientes a una venta determinada."""

        cursor = self.conexion.cursor()

        cursor.execute("""
            SELECT
                codigo_producto,
                nombre_producto,
                cantidad,
                precio_unitario,
                subtotal
            FROM detalle_ventas
            WHERE id_venta = ?
            ORDER BY id_detalle ASC
        """, (id_venta,))

        productos = cursor.fetchall()
        cursor.close()

        return productos
    def validar_usuario(self, usuario, contrasena):
        """Comprueba el usuario y la contraseña almacenados en SQLite."""

        # Convertimos la contraseña ingresada en un hash.
        contrasena_hash = hashlib.sha256(
            contrasena.encode("utf-8")
        ).hexdigest()

        cursor = self.conexion.cursor()

        # Buscamos un usuario cuyo nombre y hash coincidan.
        cursor.execute(
            """
            SELECT id_usuario
            FROM usuarios
            WHERE usuario = ? AND contrasena_hash = ?
            """,
            (usuario, contrasena_hash)
        )

        resultado = cursor.fetchone()
        cursor.close()

        # Si encontramos una fila, las credenciales son correctas.
        return resultado is not None
    def cambiar_contrasena(self, usuario, nueva_contrasena):
        """Actualiza de forma segura la contraseña de un usuario."""

        # Convertimos la nueva contraseña en un hash antes de guardarla.
        nueva_contrasena_hash = hashlib.sha256(
            nueva_contrasena.encode("utf-8")
        ).hexdigest()

        cursor = self.conexion.cursor()

        # Actualizamos únicamente la contraseña del usuario indicado.
        cursor.execute(
            """
            UPDATE usuarios
            SET contrasena_hash = ?
            WHERE usuario = ?
            """,
            (nueva_contrasena_hash, usuario)
        )

        self.conexion.commit()

        # rowcount indica cuántos usuarios fueron modificados.
        actualizado = cursor.rowcount > 0

        cursor.close()

        return actualizado

    def restablecer_contrasena_admin(self, nueva_contrasena):
        """Permite al desarrollador restablecer la contraseña del administrador."""

        # Convertimos la contraseña temporal en un hash antes de guardarla.
        nueva_contrasena_hash = hashlib.sha256(
            nueva_contrasena.encode("utf-8")
        ).hexdigest()

        cursor = self.conexion.cursor()

        # Modificamos solamente la contraseña del usuario administrador.
        cursor.execute(
            """
            UPDATE usuarios
            SET contrasena_hash = ?
            WHERE usuario = ?
            """,
            (nueva_contrasena_hash, "admin")
        )

        self.conexion.commit()
        cursor.close()
        