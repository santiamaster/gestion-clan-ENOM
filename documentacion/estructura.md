# Estructura del proyecto

## Catálogos

Contienen información fija que no forma parte de una partida guardada.

- `habilidades.py`: las quince habilidades profesionales.
- `plantillas.py`: razas, profesiones, estadísticas, costes e imágenes.
- `enemigos.py`: enemigos disponibles para las mazmorras.
- `mazmorras.py`: dificultades, oleadas y recompensas.
- `nombres.py`: nombres aleatorios de aventureros.

## Modelos

- `tipos.py`: tipos `Literal`, estructuras `TypedDict` y uniones.
- `combate.py`: estados temporales de combatientes y expediciones.

## Servicios

Los servicios contienen las reglas y no deben depender de Tkinter.

- `calculos.py`: estadísticas, experiencia y economía.
- `persistencia.py`: rutas, carga, guardado y eliminación de la partida JSON.
- `clan.py`: nivel, cupo, dinero y victoria o derrota.
- `aventureros.py`: crea los integrantes iniciales y centraliza la
  normalización y búsqueda por ID, el listado de vivos, la expulsión segura y
  la formación temporal del grupo. Opera sobre estructuras en memoria sin
  depender de Tkinter ni guardar archivos JSON.
- `reclutamiento.py`: ofertas y contrataciones.
- `iglesia.py`: consulta cuerpos recuperados, calcula costes, resucita,
  entierra y filtra el memorial histórico. Modifica las estructuras recibidas
  en memoria, pero no lee ni guarda archivos JSON directamente.
- `combate.py`: rondas, ataques y habilidades.
- `expediciones.py`: oleadas, botín y retirada.
- `validaciones.py`: conversión segura de datos externos a los tipos del dominio.

## Interfaz

Cada módulo representa una pantalla o grupo de componentes de Tkinter. La interfaz llama a los servicios, pero los servicios no conocen las ventanas.

## Datos

Los archivos se separan según su función:

```text
datos/
├── iniciales/       # Referencias vacías versionadas en Git
└── partida/         # Partida local creada durante la ejecución
```

Cada ubicación utiliza tres archivos:

- `datos_activos.json`: aventureros que ocupan cupo.
- `datos_eliminados.json`: bajas y caídos no recuperados.
- `estado_clan.json`: progreso, dinero, mercado y mazmorras completadas.

`datos/partida/` está excluido mediante `.gitignore`. Jugar no genera cambios
pendientes en el repositorio ni publica la partida personal en GitHub.

La persistencia resuelve las rutas desde la ubicación del proyecto, por lo que
funciona aunque el programa sea iniciado desde otro directorio de la terminal.

