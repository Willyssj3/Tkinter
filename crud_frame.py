# Clase que arma la ventana: formulario, tabla y botones, para cualquier entidad

import tkinter as tk
from tkinter import ttk, messagebox

from repository import RegistroReferenciadoError

# Reglas de qué se puede escribir en cada tipo de campo
VALIDADORES = {
    "numero": lambda texto: texto == "" or texto.isdigit(),
    "alfanumerico": lambda texto: texto == "" or texto.isalnum(),
}


class CRUDFrame(tk.Frame):
    # Sirve para cualquier entidad: el título, los campos y el acceso a
    # datos se reciben como parámetro, no están fijos en el código
    def __init__(self, master, titulo, campos, repository):
        super().__init__(master)
        self.campos = campos
        self.repository = repository

        self.entradas = {}        # nombre_campo -> widget de entrada
        self.mapas_opciones = {}  # nombre_campo -> {texto mostrado: id} (solo campos "relacion")
        self.id_seleccionado = None

        self._construir_formulario(titulo)
        self._construir_botones()
        self._construir_tabla()
        self.actualizar_tabla()

    # ---------- construcción de widgets (dinámica, en bucle) ----------

    def _construir_formulario(self, titulo):
        marco_form = tk.LabelFrame(self, text=titulo)
        marco_form.pack(fill="x", padx=10, pady=10)

        for fila, campo in enumerate(self.campos):
            etiqueta = tk.Label(marco_form, text=campo["etiqueta"])
            etiqueta.grid(row=fila, column=0, sticky="w", padx=5, pady=3)

            if campo["tipo_entrada"] == "relacion":
                entrada = self._crear_combobox(marco_form, campo)
            else:
                entrada = self._crear_entry(marco_form, campo)

            entrada.grid(row=fila, column=1, sticky="ew", padx=5, pady=3)
            self.entradas[campo["nombre"]] = entrada

        marco_form.columnconfigure(1, weight=1)

    def _crear_entry(self, contenedor, campo):
        entrada = tk.Entry(contenedor)
        tipo = campo["tipo_entrada"]
        if tipo in VALIDADORES:
            comando = (self.register(lambda texto, t=tipo: VALIDADORES[t](texto)), "%P")
            entrada.configure(validate="key", validatecommand=comando)
        return entrada

    def _crear_combobox(self, contenedor, campo):
        combo = ttk.Combobox(contenedor, state="readonly")
        self._cargar_opciones_combobox(combo, campo)
        return combo

    def _cargar_opciones_combobox(self, combo, campo):
        filas = campo["repo_relacionado"].listar()
        mapa = {campo["texto_opcion"](fila): fila["id"] for fila in filas}
        self.mapas_opciones[campo["nombre"]] = mapa
        combo["values"] = list(mapa.keys())

    def _construir_botones(self):
        marco_botones = tk.Frame(self)
        marco_botones.pack(fill="x", padx=10, pady=(0, 10))

        botones = [
            ("Crear", self.crear),
            ("Actualizar", self.actualizar),
            ("Eliminar", self.eliminar),
            ("Limpiar", self.limpiar_formulario),
        ]
        for texto, accion in botones:
            tk.Button(marco_botones, text=texto, command=accion, width=12).pack(side="left", padx=3)

    def _construir_tabla(self):
        columnas = ["id"] + [campo["nombre"] for campo in self.campos]
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=8)
        for nombre_columna in columnas:
            self.tabla.heading(nombre_columna, text=nombre_columna)
            self.tabla.column(nombre_columna, width=110)
        self.tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar_fila)

    # ---------- lectura / escritura del formulario ----------

    def _leer_formulario(self):
        datos = {}
        for campo in self.campos:
            widget = self.entradas[campo["nombre"]]
            if campo["tipo_entrada"] == "relacion":
                texto = widget.get()
                datos[campo["nombre"]] = self.mapas_opciones[campo["nombre"]].get(texto)
            else:
                datos[campo["nombre"]] = widget.get().strip()
        return datos

    def _hay_campos_vacios(self, datos):
        return any(valor in ("", None) for valor in datos.values())

    def limpiar_formulario(self):
        for campo in self.campos:
            widget = self.entradas[campo["nombre"]]
            if campo["tipo_entrada"] == "relacion":
                widget.set("")
            else:
                widget.delete(0, tk.END)
        self.id_seleccionado = None
        seleccion = self.tabla.selection()
        if seleccion:
            self.tabla.selection_remove(seleccion)

    # ---------- operaciones CRUD ----------

    def crear(self):
        datos = self._leer_formulario()
        if self._hay_campos_vacios(datos):
            messagebox.showerror("Faltan datos", "Completá todos los campos antes de crear el registro.")
            return
        self.repository.crear(datos)
        self.limpiar_formulario()
        self.actualizar_tabla()

    def actualizar(self):
        if self.id_seleccionado is None:
            messagebox.showerror("Sin selección", "Seleccioná un registro de la tabla antes de actualizar.")
            return
        datos = self._leer_formulario()
        if self._hay_campos_vacios(datos):
            messagebox.showerror("Faltan datos", "Completá todos los campos antes de actualizar.")
            return
        self.repository.actualizar(self.id_seleccionado, datos)
        self.limpiar_formulario()
        self.actualizar_tabla()

    def eliminar(self):
        if self.id_seleccionado is None:
            messagebox.showerror("Sin selección", "Seleccioná un registro de la tabla antes de eliminar.")
            return
        try:
            self.repository.eliminar(self.id_seleccionado)
        except RegistroReferenciadoError as error:
            messagebox.showerror("No se puede eliminar", str(error))
            return
        self.limpiar_formulario()
        self.actualizar_tabla()

    # ---------- refresco de tabla y selección ----------

    def actualizar_tabla(self):
        self._refrescar_combos_relacion()
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for registro in self.repository.listar():
            valores = [registro["id"]] + [registro[campo["nombre"]] for campo in self.campos]
            self.tabla.insert("", tk.END, values=valores)

    def _refrescar_combos_relacion(self):
        for campo in self.campos:
            if campo["tipo_entrada"] == "relacion":
                combo = self.entradas[campo["nombre"]]
                self._cargar_opciones_combobox(combo, campo)

    def _al_seleccionar_fila(self, evento):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        valores = self.tabla.item(seleccion[0], "values")
        self.id_seleccionado = int(valores[0])

        for indice, campo in enumerate(self.campos, start=1):
            widget = self.entradas[campo["nombre"]]
            valor = valores[indice]
            if campo["tipo_entrada"] == "relacion":
                mapa_inverso = {id_: texto for texto, id_ in self.mapas_opciones[campo["nombre"]].items()}
                widget.set(mapa_inverso.get(int(valor), ""))
            else:
                widget.delete(0, tk.END)
                widget.insert(0, valor)
