# Expediciones a la Mazmorra de los Limos — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Conectar selección, combate, recompensas, iglesia, mercado y persistencia para jugar de principio a fin las diez oleadas de la Mazmorra de los Limos.

**Architecture:** La expedición se representa mediante un `EstadoExpedicion` temporal y explícito. `servicios/expediciones.py` resuelve transiciones y consecuencias de dominio, mientras `servicios/partidas.py` realiza el cierre transaccional sobre copias y persiste el resultado solamente al terminar.

**Tech Stack:** Python 3.11+, `TypedDict`, `Literal`, `random.Random`, `copy.deepcopy`, `pathlib.Path`, `unittest` y `unittest.mock`; sin dependencias externas.

**Spec:** `docs/superpowers/specs/2026-11-12-expediciones-mazmorra-limos-design.md`

## Global Constraints

- Mantener compatibilidad con Python 3.11 o superior y Pyright en modo `strict`.
- No agregar dependencias externas.
- No usar `input()`, `print()` ni Tkinter en los servicios de dominio.
- Recibir una instancia de `Random` en toda operación que tome decisiones aleatorias.
- Redondear dinero y experiencia hacia abajo mediante aritmética entera.
- No guardar `EstadoExpedicion` en los tres JSON persistentes.
- No modificar registros persistentes durante las oleadas.
- Aplicar las consecuencias de una expedición exactamente una vez.
- Guardar la partida solamente al cerrar la expedición.
- Mantener intactas las estructuras originales y el generador si el cierre no puede guardarse.
- Documentar todas las funciones públicas y anotar parámetros, retornos y colecciones.
- Ejecutar cada tramo mediante TDD y conservar todas las pruebas existentes.

## Review Focus

- Una definición de mazmorra válida pero distinta de `MAZMORRA_LIMOS` debe producir `MazmorraNoDisponibleError`, no confundirse con un ID inexistente. Se fija en el Tramo 1.
- Una llamada inválida a continuar, retirar o resolver debe dejar byte por byte el mismo estado temporal. Se fija en el Tramo 2.
- Un grupo totalmente derrotado debe perder todo el dinero y la experiencia, aunque haya vencido enemigos en la última oleada. Se fija en el Tramo 3.
- Un `OSError` durante el segundo o tercer reemplazo debe restaurar los tres JSON anteriores y no dejar temporales ni respaldos. Se fija en el Tramo 4.
- Si el guardado del cierre falla, el reintento debe producir exactamente el mismo mercado y aplicar recompensas una sola vez. Se fija en el Tramo 5.

---

## Mapa de archivos

- `configuracion.py`: bonificación monetaria por oleada y premio por completar la primera mazmorra.
- `modelos/expediciones.py`: estado temporal, resultados de consecuencias y resumen final.
- `servicios/expediciones.py`: inicio, avance, decisiones, recompensas, consecuencias y derrota definitiva.
- `servicios/persistencia.py`: restauración de los tres JSON ante errores controlados de reemplazo.
- `servicios/partidas.py`: cierre coordinado sobre copias, renovación, guardado y publicación del resultado.
- `tests/test_modelos_expediciones.py`: contratos de las nuevas estructuras tipadas.
- `tests/test_expediciones.py`: flujo temporal y consecuencias de dominio.
- `tests/test_persistencia.py`: reemplazo con restauración.
- `tests/test_partidas.py`: cierre transaccional, reintento e integración completa.
- `documentacion/reglas_definidas.md`: reglas efectivamente implementadas.
- `README.md`: estado del proyecto y forma de ejecutar las pruebas.

## Tramo 1: Modelo temporal e inicio de una expedición

**Files:**
- Create: `modelos/expediciones.py`
- Create: `tests/test_modelos_expediciones.py`
- Modify: `servicios/expediciones.py`
- Create: `tests/test_expediciones.py`

**Interfaces:**
- Consumes: `seleccionar_grupo(...)`, `crear_aventurero_combate(...)`, `CATALOGO_MAZMORRAS`, `CATALOGO_PLANTILLAS`, `ResultadoExpedicion` y `DificultadMazmorra`.
- Produces: `EstadoFlujoExpedicion`, `EstadoExpedicion`, `ResultadoConsecuenciasExpedicion`, `ResumenCierreExpedicion`, las excepciones del flujo e `iniciar_expedicion(...)` para los tramos siguientes.

- [ ] **Step 1: Write failing type-contract tests**

Crear `tests/test_modelos_expediciones.py` y comprobar mediante `typing.get_args()` los cuatro valores de `EstadoFlujoExpedicion`. Construir estados anotados con estos campos exactos:

```python
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


class ResultadoConsecuenciasExpedicion(TypedDict):
    dinero_entregado: int
    experiencia_por_superviviente: int
    supervivientes_ids: list[str]
    muertos_ids: list[str]
    mazmorra_completada: bool


class ResumenCierreExpedicion(ResultadoConsecuenciasExpedicion):
    resultado: ResultadoExpedicion
    estado_partida: EstadoPartida
```

- [ ] **Step 2: Run the model tests and confirm imports fail**

Run: `python -m unittest tests.test_modelos_expediciones -v`

Expected: FAIL because `modelos/expediciones.py` does not exist.

- [ ] **Step 3: Implement the typed expedition models**

Crear `modelos/expediciones.py` con los contratos anteriores y:

```python
EstadoFlujoExpedicion: TypeAlias = Literal[
    "lista_para_oleada",
    "esperando_decision",
    "finalizada",
    "consecuencias_aplicadas",
]
```

- [ ] **Step 4: Run the model tests**

Run: `python -m unittest tests.test_modelos_expediciones -v`

Expected: PASS.

- [ ] **Step 5: Write failing initiation tests**

En `tests/test_expediciones.py`, agregar pruebas que demuestren que:

- una partida `en_curso` inicia `MAZMORRA_LIMOS` en oleada 1, con pozos en cero y sin modificar los registros persistentes;
- se admiten grupos de uno, tres y el máximo correspondiente al nivel del clan;
- los estados de combate son objetos independientes de `datos_activos`;
- se preserva el orden de los IDs elegidos;
- se reutilizan los errores existentes para grupo vacío, repetido, muerto, ausente o por encima del máximo;
- una partida en `victoria` o `derrota` produce `EstadoExpedicionInvalidoError`;
- un ID de mazmorra inexistente produce `MazmorraNoEncontradaError`;
- una mazmorra conocida distinta de la primera produce `MazmorraNoDisponibleError`.

- [ ] **Step 6: Run the initiation tests and confirm they fail**

Run: `python -m unittest tests.test_expediciones.PruebasInicioExpedicion -v`

Expected: FAIL because the public operation and errors do not exist.

- [ ] **Step 7: Implement initiation and errors**

En `servicios/expediciones.py`, definir:

```python
class MazmorraNoEncontradaError(ValueError): ...
class MazmorraNoDisponibleError(ValueError): ...
class EstadoExpedicionInvalidoError(ValueError): ...
class TransicionExpedicionInvalidaError(ValueError): ...
class ExpedicionYaAplicadaError(ValueError): ...


def iniciar_expedicion(
    estado_clan: EstadoClan,
    datos_activos: list[AventureroActivo],
    aventureros_ids: list[str],
    mazmorra_id: str,
) -> EstadoExpedicion:
    ...
```

Validar primero el estado de la partida, luego existencia y disponibilidad de la mazmorra, y finalmente el grupo. Crear cada `AventureroCombate` con el catálogo real y devolver un estado nuevo sin mutar entradas.

- [ ] **Step 8: Run focused and regression tests**

Run: `python -m unittest tests.test_modelos_expediciones tests.test_expediciones.PruebasInicioExpedicion -v`

Expected: PASS.

Run: `python -m unittest discover -s tests -v`

Expected: all tests PASS.

- [ ] **Step 9: Commit Tramo 1**

```bash
git add modelos/expediciones.py servicios/expediciones.py tests/test_modelos_expediciones.py tests/test_expediciones.py
git commit -m "feat: iniciar expediciones tipadas"
```

## Tramo 2: Resolución y decisiones entre oleadas

**Files:**
- Modify: `configuracion.py`
- Modify: `servicios/expediciones.py`
- Modify: `tests/test_expediciones.py`

**Interfaces:**
- Consumes: `EstadoExpedicion` del Tramo 1, `crear_enemigos_oleada(...)` y `resolver_oleada(...)`.
- Produces: `calcular_dinero_oleada(...)`, `resolver_siguiente_oleada(...)`, `continuar_expedicion(...)` y `retirar_expedicion(...)`.

- [ ] **Step 1: Write failing reward and transition tests**

Agregar pruebas para:

- `calcular_dinero_oleada(101, 2) == 111` y rechazo de dinero negativo u oleadas fuera de 1 a 10;
- victoria en oleadas 1 a 9: acumula XP sin multiplicador, dinero con `10% × (n - 1)`, incrementa ambos contadores y espera decisión;
- `ultima_oleada` es una copia profunda que no cambia al mutar la lista que continúa;
- `continuar_expedicion()` pasa únicamente de `esperando_decision` a `lista_para_oleada`;
- `retirar_expedicion()` pasa únicamente de `esperando_decision` a `finalizada` con resultado `retirada`;
- derrota finaliza como `derrota_total` y conserva recompensas provisionales solo en los pozos temporales;
- límite de rondas finaliza como `limite_de_rondas` y acumula recompensas parciales;
- victoria en la oleada 10 deja `proxima_oleada == 11`, `oleadas_superadas == 10`, agrega 100 monedas y finaliza como `mazmorra_completada`;
- derrota o límite en la oleada 10 no agrega el premio de 100;
- resolver, continuar o retirarse desde un estado incorrecto lanza `TransicionExpedicionInvalidaError` sin modificar el estado.

- [ ] **Step 2: Run the focused tests and confirm they fail**

Run: `python -m unittest tests.test_expediciones.PruebasRecompensas tests.test_expediciones.PruebasAvanceExpedicion -v`

Expected: FAIL because reward and transition operations do not exist.

- [ ] **Step 3: Add named expedition constants**

En `configuracion.py`, agregar:

```python
BONIFICACION_DINERO_POR_OLEADA: int = 10
BONIFICACION_COMPLETAR_MAZMORRA_LIMOS: int = 100
```

- [ ] **Step 4: Implement reward and transition operations**

En `servicios/expediciones.py`, definir:

```python
def calcular_dinero_oleada(dinero_base: int, numero_oleada: int) -> int: ...

def resolver_siguiente_oleada(
    expedicion: EstadoExpedicion,
    generador: Random,
) -> ResultadoOleada: ...

def continuar_expedicion(expedicion: EstadoExpedicion) -> None: ...

def retirar_expedicion(expedicion: EstadoExpedicion) -> None: ...
```

Validar todas las precondiciones antes de mutar. Aplicar la fórmula `dinero_base * (100 + 10 * (numero_oleada - 1)) // 100`; conservar los mismos estados de aventureros entre oleadas y almacenar `deepcopy(resultado)` en `ultima_oleada`.

- [ ] **Step 5: Run focused and full-flow service tests**

Run: `python -m unittest tests.test_expediciones.PruebasRecompensas tests.test_expediciones.PruebasAvanceExpedicion -v`

Expected: PASS.

Agregar una prueba con `resolver_oleada` controlado que recorra diez definiciones reales y compruebe la secuencia 1–10, los 416 de enemigos y los 516 finales.

Run: `python -m unittest tests.test_expediciones -v`

Expected: PASS.

- [ ] **Step 6: Run regression and static analysis**

Run: `python -m unittest discover -s tests -v`

Expected: all tests PASS.

Run: `pyright`

Expected: 0 errors.

- [ ] **Step 7: Commit Tramo 2**

```bash
git add configuracion.py servicios/expediciones.py tests/test_expediciones.py
git commit -m "feat: resolver avance de expediciones"
```

## Tramo 3: Consecuencias, progresión y derrota definitiva

**Files:**
- Modify: `servicios/expediciones.py`
- Modify: `tests/test_expediciones.py`

**Interfaces:**
- Consumes: expedición `finalizada`, `aplicar_experiencia(...)`, `calcular_coste_resurreccion(...)` y las ofertas del `EstadoClan`.
- Produces: `aplicar_consecuencias_expedicion(...)` y `evaluar_derrota_definitiva(...)` para el coordinador del Tramo 5.

- [ ] **Step 1: Write failing survivor-consequence tests**

Probar que `aplicar_consecuencias_expedicion(...)`:

- entrega dinero solamente si regresa al menos un superviviente;
- divide el pozo de XP con `//`, descarta el sobrante y aplica varios ascensos;
- marca muertos participantes como `muerto` sin sacarlos de `datos_activos`;
- deja intactos a los miembros que no participaron;
- marca `mazmorra_1` solamente para `mazmorra_completada`;
- permite repetir la bonificación y mantiene la bandera en `True`;
- no persiste la vida temporal de los supervivientes;
- cambia el flujo de la expedición recibida a `consecuencias_aplicadas` solamente después de aplicar correctamente todos los cambios en memoria;
- devuelve IDs en el orden original del grupo y un `ResultadoConsecuenciasExpedicion` exacto.

- [ ] **Step 2: Write failing total-defeat tests**

Probar que, si no regresa nadie:

- dinero y experiencia entregados son cero;
- cada participante sale de `datos_activos` y entra al final de `datos_eliminados` como `muerto` con motivo `caido_no_recuperado`;
- se conserva el orden del grupo;
- no se modifica a quienes no participaron;
- los pozos temporales no se entregan aunque contengan recompensas parciales.

También comprobar que un estado no finalizado produce `EstadoExpedicionInvalidoError`, y `consecuencias_aplicadas` produce prioritariamente `ExpedicionYaAplicadaError`, sin mutaciones parciales.

- [ ] **Step 3: Run consequence tests and confirm they fail**

Run: `python -m unittest tests.test_expediciones.PruebasConsecuenciasExpedicion -v`

Expected: FAIL because consequence application does not exist.

- [ ] **Step 4: Implement consequence application**

Definir:

```python
def aplicar_consecuencias_expedicion(
    expedicion: EstadoExpedicion,
    estado_clan: EstadoClan,
    datos_activos: list[AventureroActivo],
    datos_eliminados: list[AventureroEliminado],
) -> ResultadoConsecuenciasExpedicion:
    ...
```

Validar antes de mutar que todos los IDs elegidos sigan activos y con la misma `plantilla_id`. Usar `aplicar_experiencia()` por superviviente y construir nuevos registros históricos para la derrota total. Esta operación no renueva mercado ni guarda archivos; al completar correctamente sus cambios en memoria marca **la expedición recibida** como `consecuencias_aplicadas`. El Tramo 5 la ejecutará sobre una copia para no publicar ese cambio antes del guardado.

- [ ] **Step 5: Run consequence tests**

Run: `python -m unittest tests.test_expediciones.PruebasConsecuenciasExpedicion -v`

Expected: PASS.

- [ ] **Step 6: Write failing definitive-defeat tests**

Cubrir estas cuatro rutas de `evaluar_derrota_definitiva(...)`:

1. continúa si queda al menos un integrante vivo;
2. continúa si el dinero alcanza para resucitar al menos un muerto recuperado;
3. continúa si existe una oferta pagable y `contrataciones_restantes > 0`, aun con el cupo lleno de muertos porque se pueden enterrar;
4. cambia a `derrota` cuando ninguna alternativa es posible.

Agregar fronteras de dinero exactamente igual al coste, mercado vacío, contrataciones en cero y oferta más barata inalcanzable.

- [ ] **Step 7: Implement definitive-defeat evaluation**

Definir:

```python
def evaluar_derrota_definitiva(
    estado_clan: EstadoClan,
    datos_activos: list[AventureroActivo],
) -> None:
    ...
```

No revivir, enterrar ni contratar automáticamente; solo mantener `en_curso` o cambiarlo a `derrota`.

- [ ] **Step 8: Run focused, regression and static checks**

Run: `python -m unittest tests.test_expediciones -v`

Expected: PASS.

Run: `python -m unittest discover -s tests -v && pyright`

Expected: all tests PASS and 0 type errors.

- [ ] **Step 9: Commit Tramo 3**

```bash
git add servicios/expediciones.py tests/test_expediciones.py
git commit -m "feat: aplicar consecuencias de expedición"
```

## Tramo 4: Restauración segura de los tres JSON

**Files:**
- Modify: `servicios/persistencia.py`
- Modify: `tests/test_persistencia.py`

**Interfaces:**
- Consumes: `guardar_partida(...)` existente.
- Produces: la misma interfaz pública, reforzada para restaurar el conjunto previo ante `OSError` controlado.

- [ ] **Step 1: Write failing rollback tests**

Con un directorio que ya contiene una partida válida, simular por separado errores durante el primer, segundo y tercer `Path.replace()`. En cada caso comprobar:

- `guardar_partida()` lanza `ErrorPersistencia`;
- los tres JSON conservan exactamente sus bytes anteriores;
- `cargar_partida()` devuelve la partida anterior;
- no quedan archivos `*.tmp` ni `*.bak`.

Agregar el caso de un directorio nuevo: ante un reemplazo fallido no debe quedar una partida parcial.

- [ ] **Step 2: Run rollback tests and confirm the second/third replacement fails the guarantee**

Run: `python -m unittest tests.test_persistencia.PruebasGuardadoPersistencia -v`

Expected: FAIL because the current implementation can dejar archivos mezclados tras un reemplazo parcial.

- [ ] **Step 3: Implement controlled rollback**

Mantener `guardar_partida(...)` sin cambiar su firma. Antes de reemplazar, crear respaldos de los destinos existentes; tras escribir los tres temporales, reemplazar de forma secuencial. Ante `OSError`, restaurar cada archivo previo o eliminar cada destino que no existía originalmente. Limpiar temporales y respaldos tanto en éxito como en error.

No afirmar protección ante caída abrupta del proceso o corte de energía: la garantía corresponde solamente a excepciones controladas informadas al proceso.

- [ ] **Step 4: Run persistence and full regression tests**

Run: `python -m unittest tests.test_persistencia -v`

Expected: PASS.

Run: `python -m unittest discover -s tests -v && pyright`

Expected: all tests PASS and 0 type errors.

- [ ] **Step 5: Commit Tramo 4**

```bash
git add servicios/persistencia.py tests/test_persistencia.py
git commit -m "fix: restaurar partida ante guardado incompleto"
```

## Tramo 5: Cierre transaccional e integración completa

**Files:**
- Modify: `servicios/partidas.py`
- Modify: `tests/test_partidas.py`
- Modify: `documentacion/reglas_definidas.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: consecuencias y derrota del Tramo 3, persistencia reforzada del Tramo 4 y `renovar_mercado(...)`.
- Produces: `cerrar_expedicion_y_guardar(...) -> ResumenCierreExpedicion`, punto único de cierre para la futura interfaz.

- [ ] **Step 1: Write failing successful-closure tests**

Agregar pruebas que verifiquen:

- cierre de retirada, límite de rondas, mazmorra completada y derrota total;
- aplicación de consecuencias sobre copias, renovación del mercado, evaluación de derrota, guardado y publicación en las estructuras originales;
- `estado_flujo == "consecuencias_aplicadas"` únicamente después del guardado exitoso;
- resumen exacto con resultado, dinero entregado, XP individual, IDs supervivientes/muertos, bandera de mazmorra y estado de partida;
- un segundo cierre lanza `ExpedicionYaAplicadaError` sin cambios;
- discrepancias de ID o plantilla se rechazan antes de renovar o guardar.

- [ ] **Step 2: Run coordinator tests and confirm they fail**

Run: `python -m unittest tests.test_partidas.PruebasCierreExpedicion -v`

Expected: FAIL because the coordinator does not exist.

- [ ] **Step 3: Implement transactional closure**

En `servicios/partidas.py`, definir:

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

Secuencia obligatoria:

1. validar estado de la expedición e IDs/plantillas;
2. guardar `generador.getstate()`;
3. crear copias profundas de la expedición, del clan y de las dos listas;
4. aplicar consecuencias sobre las copias, incluida la transición de la copia de la expedición;
5. renovar mercado y evaluar derrota sobre las copias;
6. guardar las copias;
7. solo tras el éxito, reemplazar por corte completo (`[:]`/`clear()` + `update()`) las estructuras originales, marcar `consecuencias_aplicadas` y devolver el resumen;
8. ante cualquier excepción anterior a la publicación, restaurar `generador.setstate(...)` y propagar el error sin tocar originales ni expedición.

- [ ] **Step 4: Write and run failed-save retry tests**

Simular que `guardar_partida()` falla la primera vez y funciona la segunda. Comprobar tras el primer intento:

- mismo dinero, niveles, experiencia, listas, mercado y flujo originales;
- mismo estado interno del generador;
- ningún resumen publicado.

En el segundo intento, comprobar que el mercado coincide con el que habría producido un cierre exitoso directo, y que dinero/XP se aplicaron una sola vez.

Run: `python -m unittest tests.test_partidas.PruebasCierreExpedicion -v`

Expected: PASS.

- [ ] **Step 5: Add the complete Dungeon 1 integration test**

Con catálogos reales y el motor de oleadas controlado determinísticamente, recorrer las diez oleadas mediante la API pública, cerrar y recargar desde un directorio temporal. Comprobar:

- secuencia exacta de oleadas 1 a 10;
- `resultado == "mazmorra_completada"`;
- 516 monedas entregadas para la composición completa aprobada;
- XP total repartida solo entre supervivientes;
- `mazmorra_1 is True`;
- mercado renovado y partida recargada idéntica al estado publicado;
- no existe ningún archivo de expedición temporal en JSON.

- [ ] **Step 6: Update documentation**

En `documentacion/reglas_definidas.md`, registrar flujo, premios, pérdida del botín, iglesia, límite y cierre. En `README.md`, marcar expediciones de la primera mazmorra como implementadas y mantener los comandos:

```bash
python -m unittest discover -s tests -v
pyright
```

- [ ] **Step 7: Run final verification**

Run: `python -m unittest discover -s tests -v`

Expected: all tests PASS.

Run: `pyright`

Expected: 0 errors.

Run: `git diff --check`

Expected: no output.

- [ ] **Step 8: Commit Tramo 5**

```bash
git add servicios/partidas.py tests/test_partidas.py documentacion/reglas_definidas.md README.md
git commit -m "feat: cerrar expediciones de la primera mazmorra"
```

## Resultado verificable de cada tramo

| Tramo | Resultado independiente |
|---:|---|
| 1 | Se puede crear una expedición válida sin alterar la partida. |
| 2 | Se pueden resolver las diez oleadas, continuar o retirarse y acumular pozos temporales. |
| 3 | Se pueden aplicar progresión, muertes, iglesia y derrota definitiva completamente en memoria. |
| 4 | Los tres JSON se restauran ante fallos controlados de guardado. |
| 5 | Se puede cerrar, guardar y recargar una expedición completa exactamente una vez. |
