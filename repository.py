"""Acceso a datos genérico sobre SQLite. No sabe nada de Tkinter ni de la interfaz."""

import os
import sqlite3


class RegistroReferenciadoError(Exception):
    """Se lanza al intentar eliminar un registro del que dependen filas de otra tabla."""


class Repository:
    """CRUD genérico sobre una tabla SQLite.

    La misma clase sirve para cualquier entidad: solo cambian los parámetros
    del constructor (nombre de tabla y definición de columnas), nunca el código.
    """

    def __init__(self, ruta_db, tabla, campos):
        self.tabla = tabla
        self.ruta_db = ruta_db
        self.nombres_columnas = [campo["nombre"] for campo in campos]

        carpeta = os.path.dirname(ruta_db)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)

        self._crear_tabla(campos)

    def _conectar(self):
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row
        # Sin esto, SQLite ignora las claves foráneas por defecto.
        conexion.execute("PRAGMA foreign_keys = ON")
        return conexion

    def _crear_tabla(self, campos):
        definiciones = ", ".join(campo["sql"] for campo in campos)
        sql = (
            f"CREATE TABLE IF NOT EXISTS {self.tabla} "
            f"(id INTEGER PRIMARY KEY AUTOINCREMENT, {definiciones})"
        )
        with self._conectar() as conexion:
            conexion.execute(sql)

    def crear(self, datos):
        columnas = ", ".join(self.nombres_columnas)
        placeholders = ", ".join("?" for _ in self.nombres_columnas)
        valores = [datos[nombre] for nombre in self.nombres_columnas]
        sql = f"INSERT INTO {self.tabla} ({columnas}) VALUES ({placeholders})"
        with self._conectar() as conexion:
            cursor = conexion.execute(sql, valores)
            return cursor.lastrowid

    def listar(self):
        columnas = ", ".join(self.nombres_columnas)
        sql = f"SELECT id, {columnas} FROM {self.tabla} ORDER BY id"
        with self._conectar() as conexion:
            filas = conexion.execute(sql).fetchall()
        return [dict(fila) for fila in filas]

    def obtener(self, id_registro):
        columnas = ", ".join(self.nombres_columnas)
        sql = f"SELECT id, {columnas} FROM {self.tabla} WHERE id = ?"
        with self._conectar() as conexion:
            fila = conexion.execute(sql, (id_registro,)).fetchone()
        return dict(fila) if fila else None

    def actualizar(self, id_registro, datos):
        asignaciones = ", ".join(f"{nombre} = ?" for nombre in self.nombres_columnas)
        valores = [datos[nombre] for nombre in self.nombres_columnas] + [id_registro]
        sql = f"UPDATE {self.tabla} SET {asignaciones} WHERE id = ?"
        with self._conectar() as conexion:
            conexion.execute(sql, valores)

    def eliminar(self, id_registro):
        sql = f"DELETE FROM {self.tabla} WHERE id = ?"
        try:
            with self._conectar() as conexion:
                conexion.execute(sql, (id_registro,))
        except sqlite3.IntegrityError:
            raise RegistroReferenciadoError(
                "No se puede eliminar: hay registros de otra tabla que dependen de este."
            )
