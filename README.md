# Sistema CRUD — Vehículos y Propietarios

Trabajo práctico de Programación. Sistema de escritorio (Tkinter + SQLite)
con arquitectura orientada a objetos: una clase genérica de interfaz gráfica
que instancia el CRUD de dos entidades (Vehículos y Propietarios) variando
únicamente los parámetros de inicialización.

## Cómo correrlo

Requiere Python 3 (usa solo librería estándar: `tkinter` y `sqlite3`, no hay
dependencias que instalar).

```bash
python main.py
```

Al ejecutarlo se crea automáticamente `data/app.db` (SQLite). Se recomienda
cargar primero un Propietario antes de crear un Vehículo, ya que el
formulario de Vehículos elige el propietario desde un desplegable con los
propietarios ya existentes.

## Estructura

```
main.py         # arma las entidades (campos, tabla, relaciones) e inicia la ventana
crud_frame.py    # clase genérica CRUDFrame (Tkinter): formulario, tabla y botones
repository.py    # clase genérica Repository (sqlite3): acceso a datos, sin Tkinter
PRUEBAS.md       # reporte de casos de prueba ejecutados
GUIA_ESTUDIO.md  # guía de repaso para la defensa oral
```

## Diseño

- **`Repository`** (capa de datos): recibe `tabla` y `campos` por parámetro
  y expone `crear/listar/actualizar/eliminar`. No importa Tkinter.
- **`CRUDFrame`** (capa de interfaz): recibe `titulo`, `campos` y una
  instancia de `Repository` por parámetro. Genera los `Label`/`Entry` del
  formulario dinámicamente en un bucle (sin declaración manual por campo) y
  guarda las referencias a los widgets en el diccionario `self.entradas`.
  No importa `sqlite3`.
- **`main.py`** conecta ambas capas: define los campos de cada entidad
  (incluida la relación Vehículo → Propietario vía `propietario_id`) e
  instancia `CRUDFrame` dos veces, una por entidad.

Ver [PRUEBAS.md](PRUEBAS.md) para el detalle de los casos de prueba y
[GUIA_ESTUDIO.md](GUIA_ESTUDIO.md) para preparar la defensa oral.
