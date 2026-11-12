# Diseño: combate básico y primera mazmorra

## Intención

Construir el primer motor de combate jugable de Gestión de Clan ENOM usando
los diez enemigos y las diez oleadas definidas para la Mazmorra de los Limos.
El bloque resolverá ataques básicos automáticos, orden de turnos, selección de
objetivos, críticos, efectividad, defensa, daño, muertes, recompensas y el
límite de rondas.

El diseño mantiene el espíritu del sistema de mesa, pero elimina reglas que no
aportan a esta presentación. El objetivo es obtener un núcleo pequeño,
determinista en pruebas y fácil de balancear modificando solamente los
catálogos.

## Estado previo

El proyecto ya dispone de:

- quince plantillas de aventureros con estadísticas, tipo de ataque,
  probabilidad crítica adicional y estrategia de ataque básico;
- cálculo de estadísticas por nivel;
- cálculo de probabilidad crítica;
- multiplicadores de efectividad;
- formación y validación del grupo;
- constantes para diez oleadas y treinta rondas;
- estructuras persistentes separadas de los futuros estados de combate.

Los módulos `catalogos/enemigos.py`, `catalogos/mazmorras.py`,
`modelos/combate.py` y `servicios/combate.py` se encuentran preparados como
puntos de extensión, pero todavía no contienen la implementación.

## Objetivos

- Corregir el multiplicador crítico del 150% al 200%.
- Limitar la probabilidad crítica utilizada en combate al 90%.
- Definir las estructuras tipadas de enemigos, oleadas y estados temporales.
- Cargar las diez plantillas de enemigos de la primera mazmorra.
- Cargar las diez composiciones manuales de oleadas.
- Crear instancias independientes cuando una oleada repita una plantilla.
- Resolver empates mediante una operación reutilizable con tiradas de d100.
- Crear y conservar el orden de turnos durante toda una oleada.
- Resolver ataques básicos de aventureros y enemigos.
- Aplicar efectividad, crítico, defensa y daño mínimo en el orden acordado.
- Resolver rondas hasta victoria, derrota o límite de treinta rondas.
- Acumular las recompensas provisionales de los enemigos derrotados.
- Permitir pruebas reproducibles inyectando una instancia de `Random`.

## Fuera de alcance

- Ejecutar las quince habilidades profesionales.
- Administrar enfriamientos, escudos, curaciones o provocaciones.
- Preguntar al jugador si desea continuar o regresar.
- Encadenar las diez oleadas como una expedición completa.
- Repartir experiencia entre supervivientes.
- Aplicar dinero, experiencia, estados de muerte o bajas a la partida guardada.
- Renovar el mercado después de la expedición.
- Subir el nivel del clan o evaluar victoria y derrota de la partida.
- Guardar un historial permanente de ataques.
- Implementar pantallas de Tkinter.
- Realizar el balance definitivo de criaturas y oleadas.

## Enfoques considerados

### Resolver toda la oleada en una única función

Reduciría inicialmente la cantidad de funciones, pero mezclaría tiradas,
objetivos, daño, turnos, recompensas y condiciones de finalización. Sería
difícil probar cada regla y modificarla sin afectar las demás.

### Crear clases para motor, turno y combatientes

Encapsularía el estado, pero agregaría una jerarquía orientada a objetos que
no resulta necesaria para este proyecto. Los estados de combate son
temporales y las reglas pueden expresarse con estructuras tipadas y funciones.

### Funciones especializadas y estados `TypedDict` —seleccionado—

Las plantillas y estados se representarán con `TypedDict`. Las reglas se
dividirán en funciones pequeñas y documentadas. Solo los estados temporales de
combate podrán mutar durante la oleada; los aventureros persistentes y los
catálogos permanecerán intactos.

Este enfoque coincide con los servicios de reclutamiento, iglesia y gestión
de aventureros ya implementados y permite cambiar estadísticas o cantidades
sin modificar el algoritmo de combate.

## Reglas de la tirada de ataque

Cada ataque utiliza una única tirada uniforme de d100, comprendida entre 1 y
100. No existe un resultado separado de fallo crítico en esta versión.

```python
ResultadoTirada: TypeAlias = Literal[
    "fallo",
    "impacto",
    "critico",
]
```

La distribución es:

| Resultado del d100 | Efecto |
|---:|---|
| `1` hasta la probabilidad crítica total | Crítico |
| Siguiente valor hasta `90` | Impacto normal |
| `91` hasta `100` | Fallo |

La probabilidad crítica total será:

```text
min(90, max(0, 5 + crítico adicional))
```

Los aventureros usan el crítico adicional de su plantilla. Los enemigos usan
solamente el 5% base. Un fallo causa cero puntos de daño y no aplica el mínimo
de uno.

## Orden del cálculo de daño

Un ataque que impacta se resuelve en el siguiente orden:

1. partir del daño base del atacante;
2. aplicar el multiplicador de efectividad;
3. aplicar el multiplicador crítico del 200%, si corresponde;
4. redondear una única vez hacia abajo;
5. restar la defensa del objetivo;
6. aplicar un mínimo de un punto de daño;
7. restar el resultado a la vida, sin permitir valores negativos.

```text
daño modificado = floor(
    daño base
    × multiplicador de efectividad
    × multiplicador crítico
)

daño aplicado = max(1, daño modificado - defensa)

vida resultante = max(0, vida actual - daño aplicado)
```

Los multiplicadores de efectividad son:

| Efectividad | Multiplicador |
|---|---:|
| Efectivo | 1,50 |
| Neutral | 1,00 |
| Inefectivo | 0,50 |

Los ataques de aventureros consultan la efectividad que la plantilla enemiga
tiene frente al tipo de ataque recibido. Los ataques enemigos son siempre
neutrales contra aventureros.

## Selección de objetivos

Los enemigos eligen al azar entre todos los aventureros vivos.

Los aventureros usan `estrategia_ataque_basico` de su plantilla:

- `aleatorio`: cualquier enemigo vivo;
- `menor_vida_actual`: enemigo vivo con menor vida actual;
- `mayor_vida_actual`: enemigo vivo con mayor vida actual.

Si varios objetivos empatan en menor o mayor vida, se utiliza el desempate
general de d100. No se decide por el orden del catálogo ni por el orden de
creación de las instancias.

## Desempates mediante d100

Una función genérica ordenará participantes empatados mediante una tirada de
d100 por cada uno. El valor más alto obtiene prioridad. Si dos o más vuelven a
empatar, solamente esos participantes repiten la tirada hasta obtener un
orden definitivo.

La función se reutilizará en:

- empates de velocidad al crear el orden de turnos;
- empates de menor vida al seleccionar objetivo;
- empates de mayor vida al seleccionar objetivo;
- futuras reglas que necesiten una selección aleatoria ordenada.

Para conservar compatibilidad con Python 3.11 se utilizará `TypeVar`, no la
sintaxis de parámetros genéricos incorporada en Python 3.12:

```python
T = TypeVar("T")


def resolver_desempate_d100(
    participantes: Sequence[T],
    generador: Random,
) -> list[T]:
    ...
```

## Orden de turnos

Al comenzar cada oleada:

1. se reúnen todos los aventureros y enemigos vivos;
2. se ordenan por velocidad de mayor a menor;
3. cada grupo con la misma velocidad se resuelve mediante el desempate d100;
4. se conserva el orden resultante durante toda la oleada.

El orden no se vuelve a calcular al comenzar una ronda. Si un combatiente
muere antes de su turno, se lo omite. No existen incorporaciones, invocaciones
ni cambios permanentes de velocidad en este bloque.

## Rondas y finalización

Una ronda recorre una vez el orden completo de turnos. Después de cada ataque
se comprueba si alguno de los dos bandos se quedó sin combatientes vivos.

La oleada termina con uno de estos resultados:

```python
ResultadoCombate: TypeAlias = Literal[
    "victoria",
    "derrota",
    "limite_de_rondas",
]
```

- `victoria`: no quedan enemigos vivos;
- `derrota`: no quedan aventureros vivos;
- `limite_de_rondas`: ambos bandos conservan integrantes vivos al completar
  la ronda 30.

Si se alcanza el límite, los supervivientes conservan su vida y la expedición
posterior hará regresar al grupo. Los enemigos derrotados antes del límite sí
aportan recompensas provisionales; los supervivientes enemigos no aportan
nada.

Con ataques básicos secuenciales no puede producirse una muerte simultánea.
La regla ya acordada de considerar fracaso una muerte simultánea se reservará
para futuras habilidades que pudieran introducirla.

## Catálogo de enemigos

### Tipo de efectividades recibidas

```python
class EfectividadesRecibidas(TypedDict):
    cuerpo_a_cuerpo: EfectividadAtaque
    distancia: EfectividadAtaque
    magico: EfectividadAtaque
```

### Plantilla permanente

```python
class PlantillaEnemigo(TypedDict):
    id: str
    nombre: str
    estadisticas: Estadisticas
    tipo_ataque: TipoAtaque
    efectividades: EfectividadesRecibidas
    experiencia: int
    dinero: int
    es_jefe: bool
    imagen: str
    descripcion: str
```

`imagen` y `descripcion` podrán conservar cadenas vacías hasta recibir los
recursos finales. No intervienen en el combate.

### Datos de la primera mazmorra

| ID | Nombre | Vida | Daño | Defensa | Velocidad | Ataque | Cuerpo a cuerpo | Distancia | Mágico | XP | Dinero | Jefe |
|---|---|---:|---:|---:|---:|---|---|---|---|---:|---:|---|
| `LIMOS_LIMO` | Limo | 20 | 20 | 1 | 1 | Mágico | Efectivo | Efectivo | Inefectivo | 10 | 1 | No |
| `LIMOS_LIME` | Lime | 40 | 15 | 5 | 2 | Cuerpo a cuerpo | Inefectivo | Neutral | Efectivo | 10 | 1 | No |
| `LIMOS_LIMA` | Lima | 30 | 17 | 3 | 3 | Distancia | Efectivo | Inefectivo | Efectivo | 10 | 1 | No |
| `LIMOS_BRUJILIMO` | Brujilimo | 20 | 30 | 5 | 5 | Mágico | Efectivo | Neutral | Inefectivo | 15 | 3 | No |
| `LIMOS_MEDULIMO` | Medulimo | 50 | 20 | 9 | 6 | Cuerpo a cuerpo | Neutral | Neutral | Efectivo | 15 | 3 | No |
| `LIMOS_METALIMO` | Metalimo | 15 | 20 | 20 | 15 | Cuerpo a cuerpo | Inefectivo | Inefectivo | Inefectivo | 20 | 18 | No |
| `LIMOS_TRIO_LIMOSO` | Trío Limoso | 90 | 25 | 9 | 6 | Cuerpo a cuerpo | Efectivo | Efectivo | Efectivo | 20 | 8 | No |
| `LIMOS_LIMO_PRISMATICO` | Limo Prismático | 60 | 30 | 30 | 30 | Cuerpo a cuerpo | Neutral | Neutral | Neutral | 30 | 10 | No |
| `LIMOS_MEDULIMO_GUERRERO` | Medulimo Guerrero | 100 | 25 | 40 | 15 | Cuerpo a cuerpo | Neutral | Neutral | Efectivo | 40 | 15 | No |
| `LIMOS_REY_LIMO` | Rey Limo | 120 | 40 | 50 | 20 | Mágico | Inefectivo | Neutral | Neutral | 60 | 30 | Sí |

Los identificadores internos no utilizan tildes. Los nombres visibles sí se
escriben correctamente.

## Definición de oleadas y mazmorra

```python
class GrupoEnemigosOleada(TypedDict):
    plantilla_id: str
    cantidad: int


class DefinicionOleada(TypedDict):
    numero: int
    enemigos: list[GrupoEnemigosOleada]


class DefinicionMazmorra(TypedDict):
    id: str
    nombre: str
    dificultad: DificultadMazmorra
    oleadas: list[DefinicionOleada]
```

Las composiciones manuales son la única fuente de verdad. Los antiguos campos
de oleadas permitidas y cantidad máxima por criatura no se validarán ni se
utilizarán en ejecución.

| Oleada | Composición | Cantidad | XP | Dinero |
|---:|---|---:|---:|---:|
| 1 | 1 Limo, 1 Lime, 1 Lima | 3 | 30 | 3 |
| 2 | 2 Limos, 2 Limes, 2 Limas | 6 | 60 | 6 |
| 3 | 1 Limo, 1 Lime, 1 Lima, 1 Brujilimo, 1 Medulimo | 5 | 60 | 9 |
| 4 | 2 Limos, 2 Limes, 2 Limas, 1 Brujilimo, 1 Medulimo | 8 | 90 | 12 |
| 5 | 2 Limos, 2 Limes, 2 Limas, 2 Brujilimos, 2 Medulimos | 10 | 120 | 18 |
| 6 | 2 Brujilimos, 2 Medulimos, 2 Tríos Limosos | 6 | 100 | 28 |
| 7 | 1 Brujilimo, 1 Medulimo, 1 Metalimo, 1 Trío Limoso, 1 Limo Prismático | 5 | 100 | 42 |
| 8 | 1 Metalimo, 2 Tríos Limosos, 1 Limo Prismático, 1 Medulimo Guerrero | 5 | 130 | 59 |
| 9 | 2 Tríos Limosos, 2 Limos Prismáticos, 1 Medulimo Guerrero | 5 | 140 | 51 |
| 10 | 1 Rey Limo | 1 | 60 | 30 |

Totales de la mazmorra:

- 54 enemigos;
- 890 puntos de experiencia base;
- 258 monedas base.

Estos valores son parámetros iniciales. El balance posterior podrá modificar
cantidades, estadísticas y recompensas sin cambiar el motor.

## Estados temporales de combate

### Aventurero

```python
class AventureroCombate(TypedDict):
    id: str
    nombre: str
    plantilla_id: str
    vida_maxima: int
    vida_actual: int
    dano: int
    defensa: int
    velocidad: int
    probabilidad_critica: int
    tipo_ataque: TipoAtaque
    estrategia_objetivo: EstrategiaObjetivo
    esta_vivo: bool
```

### Enemigo

```python
class EnemigoCombate(TypedDict):
    id_instancia: str
    plantilla_id: str
    nombre: str
    vida_maxima: int
    vida_actual: int
    dano: int
    defensa: int
    velocidad: int
    tipo_ataque: TipoAtaque
    efectividades: EfectividadesRecibidas
    probabilidad_critica: int
    experiencia: int
    dinero: int
    es_jefe: bool
    esta_vivo: bool
```

Las instancias repetidas reciben identificadores independientes, por ejemplo:

```text
LIMOS_LIMO-01
LIMOS_LIMO-02
LIMOS_LIME-01
```

Los contadores se reinician al crear cada oleada. El ID de plantilla conserva
la relación con el catálogo; el ID de instancia permite mantener vida y turnos
independientes.

## Resultados temporales

### Ataque

```python
class ResultadoAtaque(TypedDict):
    resultado: ResultadoTirada
    dano_aplicado: int
    vida_restante: int
    objetivo_derrotado: bool
```

Este resultado existe solamente mientras se ejecuta el turno. No se acumula,
no se muestra como historial y no se guarda en JSON.

### Oleada

```python
class ResultadoOleada(TypedDict):
    resultado: ResultadoCombate
    rondas: int
    aventureros: list[AventureroCombate]
    enemigos: list[EnemigoCombate]
    enemigos_derrotados: list[str]
    experiencia_obtenida: int
    dinero_obtenido: int
```

`enemigos_derrotados` conserva los IDs de instancia en el orden de derrota.
La interfaz futura resolverá los nombres mediante los estados devueltos.

Las recompensas son provisionales. El futuro servicio de expediciones las
acumulará entre oleadas y decidirá si se entregan o se pierden según regrese
al menos un aventurero vivo.

## API prevista

Los nombres definitivos podrán ajustarse durante el plan sin cambiar sus
responsabilidades.

```python
def crear_aventurero_combate(
    aventurero: AventureroActivo,
) -> AventureroCombate:
    ...


def crear_enemigos_oleada(
    oleada: DefinicionOleada,
    catalogo: Mapping[str, PlantillaEnemigo],
) -> list[EnemigoCombate]:
    ...


def resolver_desempate_d100(
    participantes: Sequence[T],
    generador: Random,
) -> list[T]:
    ...


def calcular_orden_turnos(
    aventureros: Sequence[AventureroCombate],
    enemigos: Sequence[EnemigoCombate],
    generador: Random,
) -> list[ParticipanteTurno]:
    ...


def seleccionar_objetivo_aventurero(
    atacante: AventureroCombate,
    enemigos: Sequence[EnemigoCombate],
    generador: Random,
) -> EnemigoCombate:
    ...


def seleccionar_objetivo_enemigo(
    aventureros: Sequence[AventureroCombate],
    generador: Random,
) -> AventureroCombate:
    ...


def resolver_tirada_ataque(
    probabilidad_critica: int,
    generador: Random,
) -> ResultadoTirada:
    ...


def calcular_dano_recibido(
    dano_modificado: int,
    defensa: int,
) -> int:
    ...


def ejecutar_ataque_basico(
    atacante: ParticipanteTurno,
    objetivo: ParticipanteTurno,
    efectividad: EfectividadAtaque,
    generador: Random,
) -> ResultadoAtaque:
    ...


def resolver_ronda(
    orden_turnos: Sequence[ParticipanteTurno],
    aventureros: list[AventureroCombate],
    enemigos: list[EnemigoCombate],
    generador: Random,
) -> None:
    ...


def resolver_oleada(
    aventureros: list[AventureroCombate],
    enemigos: list[EnemigoCombate],
    generador: Random,
) -> ResultadoOleada:
    ...
```

`ParticipanteTurno` podrá definirse como una unión tipada de aventurero y
enemigo junto con un discriminador de bando, o como una estructura pequeña
que almacene bando e ID de instancia. El plan elegirá la opción que reduzca
la duplicación sin permitir confundir participantes de ambos bandos.

## Mutaciones y límites de responsabilidad

- Las plantillas, catálogos, definiciones de oleada y registros persistentes
  nunca se modifican durante el combate.
- Las funciones de creación generan estados temporales nuevos.
- La vida, el estado y demás efectos de la oleada se aplican únicamente sobre
  `AventureroCombate` y `EnemigoCombate`.
- Un ataque fallido no cambia la vida del objetivo.
- Una recompensa se agrega una sola vez, cuando la vida del enemigo llega por
  primera vez a cero.
- El motor no guarda JSON ni conoce Tkinter.

## Validaciones y errores

Se rechazarán antes de resolver la oleada:

- grupos sin al menos un aventurero vivo;
- oleadas sin enemigos;
- vidas máximas menores que uno;
- vidas actuales fuera del intervalo entre cero y la vida máxima;
- estados incoherentes, como `esta_vivo` verdadero con vida cero;
- daño, defensa o velocidad negativos;
- probabilidades críticas fuera del dominio recibido por las funciones
  internas;
- cantidades de enemigos menores que uno;
- IDs de plantilla inexistentes;
- números de oleada fuera de 1 a 10;
- plantillas repetidas dentro de una misma definición de oleada;
- IDs de instancia duplicados.

La lista de aventureros puede conservar integrantes muertos de oleadas
anteriores. Estos estados son válidos, no participan del orden de turnos y no
pueden ser seleccionados como objetivos.

Las excepciones de dominio heredarán de `ValueError`, siguiendo la convención
del proyecto. Los nombres concretos se decidirán durante el plan.

## Aleatoriedad reproducible

Toda operación aleatoria recibirá explícitamente un `Random`. Ninguna función
de dominio utilizará el generador global del módulo `random`.

Uso normal:

```python
generador = Random()
```

Uso en pruebas:

```python
generador = Random(20)
```

Las pruebas que necesiten resultados exactos podrán utilizar una semilla o un
doble controlado que entregue una secuencia predefinida de tiradas.

## Pruebas requeridas

### Cálculos existentes

- crítico neutral de 15 puntos produce 30;
- crítico efectivo de 15 puntos produce 45;
- probabilidad crítica mínima 0 y máxima 90;
- se mantienen los resultados no críticos de efectividad.

### Tiradas

- extremo inferior del crítico;
- extremo superior del crítico;
- primer impacto normal después del crítico;
- impacto con resultado 90;
- fallo con resultado 91;
- fallo con resultado 100;
- enemigos con exactamente 5% de crítico.

### Daño y defensa

- impacto que supera la defensa;
- impacto igual a la defensa causa uno;
- impacto inferior a la defensa causa uno;
- fallo causa cero y no aplica mínimo;
- vida nunca queda por debajo de cero;
- efectividad y crítico se aplican antes de defensa.

### Desempates y objetivos

- orden por velocidad descendente;
- desempate por d100 descendente;
- repetición solamente entre participantes que vuelven a empatar;
- objetivo aleatorio siempre vivo;
- menor vida con empate;
- mayor vida con empate;
- enemigos seleccionan únicamente aventureros vivos.

### Rondas y oleadas

- combatiente muerto pierde su turno;
- victoria al morir el último enemigo;
- derrota al morir el último aventurero;
- finalización después de treinta rondas;
- orden de turnos calculado una sola vez;
- recompensa agregada exactamente una vez;
- enemigo superviviente no entrega recompensa;
- resultado sin historial de ataques.

### Catálogos

- existen diez enemigos y sus IDs coinciden con las claves;
- estadísticas, efectividades y recompensas son válidas;
- existen diez oleadas numeradas consecutivamente;
- todas las plantillas referenciadas existen;
- todas las cantidades son positivas;
- la oleada 6 contiene dos Brujilimos, dos Medulimos y dos Tríos Limosos;
- la oleada 10 contiene únicamente al Rey Limo;
- la mazmorra completa contiene 54 enemigos, 890 XP y 258 monedas.

## Documentación que deberá actualizarse

- `configuracion.py`: multiplicador crítico 2,00 y límite crítico 90.
- `documentacion/reglas_definidas.md`: nuevas reglas y primera mazmorra.
- `README.md`: combate básico y catálogos implementados cuando corresponda.
- Presentación del proyecto: reemplazar daño crítico del 150% por 200%.

## Integración futura

El servicio de expediciones reutilizará `resolver_oleada()` para:

1. crear cada oleada según el catálogo;
2. conservar la vida de los aventureros entre oleadas;
3. acumular experiencia y dinero provisionales;
4. preguntar si se continúa o se regresa;
5. aplicar recompensas solo si regresa al menos un superviviente;
6. registrar muertos recuperados o caídos sin cuerpo;
7. renovar el mercado al terminar la expedición.

Las habilidades se incorporarán después sobre el mismo orden de turnos y los
mismos estados temporales. El ataque básico será la alternativa cuando una
habilidad no se utilice o se encuentre en enfriamiento.

