SISTEMA CRUD - VEHICULOS Y PROPIETARIOS
========================================

Trabajo practico de Programacion. Sistema de escritorio (Tkinter + SQLite)
con arquitectura orientada a objetos: una clase generica de interfaz grafica
que instancia el CRUD de dos entidades (Vehiculos y Propietarios) variando
unicamente los parametros de inicializacion.


COMO CORRERLO
--------------

Requiere Python 3 (usa solo libreria estandar: tkinter y sqlite3, no hay
dependencias que instalar).

    python main.py

(o hacer doble clic en ejecutar.bat)

Al ejecutarlo se crea automaticamente data/app.db (SQLite). Se recomienda
cargar primero un Propietario antes de crear un Vehiculo, ya que el
formulario de Vehiculos elige el propietario desde un desplegable con los
propietarios ya existentes.


ESTRUCTURA
-----------

main.py          - arma las entidades (campos, tabla, relaciones) e inicia
                    la ventana
crud_frame.py     - clase generica CRUDFrame (Tkinter): formulario, tabla
                    y botones
repository.py     - clase generica Repository (sqlite3): acceso a datos,
                    sin Tkinter
ejecutar.bat      - lanzador para Windows (doble clic)
PRUEBAS.md        - reporte de casos de prueba ejecutados


DISENO
-------

- Repository (capa de datos): recibe tabla y campos por parametro y expone
  crear/listar/actualizar/eliminar. No importa Tkinter.

- CRUDFrame (capa de interfaz): recibe titulo, campos y una instancia de
  Repository por parametro. Genera los Label/Entry del formulario
  dinamicamente en un bucle (sin declaracion manual por campo) y guarda
  las referencias a los widgets en el diccionario self.entradas. No
  importa sqlite3.

- main.py conecta ambas capas: define los campos de cada entidad
  (incluida la relacion Vehiculo -> Propietario via propietario_id) e
  instancia CRUDFrame dos veces, una por entidad.
