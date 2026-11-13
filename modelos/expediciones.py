"""Tipos temporales y resultados utilizados por las expediciones."""

from typing import Literal, TypeAlias, TypedDict

from modelos.combate import AventureroCombate, ResultadoOleada
from modelos.tipos import (
    DificultadMazmorra,
    EstadoPartida,
    ResultadoExpedicion,
)


EstadoFlujoExpedicion: TypeAlias = Literal[
    "lista_para_oleada",
    "esperando_decision",
    "finalizada",
    "consecuencias_aplicadas",
]


class EstadoExpedicion(TypedDict):
    """Conserva el progreso temporal de una incursión no persistente."""

    mazmorra_id: str
    dificultad: DificultadMazmorra
    proxima_oleada: int
    oleadas_superadas: int
    aventureros: list[AventureroCombate]
    experiencia_acumulada: int
    dinero_acumulado: int
    estado_flujo: EstadoFlujoExpedicion
    resultado_final: ResultadoExpedicion | None
    ultima_oleada: ResultadoOleada | None


class ResultadoConsecuenciasExpedicion(TypedDict):
    """Resume los cambios de dominio aplicados al terminar una expedición."""

    dinero_entregado: int
    experiencia_por_superviviente: int
    supervivientes_ids: list[str]
    muertos_ids: list[str]
    mazmorra_completada: bool


class ResumenCierreExpedicion(ResultadoConsecuenciasExpedicion):
    """Agrega al resumen el desenlace y el estado final de la partida."""

    resultado: ResultadoExpedicion
    estado_partida: EstadoPartida
