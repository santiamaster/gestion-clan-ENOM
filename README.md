# Gestión de Clan ENOM

Proyecto integrador de Programación II desarrollado en Python con Tkinter.

El programa permitirá administrar un clan de aventureros de ENOM, reclutar integrantes, formar grupos, explorar mazmorras, resolver combates por oleadas y gestionar a los aventureros caídos.

## Estado del proyecto

El proyecto se encuentra en la etapa de construcción de sus modelos y
servicios principales. Ya están definidos:

- Los tipos compartidos y estructuras `TypedDict`.
- Las quince plantillas de aventureros.
- Las quince habilidades profesionales.
- Las reglas principales de progresión, combate y persistencia.
- La creación y el guardado seguro de una partida nueva.
- La generación, renovación y contratación del mercado de aventureros.
- La consulta, resurrección y sepultura de aventureros caídos.
- La búsqueda, el listado y la expulsión segura de integrantes vivos.
- La formación temporal del grupo según el nivel del clan.
- Las diez plantillas enemigas de la Mazmorra de los Limos.
- Las diez oleadas manuales de la primera mazmorra.
- El combate básico automático, desde la tirada hasta el resultado de oleada.

La interfaz, las habilidades, el flujo completo de expediciones y la conexión
entre sus resultados, la partida guardada y la renovación del mercado todavía
están pendientes.

## Reclutamiento implementado

El gremio genera el doble de candidatos que el nivel actual del clan y
permite contratar, como máximo, una cantidad igual a ese nivel. Cada oferta
incluye un nombre, una de las quince plantillas, un nivel posible y el coste
calculado según su profesión.

Las contrataciones comprueban antes de modificar el estado que la oferta
exista, que queden contrataciones disponibles, que haya cupo y que el clan
disponga del dinero necesario. Los aventureros muertos que todavía pertenecen
al clan también ocupan cupo.

## Iglesia implementada

La iglesia consulta los cuerpos recuperados que permanecen en el clan y
permite resucitarlos o enterrarlos con honores. La resurrección cuesta el 70%
de la contratación equivalente, conserva la identidad y el progreso del
aventurero y solo se realiza cuando el clan posee dinero suficiente.

El entierro traslada al muerto al historial de eliminados y libera su lugar en
el cupo. El memorial conserva el orden de los aventureros enterrados y de los
caídos cuyos cuerpos no pudieron recuperarse, sin mezclar a quienes dejaron el
clan con vida.

## Gestión de aventureros y grupos implementada

Los integrantes se buscan mediante su identificador interno, ignorando los
espacios exteriores y las diferencias entre mayúsculas y minúsculas. El clan
puede listar exclusivamente a sus aventureros vivos y expulsar a uno de ellos
sin coste, siempre que la operación no deje al clan sin ningún integrante
vivo. La baja conserva sus datos en el historial con el motivo
`servicios_finalizados`.

La formación para una futura expedición recibe una selección temporal de IDs y
admite desde uno hasta `3, 4, 5, 6 o 7` integrantes según el nivel del clan. La
selección conserva el orden elegido, rechaza muertos, ausentes y duplicados, y
no modifica ni guarda la partida. El sistema de expediciones utilizará este
resultado para crear posteriormente los estados temporales de combate.

## Combate básico implementado

La Mazmorra de los Limos cuenta con diez criaturas y diez oleadas fijas. Al
iniciar una oleada se crean estados temporales independientes, se calcula una
sola vez el orden por velocidad y los empates se resuelven mediante d100.

Cada ataque usa una tirada para determinar crítico, impacto o fallo. El crítico
base es 5%, su probabilidad total tiene un máximo de 90% y el daño crítico es
del 200%. Después de aplicar crítico y efectividad se resta la defensa, con un
mínimo de un punto para todo ataque que impacte.

El motor resuelve rondas hasta victoria, derrota o un límite de 30 rondas y
devuelve la experiencia y el dinero provisionales de cada enemigo derrotado.
No modifica los registros persistentes ni decide todavía si el botín se
entrega: esa responsabilidad corresponderá al futuro servicio de expediciones.

## Tecnologías

- Python 3.11 o superior.
- Tkinter.
- Archivos JSON.
- Anotaciones de tipo compatibles con Pylance y mypy.
- `unittest` para pruebas automatizadas.

## Estructura

```text
gestion-clan-ENOM/
├── assets/             Imágenes, fondos e iconos
├── catalogos/          Datos fijos de aventureros, habilidades y mazmorras
├── datos/              Archivos JSON de la partida
├── documentacion/      Reglas y organización del proyecto
├── interfaz/           Ventanas y componentes de Tkinter
├── modelos/            Tipos y estructuras de datos
├── servicios/          Lógica del juego
├── tests/              Pruebas automatizadas
├── configuracion.py    Constantes generales
└── main.py             Punto de entrada
```

La descripción completa de cada módulo se encuentra en `documentacion/estructura.md`.

## Ejecución

La aplicación todavía no tiene una versión jugable. Durante esta etapa se pueden ejecutar las pruebas con:

```bash
python -m unittest discover -s tests -v
```

