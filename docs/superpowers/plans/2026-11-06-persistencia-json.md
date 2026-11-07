# Persistencia JSON — Plan de implementación

> **Para trabajadores con capacidad de agente:** SUBHABILIDAD REQUERIDA: usar `superpowers:subagent-driven-development` (recomendado) o `superpowers:executing-plans` para ejecutar este plan tarea por tarea. Los pasos usan casillas (`- [ ]`) para registrar el avance.

**Objetivo:** Implementar el almacenamiento local, validado y seguro de una única partida mediante tres archivos JSON.

**Arquitectura:** `servicios/validaciones.py` transformará objetos JSON desconocidos en los `TypedDict` del dominio. `servicios/persistencia.py` resolverá rutas, coordinará los tres archivos y traducirá los errores técnicos a excepciones propias, sin depender de Tkinter.

**Tecnologías:** Python 3.11+, `json`, `pathlib`, `tempfile`, `typing` y `unittest`.

**Especificación:** `docs/superpowers/specs/2026-11-06-persistencia-json-design.md`

## Restricciones globales

- Mantener compatibilidad con Pyright en modo `strict`.
- Utilizar solamente la biblioteca estándar.
- Documentar todas las funciones y excepciones públicas.
- No modificar ni borrar archivos al producirse un error de carga.
- No escribir datos que no superen la validación completa.
- Las pruebas deben usar directorios temporales.
- `datos/partida/` debe permanecer fuera del control de versiones.

## Enfoque de revisión

- Una partida parcial debe producir `PartidaIncompletaError`, nunca `False`.
- Un JSON sintácticamente válido pero estructuralmente incorrecto debe producir `PartidaInvalidaError`.
- Una plantilla inexistente debe impedir carga y guardado.
- Un fallo de validación previo al guardado no debe crear ningún archivo.
- La eliminación no debe afectar archivos desconocidos ubicados en el mismo directorio.

---

### Tarea 1: Organización de archivos y rutas

**Archivos:**
- Modificar: `.gitignore`
- Crear: `datos/iniciales/datos_activos.json`
- Crear: `datos/iniciales/datos_eliminados.json`
- Crear: `datos/iniciales/estado_clan.json`
- Eliminar: los tres JSON ubicados directamente en `datos/`
- Modificar: `servicios/persistencia.py`
- Crear: `tests/test_persistencia.py`

**Interfaces:**
- Produce: `DIRECTORIO_DATOS: Path`, `DIRECTORIO_PARTIDA: Path` y las tres rutas derivadas.
- Produce: `crear_directorio_partida(directorio: Path = DIRECTORIO_PARTIDA) -> None`.

- [ ] Escribir pruebas para resolución independiente del directorio actual y creación de carpetas.
- [ ] Ejecutar `python -m unittest tests.test_persistencia -v` y comprobar el fallo por interfaces inexistentes.
- [ ] Reorganizar los JSON, ignorar `datos/partida/` e implementar las rutas y creación.
- [ ] Ejecutar la prueba específica y comprobar que pasa.
- [ ] Confirmar con `chore: separar datos iniciales y partida local`.

### Tarea 2: Validación de aventureros

**Archivos:**
- Modificar: `servicios/validaciones.py`
- Crear: `tests/test_validaciones.py`

**Interfaces:**
- Consume: `AventureroActivo`, `AventureroEliminado` y `CATALOGO_PLANTILLAS`.
- Produce: `validar_datos_activos(datos: object) -> list[AventureroActivo]`.
- Produce: `validar_datos_eliminados(datos: object) -> list[AventureroEliminado]`.
- Produce: `ErrorValidacionDatos(ValueError)`.

- [ ] Escribir pruebas para listas válidas, campos ausentes, tipos incorrectos, niveles, experiencia, estados, motivos y plantillas desconocidas.
- [ ] Fijar mediante una prueba que nivel 10 exige experiencia cero.
- [ ] Ejecutar las pruebas y comprobar que fallan por funciones inexistentes.
- [ ] Implementar validadores que construyan nuevos diccionarios tipados sin modificar la entrada.
- [ ] Ejecutar `python -m unittest tests.test_validaciones -v` y comprobar que pasa.
- [ ] Confirmar con `feat: validar registros de aventureros`.

### Tarea 3: Validación del estado del clan

**Archivos:**
- Modificar: `servicios/validaciones.py`
- Modificar: `tests/test_validaciones.py`

**Interfaces:**
- Consume: `EstadoClan`, `OfertaReclutamiento`, `MazmorrasCompletadas` y el catálogo.
- Produce: `validar_estado_clan(datos: object) -> EstadoClan`.

- [ ] Escribir pruebas para un estado completo válido.
- [ ] Agregar pruebas de nombre vacío, nivel, dinero, identificador siguiente, mercado, estado de partida, cinco banderas y ofertas.
- [ ] Ejecutar las pruebas y comprobar que fallan por función inexistente.
- [ ] Implementar la validación completa y la construcción de una copia tipada.
- [ ] Ejecutar `python -m unittest tests.test_validaciones -v` y comprobar que pasa.
- [ ] Confirmar con `feat: validar estado persistente del clan`.

### Tarea 4: Existencia y carga de partida

**Archivos:**
- Modificar: `servicios/persistencia.py`
- Modificar: `tests/test_persistencia.py`

**Interfaces:**
- Consume: los tres validadores de las tareas 2 y 3.
- Produce: `ErrorPersistencia`, `PartidaIncompletaError` y `PartidaInvalidaError`.
- Produce: `existe_partida_guardada(directorio: Path = DIRECTORIO_PARTIDA) -> bool`.
- Produce: `cargar_partida(directorio: Path = DIRECTORIO_PARTIDA) -> tuple[EstadoClan, list[AventureroActivo], list[AventureroEliminado]]`.

- [ ] Escribir pruebas para ausencia total, tres archivos válidos, presencia parcial, JSON malformado y estructura inválida.
- [ ] Comprobar que los mensajes identifican el archivo problemático.
- [ ] Ejecutar las pruebas y comprobar que fallan por interfaces inexistentes.
- [ ] Implementar lectura UTF-8, traducción de errores y validación previa al retorno.
- [ ] Ejecutar `python -m unittest tests.test_persistencia -v` y comprobar que pasa.
- [ ] Confirmar con `feat: cargar y comprobar partidas JSON`.

### Tarea 5: Guardado seguro y eliminación

**Archivos:**
- Modificar: `servicios/persistencia.py`
- Modificar: `tests/test_persistencia.py`

**Interfaces:**
- Produce: `guardar_partida(estado_clan: EstadoClan, datos_activos: list[AventureroActivo], datos_eliminados: list[AventureroEliminado], directorio: Path = DIRECTORIO_PARTIDA) -> None`.
- Produce: `eliminar_partida(directorio: Path = DIRECTORIO_PARTIDA) -> None`.

- [ ] Escribir pruebas de guardado, Unicode, sangría, sustitución de una partida previa y recarga equivalente.
- [ ] Agregar una prueba que demuestre que datos inválidos no crean archivos.
- [ ] Agregar pruebas de eliminación inexistente y conservación de archivos desconocidos.
- [ ] Ejecutar las pruebas y comprobar que fallan por funciones inexistentes.
- [ ] Implementar validación previa, escritura temporal, reemplazo y eliminación limitada.
- [ ] Ejecutar `python -m unittest tests.test_persistencia -v` y comprobar que pasa.
- [ ] Confirmar con `feat: guardar y eliminar partidas JSON`.

### Tarea 6: Documentación y verificación integral

**Archivos:**
- Modificar: `documentacion/estructura.md`
- Modificar: `documentacion/reglas_definidas.md`

**Interfaces:**
- Consume: toda la API pública de persistencia.
- Produce: bloque documentado y comprobado integralmente.

- [ ] Documentar la ubicación local, las excepciones y el flujo de persistencia.
- [ ] Ejecutar `python -m compileall -q .`.
- [ ] Ejecutar `python -m unittest -v` y comprobar que toda la suite pasa.
- [ ] Ejecutar Pyright desde el entorno configurado y comprobar cero errores.
- [ ] Confirmar con `docs: documentar persistencia JSON`.
