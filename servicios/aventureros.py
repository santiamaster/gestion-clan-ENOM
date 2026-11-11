"""Creación, búsqueda, selección y eliminación de aventureros."""

from random import Random

from catalogos.nombres import elegir_nombre
from catalogos.plantillas import CATALOGO_PLANTILLAS, PLANTILLAS_INICIALES
from modelos.tipos import (
    AventureroActivo,
    AventureroEliminado,
    PlantillaAventurero,
)


class AventureroNoEncontradoError(ValueError):
    """Indica que el ID no pertenece a un integrante activo del clan."""


class AventureroNoEstaVivoError(ValueError):
    """Indica que una operación exclusiva para vivos recibió un muerto."""


class UltimoAventureroVivoError(ValueError):
    """Impide expulsar al único integrante vivo que queda en el clan."""


def normalizar_id_aventurero(aventurero_id: str) -> str:
    """Normaliza un identificador escrito por el usuario.

    Args:
        aventurero_id: Identificador que puede contener espacios exteriores o
            letras minúsculas.

    Returns:
        El identificador sin espacios exteriores y en mayúsculas.
    """

    return aventurero_id.strip().upper()


def buscar_aventurero_activo(
    datos_activos: list[AventureroActivo],
    aventurero_id: str,
) -> AventureroActivo:
    """Busca un integrante activo mediante su identificador interno.

    Args:
        datos_activos: Integrantes vivos y muertos que todavía ocupan cupo.
        aventurero_id: Identificador que será normalizado antes de buscar.

    Returns:
        El registro original existente dentro de ``datos_activos``.

    Raises:
        AventureroNoEncontradoError: Si el ID no pertenece a un integrante.
    """

    identificador_normalizado: str = normalizar_id_aventurero(aventurero_id)
    aventurero: AventureroActivo | None = next(
        (
            integrante
            for integrante in datos_activos
            if integrante["id"] == identificador_normalizado
        ),
        None,
    )

    if aventurero is None:
        raise AventureroNoEncontradoError(
            f"No existe un aventurero activo con el ID "
            f"'{identificador_normalizado}'."
        )

    return aventurero


def listar_aventureros_vivos(
    datos_activos: list[AventureroActivo],
) -> list[AventureroActivo]:
    """Lista los integrantes vivos que todavía pertenecen al clan.

    Args:
        datos_activos: Integrantes vivos y muertos que actualmente ocupan
            cupo.

    Returns:
        Una lista nueva con referencias a los vivos, en su orden original.
    """

    return [
        aventurero
        for aventurero in datos_activos
        if aventurero["estado"] == "vivo"
    ]


def buscar_aventurero_vivo(
    datos_activos: list[AventureroActivo],
    aventurero_id: str,
) -> AventureroActivo:
    """Busca por ID un integrante vivo del clan.

    Args:
        datos_activos: Integrantes vivos y muertos que actualmente ocupan
            cupo.
        aventurero_id: Identificador que será normalizado antes de buscar.

    Returns:
        El registro original del aventurero vivo.

    Raises:
        AventureroNoEncontradoError: Si el ID no pertenece a un integrante.
        AventureroNoEstaVivoError: Si el integrante encontrado está muerto.
    """

    aventurero: AventureroActivo = buscar_aventurero_activo(
        datos_activos,
        aventurero_id,
    )
    if aventurero["estado"] != "vivo":
        raise AventureroNoEstaVivoError(
            f"El aventurero '{aventurero['id']}' no está vivo."
        )

    return aventurero


def expulsar_aventurero(
    datos_activos: list[AventureroActivo],
    datos_eliminados: list[AventureroEliminado],
    aventurero_id: str,
) -> AventureroEliminado:
    """Expulsa a un integrante vivo sin dejar al clan sin miembros vivos.

    La existencia, el estado y la cantidad de integrantes vivos se validan
    antes de modificar las listas. La baja se guarda como un registro
    independiente al final del historial.

    Args:
        datos_activos: Integrantes vivos y muertos que actualmente ocupan
            cupo.
        datos_eliminados: Historial ordenado de integrantes fuera del clan.
        aventurero_id: Identificador del vivo que se desea expulsar.

    Returns:
        El registro histórico nuevo con sus datos y el motivo de la baja.

    Raises:
        AventureroNoEncontradoError: Si el ID no pertenece a un integrante.
        AventureroNoEstaVivoError: Si el integrante encontrado está muerto.
        UltimoAventureroVivoError: Si es el único vivo que queda en el clan.
    """

    aventurero: AventureroActivo = buscar_aventurero_vivo(
        datos_activos,
        aventurero_id,
    )
    vivos: list[AventureroActivo] = listar_aventureros_vivos(datos_activos)
    if len(vivos) <= 1:
        raise UltimoAventureroVivoError(
            "No se puede expulsar al último aventurero vivo del clan."
        )

    eliminado: AventureroEliminado = {
        "id": aventurero["id"],
        "nombre": aventurero["nombre"],
        "plantilla_id": aventurero["plantilla_id"],
        "nivel": aventurero["nivel"],
        "experiencia": aventurero["experiencia"],
        "estado": aventurero["estado"],
        "motivo_baja": "servicios_finalizados",
    }

    datos_eliminados.append(eliminado)
    datos_activos.remove(aventurero)
    return eliminado


def formatear_id_aventurero(numero: int) -> str:
    """Convierte un número positivo al identificador interno del aventurero.

    Args:
        numero: Número correlativo que se asignará al aventurero.

    Returns:
        Un identificador con el formato ``AV-0001``.

    Raises:
        ValueError: Si el número no es positivo.
    """

    if numero < 1:
        raise ValueError("El número de aventurero debe ser positivo.")
    return f"AV-{numero:04d}"


def crear_aventureros_iniciales(
    generador: Random,
) -> list[AventureroActivo]:
    """Crea el Soldado, Arquero y Hechicero de una partida nueva.

    Args:
        generador: Fuente de azar utilizada para elegir los nombres.

    Returns:
        Los tres aventureros vivos de nivel uno, en el orden acordado.
    """

    integrantes: list[AventureroActivo] = []
    for numero, plantilla_id in enumerate(PLANTILLAS_INICIALES, start=1):
        plantilla: PlantillaAventurero = CATALOGO_PLANTILLAS[plantilla_id]
        integrante: AventureroActivo = {
            "id": formatear_id_aventurero(numero),
            "nombre": elegir_nombre(plantilla["sexo"], generador),
            "plantilla_id": plantilla_id,
            "nivel": 1,
            "experiencia": 0,
            "estado": "vivo",
        }
        integrantes.append(integrante)

    return integrantes

