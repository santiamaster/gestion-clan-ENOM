# Cálculos base — Plan de implementación

> **Para trabajadores con capacidad de agente:** SUBHABILIDAD REQUERIDA: usar `superpowers:subagent-driven-development` (recomendado) o `superpowers:executing-plans` para ejecutar este plan tarea por tarea. Los pasos usan casillas (`- [ ]`) para registrar el avance.

**Objetivo:** Implementar y comprobar las reglas matemáticas compartidas por la progresión, el clan, el reclutamiento y el combate.

**Arquitectura:** Funciones puras en `servicios/calculos.py`, constantes comunes en `configuracion.py` y tipos cerrados en `modelos/tipos.py`. Ninguna función modificará objetos externos ni dependerá de Tkinter, JSON o aleatoriedad.

**Tecnologías:** Python 3.11+, `typing`, `math` y `unittest` de la biblioteca estándar.

**Especificación:** `docs/superpowers/specs/2026-11-06-calculos-base-design.md`

## Restricciones globales

- Mantener compatibilidad con Pyright en modo `strict`.
- Documentar todas las funciones públicas.
- Usar exclusivamente la biblioteca estándar.
- Redondear siempre hacia abajo, salvo regla expresa en contrario.
- Rechazar con `ValueError` niveles fuera de rango y cantidades negativas.
- El nivel máximo del aventurero es 10 y el del clan es 5.

## Enfoque de revisión

- Nivel 10: aplicar exactamente una vez el bono general del 20% y redondear hacia abajo.
- Ascenso múltiple: consumir cada umbral y conservar solo la experiencia todavía utilizable.
- Entradas límite: aceptar cero en daño, coste y experiencia, pero rechazar valores negativos.
- Crítico extremo: limitar la probabilidad total al intervalo de 0 a 100.
- Daño combinado: aplicar efectividad y crítico sobre el daño base y redondear una vez el resultado final.

---

### Tarea 1: Tipos y constantes de cálculo

**Archivos:**
- Modificar: `modelos/tipos.py`
- Modificar: `configuracion.py`
- Probar: `tests/test_calculos.py`

**Interfaces:**
- Produce: `EfectividadAtaque = Literal["efectivo", "neutral", "inefectivo"]`.
- Produce: constantes para bono de nivel 10 y multiplicadores de efectividad.

- [ ] Escribir pruebas que comprueben los valores exactos de las nuevas constantes.
- [ ] Ejecutar `python -m unittest tests.test_calculos -v` y comprobar que falla por importaciones inexistentes.
- [ ] Agregar el tipo y las constantes, con anotaciones explícitas.
- [ ] Repetir la prueba y comprobar que pasa.
- [ ] Confirmar el cambio con el mensaje `feat: agregar tipos y constantes de cálculos`.

### Tarea 2: Estadísticas y bono de nivel máximo

**Archivos:**
- Modificar: `servicios/calculos.py`
- Modificar: `tests/test_calculos.py`

**Interfaces:**
- Consume: `PlantillaAventurero`, `Estadisticas` y el bono de nivel 10.
- Produce: `calcular_estadisticas(plantilla: PlantillaAventurero, nivel: int) -> Estadisticas`.

- [ ] Escribir pruebas para nivel 1, nivel 9, nivel 10 con redondeo y niveles 0 y 11 inválidos.
- [ ] Ejecutar la prueba de la función y comprobar que falla porque todavía no existe.
- [ ] Implementar la fórmula `base racial + crecimiento profesional × nivel` y aplicar el 20% final solamente en nivel 10.
- [ ] Ejecutar `python -m unittest tests.test_calculos.PruebasEstadisticas -v` y comprobar que pasa.
- [ ] Confirmar el cambio con el mensaje `feat: calcular estadísticas por nivel`.

### Tarea 3: Experiencia, cupo y contratación

**Archivos:**
- Modificar: `servicios/calculos.py`
- Modificar: `tests/test_calculos.py`

**Interfaces:**
- Produce: `calcular_experiencia_necesaria(nivel_actual: int) -> int`.
- Produce: `aplicar_experiencia(nivel_actual: int, experiencia_actual: int, experiencia_ganada: int) -> tuple[int, int]`.
- Produce: `calcular_cupo_clan(nivel_clan: int) -> int`.
- Produce: `calcular_coste_contratacion(coste_base: int, nivel: int) -> int`.

- [ ] Escribir pruebas para cada umbral de experiencia, ascenso simple, ascenso múltiple, sobrante y nivel 10.
- [ ] Agregar pruebas de cupo para niveles 1 y 5, y coste para niveles 1 y 10.
- [ ] Agregar pruebas que rechacen niveles fuera de rango y cantidades negativas.
- [ ] Ejecutar las pruebas y comprobar que fallan por funciones inexistentes.
- [ ] Implementar las cuatro funciones; en nivel 10 la experiencia necesaria y la experiencia almacenada serán `0`.
- [ ] Ejecutar `python -m unittest tests.test_calculos -v` y comprobar que pasa.
- [ ] Confirmar el cambio con el mensaje `feat: agregar cálculos de progresión y costes`.

### Tarea 4: Crítico, efectividad y daño final

**Archivos:**
- Modificar: `servicios/calculos.py`
- Modificar: `tests/test_calculos.py`

**Interfaces:**
- Consume: `EfectividadAtaque` y multiplicadores de `configuracion.py`.
- Produce: `calcular_probabilidad_critico(critico_adicional: int) -> int`.
- Produce: `calcular_dano_final(dano_base: int, efectividad: EfectividadAtaque, es_critico: bool) -> int`.

- [ ] Escribir pruebas para crítico base, adicional, mínimo 0 y máximo 100.
- [ ] Escribir pruebas de daño neutral, efectivo, inefectivo, crítico y combinación efectivo-crítico.
- [ ] Fijar mediante una prueba que `15 × 1.50 × 1.50` devuelve `33`.
- [ ] Agregar pruebas para daño cero y daño negativo.
- [ ] Ejecutar las pruebas y comprobar que fallan por funciones inexistentes.
- [ ] Implementar las funciones y aplicar `math.floor()` una vez sobre el resultado combinado.
- [ ] Ejecutar `python -m unittest tests.test_calculos -v` y comprobar que pasa.
- [ ] Confirmar el cambio con el mensaje `feat: calcular crítico y daño final`.

### Tarea 5: Verificación integral y documentación

**Archivos:**
- Modificar: `documentacion/reglas_definidas.md`
- Verificar: todos los módulos y pruebas del proyecto.

**Interfaces:**
- Consume: todas las funciones y constantes anteriores.
- Produce: bloque documentado y comprobado como unidad.

- [ ] Documentar la bonificación del nivel 10 y el redondeo general hacia abajo.
- [ ] Ejecutar `python -m compileall -q .` y comprobar que no informa errores.
- [ ] Ejecutar `python -m unittest -v` y comprobar que todas las pruebas pasan.
- [ ] Validar los tres archivos de `datos/` mediante `json.load()`.
- [ ] Confirmar el cambio con el mensaje `docs: actualizar reglas de cálculos base`.

