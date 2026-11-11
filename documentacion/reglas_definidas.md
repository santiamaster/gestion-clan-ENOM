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
- Los enemigos usan el crítico base del 5% sin modificadores adicionales.
- Los enemigos eligen al azar entre los aventureros vivos, salvo que una
  habilidad como `Provocar` o `Proteger` cambie el objetivo.
- Por regla general, todo resultado decimal se redondea hacia abajo.
- La vida no se recupera entre oleadas.
- Los enfriamientos se conservan durante toda la expedición.
- Cada oleada tiene un límite de 30 rondas.

## Expediciones

- Hay cinco dificultades y diez oleadas por mazmorra.
- Después de cada oleada el jugador puede continuar o regresar.
- El dinero y la experiencia se obtienen si al menos un aventurero regresa vivo.
- Cada enemigo derrotado agrega su recompensa a un pozo común de experiencia.
- Al terminar la expedición, el pozo se divide en partes iguales entre quienes
  regresen vivos. La división entera redondea hacia abajo y descarta el
  sobrante.
- Una derrota total pierde el botín y los cuerpos no pueden recuperarse.

## Clan

- La partida comienza con Soldado, Arquero y Hechicero de nivel 1.
- El dinero inicial es cero.
- Los muertos recuperados permanecen en el clan y ocupan cupo.
- La iglesia permite revivirlos o enterrarlos con honores.
- Alcanzar el nivel 5 del clan representa la victoria.

## Gestión de aventureros y formación del grupo

- Los integrantes se buscan mediante su identificador interno.
- La búsqueda normaliza cada ID con `strip().upper()`, por lo que ignora
  espacios exteriores y diferencias entre mayúsculas y minúsculas.
- El listado de vivos conserva el orden de `datos_activos`, excluye a los
  muertos recuperados y devuelve una lista nueva.
- Expulsar a un aventurero vivo es gratuito y libera su lugar en el clan.
- La expulsión conserva sus datos en el historial con el motivo
  `servicios_finalizados`.
- No se puede expulsar a un muerto mediante la gestión del clan; su salida se
  resuelve en la iglesia.
- No se puede expulsar al último aventurero vivo, aunque existan muertos que
  todavía ocupen cupo.
- La existencia, el estado y la cantidad de vivos se validan antes de modificar
  las listas. Una expulsión fallida no altera los registros.

| Nivel del clan | Máximo del grupo |
|---:|---:|
| 1 | 3 |
| 2 | 4 |
| 3 | 5 |
| 4 | 6 |
| 5 | 7 |

- El grupo puede contener desde un integrante hasta el máximo correspondiente
  al nivel actual del clan.
- Solo pueden seleccionarse aventureros vivos que todavía pertenezcan al clan.
- Un mismo aventurero no puede ocupar dos lugares, incluso si sus IDs fueron
  escritos con distintos espacios o combinaciones de mayúsculas y minúsculas.
- La selección conserva el orden elegido por el jugador.
- El grupo se representa temporalmente mediante una lista de IDs: no forma
  parte del estado persistente ni modifica las listas recibidas.
- Los estados temporales de combate se crearán al iniciar la expedición y no
  forman parte de este bloque.

## Reclutamiento

| Nivel del clan | Ofertas por renovación | Contrataciones máximas | Niveles ofrecidos | Cupo |
|---:|---:|---:|---:|---:|
| 1 | 2 | 1 | 1 | 5 |
| 2 | 4 | 2 | 1–2 | 10 |
| 3 | 6 | 3 | 1–3 | 15 |
| 4 | 8 | 4 | 1–4 | 20 |
| 5 | 10 | 5 | 1–5 | 25 |

- Las plantillas se eligen con reemplazo, por lo que pueden aparecer varias
  ofertas de una misma profesión.
- El nombre se elige según el sexo definido por la plantilla.
- El coste es `coste_base × nivel del candidato`.
- Los identificadores temporales se reinician en cada renovación desde
  `OF-01`.
- `contrataciones_restantes` es la única fuente de verdad sobre cuántos
  candidatos todavía pueden contratarse.
- La contratación solo se realiza si la oferta existe, queda una contratación,
  hay cupo y alcanza el dinero.
- Una contratación fallida conserva sin cambios el dinero, el siguiente ID,
  el contador, las ofertas y los aventureros activos.
- Los vivos y los muertos que continúan en el clan ocupan cupo por igual.
- Liberar cupo permite volver a intentar la contratación con la misma oferta.
- Una partida nueva guarda dos ofertas iniciales y una contratación disponible.
- Al terminar una expedición se deberá reemplazar completamente el mercado y
  restablecer el contador según el nivel actual del clan. El servicio de
  renovación ya está implementado; su llamada quedará integrada cuando se
  desarrolle el flujo de expediciones.

## Iglesia

- Un muerto recuperado permanece en `datos_activos`, conserva todos sus datos
  y continúa ocupando un lugar del cupo.
- Si todo el grupo muere, los cuerpos no se recuperan. Esos aventureros pasan
  al historial con el motivo `caido_no_recuperado` y no pueden resucitarse.
- Los cuerpos recuperados se seleccionan mediante su identificador interno.
  La búsqueda ignora espacios exteriores y diferencias entre mayúsculas y
  minúsculas.
- El coste de resurrección se obtiene sin definir un precio base nuevo:

  ```text
  coste_contratacion_equivalente × 70 // 100
  ```

- La división entera redondea el coste hacia abajo según la regla general de
  ENOM.
- Resucitar cambia únicamente el estado a `vivo`, descuenta el dinero y
  conserva ID, nombre, plantilla, nivel y experiencia.
- Si el clan no posee dinero suficiente, no se modifica el dinero ni el
  aventurero.
- Enterrar un cuerpo es gratuito, lo elimina de `datos_activos`, libera cupo y
  agrega al historial un registro con `enterrado_con_honores`.
- El memorial incluye `enterrado_con_honores` y `caido_no_recuperado` en su
  orden histórico. Excluye las bajas con `servicios_finalizados`, porque esos
  aventureros abandonaron el clan con vida.

## Cálculos base implementados

Las funciones puras de `servicios/calculos.py` resuelven actualmente:

- Estadísticas de un aventurero según su plantilla y nivel.
- Experiencia necesaria, ascensos múltiples y experiencia sobrante.
- Cupo del clan según su nivel.
- Coste de contratación según profesión y nivel.
- Descuento del coste de resurrección con redondeo hacia abajo.
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
- El mercado, sus ofertas y las contrataciones restantes forman parte del
  estado persistente del clan.
- Las partidas del esquema anterior que solo contienen `estado_mercado` se
  rechazan de forma controlada; no se realiza una migración automática durante
  esta etapa del desarrollo.
- La interfaz será responsable de transformar estas excepciones en mensajes para
  el jugador.

