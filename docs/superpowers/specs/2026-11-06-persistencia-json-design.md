# Diseño del bloque de persistencia JSON

## Intención

Guardar y recuperar una única partida de forma segura, fuertemente tipada y
sin mezclar el acceso a archivos con la interfaz Tkinter ni con las reglas del
juego.

## Organización de los datos

```text
datos/
├── iniciales/
│   ├── datos_activos.json
│   ├── datos_eliminados.json
│   └── estado_clan.json
└── partida/                  # Creada durante la ejecución e ignorada por Git
    ├── datos_activos.json
    ├── datos_eliminados.json
    └── estado_clan.json
```

Los archivos de `datos/iniciales/` permanecerán versionados como referencias
vacías. Los archivos reales de `datos/partida/` no se publicarán en GitHub.

## Enfoques considerados

### Rechazar la carga y conservar los archivos — seleccionado

La estructura completa se valida antes de entregarla a los demás servicios. Si
falta un archivo, el JSON no puede interpretarse o algún campo es inválido, se
genera un error controlado sin modificar los datos existentes.

### Restablecimiento automático

Se descartó porque podría reemplazar silenciosamente una partida recuperable.

### Copias de seguridad automáticas

Se pospone porque agrega complejidad innecesaria para esta versión del proyecto.

## Responsabilidades

### `servicios/persistencia.py`

- Resolver las rutas desde la raíz del proyecto, sin depender del directorio
  desde el que se ejecute Python.
- Crear `datos/partida/` cuando sea necesario.
- Leer y escribir UTF-8.
- Serializar con sangría de cuatro espacios y conservar los caracteres Unicode.
- Cargar y guardar los tres archivos como una única partida lógica.
- Detectar ausencia total, presencia parcial y errores de decodificación.
- Eliminar la partida únicamente cuando una función explícita sea llamada
  después de la futura confirmación del usuario.

### `servicios/validaciones.py`

- Validar los objetos obtenidos desde JSON antes de convertirlos a los
  `TypedDict`.
- Comprobar tipos, campos obligatorios, intervalos y valores `Literal`.
- Comprobar que cada `plantilla_id` exista en `CATALOGO_PLANTILLAS`.
- No corregir ni completar datos automáticamente.

## Excepciones

```python
class ErrorPersistencia(Exception):
    """Error base producido al leer o escribir la partida."""


class PartidaIncompletaError(ErrorPersistencia):
    """Indica que existe solamente una parte de los archivos requeridos."""


class PartidaInvalidaError(ErrorPersistencia):
    """Indica JSON malformado o datos incompatibles con el modelo."""
```

Los mensajes incluirán el nombre del archivo problemático, pero no expondrán
trazas técnicas al futuro usuario de la interfaz.

## Contratos públicos

```python
def existe_partida_guardada(
    directorio: Path = DIRECTORIO_PARTIDA,
) -> bool:
    ...


def cargar_partida(
    directorio: Path = DIRECTORIO_PARTIDA,
) -> tuple[EstadoClan, list[AventureroActivo], list[AventureroEliminado]]:
    ...


def guardar_partida(
    estado_clan: EstadoClan,
    datos_activos: list[AventureroActivo],
    datos_eliminados: list[AventureroEliminado],
    directorio: Path = DIRECTORIO_PARTIDA,
) -> None:
    ...


def eliminar_partida(
    directorio: Path = DIRECTORIO_PARTIDA,
) -> None:
    ...
```

Las funciones aceptan un directorio alternativo para que las pruebas utilicen
carpetas temporales y nunca modifiquen la partida real.

## Comportamiento exacto

### Existencia

- Ningún archivo presente: devuelve `False`.
- Los tres archivos presentes y válidos: devuelve `True`.
- Solo algunos archivos presentes: lanza `PartidaIncompletaError`.
- Los tres presentes pero alguno inválido: lanza `PartidaInvalidaError`.

### Carga

- Requiere los tres archivos.
- Valida completamente el contenido antes de devolverlo.
- No modifica ningún archivo.
- Mantiene el orden de las listas.

### Guardado

- Valida los datos recibidos antes de escribir.
- Crea el directorio si no existe.
- Escribe primero archivos temporales y después reemplaza los destinos.
- Si la validación falla, no escribe nada.
- Devuelve `None` cuando finaliza correctamente.

### Eliminación

- Elimina exclusivamente los tres archivos conocidos.
- No elimina el directorio ni otros archivos que pudieran existir.
- No falla si la partida todavía no existe.

## Validaciones principales

- Nombres e identificadores obligatorios: cadenas no vacías.
- Nivel de aventurero: 1 a 10.
- Nivel de clan: 1 a 5.
- Experiencia, dinero y costes: enteros no negativos.
- Estados, motivos y mercado: valores definidos mediante `Literal`.
- Banderas de mazmorras: exactamente cinco valores booleanos.
- Ofertas: lista de estructuras válidas.
- Plantillas: identificadores existentes en el catálogo.
- Un aventurero de nivel 10 debe tener experiencia igual a cero.

## Fuera de alcance

Este bloque no crea una partida nueva, no construye los tres aventureros
iniciales, no solicita confirmaciones y no muestra ventanas. Esas operaciones
corresponderán a los servicios de clan y a la interfaz.
