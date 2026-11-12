# Basic Combat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar el combate automático sin habilidades y cargar los diez enemigos y las diez oleadas de la primera mazmorra.

**Architecture:** Las definiciones permanentes vivirán en catálogos tipados y el combate utilizará estados temporales independientes de los registros persistentes. `servicios/combate.py` dividirá tiradas, desempates, objetivos, ataques, rondas y oleadas en funciones pequeñas con una instancia de `Random` inyectada.

**Tech Stack:** Python 3.11+, `typing`, `random.Random`, `unittest`, `TypedDict`, `Literal` y funciones de dominio sin dependencias externas.

**Spec:** `docs/superpowers/specs/2026-11-12-combate-basico-design.md`

## Global Constraints

- Mantener compatibilidad con Python 3.11 o superior.
- No agregar dependencias externas, Tkinter, JSON ni acceso al sistema de archivos al motor de combate.
- Anotar parámetros, retornos, estructuras internas y colecciones.
- Documentar todas las funciones públicas y las funciones internas cuya responsabilidad no sea evidente.
- Usar una única tirada d100 por ataque: crítico, impacto o fallo.
- Limitar la probabilidad crítica total al 90% y aplicar crítico del 200%.
- Aplicar efectividad y crítico antes de defensa, redondeando una vez hacia abajo.
- Aplicar daño mínimo de uno solamente a ataques que impacten.
- Tratar todos los ataques enemigos como neutrales contra aventureros.
- Usar `Random` recibido por parámetro para toda decisión aleatoria.
- No guardar un historial de ataques ni modificar registros persistentes.
- Conservar el orden de turnos durante toda la oleada.
- Mantener la cantidad máxima de treinta rondas.
- Ejecutar cada tarea mediante TDD y conservar las 127 pruebas existentes.

## Review Focus

- Una lista con aventureros muertos y al menos uno vivo debe ser válida; los muertos no actúan ni pueden ser objetivos. Se prueba en Task 5 y Task 8.
- Un empate repetido de d100 debe volver a tirar solamente por quienes continúan empatados. Se prueba en Task 6.
- Las fronteras 90 y 91 deben producir impacto y fallo respectivamente, incluso con crítico limitado. Se prueba en Task 6.
- Un enemigo derrotado debe perder su turno y otorgar recompensa exactamente una vez. Se prueba en Task 8 y Task 9.
- Derrotar al último enemigo durante la ronda 30 debe ser victoria, no límite de rondas. Se prueba en Task 9.

---

## File Map

- `configuracion.py`: constantes de crítico, impacto y límites generales.
- `modelos/combate.py`: aliases y `TypedDict` exclusivos del combate, enemigos y mazmorras.
- `catalogos/enemigos.py`: diez plantillas permanentes de enemigos.
- `catalogos/mazmorras.py`: diez oleadas y definición de la Mazmorra de los Limos.
- `servicios/calculos.py`: probabilidad crítica y daño previo a defensa.
- `servicios/combate.py`: creación de estados, azar, objetivos, ataques, turnos, rondas y oleadas.
- `tests/test_calculos.py`: regresión del crítico del 200% y límite del 90%.
- `tests/test_enemigos.py`: validación del catálogo de enemigos.
- `tests/test_mazmorras.py`: composiciones y totales de la primera mazmorra.
- `tests/test_combate.py`: estados temporales y reglas completas del combate básico.
- `documentacion/reglas_definidas.md`: reglas implementadas y composición aprobada.
- `README.md`: estado actualizado del proyecto y forma de probar el combate.

### Task 1: Correct Critical Damage and Probability Cap

**Files:**
- Modify: `configuracion.py`
- Modify: `servicios/calculos.py`
- Modify: `tests/test_calculos.py`

**Interfaces:**
- Consumes: `calcular_probabilidad_critico(int) -> int` y `calcular_dano_final(int, EfectividadAtaque, bool) -> int` existentes.
- Produces: crítico máximo del 90% y multiplicador crítico del 200% para Tasks 5–9.

- [ ] **Step 1: Write failing tests for the approved critical rules**

Actualizar `PruebasCombateBase` con estas aserciones:

```python
def test_limita_probabilidad_critica_entre_cero_y_noventa(self) -> None:
    self.assertEqual(calcular_probabilidad_critico(-10), 0)
    self.assertEqual(calcular_probabilidad_critico(85), 90)
    self.assertEqual(calcular_probabilidad_critico(200), 90)


def test_aplica_critico_del_doscientos_por_ciento(self) -> None:
    self.assertEqual(calcular_dano_final(15, "neutral", True), 30)
    self.assertEqual(calcular_dano_final(15, "efectivo", True), 45)
```

- [ ] **Step 2: Run the focused tests and confirm the old behavior fails**

Run: `python -m unittest tests.test_calculos.PruebasCombateBase -v`

Expected: FAIL because the current cap is 100 and the current critical multiplier is 1.50.

- [ ] **Step 3: Update the constants and calculation**

In `configuracion.py` set:

```python
MULTIPLICADOR_CRITICO: float = 2.00
PROBABILIDAD_CRITICA_MAXIMA: int = 90
```

Remove `RESULTADO_FALLO_CRITICO` because the simplified combat has no special
critical-failure result. Keep `LIMITE_IMPACTO_NORMAL = 90`.

Import `PROBABILIDAD_CRITICA_MAXIMA` in `servicios/calculos.py` and use it as
the upper bound of `calcular_probabilidad_critico()`.

- [ ] **Step 4: Run focused and full tests**

Run: `python -m unittest tests.test_calculos -v`

Expected: PASS.

Run: `python -m unittest discover -s tests -v`

Expected: all existing and modified tests PASS.

- [ ] **Step 5: Commit**

```bash
git add configuracion.py servicios/calculos.py tests/test_calculos.py
git commit -m "fix: aplicar crítico del doscientos por ciento"
```

### Task 2: Define the Combat Domain Types

**Files:**
- Modify: `modelos/combate.py`
- Create: `tests/test_modelos_combate.py`

**Interfaces:**
- Consumes: `AventureroActivo`, `DificultadMazmorra`, `EfectividadAtaque`, `Estadisticas`, `EstrategiaObjetivo` y `TipoAtaque` de `modelos/tipos.py`.
- Produces: `ResultadoTirada`, `ResultadoCombate`, `EfectividadesRecibidas`, `PlantillaEnemigo`, `GrupoEnemigosOleada`, `DefinicionOleada`, `DefinicionMazmorra`, `CombatienteBase`, `AventureroCombate`, `EnemigoCombate`, `TurnoAventurero`, `TurnoEnemigo`, `ParticipanteTurno`, `ResultadoAtaque` y `ResultadoOleada`.

- [ ] **Step 1: Write failing construction tests for every public TypedDict**

Create fixtures annotated with each new type and assert representative fields,
including:

```python
def test_resultado_tirada_no_incluye_fallo_critico(self) -> None:
    self.assertEqual(
        get_args(ResultadoTirada),
        ("fallo", "impacto", "critico"),
    )
```

Also construct one adventurer state, one enemy state, one wave and one wave
result. The runtime assertions verify their exact key names and values.

- [ ] **Step 2: Run the new module and verify imports fail**

Run: `python -m unittest tests.test_modelos_combate -v`

Expected: FAIL because the types do not exist.

- [ ] **Step 3: Implement the aliases and TypedDicts in `modelos/combate.py`**

Use the fields from the approved spec. Extract the shared mutable fields
without erasing the specialized fields:

```python
class CombatienteBase(TypedDict):
    nombre: str
    vida_maxima: int
    vida_actual: int
    dano: int
    defensa: int
    velocidad: int
    probabilidad_critica: int
    esta_vivo: bool


class AventureroCombate(CombatienteBase):
    id: str
    plantilla_id: str
    tipo_ataque: TipoAtaque
    estrategia_objetivo: EstrategiaObjetivo


class EnemigoCombate(CombatienteBase):
    id_instancia: str
    plantilla_id: str
    tipo_ataque: TipoAtaque
    efectividades: EfectividadesRecibidas
    experiencia: int
    dinero: int
    es_jefe: bool
```

Define turns as a discriminated union:

```python
class TurnoAventurero(TypedDict):
    bando: Literal["aventureros"]
    combatiente: AventureroCombate


class TurnoEnemigo(TypedDict):
    bando: Literal["enemigos"]
    combatiente: EnemigoCombate


ParticipanteTurno: TypeAlias = TurnoAventurero | TurnoEnemigo
```

This keeps references to the mutable temporary states without copying life.

- [ ] **Step 4: Run the type-model tests**

Run: `python -m unittest tests.test_modelos_combate -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add modelos/combate.py tests/test_modelos_combate.py
git commit -m "feat: definir modelos tipados de combate"
```

### Task 3: Load the Ten Enemy Templates

**Files:**
- Modify: `catalogos/enemigos.py`
- Create: `tests/test_enemigos.py`

**Interfaces:**
- Consumes: `PlantillaEnemigo` and `EfectividadesRecibidas` from Task 2.
- Produces: `CATALOGO_ENEMIGOS: dict[str, PlantillaEnemigo]` with the ten approved IDs.

- [ ] **Step 1: Write failing catalog tests**

Tests must assert:

```python
self.assertEqual(len(CATALOGO_ENEMIGOS), 10)
self.assertEqual(CATALOGO_ENEMIGOS["LIMOS_LIMO"]["estadisticas"]["vida"], 20)
self.assertEqual(CATALOGO_ENEMIGOS["LIMOS_METALIMO"]["dinero"], 18)
self.assertTrue(CATALOGO_ENEMIGOS["LIMOS_REY_LIMO"]["es_jefe"])
self.assertEqual(
    CATALOGO_ENEMIGOS["LIMOS_TRIO_LIMOSO"]["nombre"],
    "Trío Limoso",
)
```

Iterate over the catalog and assert that every dictionary key equals its `id`,
all statistics are non-negative with life greater than zero, rewards are
non-negative and all three effectiveness keys exist.

- [ ] **Step 2: Run the tests and confirm the pending catalog fails**

Run: `python -m unittest tests.test_enemigos -v`

Expected: FAIL because `CATALOGO_ENEMIGOS` does not exist.

- [ ] **Step 3: Implement the ten templates**

Create a private `_enemigo(...) -> PlantillaEnemigo` helper, following the
compact pattern used by `catalogos/plantillas.py`. Copy every approved stat,
attack type, effectiveness, reward and boss flag from the spec. Use empty
strings for `imagen` and `descripcion`.

- [ ] **Step 4: Run catalog and full tests**

Run: `python -m unittest tests.test_enemigos -v`

Expected: PASS.

Run: `python -m unittest discover -s tests -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add catalogos/enemigos.py tests/test_enemigos.py
git commit -m "feat: agregar enemigos de la mazmorra de limos"
```

### Task 4: Load the Manual Dungeon Waves

**Files:**
- Modify: `catalogos/mazmorras.py`
- Create: `tests/test_mazmorras.py`

**Interfaces:**
- Consumes: `CATALOGO_ENEMIGOS` from Task 3 and `DefinicionMazmorra` from Task 2.
- Produces: `MAZMORRA_LIMOS: DefinicionMazmorra` and `CATALOGO_MAZMORRAS: dict[str, DefinicionMazmorra]`.

- [ ] **Step 1: Write failing tests for composition and totals**

Assert ten consecutive waves, valid referenced IDs and positive quantities.
Pin the corrected wave and totals:

```python
self.assertEqual(
    MAZMORRA_LIMOS["oleadas"][5]["enemigos"],
    [
        {"plantilla_id": "LIMOS_BRUJILIMO", "cantidad": 2},
        {"plantilla_id": "LIMOS_MEDULIMO", "cantidad": 2},
        {"plantilla_id": "LIMOS_TRIO_LIMOSO", "cantidad": 2},
    ],
)
self.assertEqual(total_enemigos, 54)
self.assertEqual(total_experiencia, 890)
self.assertEqual(total_dinero, 258)
```

Assert wave 10 contains only one `LIMOS_REY_LIMO`.

- [ ] **Step 2: Run tests and confirm the pending catalog fails**

Run: `python -m unittest tests.test_mazmorras -v`

Expected: FAIL because the dungeon definitions do not exist.

- [ ] **Step 3: Implement the ten manual waves**

Use a private `_grupo(plantilla_id: str, cantidad: int) -> GrupoEnemigosOleada`
helper and define the exact compositions from the spec. Do not encode or
validate the obsolete availability ranges or maximum-per-wave fields.

- [ ] **Step 4: Run dungeon and full tests**

Run: `python -m unittest tests.test_mazmorras -v`

Expected: PASS.

Run: `python -m unittest discover -s tests -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add catalogos/mazmorras.py tests/test_mazmorras.py
git commit -m "feat: definir oleadas de la mazmorra de limos"
```

### Task 5: Create and Validate Temporary Combat States

**Files:**
- Modify: `servicios/combate.py`
- Create: `tests/test_combate.py`

**Interfaces:**
- Consumes: `AventureroActivo`, `PlantillaAventurero`, Task 2 combat types, Task 3 enemy catalog and `calcular_estadisticas()` / `calcular_probabilidad_critico()`.
- Produces: `crear_aventurero_combate(aventurero, catalogo) -> AventureroCombate`, `crear_enemigos_oleada(oleada, catalogo) -> list[EnemigoCombate]` and validation exceptions inheriting from `ValueError`.

- [ ] **Step 1: Write failing tests for adventurer state creation**

Assert that a level-one initial adventurer receives calculated statistics,
full current life, the approved critical cap, its attack type and its target
strategy. Assert the returned nested values are independent of the persistent
record and catalog.

- [ ] **Step 2: Write failing tests for repeated enemy instances**

Create wave 2 and assert exactly six independent states with these IDs:

```python
[
    "LIMOS_LIMO-01",
    "LIMOS_LIMO-02",
    "LIMOS_LIME-01",
    "LIMOS_LIME-02",
    "LIMOS_LIMA-01",
    "LIMOS_LIMA-02",
]
```

Mutating the life of one Limo must not change the other instance or its
template.

- [ ] **Step 3: Write failing validation tests from Review Focus**

Cover empty groups, no living adventurer, empty enemy list, inconsistent
`vida_actual` / `esta_vivo`, unknown template ID, quantity zero, repeated
template entries and duplicate runtime IDs. A group containing one dead and
one living adventurer must be accepted by the common state validator.

- [ ] **Step 4: Run the focused tests and confirm missing functions fail**

Run: `python -m unittest tests.test_combate.PruebasCreacionEstados -v`

Expected: FAIL because the creation functions do not exist.

- [ ] **Step 5: Implement creation and validation helpers**

Define `EstadoCombateInvalidoError(ValueError)` for inconsistent temporary
states or a group without survivors. Define
`DefinicionOleadaInvalidaError(ValueError)` for unknown templates, invalid
quantities, repeated template entries or duplicate runtime IDs.

Use these signatures:

```python
def crear_aventurero_combate(
    aventurero: AventureroActivo,
    catalogo: Mapping[str, PlantillaAventurero],
) -> AventureroCombate:
    ...


def crear_enemigos_oleada(
    oleada: DefinicionOleada,
    catalogo: Mapping[str, PlantillaEnemigo],
) -> list[EnemigoCombate]:
    ...
```

Keep validation internal unless another service needs it. Validate every
precondition before returning partial state.

- [ ] **Step 6: Run focused and full tests**

Run: `python -m unittest tests.test_combate.PruebasCreacionEstados -v`

Expected: PASS.

Run: `python -m unittest discover -s tests -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add servicios/combate.py tests/test_combate.py
git commit -m "feat: crear estados temporales de combate"
```

### Task 6: Implement Dice, Ties, and Target Selection

**Files:**
- Modify: `servicios/combate.py`
- Modify: `tests/test_combate.py`

**Interfaces:**
- Consumes: temporary states from Task 5 and `Random`.
- Produces: `resolver_desempate_d100()`, `resolver_tirada_ataque()`, `seleccionar_objetivo_aventurero()` and `seleccionar_objetivo_enemigo()`.

- [ ] **Step 1: Add a controlled random test double**

Inside `tests/test_combate.py`, define a small `RandomControlado(Random)` with
`randint(inicio, fin) -> int` and `choice(secuencia)` that consumes predefined
values. It must fail loudly if a test requests more values than configured.

- [ ] **Step 2: Write failing boundary tests for the one-roll attack**

Assert critical upper edge, first normal hit, 90, 91 and 100. Include a
received critical probability greater than 90 and verify
`resolver_tirada_ataque()` raises `ValueError`; normalization belongs only to
`calcular_probabilidad_critico()`.

- [ ] **Step 3: Write failing repeated-tie tests**

Use three labeled values and the sequence necessary to produce one unique
result and a two-way repeated tie. Assert only the two tied participants
consume the second pair of d100 values and that the final order is descending.

- [ ] **Step 4: Write failing target-selection tests**

Cover random enemy selection, minimum life, maximum life, ties resolved by
d100, and enemy selection that excludes dead adventurers.

- [ ] **Step 5: Run focused tests and verify failure**

Run: `python -m unittest tests.test_combate.PruebasAzarYObjetivos -v`

Expected: FAIL because the operations do not exist.

- [ ] **Step 6: Implement the four operations**

Use Python 3.11-compatible generics:

```python
T = TypeVar("T")


def resolver_desempate_d100(
    participantes: Sequence[T],
    generador: Random,
) -> list[T]:
    ...
```

`resolver_tirada_ataque()` receives a validated probability from 0 through 90
and returns only `"critico"`, `"impacto"` or `"fallo"`.

- [ ] **Step 7: Run focused and full tests**

Run: `python -m unittest tests.test_combate.PruebasAzarYObjetivos -v`

Expected: PASS.

Run: `python -m unittest discover -s tests -v`

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add servicios/combate.py tests/test_combate.py
git commit -m "feat: resolver tiradas y objetivos de combate"
```

### Task 7: Resolve Basic Attacks and Defense

**Files:**
- Modify: `servicios/combate.py`
- Modify: `tests/test_combate.py`

**Interfaces:**
- Consumes: Task 1 calculations, Task 2 states and Task 6 attack result.
- Produces: `obtener_efectividad_ataque()`, `calcular_dano_recibido()` and `ejecutar_ataque_basico()`.

- [ ] **Step 1: Write failing effectiveness tests**

Assert an adventurer attack reads the enemy effectiveness matching
`cuerpo_a_cuerpo`, `distancia` or `magico`. Assert every enemy attack against
an adventurer resolves as `"neutral"`.

- [ ] **Step 2: Write failing defense tests**

Assert:

```python
self.assertEqual(calcular_dano_recibido(30, 10), 20)
self.assertEqual(calcular_dano_recibido(10, 10), 1)
self.assertEqual(calcular_dano_recibido(5, 10), 1)
```

Negative damage or defense must raise `ValueError`.

- [ ] **Step 3: Write failing attack tests**

Cover failure with zero damage, normal hit, critical hit before defense,
effective and ineffective attacks, life clamped to zero, death flag update and
an already-dead target rejected without mutation.

- [ ] **Step 4: Run focused tests and verify failure**

Run: `python -m unittest tests.test_combate.PruebasAtaquesBasicos -v`

Expected: FAIL because attack resolution does not exist.

- [ ] **Step 5: Implement the damage operations**

Use these signatures:

```python
def obtener_efectividad_ataque(
    atacante: ParticipanteTurno,
    objetivo: ParticipanteTurno,
) -> EfectividadAtaque:
    ...


def calcular_dano_recibido(dano_modificado: int, defensa: int) -> int:
    ...


def ejecutar_ataque_basico(
    atacante: CombatienteBase,
    objetivo: CombatienteBase,
    efectividad: EfectividadAtaque,
    generador: Random,
) -> ResultadoAtaque:
    ...
```

Call `calcular_dano_final()` only after a non-failing roll. Apply defense and
minimum damage afterward. Mutate only the temporary target state.

- [ ] **Step 6: Run focused and full tests**

Run: `python -m unittest tests.test_combate.PruebasAtaquesBasicos -v`

Expected: PASS.

Run: `python -m unittest discover -s tests -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add servicios/combate.py tests/test_combate.py
git commit -m "feat: resolver ataques básicos y defensa"
```

### Task 8: Build Turn Order and Resolve One Round

**Files:**
- Modify: `servicios/combate.py`
- Modify: `tests/test_combate.py`

**Interfaces:**
- Consumes: Task 6 target selection and Task 7 attacks.
- Produces: `calcular_orden_turnos()` and `resolver_ronda() -> list[str]`.

- [ ] **Step 1: Write failing turn-order tests**

Assert descending velocity across both factions, d100 order for equal velocity,
exclusion of dead participants and stable references to original temporary
states.

- [ ] **Step 2: Write failing round tests**

Assert every living participant acts at most once, a participant killed before
its position loses the turn, targeting uses the attacker's strategy, the round
stops when a faction has no living members and newly defeated enemy IDs are
returned in defeat order.

Include the Review Focus case where dead adventurers are present beside one
living adventurer and are neither attackers nor targets.

- [ ] **Step 3: Run focused tests and verify failure**

Run: `python -m unittest tests.test_combate.PruebasTurnosYRonda -v`

Expected: FAIL because turn and round operations do not exist.

- [ ] **Step 4: Implement turn order and round resolution**

Use:

```python
def calcular_orden_turnos(
    aventureros: Sequence[AventureroCombate],
    enemigos: Sequence[EnemigoCombate],
    generador: Random,
) -> list[ParticipanteTurno]:
    ...


def resolver_ronda(
    orden_turnos: Sequence[ParticipanteTurno],
    aventureros: list[AventureroCombate],
    enemigos: list[EnemigoCombate],
    generador: Random,
) -> list[str]:
    ...
```

The returned IDs are the only per-round history needed by wave rewards.

- [ ] **Step 5: Run focused and full tests**

Run: `python -m unittest tests.test_combate.PruebasTurnosYRonda -v`

Expected: PASS.

Run: `python -m unittest discover -s tests -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add servicios/combate.py tests/test_combate.py
git commit -m "feat: resolver turnos y rondas de combate"
```

### Task 9: Resolve a Complete Wave and Document the Feature

**Files:**
- Modify: `servicios/combate.py`
- Modify: `tests/test_combate.py`
- Modify: `documentacion/reglas_definidas.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: all Tasks 1–8.
- Produces: `resolver_oleada(aventureros, enemigos, generador) -> ResultadoOleada` as the public entry point for the future expedition service.

- [ ] **Step 1: Write failing victory tests**

Use small temporary states to assert victory, exact round count, mutated final
life, defeated IDs, XP and money. Assert each enemy reward is counted once.

- [ ] **Step 2: Write failing defeat tests**

Assert defeat when the last living adventurer dies, with no further turns.
The result may contain provisional rewards from enemies killed earlier; the
future expedition service, not this function, will decide whether to discard
them.

- [ ] **Step 3: Write failing limit and boundary tests**

Assert `"limite_de_rondas"` after completing thirty rounds with both factions
alive. Add a separate test where the last enemy dies during round 30 and assert
`"victoria"`.

- [ ] **Step 4: Write a deterministic catalog integration test**

Create the initial three adventurers and wave 1 from the real catalogs, run
with a fixed seed and assert the result is one of the three valid outcomes,
rounds remain within 1–30, every life is bounded and rewards match only the
defeated enemies. Do not pin the complete random transcript.

- [ ] **Step 5: Run focused tests and verify failure**

Run: `python -m unittest tests.test_combate.PruebasResolucionOleada -v`

Expected: FAIL because `resolver_oleada()` does not exist.

- [ ] **Step 6: Implement the wave coordinator**

```python
def resolver_oleada(
    aventureros: list[AventureroCombate],
    enemigos: list[EnemigoCombate],
    generador: Random,
) -> ResultadoOleada:
    ...
```

Validate inputs first, calculate turn order once, execute rounds from 1 through
30, stop immediately on victory or defeat, sum rewards from the unique defeated
IDs and return no attack log.

- [ ] **Step 7: Run combat and full tests**

Run: `python -m unittest tests.test_combate -v`

Expected: PASS.

Run: `python -m unittest discover -s tests -v`

Expected: all tests PASS.

- [ ] **Step 8: Update project documentation**

In `documentacion/reglas_definidas.md`, replace the 150% critical rule with
200%, document the 90% cap, defense formula, one-roll outcomes, neutral enemy
attacks, manual waves and revised wave 6.

In `README.md`, move enemies, first dungeon catalog and basic combat from
pending to implemented. Keep expeditions, abilities and Tkinter explicitly
pending. Mention the exact test command.

- [ ] **Step 9: Verify formatting and final suite**

Run: `git diff --check`

Expected: no output and exit code 0.

Run: `python -m unittest discover -s tests -v`

Expected: all tests PASS.

- [ ] **Step 10: Commit**

```bash
git add servicios/combate.py tests/test_combate.py \
    documentacion/reglas_definidas.md README.md
git commit -m "feat: resolver oleadas de combate básico"
```

## Suggested Execution Tranches

To keep each working session compact while respecting task review boundaries:

1. **Tramo 1 — Foundations:** Tasks 1 and 2.
2. **Tramo 2 — Content catalogs:** Tasks 3 and 4.
3. **Tramo 3 — Temporary states and randomness:** Tasks 5 and 6.
4. **Tramo 4 — Attack and round engine:** Tasks 7 and 8.
5. **Tramo 5 — Complete wave and documentation:** Task 9 plus whole-branch verification.

Each tranche ends with a clean commit set and the full test suite passing.

## Separate Follow-up

The PowerPoint presentation is not stored in this Git repository. After the
combat branch is implemented and verified, update its combat slide in a
separate artifact task so it states 5% base critical chance, 90% maximum
critical chance and 200% critical damage. This follow-up does not block the
code or tests in this plan.
