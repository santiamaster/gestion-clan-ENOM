# Creación de partida nueva Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear, validar y guardar una partida inicial con un clan nombrado por el jugador y tres aventureros iniciales con nombres aleatorios.

**Architecture:** Los catálogos proporcionan nombres por sexo, los servicios de clan y aventureros construyen estructuras puras y `servicios/partidas.py` coordina la detección de una partida previa y el guardado. La interfaz futura consumirá una única función pública y conservará fuera de estos servicios la confirmación visual.

**Tech Stack:** Python 3.11 o superior, biblioteca estándar (`random`, `pathlib`, `unittest`), TypedDict, Pyright estricto.

**Spec:** `docs/superpowers/specs/2026-11-06-creacion-partida-nueva-design.md`

## Global Constraints

- Python fuertemente anotado y compatible con Pyright en modo estricto.
- Sin dependencias externas.
- Los datos deben satisfacer los validadores actuales antes de guardarse.
- Los archivos incompletos o inválidos deben detener la operación y conservarse.
- El azar debe poder controlarse en las pruebas.
- Las plantillas iniciales son, en este orden: Soldado, Arquero y Hechicero.
- Los identificadores iniciales son `AV-0001`, `AV-0002` y `AV-0003`.

## Review Focus

- Un nombre formado solo por espacios debe rechazarse sin crear archivos: cubierto en la tarea 2.
- Los nombres aleatorios deben pertenecer al catálogo correspondiente al sexo de la plantilla: cubierto en las tareas 1 y 2.
- Una partida válida previa no debe cambiar si falta la autorización de sobrescritura: cubierto en la tarea 3.
- Una partida incompleta o inválida no debe reemplazarse ni siquiera al solicitar sobrescritura: cubierto en la tarea 3.
- Los tres identificadores y `siguiente_id_aventurero` deben quedar sincronizados: cubierto en las tareas 2 y 3.

---

## Estructura de archivos

- Modificar `catalogos/nombres.py`: catálogos separados por sexo y selección controlable.
- Modificar `servicios/aventureros.py`: formato de identificadores y construcción de la terna inicial.
- Modificar `servicios/clan.py`: validación del nombre y construcción del estado inicial.
- Crear `servicios/partidas.py`: coordinación, protección de sobrescritura y guardado.
- Crear `tests/test_nombres.py`: integridad y selección de nombres.
- Crear `tests/test_partidas.py`: construcción del clan, aventureros y persistencia de una partida nueva.

### Task 1: Catálogo y selección de nombres

**Files:**
- Modify: `catalogos/nombres.py`
- Create: `tests/test_nombres.py`

**Interfaces:**
- Consumes: `Sexo` de `modelos.tipos`.
- Produces: `NOMBRES_MASCULINOS: tuple[str, ...]`, `NOMBRES_FEMENINOS: tuple[str, ...]` y `elegir_nombre(sexo: Sexo, generador: Random) -> str`.

- [ ] **Step 1: Escribir las pruebas fallidas del catálogo**

Crear `PruebasCatalogoNombres` con pruebas que afirmen:

```python
self.assertEqual(len(NOMBRES_MASCULINOS) + len(NOMBRES_FEMENINOS), 100)
self.assertTrue(all(nombre.strip() == nombre and nombre for nombre in nombres))
self.assertEqual(len(set(nombres)), len(nombres))
```

Agregar una prueba con `Random(7)` que compruebe que `elegir_nombre("masculino", generador)` pertenece al catálogo masculino y la equivalente para `"femenino"`.

- [ ] **Step 2: Ejecutar las pruebas y comprobar que fallan**

Run: `python -m unittest tests.test_nombres -v`

Expected: FAIL por importaciones todavía inexistentes.

- [ ] **Step 3: Implementar el catálogo y el selector**

Definir 50 nombres masculinos y 50 femeninos, no vacíos y sin duplicados dentro del conjunto total. Implementar:

```python
def elegir_nombre(sexo: Sexo, generador: Random) -> str:
    ...
```

Seleccionar con `generador.choice()` desde el catálogo correspondiente.

- [ ] **Step 4: Ejecutar las pruebas del catálogo**

Run: `python -m unittest tests.test_nombres -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add catalogos/nombres.py tests/test_nombres.py
git commit -m "feat: agregar catálogo de nombres de aventureros"
```

### Task 2: Construcción del clan y de los aventureros iniciales

**Files:**
- Modify: `servicios/aventureros.py`
- Modify: `servicios/clan.py`
- Create: `tests/test_partidas.py`

**Interfaces:**
- Consumes: `CATALOGO_PLANTILLAS`, `PLANTILLAS_INICIALES` y `elegir_nombre(sexo, generador)`.
- Produces: `NombreClanInvalidoError`, `crear_estado_inicial_clan(nombre_clan: str) -> EstadoClan`, `formatear_id_aventurero(numero: int) -> str` y `crear_aventureros_iniciales(generador: Random) -> list[AventureroActivo]`.

- [ ] **Step 1: Escribir las pruebas fallidas de construcción**

Crear pruebas que verifiquen:

- `crear_estado_inicial_clan("  Guardianes del Alba  ")` guarda `"Guardianes del Alba"`.
- El estado contiene nivel 1, dinero 0, siguiente ID 4, mercado disponible, partida en curso, ofertas vacías y cinco banderas `False`.
- Un nombre vacío o formado por espacios lanza `NombreClanInvalidoError`.
- `formatear_id_aventurero(1)` devuelve `"AV-0001"` y un número menor que 1 lanza `ValueError`.
- `crear_aventureros_iniciales(Random(7))` devuelve exactamente tres registros con IDs consecutivos, las tres plantillas acordadas, nivel 1, experiencia 0 y estado vivo.
- Cada nombre generado pertenece al catálogo compatible con el sexo de su plantilla.

- [ ] **Step 2: Ejecutar las pruebas y comprobar que fallan**

Run: `python -m unittest tests.test_partidas -v`

Expected: FAIL por símbolos todavía inexistentes.

- [ ] **Step 3: Implementar el estado inicial del clan**

En `servicios/clan.py`, definir:

```python
class NombreClanInvalidoError(ValueError):
    ...

def crear_estado_inicial_clan(nombre_clan: str) -> EstadoClan:
    ...
```

Normalizar con `strip()`, rechazar el resultado vacío y construir los valores exactos del diseño.

- [ ] **Step 4: Implementar la creación de aventureros**

En `servicios/aventureros.py`, definir:

```python
def formatear_id_aventurero(numero: int) -> str:
    ...

def crear_aventureros_iniciales(
    generador: Random,
) -> list[AventureroActivo]:
    ...
```

Recorrer `PLANTILLAS_INICIALES` en su orden, resolver cada plantilla desde `CATALOGO_PLANTILLAS` y asignar IDs comenzando en 1.

- [ ] **Step 5: Ejecutar las pruebas de construcción**

Run: `python -m unittest tests.test_partidas -v`

Expected: Las pruebas de construcción pasan; las pruebas de coordinación de la tarea 3 todavía no existen.

- [ ] **Step 6: Commit**

```bash
git add servicios/clan.py servicios/aventureros.py tests/test_partidas.py
git commit -m "feat: construir estado inicial de partida"
```

### Task 3: Coordinación, protección y guardado

**Files:**
- Create: `servicios/partidas.py`
- Modify: `tests/test_partidas.py`

**Interfaces:**
- Consumes: `crear_estado_inicial_clan(nombre_clan)`, `crear_aventureros_iniciales(generador)`, `existe_partida_guardada(directorio)` y `guardar_partida(...)`.
- Produces: `PartidaExistenteError` y `crear_nueva_partida(nombre_clan: str, sobrescribir: bool = False, directorio: Path = DIRECTORIO_PARTIDA, generador: Random | None = None) -> tuple[EstadoClan, list[AventureroActivo], list[AventureroEliminado]]`.

- [ ] **Step 1: Escribir las pruebas fallidas de coordinación**

Añadir pruebas con `TemporaryDirectory` que comprueben:

- Sin archivos anteriores, la función guarda tres JSON y `cargar_partida()` devuelve exactamente la tupla retornada.
- Sin proporcionar un generador, se crean tres nombres válidos.
- Con una partida válida previa y `sobrescribir=False`, se lanza `PartidaExistenteError` y los archivos conservan su contenido.
- Con `sobrescribir=True`, una partida válida se reemplaza por el nuevo clan.
- Con un único JSON previo, se propaga `PartidaIncompletaError` incluso con `sobrescribir=True`, y el archivo queda intacto.
- Con tres archivos y JSON inválido, se propaga `PartidaInvalidaError` incluso con `sobrescribir=True`, y los archivos quedan intactos.

- [ ] **Step 2: Ejecutar las pruebas y comprobar que fallan**

Run: `python -m unittest tests.test_partidas -v`

Expected: FAIL porque `servicios.partidas` todavía no existe.

- [ ] **Step 3: Implementar el coordinador**

Crear en `servicios/partidas.py`:

```python
class PartidaExistenteError(ErrorPersistencia):
    ...

def crear_nueva_partida(
    nombre_clan: str,
    sobrescribir: bool = False,
    directorio: Path = DIRECTORIO_PARTIDA,
    generador: Random | None = None,
) -> tuple[
    EstadoClan,
    list[AventureroActivo],
    list[AventureroEliminado],
]:
    ...
```

Siempre llamar primero a `existe_partida_guardada()`: sus errores de integridad deben propagarse antes de cualquier escritura. Si devuelve `True` y no hay autorización, lanzar `PartidaExistenteError`. Construir con `generador if generador is not None else Random()`, usar una lista eliminada vacía, guardar y devolver las mismas estructuras.

- [ ] **Step 4: Ejecutar las pruebas de partida**

Run: `python -m unittest tests.test_partidas -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add servicios/partidas.py tests/test_partidas.py
git commit -m "feat: crear y guardar una partida nueva"
```

### Task 4: Verificación integral

**Files:**
- Modify only if verification reveals a defect in files from Tasks 1–3.

**Interfaces:**
- Consumes: todos los resultados de las tareas anteriores.
- Produces: bloque completo verificado.

- [ ] **Step 1: Ejecutar toda la suite**

Run: `python -m unittest discover -s tests -v`

Expected: Todos los tests pasan.

- [ ] **Step 2: Ejecutar el análisis estático**

Run: `pyright`

Expected: `0 errors, 0 warnings, 0 informations`.

- [ ] **Step 3: Revisar el diff**

Run: `git diff HEAD~3 --check`

Expected: sin errores de espacios ni marcadores de conflicto.

- [ ] **Step 4: Confirmar el estado del repositorio**

Run: `git status --short`

Expected: salida vacía.
