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


class BaseDatos:
    def __init__(self, ruta_db):
        # La conexión se abre una sola vez, al crear el objeto.
        self.conexion = sqlite3.connect(ruta_db)
        self.crear_tabla_si_no_existe()

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
        """Búsqueda exacta por código de barras, para cuando el cliente
        use el lector."""
        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM productos WHERE codigo_barras = ?", (codigo_barras,))
        resultado = cursor.fetchall()
        cursor.close()
        return resultado

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
