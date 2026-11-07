"""Coordinación de la creación y el guardado de partidas."""

from pathlib import Path
from random import Random

from modelos.tipos import AventureroActivo, AventureroEliminado, EstadoClan
from servicios.aventureros import crear_aventureros_iniciales
from servicios.clan import crear_estado_inicial_clan
from servicios.persistencia import (
    DIRECTORIO_PARTIDA,
    ErrorPersistencia,
    existe_partida_guardada,
    guardar_partida,
)


class PartidaExistenteError(ErrorPersistencia):
    """Indica que una partida válida requiere autorización para reemplazarse."""


def crear_nueva_partida(
    nombre_clan: str,
    sobrescribir: bool = False,
    directorio: Path = DIRECTORIO_PARTIDA,
    generador: Random | None = None,
) -> tuple[
    EstadoClan,
    list[AventureroActivo],
    list[AventureroEliminado],
]:
    """Construye y guarda todos los datos iniciales de una partida.

    Args:
        nombre_clan: Nombre elegido por el jugador para su clan.
        sobrescribir: Autoriza reemplazar una partida completa y válida.
        directorio: Carpeta que contendrá los tres archivos JSON.
        generador: Fuente de azar opcional para controlar los nombres.

    Returns:
        El estado del clan, los tres aventureros activos y el historial vacío.

    Raises:
        PartidaExistenteError: Si ya existe una partida y no se autorizó
            reemplazarla.
        ErrorPersistencia: Si los archivos existentes están dañados o no
            pueden leerse o escribirse.
    """

    if existe_partida_guardada(directorio) and not sobrescribir:
        raise PartidaExistenteError(
            "Ya existe una partida guardada. Debe confirmar su reemplazo."
        )

    generador_nombres: Random = generador if generador is not None else Random()
    estado_clan: EstadoClan = crear_estado_inicial_clan(nombre_clan)
    datos_activos: list[AventureroActivo] = crear_aventureros_iniciales(
        generador_nombres
    )
    datos_eliminados: list[AventureroEliminado] = []

    guardar_partida(
        estado_clan,
        datos_activos,
        datos_eliminados,
        directorio,
    )
    return estado_clan, datos_activos, datos_eliminados
