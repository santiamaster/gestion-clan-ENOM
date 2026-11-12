# Diseño de la presentación preliminar del proyecto ENOM

## Intención

Preparar una presentación de aproximadamente veinte minutos para mostrar al
profesor el proyecto integrador en construcción. La exposición debe permitirle
entender qué clase de juego será, cuáles son sus mecánicas principales, cómo se
relaciona con los contenidos de Programación II y cuánto trabajo funcional ya
existe.

La presentación no pretende defender una versión terminada ni demostrar una
partida completa. Debe comunicar una propuesta concreta, viable y con una base
técnica verificable.

## Audiencia y contexto

- Audiencia principal: profesor de Programación II.
- Contexto: presentación preliminar de lo que se está desarrollando.
- Duración disponible: alrededor de veinte minutos.
- Expositor: Daniel.
- Conocimiento supuesto: fundamentos de Python, archivos JSON, Tkinter y
  estructuras de datos.

## Objetivos

- Explicar en pocos minutos la fantasía central y el papel del jugador.
- Mostrar el ciclo completo de gestión, expedición, recompensa y mejora.
- Presentar las quince combinaciones de raza y profesión sin convertir la
  exposición en una lectura de estadísticas.
- Explicar cómo las habilidades generan funciones diferentes dentro del grupo.
- Mostrar el riesgo asociado a continuar una expedición y perder aventureros.
- Relacionar las mecánicas con la arquitectura Python ya construida.
- Diferenciar claramente lo implementado de lo planificado.

## Fuera de alcance

- Explicar las estadísticas numéricas completas de las quince plantillas.
- Describir campo por campo los `TypedDict` o mostrar grandes bloques de código.
- Presentar enemigos y oleadas definitivos, porque todavía se están balanceando.
- Afirmar que la interfaz o el motor de combate ya están terminados.
- Explicar la historia completa del mundo de ENOM.
- Utilizar las imágenes finales de personajes o ciudad, que se incorporarán
  cuando estén disponibles.

## Criterios de éxito

Al finalizar, el profesor debería poder responder:

1. ¿Qué administra el jugador?
2. ¿Qué decisiones toma antes, durante y después de una expedición?
3. ¿Qué diferencia a los aventureros?
4. ¿Cómo se gana y cómo se pierde?
5. ¿Qué tecnologías y contenidos de la materia utiliza el proyecto?
6. ¿Qué partes funcionan actualmente y cuáles faltan desarrollar?

## Enfoques considerados

### Presentación conceptual

Prioriza ambientación y mecánicas. Resulta atractiva, pero ofrece poca evidencia
del trabajo técnico ya realizado.

### Presentación técnica

Prioriza tipos, módulos, JSON y pruebas. Demuestra programación, pero dificulta
entender por qué el programa es un juego y qué experiencia busca ofrecer.

### Presentación híbrida —seleccionada—

Dedica aproximadamente quince minutos al juego y cinco minutos a la estructura
técnica y el estado actual. Este enfoque permite explicar la idea con claridad y
demostrar que ya existe una implementación organizada y probada.

## Formato

- Presentación editable de 15 diapositivas.
- Relación de aspecto 16:9.
- Pocas frases por diapositiva y explicaciones ampliadas en las notas del
  presentador.
- Duración orientativa de 60 a 90 segundos por diapositiva.
- Tablas y diagramas editables cuando comuniquen mejor una relación exacta.
- Sin animaciones necesarias para comprender la exposición.

## Dirección visual

- Fantasía oscura legible, sin perder el aspecto académico del proyecto.
- Fondo carbón o azul muy oscuro con acentos dorados y turquesa.
- Tipografía clara y de alto contraste.
- Ilustraciones atmosféricas para portada, ciudad y mazmorra.
- Diagramas simples para el ciclo de juego y la arquitectura.
- Evitar interfaces ficticias que puedan confundirse con pantallas ya
  implementadas.
- Las funciones y progresiones se presentan mediante tablas planas, no mediante
  paneles que imiten una aplicación.

## Guion de diapositivas

### 1. Gestión de Clan ENOM

Portada mínima con el nombre del proyecto, la asignatura y el autor. La imagen
debe comunicar una ciudad de fantasía desde la cual parte un grupo de
aventureros.

### 2. La propuesta del juego

El jugador dirige un clan de aventureros. Recluta integrantes, forma un grupo,
elige una mazmorra y decide cuánto riesgo asumir para conseguir dinero y
experiencia.

### 3. Objetivo de la partida

El clan comienza en nivel 1 con tres aventureros y sin dinero. Completar
mazmorras permite aumentar su nivel. Alcanzar el nivel 5 representa la victoria.
La derrota ocurre cuando no quedan vivos y no existe dinero suficiente para
reclutar o resucitar.

### 4. La ciudad como centro de gestión

Diagrama de los cuatro lugares principales:

- Edificio del clan: integrantes y formación del grupo.
- Gremio: ofertas y contratación.
- Iglesia: muertos recuperados, resurrección y entierro.
- Mazmorra: selección de dificultad e inicio de expediciones.

La futura pantalla principal utilizará una ciudad con edificios seleccionables.

### 5. Ciclo principal del juego

Diagrama circular editable:

1. Administrar el clan.
2. Reclutar o reorganizar integrantes.
3. Formar el grupo.
4. Entrar en una mazmorra.
5. Resolver oleadas y decidir si continuar.
6. Regresar con recompensas y mejorar el clan.

### 6. Progresión del clan

Tabla que relacione nivel del clan, cupo total y máximo del grupo:

| Nivel | Cupo del clan | Máximo del grupo |
|---:|---:|---:|
| 1 | 5 | 3 |
| 2 | 10 | 4 |
| 3 | 15 | 5 |
| 4 | 20 | 6 |
| 5 | 25 | 7 |

La mejora del clan amplía las opciones de reclutamiento y la cantidad de
aventureros que pueden entrar en una expedición.

### 7. Progresión de los aventureros

- Niveles del 1 al 10.
- Estadísticas: vida, daño, defensa y velocidad.
- Fórmula: estadística racial más crecimiento profesional multiplicado por el
  nivel.
- Experiencia necesaria: nivel actual multiplicado por 100.
- La experiencia sobrante se conserva.
- Al llegar a nivel 10, las estadísticas reciben un 20% adicional.

### 8. Quince razas y quince profesiones

Presentar las combinaciones permanentes en tres columnas, agrupadas por función
principal para facilitar la lectura:

- Daño y ofensiva: Mago Arcano Draia’seikan, Hechicero Alh-Zarqai, Arquero
  Baz-Zarqai, Ninja Dac-Zarqai, Bárbaro Uk-Haaie, Alabardero Rapzil, Cazador
  Garonido, Asesino Kitsu e Infernal Kormak.
- Defensa y control: Defensor Dangabaruk, Soldado Doker y Paladín Wirmann.
- Soporte: Curador Dri’wing, Psíquico Soul’viraph y Conjurador de Mareas
  Bransha’kana.

La agrupación es expositiva. Cada plantilla conserva su raza, profesión,
estadísticas, tipo de ataque, crítico, coste y estrategia propios.

### 9. Habilidades y funciones dentro del grupo

Mostrar ejemplos representativos en lugar de enumerar las quince habilidades:

- Explosión Arcana: daño elevado a todos los enemigos.
- Provocar: obliga a los enemigos a atacar al Defensor.
- Gran Cura: recupera al aliado más herido.
- Escudo mental: reduce temporalmente el daño recibido.
- Muerte: posibilidad de eliminar un objetivo, con menor probabilidad contra
  jefes si se incorporan.

Explicar que cada profesión posee una habilidad automática con enfriamiento.

### 10. Reclutamiento y economía

El gremio genera ofertas según el nivel del clan. Puede repetir profesiones y
ofrecer candidatos de distintos niveles. El coste depende de la profesión y el
nivel. El jugador debe equilibrar dinero, cupo y calidad del candidato.

La cantidad de ofertas y contrataciones aumenta de forma progresiva entre los
niveles 1 y 5.

### 11. Mazmorras y oleadas

- Cinco dificultades.
- Diez oleadas por mazmorra.
- Enemigos y recompensas mayores en dificultades superiores.
- Después de cada oleada, el jugador elige entre continuar o regresar.
- La vida no se recupera entre oleadas.
- Cada oleada tiene un límite de treinta rondas.

Los enemigos y las composiciones definitivas todavía se encuentran en etapa de
balanceo.

### 12. Combate simplificado

Diagrama secuencial editable:

1. Orden de turnos por velocidad al comenzar la oleada.
2. Desempates mediante una tirada automática de d100.
3. Ataques y habilidades automáticos según la profesión.
4. Efectividad del ataque: 150%, 100% o 50%.
5. Crítico base del 5% con 150% de daño.

Las habilidades conservan sus enfriamientos durante la expedición. Los cálculos
decimales se redondean hacia abajo.

### 13. Riesgo, recompensas y muerte

Los enemigos derrotados acumulan dinero y experiencia. La experiencia se
reparte entre quienes regresan vivos. Si todos mueren, el clan pierde el botín
y no recupera los cuerpos.

Los muertos recuperados ocupan cupo. La iglesia permite resucitarlos con un
descuento del 30% respecto de una contratación equivalente o enterrarlos para
liberar espacio.

### 14. Arquitectura técnica

Diagrama editable de cuatro capas:

- Interfaz con Tkinter.
- Servicios con las reglas del juego.
- Modelos tipados con `Literal` y `TypedDict`.
- Persistencia mediante archivos JSON.

Mencionar Python 3.11+, anotaciones de tipo, validaciones, guardado seguro y
pruebas automatizadas con `unittest`.

### 15. Estado actual y próximos pasos

Implementado:

- Tipos y catálogos de quince aventureros y habilidades.
- Cálculos de progresión, economía, crítico y efectividad.
- Creación, validación y guardado de la partida.
- Reclutamiento, iglesia y gestión segura de integrantes.
- Formación temporal del grupo.
- 127 pruebas automatizadas correctas al 11 de noviembre de 2026.

Próximos bloques:

- Enemigos y oleadas definitivas.
- Motor de combate y expediciones.
- Integración de pantallas Tkinter.
- Imágenes finales, balanceo y pruebas de juego.

## Notas del presentador

Cada diapositiva tendrá notas breves con:

- objetivo de la diapositiva;
- explicación oral sugerida;
- transición hacia la siguiente parte;
- aclaración de qué está implementado y qué está planificado cuando pueda
  existir ambigüedad.

Las notas no se escribirán como un discurso rígido. Servirán como guía para una
explicación natural de veinte minutos.

## Fuentes de contenido

La presentación se basará en:

- `README.md`;
- `documentacion/reglas_definidas.md`;
- `documentacion/estructura.md`;
- `catalogos/plantillas.py`;
- `catalogos/habilidades.py`;
- `configuracion.py`;
- resultados actuales de la suite de pruebas.

No se incorporarán cifras o mecánicas externas que no estén definidas en el
proyecto. Las funciones futuras aparecerán identificadas como planificadas.

## Decisiones dejadas al armado visual

- Ilustración atmosférica exacta de la portada.
- Distribución gráfica de los quince arquetipos dentro de tres columnas.
- Selección de iconos sencillos para ciudad, combate, economía e iglesia.
- Ajustes de texto para mantener un mínimo de 17 puntos sin perder contenido.
- Equilibrio entre fondos ilustrados y fondos planos para conservar legibilidad.
