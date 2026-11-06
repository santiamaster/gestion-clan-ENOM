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
- `persistencia.py`: archivos JSON.
- `clan.py`: nivel, cupo, dinero y victoria o derrota.
- `aventureros.py`: altas, búsquedas y bajas.
- `reclutamiento.py`: ofertas y contrataciones.
- `iglesia.py`: resurrecciones y entierros.
- `combate.py`: rondas, ataques y habilidades.
- `expediciones.py`: oleadas, botín y retirada.
- `validaciones.py`: controles de entrada y reglas.

## Interfaz

Cada módulo representa una pantalla o grupo de componentes de Tkinter. La interfaz llama a los servicios, pero los servicios no conocen las ventanas.

## Datos

- `datos_activos.json`: aventureros que ocupan cupo.
- `datos_eliminados.json`: bajas y caídos no recuperados.
- `estado_clan.json`: progreso, dinero, mercado y mazmorras completadas.

