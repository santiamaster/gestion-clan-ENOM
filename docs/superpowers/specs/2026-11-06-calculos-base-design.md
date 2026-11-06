# Diseño del bloque de cálculos base

## Intención

Centralizar las reglas matemáticas del juego en funciones puras, fuertemente
tipadas, documentadas y sin dependencias de Tkinter, JSON ni estado global.
Esto permite reutilizarlas desde combate, reclutamiento, clan e interfaz y
comprobar cada regla mediante pruebas unitarias.

## Alcance

El bloque implementará:

- Estadísticas por nivel.
- Experiencia necesaria y ascensos múltiples.
- Conservación de experiencia sobrante.
- Límite de nivel 10.
- Cupo del clan por nivel.
- Coste de contratación por nivel.
- Probabilidad crítica total.
- Multiplicadores de efectividad y crítico.
- Daño final entero.

No incluirá todavía:

- Tiradas aleatorias de d100.
- Defensa del objetivo.
- Selección de objetivos.
- Habilidades particulares.
- Recompensas de mazmorras o resurrección.
- Modificación de listas, archivos JSON o widgets.

## Enfoques considerados

### Funciones puras independientes — seleccionado

Cada función recibe valores y devuelve un resultado sin modificar datos
externos. Es el enfoque más sencillo de probar, reutilizar y explicar.

### Una función general para todos los cálculos

Reduce la cantidad de funciones, pero mezcla reglas sin relación directa y
dificulta las pruebas y el mantenimiento.

### Clases calculadoras

Podrían encapsular las reglas, pero por ahora no existe estado que justifique
crear objetos. Agregarían estructura sin aportar una ventaja concreta.

## Contratos propuestos

```python
def calcular_estadisticas(
    plantilla: PlantillaAventurero,
    nivel: int,
) -> Estadisticas:
    ...


def calcular_experiencia_necesaria(nivel_actual: int) -> int:
    ...


def aplicar_experiencia(
    nivel_actual: int,
    experiencia_actual: int,
    experiencia_ganada: int,
) -> tuple[int, int]:
    ...


def calcular_cupo_clan(nivel_clan: int) -> int:
    ...


def calcular_coste_contratacion(coste_base: int, nivel: int) -> int:
    ...


def calcular_probabilidad_critico(critico_adicional: int) -> int:
    ...


def calcular_dano_final(
    dano_base: int,
    efectividad: EfectividadAtaque,
    es_critico: bool,
) -> int:
    ...
```

## Reglas exactas

- Estadística final: `estadística racial + crecimiento profesional × nivel`.
- La fórmula se aplica desde nivel 1; por lo tanto, un aventurero inicial ya
  recibe una vez el crecimiento de su profesión.
- Para subir de nivel se necesita `nivel actual × 100` de experiencia.
- Un aventurero puede subir varios niveles en una sola entrega de experiencia.
- La experiencia sobrante se conserva.
- Al alcanzar el nivel 10 deja de ascender; la experiencia sobrante queda en
  cero porque ya no tiene uso en esta versión.
- Cupo del clan: `nivel del clan × 5`.
- Contratación: `coste base × nivel del aventurero`.
- Crítico total: `5 + crítico adicional`, limitado al intervalo de 0 a 100.
- Ataque efectivo: multiplicador `1.50`.
- Ataque neutral: multiplicador `1.00`.
- Ataque inefectivo: multiplicador `0.50`.
- Un crítico vuelve a multiplicar el daño por `1.50`.
- Todos los resultados decimales se redondean hacia abajo con `math.floor()`.
- Se rechazará con `ValueError` cualquier nivel, experiencia, coste o daño
  negativo, así como niveles fuera de sus límites.

## Tipado

Se agregará:

```python
EfectividadAtaque: TypeAlias = Literal[
    "efectivo",
    "neutral",
    "inefectivo",
]
```

## Comprobación

`tests/test_calculos.py` cubrirá valores normales, límites, ascensos múltiples,
experiencia sobrante, nivel máximo, redondeo hacia abajo, efectividad, crítico
y entradas inválidas.

