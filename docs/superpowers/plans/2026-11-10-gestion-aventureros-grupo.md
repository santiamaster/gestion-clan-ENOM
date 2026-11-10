# Gestión de aventureros y formación del grupo — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Centralizar la búsqueda de integrantes, permitir expulsiones seguras y validar grupos temporales de uno a siete aventureros vivos según el nivel del clan.

**Architecture:** `servicios/aventureros.py` será la fuente única de búsqueda y gestión de integrantes activos. La iglesia delegará allí la localización general, mientras que la formación del grupo recibirá IDs temporales y devolverá referencias ordenadas a los registros vivos sin persistir ni mutar la partida.

**Tech Stack:** Python 3.11+, `TypedDict`, anotaciones compatibles con Pyright estricto, `unittest`, JSON y Tkinter desacoplados de los servicios.

**Spec:** `docs/superpowers/specs/2026-11-10-gestion-aventureros-grupo-design.md`

## Global Constraints

- Los servicios no dependen de Tkinter ni leen o guardan JSON directamente.
- Los IDs se normalizan con `strip().upper()`.
- Los muertos recuperados solo se retiran mediante la iglesia.
- No se puede expulsar al último aventurero vivo.
- La selección se representa con `list[str]` y no forma parte del estado persistente.
- El grupo admite desde un integrante hasta `min(nivel_clan + 2, 7)`.
- Toda operación fallida conserva sin cambios las estructuras recibidas.
- Los listados y selecciones devuelven listas nuevas; los registros seleccionados mantienen identidad con `datos_activos`.
- Las nuevas excepciones de dominio heredan de `ValueError`.

## Review Focus

- IDs equivalentes por espacios o mayúsculas deben localizar al mismo integrante y contarse como duplicados dentro de un grupo: Task 1 y Task 3.
- Un ID inexistente, un muerto usado donde se exige un vivo y un vivo usado en la iglesia deben conservar errores diferenciados: Task 1 y Task 2.
- Expulsar al último vivo, un muerto o un ID ausente no debe modificar ninguna de las dos listas: Task 2.
- Los límites de los niveles 1 y 5 deben aceptar exactamente 3 y 7 integrantes, y rechazar uno adicional: Task 3.
- La refactorización debe conservar la identidad pública de `AventureroNoEncontradoError` importada desde `servicios.iglesia`: Task 1.

---

## Estructura de archivos

- `servicios/aventureros.py`: búsqueda general, consulta de vivos, expulsión y selección del grupo.
- `servicios/iglesia.py`: reglas exclusivas de muertos; delega la búsqueda general.
- `configuracion.py`: tope global de siete integrantes por grupo.
- `tests/test_aventureros.py`: pruebas unitarias de búsqueda, expulsión y formación.
- `tests/test_iglesia.py`: regresión de la API pública de la iglesia.
- `README.md`: estado funcional del proyecto.
- `documentacion/reglas_definidas.md`: reglas de expulsión y progresión del grupo.
- `documentacion/estructura.md`: responsabilidades finales del servicio.

### Task 1: Centralizar normalización y búsqueda

**Files:**
- Create: `tests/test_aventureros.py`
- Modify: `servicios/aventureros.py`
- Modify: `servicios/iglesia.py`
- Modify: `tests/test_iglesia.py`

**Interfaces:**
- Consumes: `AventureroActivo` desde `modelos.tipos`.
- Produces: `AventureroNoEncontradoError`, `normalizar_id_aventurero()` y `buscar_aventurero_activo()` para Tasks 2 y 3 y para `servicios.iglesia`.

- [ ] **Step 1: Crear auxiliares tipados de prueba en `tests/test_aventureros.py`**

Definir `crear_aventurero(identificador: str, estado: EstadoAventurero = "vivo") -> AventureroActivo` con plantilla `PLANTILLA_SOLDADO`, nivel 1 y experiencia 0.

- [ ] **Step 2: Escribir pruebas fallidas de normalización y búsqueda general**

Agregar pruebas que exijan:

```python
normalizar_id_aventurero(" av-0001 ") == "AV-0001"
buscar_aventurero_activo(activos, " av-0001 ") is activos[0]
```

Un ID ausente debe producir `AventureroNoEncontradoError` sin modificar `activos`.

- [ ] **Step 3: Escribir una regresión de identidad pública en `tests/test_iglesia.py`**

Importar la excepción desde ambos módulos y comprobar:

```python
IglesiaAventureroNoEncontradoError is AventureroNoEncontradoError
```

Mantener las pruebas existentes que distinguen ID ausente de aventurero vivo.

- [ ] **Step 4: Ejecutar las pruebas y verificar que fallen**

Run: `python -m unittest tests.test_aventureros tests.test_iglesia -v`

Expected: FAIL por los símbolos nuevos todavía inexistentes.

- [ ] **Step 5: Implementar las interfaces generales en `servicios/aventureros.py`**

```python
class AventureroNoEncontradoError(ValueError):
    ...


def normalizar_id_aventurero(aventurero_id: str) -> str:
    ...


def buscar_aventurero_activo(
    datos_activos: list[AventureroActivo],
    aventurero_id: str,
) -> AventureroActivo:
    ...
```

La búsqueda devuelve el registro original y utiliza el ID normalizado en el mensaje de error.

- [ ] **Step 6: Adaptar `servicios/iglesia.py` sin cambiar su API**

Importar explícitamente `AventureroNoEncontradoError` y `buscar_aventurero_activo`. Eliminar la definición local de la excepción y hacer que `buscar_aventurero_muerto()` delegue la localización antes de validar el estado muerto.

- [ ] **Step 7: Ejecutar las pruebas focalizadas**

Run: `python -m unittest tests.test_aventureros tests.test_iglesia -v`

Expected: PASS, incluidas todas las regresiones de iglesia.

- [ ] **Step 8: Ejecutar la suite completa**

Run: `python -m unittest discover -s tests -q`

Expected: `OK` sin regresiones.

- [ ] **Step 9: Commit**

```bash
git add servicios/aventureros.py servicios/iglesia.py tests/test_aventureros.py tests/test_iglesia.py
git commit -m "refactor: centralizar búsqueda de aventureros"
```

### Task 2: Listar y expulsar aventureros vivos

**Files:**
- Modify: `servicios/aventureros.py`
- Modify: `tests/test_aventureros.py`

**Interfaces:**
- Consumes: `buscar_aventurero_activo(datos_activos, aventurero_id) -> AventureroActivo` de Task 1.
- Produces: `AventureroNoEstaVivoError`, `UltimoAventureroVivoError`, `listar_aventureros_vivos()`, `buscar_aventurero_vivo()` y `expulsar_aventurero()`.

- [ ] **Step 1: Escribir pruebas fallidas del listado y la búsqueda de vivos**

Comprobar que `listar_aventureros_vivos()`:

- conserva solo registros con estado `"vivo"`;
- mantiene el orden original;
- devuelve una lista distinta de `datos_activos`.

Comprobar que `buscar_aventurero_vivo()` devuelve el registro original y produce `AventureroNoEstaVivoError` para un muerto.

- [ ] **Step 2: Escribir pruebas fallidas de expulsión válida**

Con dos vivos y un registro histórico anterior, verificar que expulsar uno:

- lo elimina de `datos_activos`;
- agrega al final un registro independiente en `datos_eliminados`;
- conserva ID, nombre, plantilla, nivel, experiencia y estado `"vivo"`;
- fija `motivo_baja == "servicios_finalizados"`;
- no agrega `motivo_baja` al registro activo original.

- [ ] **Step 3: Escribir pruebas fallidas de atomicidad**

Usar `deepcopy()` para comprobar que ambas listas permanecen idénticas al intentar expulsar:

- un ID inexistente;
- un aventurero muerto;
- el único aventurero vivo, aunque existan muertos en el clan.

- [ ] **Step 4: Ejecutar las pruebas y verificar que fallen**

Run: `python -m unittest tests.test_aventureros -v`

Expected: FAIL por funciones y excepciones inexistentes.

- [ ] **Step 5: Implementar consulta de vivos en `servicios/aventureros.py`**

```python
class AventureroNoEstaVivoError(ValueError):
    ...


def listar_aventureros_vivos(
    datos_activos: list[AventureroActivo],
) -> list[AventureroActivo]:
    ...


def buscar_aventurero_vivo(
    datos_activos: list[AventureroActivo],
    aventurero_id: str,
) -> AventureroActivo:
    ...
```

- [ ] **Step 6: Implementar expulsión segura**

```python
class UltimoAventureroVivoError(ValueError):
    ...


def expulsar_aventurero(
    datos_activos: list[AventureroActivo],
    datos_eliminados: list[AventureroEliminado],
    aventurero_id: str,
) -> AventureroEliminado:
    ...
```

Buscar al vivo y contar los vivos antes de crear o agregar el registro. Solo después de validar todo, añadir el eliminado al final y retirar el activo.

- [ ] **Step 7: Ejecutar pruebas focalizadas y completas**

Run: `python -m unittest tests.test_aventureros -v`

Expected: PASS.

Run: `python -m unittest discover -s tests -q`

Expected: `OK` sin regresiones.

- [ ] **Step 8: Commit**

```bash
git add servicios/aventureros.py tests/test_aventureros.py
git commit -m "feat: gestionar expulsión de aventureros"
```

### Task 3: Validar la formación temporal del grupo

**Files:**
- Modify: `configuracion.py`
- Modify: `servicios/aventureros.py`
- Modify: `tests/test_aventureros.py`

**Interfaces:**
- Consumes: `normalizar_id_aventurero()` y `buscar_aventurero_vivo()` de Tasks 1 y 2; `NIVEL_MAXIMO_CLAN` de `configuracion.py`.
- Produces: `MAXIMO_INTEGRANTES_GRUPO`, errores de selección, `calcular_maximo_grupo()` y `seleccionar_grupo()` para el futuro servicio de expediciones.

- [ ] **Step 1: Escribir pruebas fallidas de la progresión del grupo**

Comprobar la tabla completa:

```python
esperados = {1: 3, 2: 4, 3: 5, 4: 6, 5: 7}
```

Los niveles `0` y `6` deben producir `ValueError`.

- [ ] **Step 2: Escribir pruebas fallidas de selecciones válidas**

Comprobar que:

- un grupo de un vivo es válido;
- los niveles 1 y 5 aceptan exactamente 3 y 7 vivos;
- el resultado conserva el orden de los IDs recibidos;
- cada elemento devuelto es el mismo objeto existente en `datos_activos`;
- ni `datos_activos` ni `aventureros_ids` se modifican.

- [ ] **Step 3: Escribir pruebas fallidas de límites y duplicados**

Comprobar que:

- una lista vacía produce `GrupoVacioError`;
- 4 integrantes en nivel 1 y 8 en nivel 5 producen `GrupoExcedeLimiteError`;
- `"AV-0001"` y `" av-0001 "` juntos producen `AventureroRepetidoEnGrupoError`.

Todos los casos deben conservar sin cambios la lista activa y la lista de IDs.

- [ ] **Step 4: Escribir pruebas fallidas de integrantes inválidos**

Un ID inexistente debe conservar `AventureroNoEncontradoError`; un ID muerto debe producir `AventureroNoEstaVivoError`. Verificar ausencia de mutaciones en ambos casos.

- [ ] **Step 5: Ejecutar las pruebas y verificar que fallen**

Run: `python -m unittest tests.test_aventureros -v`

Expected: FAIL por las interfaces de grupo inexistentes.

- [ ] **Step 6: Agregar el límite global en `configuracion.py`**

```python
MAXIMO_INTEGRANTES_GRUPO: int = 7
```

- [ ] **Step 7: Implementar cálculo y errores de grupo**

```python
class GrupoVacioError(ValueError):
    ...


class GrupoExcedeLimiteError(ValueError):
    ...


class AventureroRepetidoEnGrupoError(ValueError):
    ...


def calcular_maximo_grupo(nivel_clan: int) -> int:
    ...
```

Validar primero el intervalo `1..NIVEL_MAXIMO_CLAN` y devolver `min(nivel_clan + 2, MAXIMO_INTEGRANTES_GRUPO)`.

- [ ] **Step 8: Implementar selección sin mutaciones**

```python
def seleccionar_grupo(
    datos_activos: list[AventureroActivo],
    nivel_clan: int,
    aventureros_ids: list[str],
) -> list[AventureroActivo]:
    ...
```

Validar en este orden: nivel, grupo vacío, límite, duplicados normalizados y resolución de cada vivo. Construir una lista nueva en el orden recibido.

- [ ] **Step 9: Ejecutar pruebas focalizadas y completas**

Run: `python -m unittest tests.test_aventureros -v`

Expected: PASS.

Run: `python -m unittest discover -s tests -q`

Expected: `OK` sin regresiones.

- [ ] **Step 10: Commit**

```bash
git add configuracion.py servicios/aventureros.py tests/test_aventureros.py
git commit -m "feat: validar formación del grupo"
```

### Task 4: Documentar y verificar el bloque completo

**Files:**
- Modify: `README.md`
- Modify: `documentacion/reglas_definidas.md`
- Modify: `documentacion/estructura.md`

**Interfaces:**
- Consumes: API completa producida por Tasks 1–3.
- Produces: documentación de usuario y arquitectura alineada con el comportamiento probado.

- [ ] **Step 1: Actualizar `README.md`**

Agregar la gestión de integrantes y formación del grupo al estado implementado. Explicar brevemente la expulsión segura y la selección temporal por ID.

- [ ] **Step 2: Actualizar `documentacion/reglas_definidas.md`**

Documentar:

- búsqueda normalizada por ID;
- expulsión gratuita con `servicios_finalizados`;
- prohibición de expulsar al último vivo;
- progresión `3, 4, 5, 6, 7`;
- mínimo de un integrante;
- selección exclusiva de vivos, sin repetidos y sin persistencia.

- [ ] **Step 3: Actualizar `documentacion/estructura.md`**

Describir que `servicios/aventureros.py` centraliza creación, búsqueda, listado, expulsión y formación temporal del grupo.

- [ ] **Step 4: Ejecutar la verificación integral**

Run: `python -m unittest discover -s tests -v`

Expected: todas las pruebas en `OK`.

Run: `python -m compileall -q catalogos modelos servicios tests`

Expected: exit code `0`.

Run: `git diff --check`

Expected: sin salida.

- [ ] **Step 5: Revisar los cinco casos de Review Focus**

Confirmar mediante las pruebas de Tasks 1–3 que cada caso está cubierto y que no existe desviación respecto del diseño aprobado.

- [ ] **Step 6: Commit**

```bash
git add README.md documentacion/reglas_definidas.md documentacion/estructura.md
git commit -m "docs: documentar gestión de aventureros y grupo"
```
