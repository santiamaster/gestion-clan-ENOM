# Sistema de reclutamiento Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generar y renovar ofertas de aventureros, permitir varias contrataciones según el nivel del clan y preservar todas las restricciones de dinero, cupo y persistencia.

**Architecture:** `modelos/tipos.py` y `servicios/validaciones.py` adoptan el contador persistente como única fuente de verdad. `servicios/reclutamiento.py` contiene generación, renovación y contratación sin depender de Tkinter ni del sistema de archivos; `servicios/partidas.py` incorpora la renovación inicial antes del primer guardado.

**Tech Stack:** Python 3.11 o superior, biblioteca estándar (`random`, `unittest`), TypedDict, JSON y Pyright estricto.

**Spec:** `docs/superpowers/specs/2026-11-07-reclutamiento-design.md`

## Global Constraints

- El mercado ofrece `nivel_clan × 2` candidatos.
- Cada renovación permite `nivel_clan` contrataciones.
- Los candidatos tienen niveles enteros entre 1 y el nivel del clan.
- Las plantillas se seleccionan con reemplazo y pueden repetirse.
- El coste es `coste_base × nivel`.
- El cupo es `nivel_clan × 5` e incluye aventureros vivos y muertos que sigan activos.
- Los errores no pueden producir modificaciones parciales.
- Las ofertas y el contador se conservan si falta dinero o cupo.
- Python permanece libre de dependencias externas y compatible con Pyright estricto.

## Review Focus

- Un contador booleano debe rechazarse aunque `bool` sea subtipo de `int`: prueba en Task 1.
- Una oferta cuyo coste no coincide con plantilla y nivel debe invalidar el guardado: prueba en Task 1.
- Un clan lleno con aventureros muertos debe seguir bloqueando la contratación sin mutaciones: prueba en Task 4.
- Una oferta inexistente no debe consumir dinero, contador, ID ni lista: prueba en Task 4.
- Tras liberar cupo, las ofertas y contrataciones conservadas deben permitir continuar: prueba en Task 4.

---

## Estructura de archivos

- Modify: `modelos/tipos.py` — reemplazo del estado textual por el contador.
- Modify: `servicios/validaciones.py` — validación relacional de contador y ofertas.
- Modify: `servicios/clan.py` — estado base con contador cero.
- Modify: `servicios/reclutamiento.py` — tablas, generación, renovación y contratación.
- Modify: `servicios/partidas.py` — mercado inicial antes del guardado.
- Modify: `tests/test_validaciones.py`, `tests/test_persistencia.py`, `tests/test_partidas.py`.
- Create: `tests/test_reclutamiento.py`.
- Modify: `documentacion/reglas_definidas.md` y `README.md` para reflejar el bloque terminado.

### Task 1: Esquema persistente y validación del mercado

**Files:**
- Modify: `modelos/tipos.py`
- Modify: `servicios/validaciones.py`
- Modify: `tests/test_validaciones.py`
- Modify: `tests/test_persistencia.py`

**Interfaces:**
- Produces: `EstadoClan["contrataciones_restantes"]: int`.
- Removes: `EstadoMercado` y `EstadoClan["estado_mercado"]`.
- Consumes: `CATALOGO_PLANTILLAS` y `calcular_coste_contratacion(coste_base: int, nivel: int) -> int`.

- [ ] **Step 1: Escribir pruebas fallidas del nuevo esquema**

Actualizar `crear_estado_clan()` para usar `contrataciones_restantes=1` y dos ofertas válidas `OF-01` y `OF-02`. Agregar pruebas que rechacen:

- ausencia del contador;
- contador booleano, negativo o superior al nivel del clan;
- más de `nivel × 2` ofertas;
- menos ofertas que contrataciones restantes;
- IDs de oferta repetidos;
- nivel de candidato superior al nivel del clan;
- coste diferente de `coste_base × nivel`;
- el esquema anterior con `estado_mercado` y sin contador.

- [ ] **Step 2: Ejecutar y comprobar RED**

Run: `python -m unittest tests.test_validaciones tests.test_persistencia -v`

Expected: FAIL porque el validador todavía exige `estado_mercado`.

- [ ] **Step 3: Modificar tipos y validadores**

Eliminar `EstadoMercado`. Incorporar el contador a `EstadoClan`. Hacer que `_validar_oferta()` reciba el nivel del clan y valide nivel y coste; hacer que `validar_estado_clan()` compruebe límites, cantidad, unicidad y relación entre contador y ofertas.

- [ ] **Step 4: Ejecutar pruebas del esquema**

Run: `python -m unittest tests.test_validaciones tests.test_persistencia -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add modelos/tipos.py servicios/validaciones.py tests/test_validaciones.py tests/test_persistencia.py
git commit -m "refactor: adoptar contador de contrataciones"
```

### Task 2: Reglas numéricas del mercado

**Files:**
- Modify: `servicios/reclutamiento.py`
- Create: `tests/test_reclutamiento.py`

**Interfaces:**
- Produces: `calcular_cantidad_ofertas(nivel_clan: int) -> int` y `calcular_limite_contrataciones(nivel_clan: int) -> int`.
- Consumes: niveles de clan válidos entre 1 y 5.

- [ ] **Step 1: Escribir pruebas fallidas de la tabla**

Comprobar literalmente:

```python
ofertas = {1: 2, 2: 4, 3: 6, 4: 8, 5: 10}
contrataciones = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
```

Ambas funciones deben lanzar `ValueError` para niveles 0 y 6.

- [ ] **Step 2: Ejecutar y comprobar RED**

Run: `python -m unittest tests.test_reclutamiento -v`

Expected: FAIL por funciones inexistentes.

- [ ] **Step 3: Implementar las dos funciones**

Aplicar las fórmulas `nivel × 2` y `nivel`, validando el intervalo 1–5.

- [ ] **Step 4: Ejecutar pruebas del mercado**

Run: `python -m unittest tests.test_reclutamiento -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add servicios/reclutamiento.py tests/test_reclutamiento.py
git commit -m "feat: agregar progresión del mercado"
```

### Task 3: Generación y renovación de ofertas

**Files:**
- Modify: `servicios/reclutamiento.py`
- Modify: `tests/test_reclutamiento.py`

**Interfaces:**
- Consumes: `CATALOGO_PLANTILLAS`, `elegir_nombre()`, `calcular_coste_contratacion()` y funciones de Task 2.
- Produces: `generar_ofertas(nivel_clan: int, generador: Random) -> list[OfertaReclutamiento]` y `renovar_mercado(estado_clan: EstadoClan, generador: Random) -> None`.

- [ ] **Step 1: Escribir pruebas fallidas de generación**

Comprobar con semillas fijas que para cada nivel 1–5:

- la cantidad es `2, 4, 6, 8, 10`;
- los IDs son `OF-01` a `OF-N`;
- cada plantilla existe;
- cada nivel está entre 1 y el nivel del clan;
- cada nombre corresponde al sexo de la plantilla;
- cada coste coincide con plantilla y nivel.

Agregar una prueba con un generador controlado que demuestre que las plantillas repetidas se conservan.

- [ ] **Step 2: Ejecutar y comprobar RED**

Run: `python -m unittest tests.test_reclutamiento -v`

Expected: FAIL por generador inexistente.

- [ ] **Step 3: Implementar generación**

Seleccionar plantillas con reemplazo desde una tupla estable de `CATALOGO_PLANTILLAS.values()`, niveles con `randint(1, nivel_clan)`, nombres mediante `elegir_nombre()` e IDs temporales secuenciales.

- [ ] **Step 4: Escribir prueba fallida de renovación**

Partir de un estado con ofertas antiguas y contador cero; comprobar que `renovar_mercado()` reemplaza la lista completa y restablece el contador al nivel del clan.

- [ ] **Step 5: Implementar y verificar renovación**

Run: `python -m unittest tests.test_reclutamiento -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add servicios/reclutamiento.py tests/test_reclutamiento.py
git commit -m "feat: generar y renovar ofertas"
```

### Task 4: Contratación transaccional

**Files:**
- Modify: `servicios/reclutamiento.py`
- Modify: `tests/test_reclutamiento.py`

**Interfaces:**
- Produces: `OfertaNoEncontradaError`, `MercadoAgotadoError`, `CupoClanCompletoError`, `DineroInsuficienteError` y `contratar_aventurero(estado_clan: EstadoClan, datos_activos: list[AventureroActivo], id_oferta: str) -> AventureroActivo`.
- Consumes: `calcular_cupo_clan()` y `formatear_id_aventurero()`.

- [ ] **Step 1: Escribir pruebas fallidas de contratación correcta**

Comprobar que una contratación:

- devuelve y agrega `AV-0004`, vivo, nivel y nombre de la oferta, experiencia cero;
- descuenta el coste;
- incrementa el siguiente ID;
- elimina solo la oferta elegida;
- reduce el contador;
- permite una segunda contratación si el nivel y el contador lo permiten.

- [ ] **Step 2: Ejecutar y comprobar RED**

Run: `python -m unittest tests.test_reclutamiento -v`

Expected: FAIL por contratación inexistente.

- [ ] **Step 3: Implementar la ruta correcta**

Localizar la oferta por ID, ejecutar todas las validaciones antes de mutar y aplicar los siete cambios acordados.

- [ ] **Step 4: Escribir pruebas fallidas de errores y atomicidad**

Cubrir oferta inexistente, contador cero, dinero insuficiente y clan lleno con vivos o muertos. Antes de cada intento, copiar estado y activos; después del error deben ser exactamente iguales.

Agregar el caso: clan lleno conserva mercado, se elimina un activo fuera del servicio y el siguiente intento con la misma oferta resulta correcto.

- [ ] **Step 5: Implementar errores y verificar**

Run: `python -m unittest tests.test_reclutamiento -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add servicios/reclutamiento.py tests/test_reclutamiento.py
git commit -m "feat: contratar aventureros del mercado"
```

### Task 5: Mercado inicial, documentación y verificación integral

**Files:**
- Modify: `servicios/clan.py`
- Modify: `servicios/partidas.py`
- Modify: `tests/test_partidas.py`
- Modify: `README.md`
- Modify: `documentacion/reglas_definidas.md`

**Interfaces:**
- Consumes: `renovar_mercado(estado_clan, generador)`.
- Produces: partidas nuevas guardadas con dos ofertas, una contratación restante y el nuevo esquema persistente.

- [ ] **Step 1: Escribir pruebas fallidas de partida nueva**

Actualizar la expectativa de `crear_estado_inicial_clan()` a contador cero sin ofertas. Comprobar que `crear_nueva_partida(..., Random(7))` renueva antes de guardar, devuelve dos ofertas y contador uno, y que `cargar_partida()` conserva exactamente esos datos.

- [ ] **Step 2: Ejecutar y comprobar RED**

Run: `python -m unittest tests.test_partidas -v`

Expected: FAIL porque la partida nueva todavía no renueva el mercado.

- [ ] **Step 3: Integrar renovación inicial**

Cambiar `crear_estado_inicial_clan()` al nuevo campo y llamar a `renovar_mercado()` en `crear_nueva_partida()` antes de `guardar_partida()`, reutilizando el mismo `Random`.

- [ ] **Step 4: Actualizar documentación**

Reflejar el sistema de reclutamiento terminado, la tabla 1–5, el contador persistente y la renovación posterior a expediciones.

- [ ] **Step 5: Ejecutar verificación completa**

Run: `python -m unittest discover -s tests -v`

Expected: todos los tests pasan.

Run: `npx --offline pyright`

Expected: `0 errors, 0 warnings, 0 informations`.

Run: `git diff --check`

Expected: sin errores.

- [ ] **Step 6: Commit**

```bash
git add servicios/clan.py servicios/partidas.py tests/test_partidas.py README.md documentacion/reglas_definidas.md
git commit -m "feat: iniciar partidas con mercado disponible"
```
