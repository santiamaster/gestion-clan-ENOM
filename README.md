# Gestión de Clan ENOM

Proyecto integrador de Programación II desarrollado en Python con Tkinter.

El programa permitirá administrar un clan de aventureros de ENOM, reclutar integrantes, formar grupos, explorar mazmorras, resolver combates por oleadas y gestionar a los aventureros caídos.

## Estado del proyecto

El proyecto se encuentra en la etapa de diseño y construcción de sus modelos. Ya están definidos:

- Los tipos compartidos y estructuras `TypedDict`.
- Las quince plantillas de aventureros.
- Las quince habilidades profesionales.
- Las reglas principales de progresión, combate y persistencia.

La interfaz, el motor de combate, los enemigos y las mazmorras todavía están pendientes.

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
python -m unittest
```

