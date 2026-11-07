# Diseño del sistema de iglesia

## Intención

Completar el ciclo de los aventureros muertos que fueron recuperados después
de una expedición. La iglesia permitirá consultar los cuerpos que todavía
pertenecen al clan, resucitarlos pagando dinero o enterrarlos con honores para
liberar cupo. También permitirá consultar el historial de caídos que ya no
ocupan un lugar en el clan.

El diseño debe conservar el estilo funcional utilizado por los servicios
existentes: estructuras `TypedDict`, funciones fuertemente anotadas y
validación completa antes de modificar el estado en memoria.

## Objetivos

- Listar los aventureros muertos que permanecen en el clan.
- Buscar un cuerpo mediante el identificador interno del aventurero.
- Calcular el coste de resurrección sin introducir un coste base nuevo.
- Resucitar conservando identidad, plantilla, nivel y experiencia.
- Enterrar con honores y trasladar el registro al historial de eliminados.
- Consultar el historial de caídos sin mezclarlo con aventureros vivos
  expulsados del clan.
- Garantizar que una operación rechazada no modifique dinero ni listas.
- Dejar una API independiente de Tkinter y de los archivos JSON.

## Fuera de alcance

- La expulsión de aventureros vivos por finalización de servicios.
- La muerte y recuperación de cuerpos durante una expedición.
- El registro automático de `caido_no_recuperado`; corresponderá al futuro
  servicio de expediciones.
- Ventanas, botones, confirmaciones y mensajes de Tkinter.
- Guardar automáticamente los cambios en JSON. La capa que coordine la
  interfaz y la partida llamará a persistencia después de una operación
  exitosa.
- La evaluación de la derrota definitiva del clan después de un entierro o
  una resurrección. El flujo general deberá combinar aventureros disponibles,
  dinero, cupo y mercado antes de decidirla.
- El balance definitivo de la economía.

## Enfoques considerados

### 1. Servicios funcionales con modificación en memoria —elegido—

Las funciones de `servicios/iglesia.py` reciben el estado y las listas que
necesitan, validan todas las condiciones y solo después realizan las
modificaciones. Es el mismo criterio aplicado en reclutamiento y evita agregar
una arquitectura distinta para un único módulo.

### 2. Devolver copias completas

Cada operación podría construir un estado nuevo sin tocar los argumentos. Es
seguro, pero obliga a copiar estructuras completas y no coincide con los
servicios ya implementados.

### 3. Clase `Iglesia`

Una clase podría encapsular el dinero y los registros, pero duplicaría la
responsabilidad de `EstadoClan` y agregaría trabajo innecesario para el alcance
académico del proyecto.

Aunque el proyecto podría diseñarse completamente con orientación a objetos,
se eligió el primer enfoque para mantener una solución proporcionada y
uniforme.

## Representación de los cuerpos

Un aventurero recuperado permanece en `datos_activos` y conserva su estructura
`AventureroActivo`:

```python
{
    "id": "AV-0004",
    "nombre": "Aldren",
    "plantilla_id": "soldado",
    "nivel": 3,
    "experiencia": 40,
    "estado": "muerto",
}
```

Mientras permanezca en esta lista continúa ocupando cupo. No se almacenan
estadísticas temporales ni vida actual; al resucitar volverá vivo y sus
estadísticas completas se calcularán desde la plantilla y el nivel.

## API propuesta

### Consulta de cuerpos

```python
def listar_aventureros_muertos(
    datos_activos: list[AventureroActivo],
) -> list[AventureroActivo]:
    ...


def buscar_aventurero_muerto(
    datos_activos: list[AventureroActivo],
    aventurero_id: str,
) -> AventureroActivo:
    ...
```

La búsqueda normalizará el identificador con `strip().upper()`. Si el ID no
existe o corresponde a un aventurero vivo, se producirá un error de dominio
específico y no se modificará ninguna estructura.

Estas operaciones parten de la precondición de que los datos cargados poseen
identificadores únicos con formato `AV-0001`. La persistencia actual todavía
no comprueba esa integridad; agregar esa validación general queda reservado
para un bloque posterior para no ampliar el alcance de la iglesia.

Las funciones de consulta devolverán listas nuevas, por lo que agregar o
quitar elementos del resultado no alterará las listas originales. Los
registros contenidos serán los objetos existentes, igual que los aventureros
devueltos por reclutamiento y las demás operaciones del dominio.

### Coste de resurrección

```python
def calcular_coste_resurreccion(
    aventurero: AventureroActivo,
) -> int:
    ...
```

El coste de contratación equivalente ya se define como:

```text
coste_base_profesion × nivel
```

La resurrección costará un 30% menos:

```text
coste_resurreccion = coste_contratacion_equivalente × 70 // 100
```

La división entera aplica la regla general de ENOM de redondear hacia abajo.
No se agrega un coste base independiente; se reutilizan el coste de la
plantilla y el nivel actual del aventurero.

### Resurrección

```python
def resucitar_aventurero(
    estado_clan: EstadoClan,
    datos_activos: list[AventureroActivo],
    aventurero_id: str,
) -> AventureroActivo:
    ...
```

La operación seguirá este orden:

1. Normalizar y buscar el identificador.
2. Comprobar que el aventurero está muerto.
3. Calcular el coste desde su plantilla y nivel.
4. Comprobar que el clan posee dinero suficiente.
5. Descontar el coste.
6. Cambiar `estado` de `"muerto"` a `"vivo"`.
7. Devolver el aventurero resucitado.

El aventurero mantiene el mismo ID, nombre, plantilla, nivel y experiencia.
Como nunca salió de `datos_activos`, la operación no modifica el cupo ni el
historial de eliminados.

### Entierro

```python
def enterrar_aventurero(
    datos_activos: list[AventureroActivo],
    datos_eliminados: list[AventureroEliminado],
    aventurero_id: str,
) -> AventureroEliminado:
    ...
```

La operación comprobará primero que el ID existe y pertenece a un muerto.
Después retirará al aventurero de `datos_activos`, creará su registro con
`motivo_baja = "enterrado_con_honores"` y lo agregará al final de
`datos_eliminados`. El orden de la lista funcionará como orden histórico de
las bajas. El entierro no cuesta dinero y libera un lugar del cupo.

La confirmación del jugador se resolverá en la futura interfaz antes de llamar
a esta función. El servicio no realizará preguntas ni mostrará mensajes.

### Memorial e historial de caídos

```python
def listar_caidos_historicos(
    datos_eliminados: list[AventureroEliminado],
) -> list[AventureroEliminado]:
    ...
```

La consulta incluirá los motivos `enterrado_con_honores` y
`caido_no_recuperado`. Excluirá `servicios_finalizados`, porque corresponde a
un aventurero vivo que abandonó el clan y no a un caído recordado por la
iglesia. La vista se denominará memorial o historial, no lista de cuerpos
enterrados, porque los caídos no recuperados no poseen un cuerpo en la
iglesia.

## Errores del dominio

`servicios/iglesia.py` definirá errores concretos para que la interfaz pueda
transformarlos posteriormente en mensajes claros:

- `AventureroNoEncontradoError`: el ID no pertenece a un integrante activo.
- `AventureroNoEstaMuertoError`: el ID existe, pero su estado es `"vivo"`.
- `DineroInsuficienteResurreccionError`: el clan no alcanza a pagar el coste.

Los errores se comprobarán antes de la primera modificación. Una resurrección
fallida conservará el dinero y el estado del aventurero. Un entierro fallido
conservará ambas listas sin cambios.

## Relación con persistencia y expediciones

La iglesia trabaja solamente con estructuras válidas cargadas en memoria. La
capa coordinadora será responsable de guardar los tres archivos JSON después
de una operación exitosa.

El futuro servicio de expediciones tendrá dos destinos para un aventurero
muerto:

- Si alguien regresa con el cuerpo, permanece en `datos_activos` como
  `"muerto"` y queda disponible en la iglesia.
- Si todo el grupo muere, pasa a `datos_eliminados` con
  `"caido_no_recuperado"` y no puede resucitarse.

La iglesia no intentará reconstruir ni recuperar un cuerpo que ya se encuentre
en el historial.

## Pruebas previstas

Las pruebas unitarias cubrirán al menos:

- Listado exclusivo de muertos activos.
- Búsqueda con espacios y diferencias entre mayúsculas y minúsculas.
- Distinción entre ID inexistente y aventurero vivo.
- Coste de resurrección para distintos niveles y redondeo hacia abajo.
- Resurrección correcta con descuento de dinero.
- Conservación de ID, nombre, plantilla, nivel y experiencia.
- Rechazo por dinero insuficiente sin mutaciones parciales.
- Entierro correcto, liberación de cupo y registro del motivo.
- Orden histórico de varios entierros.
- Rechazo del entierro de un aventurero vivo sin modificar las listas.
- Historial que incluye entierros y caídos no recuperados, pero excluye bajas
  por servicios finalizados.

## Documentación afectada

Al completar la implementación se actualizarán:

- `README.md`, para indicar que la iglesia ya está disponible.
- `documentacion/reglas_definidas.md`, con la fórmula y las operaciones.
- `documentacion/estructura.md`, si la responsabilidad descrita del módulo
  necesita mayor precisión.
