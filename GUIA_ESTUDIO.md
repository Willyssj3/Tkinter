# Guía de estudio — CRUD genérico de Vehículos y Propietarios

Para preparar la defensa oral. No es para leer una sola vez: la idea es que
puedas explicar cada punto con tus palabras, sin mirar el código.

---

## 1. Qué hace el sistema, en una frase

Una app de escritorio (Tkinter) que permite dar de alta, listar, modificar y
borrar Propietarios y Vehículos, guardando los datos en SQLite, donde cada
Vehículo pertenece a un Propietario.

## 2. Los 3 archivos y su responsabilidad

```
repository.py   -> capa de DATOS. Habla con SQLite. No sabe que existe Tkinter.
crud_frame.py    -> capa de INTERFAZ. Dibuja ventanas. No sabe que existe SQL.
main.py          -> capa de ARMADO. Define los campos de cada entidad y conecta
                    las otras dos capas.
```

Si te preguntan **"¿por qué 3 archivos y no todo junto?"**: porque es más
fácil de mantener y de probar. Si mañana cambiás SQLite por otra base de
datos, tocás solo `repository.py`. Si querés cambiar cómo se ve el
formulario, tocás solo `crud_frame.py`. Ninguno de los dos cambios rompe al
otro. Eso es "separación lógica" / bajo acoplamiento.

---

## 3. Conceptos de POO que usa el proyecto (repaso rápido)

- **Clase**: un molde para crear objetos. Acá tenemos dos clases propias:
  `Repository` y `CRUDFrame`.
- **Instancia / objeto**: un objeto concreto creado a partir de una clase.
  En `main.py` creamos **dos instancias** de `Repository` (una para
  propietarios, otra para vehículos) y **dos instancias** de `CRUDFrame`.
- **`__init__`**: el método que se ejecuta automáticamente al crear una
  instancia. Ahí se reciben los parámetros y se guardan como atributos.
- **`self`**: la forma en que un objeto se refiere a sus propios datos.
- **Atributo de instancia**: un dato que vive "adentro" de un objeto
  (`self.campos`, `self.entradas`, etc.), distinto por cada instancia.
- **Composición**: `CRUDFrame` **tiene** un `Repository` (se lo pasan por
  parámetro y lo guarda en `self.repository`), no **hereda** de él. Es la
  relación "tiene un/a", no "es un/a". Por eso, si te preguntan "¿usaron
  herencia?", la respuesta es: no directamente entre estas dos clases —
  `CRUDFrame` sí hereda de `tk.Frame` (la clase base de Tkinter), pero la
  relación con `Repository` es composición.
- **Genérico / parametrizable**: una clase que no tiene hardcodeado a qué
  entidad sirve. Ambas clases (`Repository` y `CRUDFrame`) reciben toda la
  información específica de la entidad (nombre de tabla, columnas,
  etiquetas) **por parámetro** en el `__init__`, no escrita adentro del
  cuerpo de la clase.

---

## 4. `repository.py` — capa de datos

### La clase y el `__init__`

```python
class Repository:
    def __init__(self, ruta_db, tabla, campos):
        self.tabla = tabla
        self.ruta_db = ruta_db
        self.nombres_columnas = [campo["nombre"] for campo in campos]
        ...
        self._crear_tabla(campos)
```

- Recibe `tabla` (string, ej. `"propietarios"`) y `campos` (una lista de
  diccionarios, uno por columna).
- `self.nombres_columnas` guarda solo los nombres (`["dni", "nombre", ...]`)
  usando **comprensión de listas**, para no tener que repetir
  `campo["nombre"]` en cada método de abajo.
- Al final llama a `_crear_tabla`, que ejecuta un `CREATE TABLE IF NOT
  EXISTS` armado dinámicamente a partir de `campos` (cada campo trae su
  propio pedacito de SQL en la clave `"sql"`, ej. `"dni TEXT NOT NULL"`).

**Por qué esto es genérico:** la clase nunca dice `"propietarios"` ni
`"dni"` en su código. Todo lo específico entra por los parámetros del
`__init__`. La misma clase, instanciada con otros parámetros, sirve para
cualquier tabla.

### `_conectar`

Abre una conexión nueva a SQLite cada vez que se necesita (no mantiene una
conexión abierta todo el tiempo — más simple y evita problemas de
concurrencia en una app chica). Dos detalles para poder explicar:

- `conexion.row_factory = sqlite3.Row` — hace que las filas se puedan leer
  como si fueran diccionarios (`fila["dni"]`) en vez de tuplas posicionales
  (`fila[0]`), lo cual es mucho más legible y menos propenso a errores si
  cambia el orden de las columnas.
- `PRAGMA foreign_keys = ON` — SQLite, por defecto, **no** hace cumplir las
  claves foráneas a menos que se lo pidas explícitamente en cada conexión.
  Sin esta línea, se podría borrar un Propietario con Vehículos asociados
  sin ningún aviso.

### `crear`, `listar`, `actualizar`, `eliminar`

Los cuatro arman el SQL usando `self.tabla` y `self.nombres_columnas`
(nunca un nombre de columna escrito a mano), y usan **parámetros
`?`** en vez de meter los valores directo en el string SQL:

```python
sql = f"INSERT INTO {self.tabla} ({columnas}) VALUES ({placeholders})"
conexion.execute(sql, valores)
```

**Pregunta típica: "¿por qué usan `?` en vez de armar el string con
f-strings directamente?"** — Porque meter valores del usuario directo en un
string SQL abre la puerta a **inyección SQL**. Los `?` le dicen a sqlite3
"estos son datos, no código SQL", y la librería los escapa de forma segura.
(Los nombres de tabla/columna sí van con f-string, pero esos **no** vienen
del usuario: están fijos en el código de `main.py`, así que no hay riesgo.)

### `eliminar` y `RegistroReferenciadoError`

```python
def eliminar(self, id_registro):
    ...
    try:
        ...
    except sqlite3.IntegrityError:
        raise RegistroReferenciadoError(
            "No se puede eliminar: hay registros de otra tabla que dependen de este."
        )
```

Si intentás borrar un Propietario que tiene Vehículos asociados, SQLite
lanza `IntegrityError` (por el `PRAGMA foreign_keys = ON`). La atrapamos y
relanzamos como una excepción **propia** (`RegistroReferenciadoError`).

**Pregunta típica: "¿por qué no dejan pasar directamente el error de
sqlite3?"** — Porque `crud_frame.py` no debería tener que saber nada de
`sqlite3` (la separación lógica de la que habla la consigna). Si mañana
cambiamos la base de datos, la GUI sigue reaccionando al mismo tipo de
error propio, sin cambios.

---

## 5. `crud_frame.py` — capa de interfaz

### El `__init__` y la idea de "genérico" aplicada a la GUI

```python
class CRUDFrame(tk.Frame):
    def __init__(self, master, titulo, campos, repository):
        super().__init__(master)
        self.campos = campos
        self.repository = repository
        self.entradas = {}
        self.mapas_opciones = {}
        self.id_seleccionado = None
        ...
```

- `CRUDFrame` **hereda** de `tk.Frame` (por eso `super().__init__(master)`
  — hay que inicializar la parte de Tkinter también). Esto es herencia de
  verdad: `CRUDFrame` **es un** `Frame` (con widgets propios adentro),
  además de tener (composición) un `Repository`.
- Recibe `titulo`, `campos` y `repository` por parámetro. Nada de esto está
  fijo en el código de la clase — por eso en `main.py` se puede instanciar
  dos veces con datos distintos y obtener dos pantallas distintas.

### Generación dinámica de widgets (el requisito más importante de la consigna)

```python
def _construir_formulario(self, titulo):
    marco_form = tk.LabelFrame(self, text=titulo)
    marco_form.pack(fill="x", padx=10, pady=10)

    for fila, campo in enumerate(self.campos):
        etiqueta = tk.Label(marco_form, text=campo["etiqueta"])
        etiqueta.grid(row=fila, column=0, ...)

        entrada = self._crear_entry(marco_form, campo)   # (o combobox)
        entrada.grid(row=fila, column=1, ...)

        self.entradas[campo["nombre"]] = entrada
```

Esto es la respuesta directa a **"Generación Dinámica"** de la consigna: un
único `for` recorre `self.campos` (que puede tener 4 campos o 10) y crea un
`Label` + un campo de entrada por cada uno. No hay ninguna línea del tipo
`tk.Entry(...)` escrita a mano por cada campo puntual — si mañana la
entidad Vehículos tuviera 8 campos en vez de 5, el código de esta función
**no cambia en absoluto**, solo cambia la lista `campos` en `main.py`.

### El diccionario `self.entradas` (Gestión del Estado)

Cada vez que el bucle crea un widget de entrada, lo guarda con
`self.entradas[campo["nombre"]] = entrada`. Ese diccionario es la respuesta
a **"Gestión del Estado"** de la consigna: gracias a él, funciones como
`_leer_formulario` o `limpiar_formulario` también son un solo bucle
genérico:

```python
def limpiar_formulario(self):
    for campo in self.campos:
        widget = self.entradas[campo["nombre"]]
        widget.delete(0, tk.END)   # (o widget.set("") si es combobox)
```

Sin el diccionario, tendríamos que escribir a mano
`entry_dni.delete(...)`, `entry_nombre.delete(...)`, etc. — exactamente lo
que la consigna prohíbe.

### Validación de tipeo (`VALIDADORES`)

```python
VALIDADORES = {
    "numero": lambda texto: texto == "" or texto.isdigit(),
    "alfanumerico": lambda texto: texto == "" or texto.isalnum(),
}
```

Un diccionario de funciones. Tkinter permite interceptar cada tecla que se
tipea con `validatecommand` (`validate="key"`) y decidir si se acepta o se
rechaza. Así, el DNI/Teléfono/Año solo aceptan dígitos, y la Patente solo
letras/números, **en el momento en que se tipean**, no recién al guardar.

### El campo "relación" (Combobox Propietario → Vehículo)

El campo `propietario_id` de Vehículos tiene `tipo_entrada = "relacion"`.
En vez de un `Entry`, se crea un `ttk.Combobox` cuyas opciones se arman
consultando otro `Repository` (el de propietarios):

```python
filas = campo["repo_relacionado"].listar()
mapa = {campo["texto_opcion"](fila): fila["id"] for fila in filas}
```

`mapa` traduce **lo que ve el usuario** ("Ana Gomez (DNI 30111222)") al
**id real** que hay que guardar en la base. Por eso hace falta ese mapa en
los dos sentidos: al leer el formulario (texto → id) y al mostrar un
registro seleccionado (id → texto).

**Pregunta típica: "¿por qué no dejaron que el usuario tipee el nombre del
propietario a mano?"** — Porque así se podría escribir cualquier cosa (un
nombre que no existe, con errores de tipeo) y quedaría un dato "huérfano".
Con el Combobox solo se puede elegir un propietario que **ya existe**, y se
guarda su `id`, no su nombre — si el propietario después cambia de nombre,
el vehículo lo sigue apuntando correctamente.

### Los 4 botones y sus validaciones (esto es literalmente el plan de pruebas)

```python
def crear(self):
    datos = self._leer_formulario()
    if self._hay_campos_vacios(datos):
        messagebox.showerror(...)   # Caso de prueba 1
        return
    self.repository.crear(datos)
    ...

def actualizar(self):
    if self.id_seleccionado is None:
        messagebox.showerror(...)   # Caso de prueba 3
        return
    ...
```

`self.id_seleccionado` es `None` hasta que el usuario hace clic en una fila
de la tabla (`_al_seleccionar_fila` lo actualiza). Actualizar/Eliminar
chequean eso **antes** de tocar la base — así nunca se intenta operar sobre
"nada seleccionado".

---

## 6. `main.py` — el armado (composition root)

```python
CAMPOS_PROPIETARIOS = [
    {"nombre": "dni", "etiqueta": "DNI", "sql": "dni TEXT NOT NULL", "tipo_entrada": "numero"},
    ...
]

def crear_campos_vehiculos(repo_propietarios):
    return [..., {"nombre": "propietario_id", "tipo_entrada": "relacion",
                   "repo_relacionado": repo_propietarios, ...}]

repo_propietarios = Repository(RUTA_DB, "propietarios", CAMPOS_PROPIETARIOS)
campos_vehiculos = crear_campos_vehiculos(repo_propietarios)
repo_vehiculos = Repository(RUTA_DB, "vehiculos", campos_vehiculos)

frame_propietarios = CRUDFrame(notebook, "Propietarios", CAMPOS_PROPIETARIOS, repo_propietarios)
frame_vehiculos = CRUDFrame(notebook, "Vehículos", campos_vehiculos, repo_vehiculos)
```

**Esta es la prueba central de la consigna**: `CRUDFrame` se instancia
**dos veces**, con la **misma clase**, cambiando solo `titulo`, `campos` y
`repository`. Ningún `if entidad == "vehiculos"` en ningún lado. Si tu
profesor te pide agregar una tercera entidad (por ejemplo "Marcas"), la
respuesta correcta es: "agrego una lista `CAMPOS_MARCAS`, creo un
`Repository` y un `CRUDFrame` más, y los agrego al `notebook` — no toco
`crud_frame.py` ni `repository.py` para nada."

`propietario_id` necesita a `repo_propietarios` ya creado, por eso los
campos de Vehículos se arman con una función (`crear_campos_vehiculos`)
llamada **después** de crear `repo_propietarios`, y no como una constante
fija al principio del archivo (como sí pasa con `CAMPOS_PROPIETARIOS`, que
no depende de nadie).

---

## 7. Plan de pruebas — ver también [PRUEBAS.md](PRUEBAS.md)

Resumen para decir de memoria:

1. **Campos vacíos**: crear sin completar nada → error, no se crea nada.
2. **Happy path**: completar todo y crear → aparece en la tabla, formulario
   se limpia.
3. **Sin selección**: Actualizar/Eliminar sin haber clickeado una fila →
   error, no rompe nada.
4. *(extra)* **Integridad referencial**: borrar un Propietario con
   Vehículos asociados → bloqueado con mensaje claro.
5. *(extra)* **Validación de formato**: letras en DNI o símbolos en Patente
   se rechazan mientras se tipean.

Todos se probaron manualmente contra la app corriendo de verdad (no solo
leyendo el código).

---

## 8. Cómo hacer la demo en vivo

```bash
python main.py
```

1. Mostrar la pestaña **Propietarios**: crear 2 registros.
2. Ir a **Vehículos**: abrir el combo "Propietario" y mostrar que aparecen
   los que acabás de crear. Crear un vehículo relacionado a uno de ellos.
3. Clickear una fila de la tabla → mostrar que el formulario se completa
   solo (incluido el combo).
4. Modificar un dato y **Actualizar**.
5. Volver a Propietarios, seleccionar al que tiene un vehículo asociado, y
   tocar **Eliminar** → mostrar el mensaje de error (integridad
   referencial). Ese es un buen momento para explicar `PRAGMA foreign_keys`
   y `RegistroReferenciadoError`.
6. Tocar **Actualizar** o **Eliminar** sin seleccionar nada → mostrar el
   aviso.

## 9. Preguntas que probablemente te hagan (con respuesta corta)

- **"¿Dónde está la clase genérica?"** → `CRUDFrame` en `crud_frame.py`.
  Recibe todo lo que varía por parámetro.
- **"¿Cómo se genera la interfaz sin escribir cada widget a mano?"** →
  `_construir_formulario` recorre `self.campos` con un `for`.
- **"¿Dónde guardan las referencias a los campos?"** → `self.entradas`, un
  diccionario `nombre_de_campo -> widget`.
- **"¿Cómo separaron la GUI de la base de datos?"** → `CRUDFrame` nunca
  importa `sqlite3`; `Repository` nunca importa `tkinter`. Se comunican
  solo a través de los métodos `crear/listar/actualizar/eliminar`.
- **"¿Qué pasa si el usuario no completa un campo?"** → `_hay_campos_vacios`
  revisa el diccionario que devuelve `_leer_formulario` antes de tocar la
  base.
- **"¿Qué pasa si no seleccionás nada y tocás Actualizar/Eliminar?"** →
  `self.id_seleccionado` es `None`, se chequea al principio de cada método
  y se corta con un mensaje de error.
- **"¿Por qué SQLite y no una lista en memoria?"** → para que los datos
  persistan al cerrar y reabrir la app (fue una decisión explícita para
  esta entrega).
- **"¿Cómo implementaron la relación Vehículo-Propietario?"** → clave
  foránea `propietario_id` en la tabla `vehiculos`, con
  `PRAGMA foreign_keys = ON`, y un `Combobox` en la GUI que traduce
  nombre↔id mediante `mapas_opciones`.
