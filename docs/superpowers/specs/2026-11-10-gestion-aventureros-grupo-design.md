# Diseño: gestión de aventureros y formación del grupo

## Propósito

Completar la gestión básica de los integrantes del clan y preparar la entrada
al futuro sistema de expediciones. El jugador podrá consultar aventureros
vivos, buscarlos mediante su identificador, expulsar integrantes y formar un
grupo válido para una incursión.

El bloque también centralizará la búsqueda general de aventureros para evitar
que la iglesia y los demás servicios mantengan reglas distintas de
normalización y detección de errores.

## Objetivos

- Centralizar la normalización y búsqueda por ID en
  `servicios/aventureros.py`.
- Listar únicamente los integrantes vivos del clan.
- Expulsar a un aventurero vivo y conservar su registro histórico.
- Impedir que la expulsión deje al clan sin ningún integrante vivo.
- Calcular el máximo del grupo según el nivel del clan.
- Validar una selección temporal representada mediante `list[str]`.
- Conservar el orden elegido por el jugador.
- Reutilizar la búsqueda general desde la iglesia sin cambiar su
  comportamiento público.

## Fuera de alcance

- Crear combatientes temporales o calcular sus estadísticas de batalla.
- Guardar el grupo seleccionado en JSON.
- Resolver expediciones, oleadas, recompensas o muertes.
- Implementar pantallas de Tkinter o cuadros de confirmación.
- Modificar el nivel, la experiencia o la vida de los aventureros.
- Evaluar la derrota definitiva de la partida.

## Enfoques considerados

### Búsquedas separadas por servicio

Cada servicio podría normalizar y buscar identificadores por su cuenta. Es una
solución local sencilla, pero duplicaría reglas y permitiría que la iglesia,
el clan y las expediciones terminaran distinguiendo los mismos errores de
formas diferentes.

### Búsqueda general centralizada —seleccionado—

`servicios/aventureros.py` será la única fuente de la normalización y búsqueda
general. La iglesia reutilizará esa operación y agregará exclusivamente la
restricción de que el aventurero esté muerto. La gestión del clan agregará la
restricción equivalente para vivos.

### Grupo con registros completos

La selección podría mantener copias o referencias de
`AventureroActivo`. Esto facilitaría el acceso inmediato a sus campos, pero
mezclaría el estado persistente con el futuro estado temporal del combate y
podría producir copias desactualizadas.

### Grupo temporal mediante identificadores —seleccionado—

La selección se representará con `list[str]`. Al confirmarla, el servicio
resolverá esos identificadores contra `datos_activos` y devolverá los
aventureros vivos correspondientes. Los futuros modelos de combate se
construirán recién al iniciar la expedición.

## Reglas de búsqueda

La búsqueda recibirá `datos_activos` y un ID introducido por el usuario.
Normalizará el texto mediante:

```python
aventurero_id.strip().upper()
```

Por lo tanto, `" av-0001 "` y `"AV-0001"` identificarán al mismo
aventurero.

La búsqueda general distinguirá un ID inexistente mediante
`AventureroNoEncontradoError`. Las operaciones que exijan un vivo utilizarán
además `AventureroNoEstaVivoError`. La iglesia conservará
`AventureroNoEstaMuertoError` para el caso inverso.

Las nuevas excepciones de dominio heredarán de `ValueError`, siguiendo la
convención actual del repositorio. Un nivel de clan fuera del intervalo
permitido también producirá `ValueError`.

`AventureroNoEncontradoError` pasará de `servicios/iglesia.py` a
`servicios/aventureros.py`. La iglesia lo importará desde allí para mantener
el mismo tipo de error observable por sus consumidores.

## Consulta de integrantes vivos

El listado de vivos devolverá una lista nueva, en el mismo orden que
`datos_activos`, con los registros cuyo estado sea `"vivo"`. No modificará la
lista original ni incluirá cuerpos recuperados.

## Expulsión

La expulsión se realizará por ID y solamente sobre un aventurero vivo. Antes
de modificar las listas se validará:

1. que el ID exista;
2. que el aventurero esté vivo;
3. que haya al menos otro aventurero vivo en el clan.

Si el seleccionado es el último vivo se producirá
`UltimoAventureroVivoError` y no se modificará ninguna estructura.

Una expulsión válida:

- elimina el registro de `datos_activos` y libera cupo;
- crea un `AventureroEliminado` independiente;
- conserva ID, nombre, plantilla, nivel, experiencia y estado;
- agrega `motivo_baja: "servicios_finalizados"`;
- añade el registro al final de `datos_eliminados` para preservar el orden
  histórico;
- no cuesta dinero.

La confirmación del usuario y el mensaje de agradecimiento pertenecen a la
futura interfaz, no al servicio.

Los muertos recuperados no pueden expulsarse desde esta operación: deben
enterrarse mediante la iglesia.

## Tamaño del grupo

El máximo aumenta con el nivel del clan y respeta el tope de siete
participantes del juego de mesa ENOM:

| Nivel del clan | Máximo del grupo |
|---:|---:|
| 1 | 3 |
| 2 | 4 |
| 3 | 5 |
| 4 | 6 |
| 5 | 7 |

La regla se expresará como:

```python
maximo_grupo = min(nivel_clan + 2, 7)
```

Solo se aceptarán niveles de clan entre 1 y 5. El valor representa un máximo:
el jugador podrá iniciar una expedición con cualquier cantidad desde uno hasta
el límite correspondiente.

La implementación reutilizará `NIVEL_MAXIMO_CLAN` y declarará el tope de grupo
como una constante, en lugar de dispersar valores mágicos.

## Validación de la selección

La operación de selección recibirá:

- `datos_activos: list[AventureroActivo]`;
- `nivel_clan: int`;
- `aventureros_ids: list[str]`.

Las validaciones se ejecutarán antes de devolver el grupo:

1. el nivel del clan debe ser válido;
2. la lista no puede estar vacía;
3. su cantidad no puede superar el máximo del nivel;
4. los IDs normalizados no pueden repetirse;
5. cada ID debe existir en `datos_activos`;
6. todos los seleccionados deben estar vivos.

Los duplicados se detectarán después de normalizar, por lo que `"AV-0001"` y
`" av-0001 "` se considerarán el mismo integrante.

La operación devolverá una lista nueva con las referencias a los registros
activos, en el mismo orden de los IDs recibidos. No modificará
`datos_activos`, la selección original ni `EstadoClan`.

Los errores previstos para la selección son:

- `GrupoVacioError`;
- `GrupoExcedeLimiteError`;
- `AventureroRepetidoEnGrupoError`;
- `AventureroNoEncontradoError`;
- `AventureroNoEstaVivoError`.

## API prevista

El diseño se implementará principalmente mediante estas operaciones públicas:

```python
def normalizar_id_aventurero(aventurero_id: str) -> str:
    ...


def listar_aventureros_vivos(
    datos_activos: list[AventureroActivo],
) -> list[AventureroActivo]:
    ...


def buscar_aventurero_activo(
    datos_activos: list[AventureroActivo],
    aventurero_id: str,
) -> AventureroActivo:
    ...


def buscar_aventurero_vivo(
    datos_activos: list[AventureroActivo],
    aventurero_id: str,
) -> AventureroActivo:
    ...


def expulsar_aventurero(
    datos_activos: list[AventureroActivo],
    datos_eliminados: list[AventureroEliminado],
    aventurero_id: str,
) -> AventureroEliminado:
    ...


def calcular_maximo_grupo(nivel_clan: int) -> int:
    ...


def seleccionar_grupo(
    datos_activos: list[AventureroActivo],
    nivel_clan: int,
    aventureros_ids: list[str],
) -> list[AventureroActivo]:
    ...
```

Los nombres definitivos podrán ajustarse en el plan si una convención ya
presente en el repositorio permite mayor claridad, sin cambiar estas
responsabilidades.

## Integración con la iglesia

`buscar_aventurero_muerto()` continuará siendo la entrada pública específica
de la iglesia, pero delegará la normalización y localización a
`buscar_aventurero_activo()`. Luego comprobará que el estado sea `"muerto"`.

La iglesia importará expresamente `AventureroNoEncontradoError`, por lo que el
import existente desde `servicios.iglesia` conservará la misma identidad de
clase y seguirá siendo compatible con sus consumidores actuales.

Las funciones de resurrección y entierro conservarán sus firmas y reglas. Sus
pruebas existentes deberán seguir pasando sin cambios de comportamiento.

## Atomicidad y mutaciones

- Las búsquedas, listados, cálculo del máximo y selección no mutan datos.
- La expulsión valida todas sus precondiciones antes de modificar las listas.
- Ante cualquier error, `datos_activos` y `datos_eliminados` deben conservar
  exactamente su contenido anterior.
- No se realizará persistencia JSON dentro de este servicio; el coordinador de
  la futura interfaz guardará el estado después de una operación exitosa.

## Pruebas requeridas

Las pruebas automatizadas cubrirán al menos:

- listado exclusivo de vivos en una lista nueva;
- búsqueda con espacios y diferencias de mayúsculas;
- distinción entre ID inexistente, vivo y muerto;
- expulsión correcta y registro `servicios_finalizados`;
- conservación del orden histórico;
- rechazo de la expulsión de un muerto;
- rechazo de un ID inexistente durante la expulsión sin mutaciones;
- rechazo de la expulsión del último vivo sin mutaciones;
- máximos `3, 4, 5, 6, 7` para los cinco niveles;
- rechazo de niveles de clan inválidos;
- selección mínima de un aventurero;
- selección válida hasta el máximo de cada nivel;
- rechazo de grupo vacío y grupo demasiado grande;
- rechazo de IDs duplicados después de normalizar;
- rechazo de aventureros inexistentes o muertos;
- conservación del orden elegido;
- ausencia de mutaciones en todas las validaciones fallidas;
- regresión completa de las pruebas de iglesia, reclutamiento y persistencia.

## Documentación

Al completar la implementación se actualizarán:

- `README.md`, para reflejar la gestión del clan y la formación del grupo;
- `documentacion/reglas_definidas.md`, con el límite progresivo de 3 a 7;
- `documentacion/estructura.md`, con las responsabilidades finales de
  `servicios/aventureros.py`.

## Criterio de finalización

El bloque estará terminado cuando el clan pueda buscar y listar integrantes
vivos, expulsarlos sin quedar vacío y validar una formación temporal de uno a
siete aventureros según su nivel, manteniendo todas las pruebas actuales y las
nuevas sin depender de Tkinter ni de archivos JSON.
