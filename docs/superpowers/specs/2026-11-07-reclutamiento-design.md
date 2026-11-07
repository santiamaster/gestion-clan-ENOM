# Diseño: mercado y contratación de aventureros

Fecha: 2026-11-07

## Intención

Implementar el primer ciclo de gestión del gremio de aventureros: generar ofertas acordes con el nivel del clan, permitir varias contrataciones por renovación y respetar simultáneamente dinero, cupo y límite de contrataciones. El sistema debe favorecer partidas cortas y quedar preparado para ser consumido por Tkinter sin depender de la interfaz.

## Objetivos

- Generar el doble de ofertas que el nivel actual del clan.
- Permitir como máximo tantas contrataciones como el nivel del clan.
- Generar candidatos entre nivel 1 y el nivel actual del clan.
- Permitir plantillas y profesiones repetidas.
- Calcular cada coste como `coste_base × nivel`.
- Crear inmediatamente las ofertas iniciales de una partida nueva.
- Conservar ofertas y contrataciones restantes cuando falta dinero o cupo.
- Permitir liberar cupo y continuar contratando durante la misma renovación.
- Renovar por completo el mercado después de cada expedición.
- Guardar toda la información necesaria dentro de `EstadoClan`.

## Reglas acordadas

| Nivel del clan | Ofertas | Contrataciones máximas | Niveles posibles | Cupo |
|---:|---:|---:|---:|---:|
| 1 | 2 | 1 | 1 | 5 |
| 2 | 4 | 2 | 1–2 | 10 |
| 3 | 6 | 3 | 1–3 | 15 |
| 4 | 8 | 4 | 1–4 | 20 |
| 5 | 10 | 5 | 1–5 | 25 |

El nivel 5 se implementará para mantener completo el dominio, aunque normalmente la partida ya habrá terminado al alcanzarlo.

Los aventureros muertos que permanezcan en el clan siguen formando parte de `datos_activos` y ocupan cupo. Los eliminados históricos no ocupan cupo.

## Fuera de alcance

- Pantallas de Tkinter.
- Expulsión, entierro y resurrección.
- Ejecución de expediciones.
- Balance económico definitivo.
- Migración automática de partidas creadas con el esquema anterior.
- Historial de mercados o contrataciones anteriores.

## Cambio del modelo persistente

Se elimina `EstadoMercado` y el campo:

```python
estado_mercado: Literal["disponible", "contratacion_realizada"]
```

Se incorpora en `EstadoClan`:

```python
contrataciones_restantes: int
```

El contador será la única fuente de verdad:

- mayor que cero: todavía se puede contratar;
- igual a cero: se agotó la renovación.

Esto evita mantener un estado textual redundante que podría contradecir al contador.

Las partidas guardadas durante el desarrollo con `estado_mercado` y sin el nuevo contador serán rechazadas por el validador. No se agrega migración porque el proyecto todavía no posee partidas de usuario que deban conservarse.

## Enfoques considerados

### 1. Contador como única fuente de verdad — elegido

El estado conserva únicamente `contrataciones_restantes`. Es directo, suficiente y no admite contradicciones.

### 2. Estado textual más contador

Facilita leer el JSON, pero duplica información y obliga a sincronizar ambos campos en cada operación.

### 3. Historial de contrataciones

Permite reconstruir el límite contando registros, pero persiste información sin utilidad para esta versión corta del juego.

## Generación de ofertas

`servicios/reclutamiento.py` será responsable de las reglas del mercado.

Funciones principales propuestas:

```python
def calcular_cantidad_ofertas(nivel_clan: int) -> int:
    ...

def calcular_limite_contrataciones(nivel_clan: int) -> int:
    ...

def generar_ofertas(
    nivel_clan: int,
    generador: Random,
) -> list[OfertaReclutamiento]:
    ...

def renovar_mercado(
    estado_clan: EstadoClan,
    generador: Random,
) -> None:
    ...
```

Por cada oferta:

1. Se elige una plantilla de las quince con reemplazo.
2. Se elige un nivel entero uniforme entre 1 y el nivel del clan.
3. Se elige un nombre compatible con el sexo de la plantilla.
4. Se calcula el coste mediante `calcular_coste_contratacion()`.
5. Se asigna un identificador temporal `OF-01`, `OF-02`, etcétera.

Los identificadores se reinician en cada renovación porque las ofertas anteriores dejan de existir.

`renovar_mercado()` reemplaza todas las ofertas pendientes y establece `contrataciones_restantes` en el nivel actual del clan. En el futuro, el servicio de expediciones llamará a esta función al terminar cualquier incursión.

## Partida nueva

`crear_estado_inicial_clan()` construirá inicialmente el contador en cero y la lista de ofertas vacía. Después, `crear_nueva_partida()` llamará a `renovar_mercado()` con el mismo generador utilizado para los nombres iniciales y guardará el resultado completo.

Una partida de nivel 1 comenzará, por tanto, con:

- dos ofertas;
- una contratación restante;
- dinero cero.

El jugador podrá consultar el mercado, pero no contratar hasta obtener dinero.

## Contratación

Interfaz propuesta:

```python
def contratar_aventurero(
    estado_clan: EstadoClan,
    datos_activos: list[AventureroActivo],
    id_oferta: str,
) -> AventureroActivo:
    ...
```

La función modificará las estructuras recibidas únicamente después de superar todas las validaciones.

Orden de validación:

1. La oferta solicitada existe.
2. Quedan contrataciones disponibles.
3. El clan todavía tiene cupo.
4. El clan dispone del dinero necesario.

Si todo es válido:

1. Se crea un aventurero vivo con la información de la oferta.
2. Se utiliza `siguiente_id_aventurero` y el formato `AV-NNNN`.
3. Se agrega el aventurero a `datos_activos`.
4. Se descuenta el coste.
5. Se incrementa el siguiente identificador.
6. Se elimina únicamente la oferta contratada.
7. Se reduce `contrataciones_restantes` en uno.
8. Se devuelve el nuevo aventurero.

Los errores de dominio serán específicos:

- `OfertaNoEncontradaError`;
- `MercadoAgotadoError`;
- `CupoClanCompletoError`;
- `DineroInsuficienteError`.

Ningún error modificará parcialmente el estado.

El servicio trabajará sobre el estado en memoria. La futura capa coordinadora de la aplicación será responsable de llamar a `guardar_partida()` después de una contratación correcta; así las reglas del gremio no dependen del sistema de archivos.

## Validación de datos guardados

`validar_estado_clan()` comprobará:

- `contrataciones_restantes` es un entero entre 0 y el nivel del clan;
- la cantidad de ofertas no supera `nivel_clan × 2`;
- no existen identificadores de oferta repetidos;
- cada nivel ofrecido está entre 1 y el nivel del clan;
- cada coste coincide con el coste base de la plantilla multiplicado por el nivel;
- la cantidad de ofertas restantes no es menor que las contrataciones restantes.

Las demás validaciones actuales se conservan.

## Pruebas necesarias

Las pruebas cubrirán:

- las tablas completas de niveles 1 a 5;
- generación determinista mediante `Random` sembrado;
- cantidad, identificadores, niveles, nombres, costes y plantillas válidas;
- repetición permitida de plantillas;
- renovación que descarta ofertas viejas y reinicia el contador;
- partida nueva con dos ofertas y una contratación;
- contratación correcta y todos sus cambios de estado;
- varias contrataciones en la misma renovación;
- oferta inexistente;
- mercado agotado;
- dinero insuficiente;
- clan lleno, incluyendo aventureros muertos;
- liberación posterior de cupo y continuación de la contratación;
- ausencia de mutaciones cuando una contratación falla;
- validación y persistencia del nuevo esquema;
- suite completa y Pyright en modo estricto.

## Decisiones de implementación

- Se reutilizarán `calcular_cupo_clan()`, `calcular_coste_contratacion()`, `elegir_nombre()` y `formatear_id_aventurero()`.
- Las reglas se mantendrán independientes de Tkinter y del sistema de archivos.
- No se agregará una clase de sesión ni una migración en este bloque.
- Las funciones nuevas y errores públicos tendrán documentación interna y anotaciones completas.
