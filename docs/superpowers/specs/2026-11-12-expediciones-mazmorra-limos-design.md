# Diseño: expedición completa a la Mazmorra de los Limos

## Intención

Conectar los sistemas ya implementados para que el jugador pueda realizar una
expedición completa por las diez oleadas de la Mazmorra de los Limos. El flujo
debe permitir decidir entre continuar o retirarse después de cada victoria,
acumular botín provisional y aplicar todas las consecuencias al finalizar.

Este bloque constituirá el primer recorrido jugable de principio a fin antes de
crear las pantallas de Tkinter.

## Objetivos

- Iniciar una expedición con un grupo válido de aventureros vivos.
- Mantener un estado temporal explícito que no se guarde en JSON.
- Resolver una oleada por vez mediante el motor de combate existente.
- Permitir continuar o retirarse después de cada oleada superada.
- Finalizar automáticamente por derrota total, límite de rondas o victoria en
  la décima oleada.
- Acumular experiencia base y dinero con bonificación progresiva por oleada.
- Entregar el botín solamente cuando regrese al menos un superviviente.
- Repartir la experiencia entre los supervivientes y aplicar sus ascensos.
- Enviar los muertos recuperados a la iglesia.
- Registrar como caídos no recuperados a todo el grupo si nadie regresa.
- Marcar la primera mazmorra como completada.
- Renovar el mercado y evaluar la derrota definitiva.
- Guardar la partida solamente al cerrar la expedición.

## Fuera de alcance

- Guardar o reanudar una expedición en curso.
- Implementar las quince habilidades y sus enfriamientos.
- Crear las mazmorras de dificultad 2 a 5.
- Definir todavía las reglas de desbloqueo de las mazmorras futuras.
- Aumentar el nivel del clan al completar la mazmorra de dificultad 1.
- Crear ventanas, botones o cuadros de diálogo de Tkinter.
- Realizar el balance definitivo de criaturas, dinero o experiencia.
- Permitir más de una expedición simultánea.

## Restricciones

- Python 3.11 o superior y Pyright en modo `strict`.
- Sin dependencias externas.
- Los servicios de dominio no usarán `input()`, `print()` ni Tkinter.
- Toda decisión aleatoria recibirá una instancia de `Random`.
- Todo redondeo monetario y de experiencia será hacia abajo.
- El estado temporal no formará parte de los tres JSON persistentes.
- Los catálogos y registros persistentes no se modificarán durante las
  oleadas; las consecuencias se aplicarán una sola vez al cierre.

## Enfoques considerados

### Estado temporal explícito — seleccionado

Una estructura `EstadoExpedicion` se pasa entre operaciones pequeñas para
iniciar, resolver, continuar, retirarse y cerrar la incursión. La futura
interfaz podrá mostrar cada resultado y esperar la decisión del jugador sin
bloquear el servicio.

### Generador con `yield`

Permitiría pausar naturalmente entre oleadas, pero complicaría el tipado, las
transiciones inválidas y la integración con botones de Tkinter.

### Función única con callback

Reduciría la API, pero mezclaría la resolución con la obtención de decisiones y
acoplaría el dominio con la interfaz.

## Separación de responsabilidades

### `modelos/expediciones.py`

Contendrá los aliases y `TypedDict` temporales del flujo de expedición.

### `servicios/expediciones.py`

Controlará las transiciones en memoria, los pozos de recompensa y la
aplicación de consecuencias sobre copias o estructuras persistentes recibidas.
No leerá ni escribirá archivos.

### `servicios/partidas.py`

Ofrecerá la operación coordinadora que cierre la expedición, renueve el mercado,
evalúe el estado de la partida y llame a `guardar_partida()`.

### Servicios existentes

- `aventureros.py`: selección y validación del grupo.
- `combate.py`: creación de estados y resolución de cada oleada.
- `calculos.py`: reparto de experiencia y ascensos.
- `reclutamiento.py`: renovación del mercado.
- `iglesia.py`: coste de resurrección usado al evaluar si la partida puede
  continuar.
- `persistencia.py`: validación y escritura atómica de los tres JSON.

## Modelo temporal

```python
EstadoFlujoExpedicion: TypeAlias = Literal[
    "lista_para_oleada",
    "esperando_decision",
    "finalizada",
    "consecuencias_aplicadas",
]


class EstadoExpedicion(TypedDict):
    mazmorra_id: str
    dificultad: DificultadMazmorra
    proxima_oleada: int
    oleadas_superadas: int
    aventureros: list[AventureroCombate]
    experiencia_acumulada: int
    dinero_acumulado: int
    estado_flujo: EstadoFlujoExpedicion
    resultado_final: ResultadoExpedicion | None
    ultima_oleada: ResultadoOleada | None
```

`proxima_oleada` comienza en 1. Después de superar una oleada se incrementa y
el estado queda esperando la decisión del jugador. La victoria en la oleada 10
deja `proxima_oleada` en 11, `oleadas_superadas` en 10 y finaliza la mazmorra
sin pedir otra decisión.

Las invariantes del flujo son:

- `resultado_final` es `None` mientras la expedición no está finalizada;
- `resultado_final` no es `None` en `finalizada` y
  `consecuencias_aplicadas`;
- `ultima_oleada` es `None` antes del primer combate;
- los pozos y contadores nunca son negativos.

El estado no duplica los registros persistentes completos. Los estados de
combate conservan los IDs necesarios para relacionar supervivientes y muertos
con `datos_activos` al finalizar.

## Inicio

```python
def iniciar_expedicion(
    estado_clan: EstadoClan,
    datos_activos: list[AventureroActivo],
    aventureros_ids: list[str],
    mazmorra_id: str,
) -> EstadoExpedicion:
    ...
```

La operación:

1. exige una partida `en_curso`;
2. comprueba que la mazmorra exista;
3. en este bloque acepta solamente `MAZMORRA_LIMOS`;
4. reutiliza `seleccionar_grupo()` para validar IDs, vivos y cantidad;
5. crea estados independientes mediante `crear_aventurero_combate()`;
6. devuelve una expedición lista para resolver la oleada 1.

No modifica el clan, las listas persistentes ni los archivos.

## Resolución de una oleada

```python
def resolver_siguiente_oleada(
    expedicion: EstadoExpedicion,
    generador: Random,
) -> ResultadoOleada:
    ...
```

Solo puede ejecutarse cuando `estado_flujo` es `lista_para_oleada`.

1. Obtiene la definición indicada por `proxima_oleada`.
2. Crea instancias enemigas nuevas.
3. Llama a `resolver_oleada()` conservando la vida de los aventureros entre
   oleadas.
4. Agrega la experiencia de los enemigos derrotados al pozo común.
5. Calcula el dinero de esa oleada.
6. Guarda el resultado como `ultima_oleada`.

`ultima_oleada` será una copia profunda del resultado, no una vista de los
aventureros que continuarán mutando. De esa manera la interfaz puede mostrar el
estado exacto al terminar la oleada anterior.

Si el resultado es victoria y no era la décima oleada, incrementa
`proxima_oleada`, aumenta `oleadas_superadas` y cambia a
`esperando_decision`.

Solo una **victoria** en la oleada 10 agrega la bonificación de finalización y
termina con `mazmorra_completada`. Una derrota o un límite de rondas en esa
oleada conservan su resultado normal, no agregan 100 monedas y no marcan la
mazmorra.

Una derrota termina con `derrota_total`. Un límite de treinta rondas termina
con `limite_de_rondas` y el grupo regresa con el botín acumulado, incluidos los
enemigos derrotados en esa oleada.

## Dinero y experiencia

La experiencia no recibe multiplicadores:

```text
experiencia de oleada = suma de XP de enemigos derrotados
```

El dinero usa una bonificación acumulativa del 10% desde la segunda oleada:

```text
porcentaje = 100 + 10 × (número de oleada - 1)
dinero de oleada = dinero base derrotado × porcentaje // 100
```

La bonificación se aplica también sobre recompensas parciales de una oleada
terminada por límite de rondas.

Completar la oleada 10 agrega 100 monedas. La bonificación se obtiene en cada
finalización completa, incluso si `mazmorra_1` ya estaba marcada.

Con los valores iniciales, derrotar las diez oleadas entrega 416 monedas por
enemigos y 100 adicionales, para un total de 516.

## Decisión entre oleadas

```python
def continuar_expedicion(expedicion: EstadoExpedicion) -> None:
    ...


def retirar_expedicion(expedicion: EstadoExpedicion) -> None:
    ...
```

Ambas operaciones exigen `esperando_decision`. Continuar cambia el flujo a
`lista_para_oleada`. Retirarse cambia a `finalizada` con resultado
`retirada`.

No se permite retirarse antes de resolver la primera oleada ni continuar tras
una finalización automática. Una transición inválida no modifica el estado.

## Aplicación de consecuencias

El cierre solo admite una expedición `finalizada` y se aplica una vez.

### Si regresa al menos un aventurero

- El clan recibe `dinero_acumulado`.
- El pozo de experiencia se divide mediante división entera entre los
  supervivientes.
- Cada superviviente recibe la misma parte y puede subir varios niveles.
- El sobrante de la división se descarta.
- Los supervivientes quedan vivos. La vida no se persiste y la próxima
  expedición los creará con vida completa.
- Los integrantes del grupo que murieron quedan en `datos_activos` con estado
  `muerto`, disponibles en la iglesia y ocupando cupo.
- Si se completó la mazmorra, se marca `mazmorra_1 = True`.
- El nivel actual del clan no se modifica; la progresión de dificultades
  futuras queda fuera de este bloque.

### Si no regresa nadie

- No se entrega dinero ni experiencia.
- Cada integrante del grupo se elimina de `datos_activos`.
- Se agrega a `datos_eliminados` en el orden del grupo con estado `muerto` y
  motivo `caido_no_recuperado`.
- Los miembros del clan que no participaron permanecen sin cambios.

## Renovación, derrota y guardado

Al cerrar cualquier expedición se renueva completamente el mercado mediante
`renovar_mercado()`.

Después se evalúa la derrota definitiva:

1. si queda al menos un aventurero vivo en el clan, continúa;
2. si no quedan vivos pero el dinero alcanza para resucitar al menos un cuerpo
   recuperado, continúa;
3. si no puede resucitar pero puede pagar al menos una oferta y quedan
   contrataciones, continúa;
4. un cupo lleno de muertos no bloquea esta posibilidad porque pueden
   enterrarse gratuitamente;
5. si ninguna alternativa existe, `estado_partida` pasa a `derrota`.

La coordinación pública será:

```python
def cerrar_expedicion_y_guardar(
    expedicion: EstadoExpedicion,
    estado_clan: EstadoClan,
    datos_activos: list[AventureroActivo],
    datos_eliminados: list[AventureroEliminado],
    generador: Random,
    directorio: Path = DIRECTORIO_PARTIDA,
) -> ResumenCierreExpedicion:
    ...
```

El cierre tendrá comportamiento transaccional frente a errores controlados:

1. valida que la expedición esté `finalizada` y no aplicada;
2. valida que todos los IDs del grupo sigan en `datos_activos` con su misma
   plantilla; ninguna lista se modifica durante esta validación;
3. crea copias profundas del clan y de ambas listas persistentes;
4. aplica consecuencias, renovación y derrota definitiva sobre las copias;
5. conserva el estado del generador aleatorio antes de renovar;
6. guarda y valida las copias;
7. solamente después del guardado exitoso reemplaza el contenido de las
   estructuras originales y cambia la expedición a
   `consecuencias_aplicadas`;
8. devuelve un resumen tipado del cierre.

Si preparar o guardar falla, las estructuras originales y el estado de la
expedición permanecen intactos. El generador recupera su estado para que un
reintento produzca el mismo mercado. Un segundo cierre posterior al éxito
produce `ExpedicionYaAplicadaError`.

`ResumenCierreExpedicion` informará resultado final, dinero entregado,
experiencia individual, IDs supervivientes, IDs muertos, si se completó la
mazmorra y el estado resultante de la partida.

## Garantía de persistencia

La escritura actual prepara tres archivos temporales, pero reemplaza los
destinos de forma secuencial. Este bloque mejorará `guardar_partida()` para que,
ante un `OSError` controlado durante los reemplazos, restaure los archivos
originales ya sustituidos y elimine temporales y respaldos.

La garantía cubrirá errores de escritura y reemplazo informados al proceso. No
se afirmará atomicidad absoluta ante una caída abrupta del sistema operativo o
un corte de energía entre reemplazos; resolver ese escenario requeriría un
journal transaccional y queda fuera del proyecto integrador.

## Exclusividad de la expedición

La aplicación mantendrá como máximo un `EstadoExpedicion` activo. Mientras su
flujo sea `lista_para_oleada` o `esperando_decision`, la futura interfaz no
permitirá reclutar, expulsar, resucitar, enterrar ni iniciar otra expedición.

No se creará un gestor global dentro del servicio. La exclusividad pertenece al
coordinador de aplicación; el cierre agrega la validación defensiva de IDs y
plantillas para rechazar datos incompatibles antes de cualquier mutación.

## Errores de dominio

Las nuevas excepciones heredarán de `ValueError`:

- `MazmorraNoEncontradaError`;
- `MazmorraNoDisponibleError` para cualquier mazmorra distinta de la primera
  durante este bloque;
- `EstadoExpedicionInvalidoError`;
- `TransicionExpedicionInvalidaError`;
- `ExpedicionYaAplicadaError`.

Los errores de persistencia conservarán las excepciones existentes de
`persistencia.py`.

## Pruebas requeridas

- Inicio con uno, tres y el máximo de aventureros permitido.
- Rechazo de IDs ausentes, muertos, repetidos y grupos demasiado grandes.
- Independencia entre estados temporales y registros persistentes.
- Transiciones válidas e inválidas del flujo.
- Conservación de vida entre oleadas.
- Multiplicador monetario y redondeo hacia abajo.
- Bonificación repetible de 100 monedas al completar.
- Retirada después de una o varias oleadas.
- Retorno automático por límite de rondas con recompensa parcial.
- Reparto de experiencia solo entre supervivientes y descarte del sobrante.
- Ascensos múltiples mediante `aplicar_experiencia()`.
- Muertos recuperados en la iglesia.
- Derrota total con caídos no recuperados y pérdida completa del botín.
- Conservación de miembros del clan que no participaron.
- Renovación del mercado en todos los finales.
- Derrota definitiva con cada alternativa de recuperación.
- Rechazo de una segunda aplicación de consecuencias.
- Fallo de guardado seguido de reintento sin duplicar recompensas ni renovar el
  mercado de forma diferente.
- Restauración de los tres JSON ante errores controlados durante el reemplazo.
- Guardado y recarga desde un directorio temporal.
- Integración determinista de las diez oleadas con catálogos reales.
- Suite completa y Pyright estricto sin errores nuevos.

## Criterio de finalización

El bloque estará completo cuando una capa de interfaz pueda:

1. iniciar la Mazmorra de los Limos con IDs seleccionados;
2. resolver y mostrar una oleada;
3. continuar o retirarse cuando corresponda;
4. cerrar la expedición y recargar desde JSON el mismo resultado persistente;
5. distinguir retirada, mazmorra completada, derrota total y límite de rondas.
