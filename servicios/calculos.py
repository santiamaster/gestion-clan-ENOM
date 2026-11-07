"""Cálculos de estadísticas, experiencia, costes y recompensas."""

from math import floor

from configuracion import (
    BONO_ESTADISTICAS_NIVEL_MAXIMO,
    CRITICO_BASE,
    MULTIPLICADOR_ATAQUE_EFECTIVO,
    MULTIPLICADOR_ATAQUE_INEFECTIVO,
    MULTIPLICADOR_ATAQUE_NEUTRAL,
    MULTIPLICADOR_CRITICO,
    NIVEL_MAXIMO_AVENTURERO,
    NIVEL_MAXIMO_CLAN,
)
from modelos.tipos import EfectividadAtaque, Estadisticas, PlantillaAventurero


def calcular_estadisticas(
    plantilla: PlantillaAventurero,
    nivel: int,
) -> Estadisticas:
    """Calcula las estadísticas de una plantilla para un nivel determinado.

    En el nivel máximo se aplica un 20% adicional a cada estadística. Todo
    resultado decimal se redondea hacia abajo según la regla general de ENOM.

    Args:
        plantilla: Datos raciales y crecimiento profesional del aventurero.
        nivel: Nivel del aventurero, comprendido entre 1 y 10.

    Returns:
        Las cuatro estadísticas finales del aventurero.

    Raises:
        ValueError: Si el nivel está fuera del intervalo permitido.
    """

    if not 1 <= nivel <= NIVEL_MAXIMO_AVENTURERO:
        raise ValueError(
            f"El nivel debe estar entre 1 y {NIVEL_MAXIMO_AVENTURERO}."
        )

    estadisticas: Estadisticas = {
        "vida": (
            plantilla["estadisticas_raza"]["vida"]
            + plantilla["crecimiento_profesion"]["vida"] * nivel
        ),
        "dano": (
            plantilla["estadisticas_raza"]["dano"]
            + plantilla["crecimiento_profesion"]["dano"] * nivel
        ),
        "defensa": (
            plantilla["estadisticas_raza"]["defensa"]
            + plantilla["crecimiento_profesion"]["defensa"] * nivel
        ),
        "velocidad": (
            plantilla["estadisticas_raza"]["velocidad"]
            + plantilla["crecimiento_profesion"]["velocidad"] * nivel
        ),
    }

    if nivel == NIVEL_MAXIMO_AVENTURERO:
        return {
            "vida": floor(
                estadisticas["vida"] * BONO_ESTADISTICAS_NIVEL_MAXIMO
            ),
            "dano": floor(
                estadisticas["dano"] * BONO_ESTADISTICAS_NIVEL_MAXIMO
            ),
            "defensa": floor(
                estadisticas["defensa"] * BONO_ESTADISTICAS_NIVEL_MAXIMO
            ),
            "velocidad": floor(
                estadisticas["velocidad"] * BONO_ESTADISTICAS_NIVEL_MAXIMO
            ),
        }

    return estadisticas


def calcular_experiencia_necesaria(nivel_actual: int) -> int:
    """Devuelve la experiencia necesaria para alcanzar el siguiente nivel.

    Args:
        nivel_actual: Nivel del aventurero, comprendido entre 1 y 10.

    Returns:
        El umbral del siguiente nivel o cero si ya alcanzó el nivel máximo.

    Raises:
        ValueError: Si el nivel está fuera del intervalo permitido.
    """

    if not 1 <= nivel_actual <= NIVEL_MAXIMO_AVENTURERO:
        raise ValueError(
            f"El nivel debe estar entre 1 y {NIVEL_MAXIMO_AVENTURERO}."
        )

    if nivel_actual == NIVEL_MAXIMO_AVENTURERO:
        return 0

    return nivel_actual * 100


def aplicar_experiencia(
    nivel_actual: int,
    experiencia_actual: int,
    experiencia_ganada: int,
) -> tuple[int, int]:
    """Aplica experiencia y devuelve el nivel y el sobrante resultantes.

    La función permite varios ascensos consecutivos. Al alcanzar el nivel 10,
    la experiencia se establece en cero porque ya no tiene uso en esta versión.

    Args:
        nivel_actual: Nivel del aventurero antes de recibir experiencia.
        experiencia_actual: Experiencia acumulada hacia el siguiente nivel.
        experiencia_ganada: Experiencia obtenida en la expedición.

    Returns:
        Una tupla formada por el nivel final y la experiencia sobrante.

    Raises:
        ValueError: Si el nivel es inválido o alguna experiencia es negativa.
    """

    calcular_experiencia_necesaria(nivel_actual)
    if experiencia_actual < 0 or experiencia_ganada < 0:
        raise ValueError("La experiencia no puede ser negativa.")

    if nivel_actual == NIVEL_MAXIMO_AVENTURERO:
        return NIVEL_MAXIMO_AVENTURERO, 0

    nivel: int = nivel_actual
    experiencia: int = experiencia_actual + experiencia_ganada

    while nivel < NIVEL_MAXIMO_AVENTURERO:
        experiencia_necesaria: int = calcular_experiencia_necesaria(nivel)
        if experiencia < experiencia_necesaria:
            break

        experiencia -= experiencia_necesaria
        nivel += 1

    if nivel == NIVEL_MAXIMO_AVENTURERO:
        return nivel, 0

    return nivel, experiencia


def calcular_cupo_clan(nivel_clan: int) -> int:
    """Calcula la cantidad máxima de aventureros permitida en el clan.

    Args:
        nivel_clan: Nivel actual del clan, comprendido entre 1 y 5.

    Returns:
        El cupo correspondiente, desde 5 hasta 25 aventureros.

    Raises:
        ValueError: Si el nivel del clan está fuera del intervalo permitido.
    """

    if not 1 <= nivel_clan <= NIVEL_MAXIMO_CLAN:
        raise ValueError(
            f"El nivel del clan debe estar entre 1 y {NIVEL_MAXIMO_CLAN}."
        )

    return nivel_clan * 5


def calcular_coste_contratacion(coste_base: int, nivel: int) -> int:
    """Calcula el coste de contratar un aventurero según su nivel.

    Args:
        coste_base: Coste definido por la profesión del aventurero.
        nivel: Nivel del candidato, comprendido entre 1 y 10.

    Returns:
        El coste base multiplicado por el nivel del candidato.

    Raises:
        ValueError: Si el coste es negativo o el nivel es inválido.
    """

    if coste_base < 0:
        raise ValueError("El coste base no puede ser negativo.")
    if not 1 <= nivel <= NIVEL_MAXIMO_AVENTURERO:
        raise ValueError(
            f"El nivel debe estar entre 1 y {NIVEL_MAXIMO_AVENTURERO}."
        )

    return coste_base * nivel


def aplicar_descuento_resurreccion(coste_contratacion: int) -> int:
    """Calcula el 70% del coste de contratación equivalente.

    El resultado se redondea hacia abajo mediante división entera, de acuerdo
    con la regla general de ENOM.

    Args:
        coste_contratacion: Precio de contratar al mismo aventurero y nivel.

    Returns:
        El coste de resurrección con un descuento del 30%.

    Raises:
        ValueError: Si el coste de contratación recibido es negativo.
    """

    if coste_contratacion < 0:
        raise ValueError("El coste de contratación no puede ser negativo.")

    return coste_contratacion * 70 // 100


def calcular_probabilidad_critico(critico_adicional: int) -> int:
    """Calcula la probabilidad crítica total de un aventurero.

    Args:
        critico_adicional: Modificador propio de la profesión del aventurero.

    Returns:
        La suma del 5% base y el modificador, limitada entre 0 y 100.
    """

    probabilidad: int = CRITICO_BASE + critico_adicional
    return max(0, min(100, probabilidad))


def calcular_dano_final(
    dano_base: int,
    efectividad: EfectividadAtaque,
    es_critico: bool,
) -> int:
    """Aplica los multiplicadores de efectividad y crítico al daño base.

    Los multiplicadores se combinan antes de redondear una única vez hacia
    abajo. La defensa del objetivo se incorporará en un bloque posterior.

    Args:
        dano_base: Daño previo a efectividad y crítico.
        efectividad: Relación del ataque con el objetivo.
        es_critico: Indica si la tirada produjo un golpe crítico.

    Returns:
        El daño entero resultante de aplicar los multiplicadores.

    Raises:
        ValueError: Si el daño base es negativo.
    """

    if dano_base < 0:
        raise ValueError("El daño base no puede ser negativo.")

    multiplicadores: dict[EfectividadAtaque, float] = {
        "efectivo": MULTIPLICADOR_ATAQUE_EFECTIVO,
        "neutral": MULTIPLICADOR_ATAQUE_NEUTRAL,
        "inefectivo": MULTIPLICADOR_ATAQUE_INEFECTIVO,
    }
    multiplicador_critico: float = MULTIPLICADOR_CRITICO if es_critico else 1.0

    return floor(
        dano_base * multiplicadores[efectividad] * multiplicador_critico
    )

