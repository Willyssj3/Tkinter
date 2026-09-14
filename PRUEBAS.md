# Plan de Pruebas — Sistema CRUD de Vehículos y Propietarios

Casos de prueba manuales ejecutados sobre la interfaz gráfica (Tkinter) para
verificar la robustez del sistema frente al usuario. Se probaron ambas
entidades (Propietarios y Vehículos); a continuación se documenta un caso
representativo por escenario.

## Caso 1 — Validación de campos vacíos

| | |
|---|---|
| **Objetivo** | Verificar que no se pueda crear un registro dejando uno o más campos en blanco. |
| **Pasos** | 1. Ir a la pestaña Propietarios.<br>2. Dejar DNI, Nombre, Apellido y Teléfono vacíos.<br>3. Presionar **Crear**. |
| **Resultado esperado** | El sistema rechaza la operación, muestra un aviso y no agrega ninguna fila a la tabla. |
| **Resultado obtenido** | Diálogo "Faltan datos" → "Completá todos los campos antes de crear el registro." No se creó ningún registro. |
| **Estado** | ✅ OK |

## Caso 2 — Flujo normal (Happy Path)

| | |
|---|---|
| **Objetivo** | Verificar que, cargando datos válidos en todos los campos, el registro se crea correctamente. |
| **Pasos** | 1. Completar DNI=30111222, Nombre=Ana, Apellido=Gomez, Teléfono=1155667788.<br>2. Presionar **Crear**.<br>3. Repetir en Vehículos completando Patente, Marca, Modelo, Año y eligiendo un Propietario del desplegable. |
| **Resultado esperado** | El registro aparece en la tabla con los datos cargados y el formulario se limpia. |
| **Resultado obtenido** | Apareció la fila con id=1 y los datos correctos en ambas pestañas; el formulario quedó vacío tras crear. |
| **Estado** | ✅ OK |

## Caso 3 — Acciones sin selección previa

| | |
|---|---|
| **Objetivo** | Verificar que "Actualizar" y "Eliminar" no fallen ni actúen sobre datos indefinidos si no se seleccionó ninguna fila. |
| **Pasos** | 1. Sin seleccionar ninguna fila, presionar **Actualizar**.<br>2. Sin seleccionar ninguna fila, presionar **Eliminar**. |
| **Resultado esperado** | El sistema muestra un aviso pidiendo seleccionar un registro, sin lanzar errores. |
| **Resultado obtenido** | Ambos botones mostraron "Sin selección" → "Seleccioná un registro de la tabla antes de actualizar/eliminar." Sin excepciones. |
| **Estado** | ✅ OK |

## Caso 4 (adicional) — Integridad referencial al eliminar

| | |
|---|---|
| **Objetivo** | Verificar que no se pueda eliminar un Propietario que tiene Vehículos asociados (clave foránea `propietario_id`). |
| **Pasos** | 1. Crear un Propietario y un Vehículo relacionado a él.<br>2. Seleccionar al Propietario en la tabla y presionar **Eliminar**. |
| **Resultado esperado** | El sistema impide el borrado y explica el motivo, sin romper la base de datos. |
| **Resultado obtenido** | Diálogo "No se puede eliminar" → "No se puede eliminar: hay registros de otra tabla que dependen de este." El propietario permaneció en la tabla. |
| **Estado** | ✅ OK |

## Caso 5 (adicional) — Validación de formato en campos restringidos

| | |
|---|---|
| **Objetivo** | Verificar que DNI/Teléfono/Año solo acepten dígitos y que Patente solo acepte letras y números. |
| **Pasos** | 1. Escribir `abc123` en el campo DNI.<br>2. Escribir `AB-123` en el campo Patente. |
| **Resultado esperado** | Los caracteres no permitidos se rechazan en el momento de tipearlos. |
| **Resultado obtenido** | En DNI solo quedó `123` (las letras no se ingresaron). En Patente solo quedó `AB123` (el guion no se ingresó). |
| **Estado** | ✅ OK |

## Conclusión

Se ejecutaron los 3 casos pedidos por la consigna (campos vacíos, happy path,
acciones sin selección) más 2 casos adicionales propios del diseño elegido
(relación entre entidades y validación de formato). Los 5 casos dieron el
resultado esperado.
