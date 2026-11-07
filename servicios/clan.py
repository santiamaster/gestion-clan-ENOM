"""Gestión del progreso, cupo y estado general del clan."""

from modelos.tipos import EstadoClan


class NombreClanInvalidoError(ValueError):
    """Indica que el nombre elegido para el clan está vacío."""


def crear_estado_inicial_clan(nombre_clan: str) -> EstadoClan:
    """Construye el estado general de una partida recién iniciada.

    Args:
        nombre_clan: Nombre elegido por el jugador.

    Returns:
        Un clan de nivel uno con todo su progreso inicializado.

    Raises:
        NombreClanInvalidoError: Si el nombre queda vacío al quitar espacios.
    """

    nombre_normalizado: str = nombre_clan.strip()
    if nombre_normalizado == "":
        raise NombreClanInvalidoError("El nombre del clan no puede estar vacío.")

    return {
        "nombre": nombre_normalizado,
        "nivel": 1,
        "dinero": 0,
        "siguiente_id_aventurero": 4,
        "contrataciones_restantes": 0,
        "estado_partida": "en_curso",
        "mazmorras_completadas": {
            "mazmorra_1": False,
            "mazmorra_2": False,
            "mazmorra_3": False,
            "mazmorra_4": False,
            "mazmorra_5": False,
        },
        "ofertas_reclutamiento": [],
    }

