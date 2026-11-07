# Reglas definidas

## Progresión

- El clan tiene niveles del 1 al 5.
- El cupo aumenta de 5 a 25 en intervalos de 5.
- Los aventureros tienen niveles del 1 al 10.
- La experiencia necesaria para subir es `nivel actual × 100`.
- La experiencia sobrante se conserva.
- Al alcanzar el nivel 10, las cuatro estadísticas reciben un 20% adicional.
- En el nivel 10 la experiencia deja de acumularse y se conserva en cero.

## Combate

- Las estadísticas son vida, daño, defensa y velocidad.
- Los turnos se ordenan por velocidad al comenzar cada oleada.
- Los empates se resuelven con una tirada de d100.
- El crítico base es 5% y causa 150% del daño.
- Los ataques efectivos causan 150%, los neutrales 100% y los inefectivos 50%.
- Los multiplicadores de efectividad y crítico se combinan antes de redondear.
- Por regla general, todo resultado decimal se redondea hacia abajo.
- La vida no se recupera entre oleadas.
- Los enfriamientos se conservan durante toda la expedición.
- Cada oleada tiene un límite de 30 rondas.

## Expediciones

- Hay cinco dificultades y diez oleadas por mazmorra.
- Después de cada oleada el jugador puede continuar o regresar.
- El dinero y la experiencia se obtienen si al menos un aventurero regresa vivo.
- La experiencia se reparte solamente entre los supervivientes.
- Una derrota total pierde el botín y los cuerpos no pueden recuperarse.

## Clan

- La partida comienza con Soldado, Arquero y Hechicero de nivel 1.
- El dinero inicial es cero.
- Los muertos recuperados permanecen en el clan y ocupan cupo.
- La iglesia permite revivirlos o enterrarlos con honores.
- Alcanzar el nivel 5 del clan representa la victoria.

## Cálculos base implementados

Las funciones puras de `servicios/calculos.py` resuelven actualmente:

- Estadísticas de un aventurero según su plantilla y nivel.
- Experiencia necesaria, ascensos múltiples y experiencia sobrante.
- Cupo del clan según su nivel.
- Coste de contratación según profesión y nivel.
- Probabilidad crítica total.
- Daño modificado por efectividad y crítico.

Estas funciones no modifican listas, archivos JSON ni elementos de la
interfaz. La defensa, las tiradas y las habilidades se incorporarán en los
bloques correspondientes al sistema de combate.

## Persistencia implementada

- Una partida está formada por estado del clan, aventureros activos e historial
  de eliminados.
- La ausencia total de los archivos significa que todavía no existe partida.
- Una presencia parcial produce `PartidaIncompletaError`.
- Un JSON malformado o incompatible produce `PartidaInvalidaError`.
- Los archivos problemáticos se conservan intactos para evitar pérdida de datos.
- Los datos se validan antes de cargarse y antes de guardarse.
- El guardado utiliza archivos temporales y codificación UTF-8.
- Los nombres con tildes y otros caracteres se conservan directamente.
- La eliminación afecta solamente a los tres archivos conocidos.
- La interfaz será responsable de transformar estas excepciones en mensajes para
  el jugador.

