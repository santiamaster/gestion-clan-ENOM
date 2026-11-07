# Diseño: creación de una partida nueva

Fecha: 2026-11-06

## Intención

Crear el estado inicial jugable del clan y guardarlo con el servicio de persistencia ya existente. El bloque debe poder probarse sin Tkinter para que la futura interfaz se limite a solicitar el nombre del clan y confirmar una sobrescritura.

## Objetivos

- Crear un clan de nivel 1, sin dinero y con la partida en curso.
- Crear tres aventureros de nivel 1 a partir de las plantillas fijas Soldado, Arquero y Hechicero.
- Asignar nombres aleatorios acordes con el sexo de cada plantilla.
- Asignar los identificadores `AV-0001`, `AV-0002` y `AV-0003`.
- Dejar `siguiente_id_aventurero` en 4.
- Inicializar mazmorras, mercado, ofertas e historial eliminado.
- Guardar los tres JSON con la persistencia existente.
- Impedir una sobrescritura accidental.

## Fuera de alcance

- Interfaz de Tkinter.
- Generación de ofertas de reclutamiento.
- Varias ranuras de guardado.
- Edición de los nombres iniciales por el jugador.
- Recuperación automática de archivos incompletos o inválidos.

## Restricciones

- Python fuertemente anotado y compatible con Pyright en modo estricto.
- Sin dependencias externas.
- Los datos deben satisfacer los validadores actuales antes de guardarse.
- Los archivos incompletos o inválidos deben detener la operación y conservarse.
- El azar debe poder controlarse en las pruebas.

## Enfoques considerados

### 1. Concentrar todo en `servicios/clan.py`

Es el enfoque más corto, pero mezcla la construcción del clan, la creación de aventureros, la selección de nombres y la escritura de archivos.

### 2. Usar un coordinador en `servicios/partidas.py` — elegido

`clan.py` construye el estado general, `aventureros.py` crea los integrantes y `partidas.py` coordina la operación y llama a persistencia. Esta separación facilita las pruebas y prepara la futura interfaz.

### 3. Coordinar la creación desde Tkinter

Evita un servicio adicional, pero acopla las reglas del juego a la interfaz y dificulta las pruebas automatizadas. Se descarta.

## Diseño acordado

### Catálogo de nombres

`catalogos/nombres.py` contendrá catálogos masculinos y femeninos. Una función seleccionará un nombre mediante un objeto `random.Random` recibido, lo que permitirá resultados deterministas durante las pruebas.

### Creación de aventureros

`servicios/aventureros.py` construirá cada `AventureroActivo` con:

- plantilla fija;
- nivel 1;
- experiencia 0;
- estado `"vivo"`;
- identificador con formato `AV-NNNN`;
- nombre aleatorio correspondiente al sexo de la plantilla.

### Estado inicial del clan

`servicios/clan.py` construirá un `EstadoClan` con:

- nombre normalizado con `strip()`;
- nivel 1;
- dinero 0;
- siguiente identificador 4;
- mercado disponible;
- partida en curso;
- cinco mazmorras sin completar;
- ofertas de reclutamiento vacías.

El nombre vacío se rechazará mediante una excepción específica del dominio.

### Coordinación y persistencia

`servicios/partidas.py` expondrá una función pública semejante a:

```python
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

Si no se proporciona un generador, la función creará uno para el uso normal. Si ya existe una partida válida y `sobrescribir` es falso, lanzará `PartidaExistenteError`. Si los archivos existentes están incompletos o son inválidos, propagará el error de persistencia y no los reemplazará.

Con `sobrescribir=True`, una partida válida podrá reemplazarse; la confirmación visual pertenecerá más adelante a Tkinter.

## Comprobaciones

Las pruebas cubrirán:

- estado inicial completo;
- tres plantillas y tres identificadores esperados;
- nombres deterministas con un generador controlado;
- rechazo de nombre vacío;
- guardado y recarga de la partida;
- bloqueo de sobrescritura;
- sobrescritura explícita;
- conservación de archivos incompletos o inválidos.

La verificación final incluirá toda la suite de `unittest` y Pyright en modo estricto.
