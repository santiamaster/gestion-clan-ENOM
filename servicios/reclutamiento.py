"""Generación de ofertas y contratación de aventureros."""

from configuracion import NIVEL_MAXIMO_CLAN


def _validar_nivel_clan(nivel_clan: int) -> None:
    """Valida que un nivel pertenezca al dominio definido para el clan.

    Args:
        nivel_clan: Nivel que se utilizará para calcular el mercado.

    Raises:
        ValueError: Si el nivel no se encuentra entre 1 y 5.
    """

    if not 1 <= nivel_clan <= NIVEL_MAXIMO_CLAN:
        raise ValueError(
            f"El nivel del clan debe estar entre 1 y {NIVEL_MAXIMO_CLAN}."
        )


def calcular_cantidad_ofertas(nivel_clan: int) -> int:
    """Calcula cuántos candidatos muestra una renovación del mercado.

    Args:
        nivel_clan: Nivel actual del clan, comprendido entre 1 y 5.

    Returns:
        El doble del nivel del clan.

    Raises:
        ValueError: Si el nivel queda fuera del intervalo permitido.
    """

    _validar_nivel_clan(nivel_clan)
    return nivel_clan * 2


def calcular_limite_contrataciones(nivel_clan: int) -> int:
    """Calcula cuántos candidatos pueden contratarse por renovación.

    Args:
        nivel_clan: Nivel actual del clan, comprendido entre 1 y 5.

    Returns:
        Una cantidad de contrataciones igual al nivel del clan.

    Raises:
        ValueError: Si el nivel queda fuera del intervalo permitido.
    """

    _validar_nivel_clan(nivel_clan)
    return nivel_clan

