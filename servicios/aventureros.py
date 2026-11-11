"""Creación, búsqueda, selección y eliminación de aventureros."""

from random import Random

from catalogos.nombres import elegir_nombre
from catalogos.plantillas import CATALOGO_PLANTILLAS, PLANTILLAS_INICIALES
from configuracion import MAXIMO_INTEGRANTES_GRUPO, NIVEL_MAXIMO_CLAN
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


class GrupoVacioError(ValueError):
    """Indica que una expedición no posee aventureros seleccionados."""


class GrupoExcedeLimiteError(ValueError):
    """Indica que el grupo supera el máximo permitido por el clan."""


class AventureroRepetidoEnGrupoError(ValueError):
    """Indica que un integrante fue seleccionado más de una vez."""


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


def calcular_maximo_grupo(nivel_clan: int) -> int:
    """Calcula cuántos aventureros puede enviar el clan a una expedición.

    Args:
        nivel_clan: Nivel actual del clan, comprendido entre uno y cinco.

    Returns:
        El máximo progresivo de tres a siete integrantes.

    Raises:
        ValueError: Si el nivel no pertenece al intervalo permitido.
    """

    if not 1 <= nivel_clan <= NIVEL_MAXIMO_CLAN:
        raise ValueError(
            f"El nivel del clan debe estar entre 1 y {NIVEL_MAXIMO_CLAN}."
        )

    return min(nivel_clan + 2, MAXIMO_INTEGRANTES_GRUPO)


def seleccionar_grupo(
    datos_activos: list[AventureroActivo],
    nivel_clan: int,
    aventureros_ids: list[str],
) -> list[AventureroActivo]:
    """Valida y resuelve una selección temporal para una expedición.

    La selección no se persiste ni modifica sus listas de entrada. El grupo
    resultante conserva el orden elegido y contiene referencias a los
    registros originales de los integrantes vivos.

    Args:
        datos_activos: Integrantes vivos y muertos que ocupan cupo.
        nivel_clan: Nivel utilizado para calcular el máximo permitido.
        aventureros_ids: Identificadores elegidos por el jugador.

    Returns:
        Una lista nueva con los aventureros vivos, en el orden solicitado.

    Raises:
        ValueError: Si el nivel del clan no es válido.
        GrupoVacioError: Si no se seleccionó ningún integrante.
        GrupoExcedeLimiteError: Si la selección supera el máximo permitido.
        AventureroRepetidoEnGrupoError: Si un ID normalizado está repetido.
        AventureroNoEncontradoError: Si algún ID no pertenece al clan.
        AventureroNoEstaVivoError: Si algún integrante está muerto.
    """

    maximo: int = calcular_maximo_grupo(nivel_clan)
    if not aventureros_ids:
        raise GrupoVacioError(
            "Debe seleccionar al menos un aventurero para la expedición."
        )
    if len(aventureros_ids) > maximo:
        raise GrupoExcedeLimiteError(
            f"El clan de nivel {nivel_clan} puede enviar como máximo "
            f"{maximo} aventureros."
        )

    ids_normalizados: list[str] = [
        normalizar_id_aventurero(aventurero_id)
        for aventurero_id in aventureros_ids
    ]
    if len(set(ids_normalizados)) != len(ids_normalizados):
        raise AventureroRepetidoEnGrupoError(
            "Un aventurero no puede ocupar más de un lugar en el grupo."
        )

    return [
        buscar_aventurero_vivo(datos_activos, aventurero_id)
        for aventurero_id in ids_normalizados
    ]


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

