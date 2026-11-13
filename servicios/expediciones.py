"""Preparación, avance y cierre temporal de expediciones."""

from catalogos.mazmorras import CATALOGO_MAZMORRAS, MAZMORRA_LIMOS
from catalogos.plantillas import CATALOGO_PLANTILLAS
from modelos.combate import AventureroCombate, DefinicionMazmorra
from modelos.expediciones import EstadoExpedicion
from modelos.tipos import AventureroActivo, EstadoClan
from servicios.aventureros import seleccionar_grupo
from servicios.combate import crear_aventurero_combate


class MazmorraNoEncontradaError(ValueError):
    """Indica que el identificador no pertenece al catálogo de mazmorras."""


class MazmorraNoDisponibleError(ValueError):
    """Indica que una mazmorra conocida todavía no puede jugarse."""


class EstadoExpedicionInvalidoError(ValueError):
    """Indica que el estado de la partida o expedición impide la operación."""


class TransicionExpedicionInvalidaError(ValueError):
    """Indica que una acción no corresponde al punto actual del flujo."""


class ExpedicionYaAplicadaError(ValueError):
    """Indica que las consecuencias de la expedición ya fueron publicadas."""


def iniciar_expedicion(
    estado_clan: EstadoClan,
    datos_activos: list[AventureroActivo],
    aventureros_ids: list[str],
    mazmorra_id: str,
) -> EstadoExpedicion:
    """Crea una expedición temporal con un grupo válido de aventureros vivos.

    La operación valida el estado general, la disponibilidad de la mazmorra y
    la selección antes de construir combatientes independientes. No modifica
    los registros persistentes recibidos.

    Args:
        estado_clan: Progreso persistente que determina partida y grupo máximo.
        datos_activos: Integrantes vivos y muertos que todavía ocupan cupo.
        aventureros_ids: Identificadores elegidos, en el orden del grupo.
        mazmorra_id: Identificador interno de la mazmorra solicitada.

    Returns:
        Un estado temporal preparado para resolver la primera oleada.

    Raises:
        EstadoExpedicionInvalidoError: Si la partida ya terminó.
        MazmorraNoEncontradaError: Si el identificador no existe.
        MazmorraNoDisponibleError: Si la mazmorra aún no está implementada.
        ValueError: Si la selección del grupo incumple sus reglas.
    """

    if estado_clan["estado_partida"] != "en_curso":
        raise EstadoExpedicionInvalidoError(
            "Solo puede iniciarse una expedición durante una partida en curso."
        )

    mazmorra: DefinicionMazmorra | None = CATALOGO_MAZMORRAS.get(mazmorra_id)
    if mazmorra is None:
        raise MazmorraNoEncontradaError(
            f"No existe una mazmorra con el ID '{mazmorra_id}'."
        )
    if mazmorra["id"] != MAZMORRA_LIMOS["id"]:
        raise MazmorraNoDisponibleError(
            "En esta versión solo está disponible la Mazmorra de los Limos."
        )

    grupo: list[AventureroActivo] = seleccionar_grupo(
        datos_activos,
        estado_clan["nivel"],
        aventureros_ids,
    )
    combatientes: list[AventureroCombate] = [
        crear_aventurero_combate(aventurero, CATALOGO_PLANTILLAS)
        for aventurero in grupo
    ]

    return {
        "mazmorra_id": mazmorra["id"],
        "dificultad": mazmorra["dificultad"],
        "proxima_oleada": 1,
        "oleadas_superadas": 0,
        "aventureros": combatientes,
        "experiencia_acumulada": 0,
        "dinero_acumulado": 0,
        "estado_flujo": "lista_para_oleada",
        "resultado_final": None,
        "ultima_oleada": None,
    }

