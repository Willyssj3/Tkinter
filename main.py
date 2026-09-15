# Acá se arman las entidades (campos de cada una) y se abre la ventana

import os
import tkinter as tk
from tkinter import ttk

from repository import Repository
from crud_frame import CRUDFrame

RUTA_DB = os.path.join("data", "app.db")

CAMPOS_PROPIETARIOS = [
    {"nombre": "dni", "etiqueta": "DNI", "sql": "dni TEXT NOT NULL", "tipo_entrada": "numero"},
    {"nombre": "nombre", "etiqueta": "Nombre", "sql": "nombre TEXT NOT NULL", "tipo_entrada": "texto"},
    {"nombre": "apellido", "etiqueta": "Apellido", "sql": "apellido TEXT NOT NULL", "tipo_entrada": "texto"},
    {"nombre": "telefono", "etiqueta": "Teléfono", "sql": "telefono TEXT", "tipo_entrada": "numero"},
]


def crear_campos_vehiculos(repo_propietarios):
    # Necesita el repository de propietarios ya creado para armar el combo
    return [
        {"nombre": "patente", "etiqueta": "Patente", "sql": "patente TEXT NOT NULL", "tipo_entrada": "alfanumerico"},
        {"nombre": "marca", "etiqueta": "Marca", "sql": "marca TEXT NOT NULL", "tipo_entrada": "texto"},
        {"nombre": "modelo", "etiqueta": "Modelo", "sql": "modelo TEXT NOT NULL", "tipo_entrada": "texto"},
        {"nombre": "anio", "etiqueta": "Año", "sql": "anio INTEGER", "tipo_entrada": "numero"},
        {
            "nombre": "propietario_id",
            "etiqueta": "Propietario",
            "sql": "propietario_id INTEGER REFERENCES propietarios(id)",
            "tipo_entrada": "relacion",
            "repo_relacionado": repo_propietarios,
            "texto_opcion": lambda fila: f"{fila['nombre']} {fila['apellido']} (DNI {fila['dni']})",
        },
    ]


def main():
    ventana = tk.Tk()
    ventana.title("Gestión de Vehículos y Propietarios")
    ventana.geometry("780x520")

    repo_propietarios = Repository(RUTA_DB, "propietarios", CAMPOS_PROPIETARIOS)
    campos_vehiculos = crear_campos_vehiculos(repo_propietarios)
    repo_vehiculos = Repository(RUTA_DB, "vehiculos", campos_vehiculos)

    notebook = ttk.Notebook(ventana)
    notebook.pack(fill="both", expand=True)

    # Misma clase (CRUDFrame), dos instancias: solo cambian título, campos y repository.
    frame_propietarios = CRUDFrame(notebook, "Propietarios", CAMPOS_PROPIETARIOS, repo_propietarios)
    frame_vehiculos = CRUDFrame(notebook, "Vehículos", campos_vehiculos, repo_vehiculos)

    notebook.add(frame_propietarios, text="Propietarios")
    notebook.add(frame_vehiculos, text="Vehículos")

    def al_cambiar_pestana(evento):
        # Refresca tabla y combo de relación al entrar a una pestaña
        # (por si se cargó un propietario nuevo desde la otra pestaña).
        pestana_actual = notebook.nametowidget(notebook.select())
        pestana_actual.actualizar_tabla()

    notebook.bind("<<NotebookTabChanged>>", al_cambiar_pestana)

    ventana.mainloop()


if __name__ == "__main__":
    main()
