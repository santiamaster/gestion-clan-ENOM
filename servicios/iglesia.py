"""Consulta, resurrección y entierro de aventureros caídos."""

from catalogos.plantillas import CATALOGO_PLANTILLAS
from modelos.tipos import AventureroActivo, EstadoClan, PlantillaAventurero
from servicios.calculos import (
    aplicar_descuento_resurreccion,
    calcular_coste_contratacion,
)


class AventureroNoEncontradoError(ValueError):
    """Indica que el ID no pertenece a un integrante activo del clan."""


class AventureroNoEstaMuertoError(ValueError):
    """Indica que el aventurero seleccionado todavía está vivo."""


class DineroInsuficienteResurreccionError(ValueError):
    """Indica que el clan no puede pagar el coste de la resurrección."""


def listar_aventureros_muertos(
    datos_activos: list[AventureroActivo],
) -> list[AventureroActivo]:
    """Devuelve los cuerpos recuperados que todavía pertenecen al clan.

    Args:
        datos_activos: Integrantes vivos y muertos que actualmente ocupan
            cupo.

    Returns:
        Una lista nueva que conserva únicamente los registros muertos.
    """

    return [
        aventurero
        for aventurero in datos_activos
        if aventurero["estado"] == "muerto"
    ]


def buscar_aventurero_muerto(
    datos_activos: list[AventureroActivo],
    aventurero_id: str,
) -> AventureroActivo:
    """Busca un cuerpo recuperado mediante su identificador interno.

    Args:
        datos_activos: Integrantes vivos y muertos que ocupan cupo.
        aventurero_id: Identificador que será normalizado antes de buscar.

    Returns:
        El registro muerto existente dentro de ``datos_activos``.

    Raises:
        AventureroNoEncontradoError: Si el ID no pertenece a un integrante.
        AventureroNoEstaMuertoError: Si el integrante encontrado está vivo.
    """

    identificador_normalizado: str = aventurero_id.strip().upper()
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
    if aventurero["estado"] != "muerto":
        raise AventureroNoEstaMuertoError(
            f"El aventurero '{identificador_normalizado}' no está muerto."
        )

    return aventurero


def calcular_coste_resurreccion(
    aventurero: AventureroActivo,
) -> int:
    """Calcula cuánto cuesta resucitar a un aventurero recuperado.

    Args:
        aventurero: Registro cuyo nivel y plantilla determinan el precio.

    Returns:
        El 70% del coste de contratar la misma profesión y nivel.
    """

    plantilla: PlantillaAventurero = CATALOGO_PLANTILLAS[
        aventurero["plantilla_id"]
    ]
    coste_contratacion: int = calcular_coste_contratacion(
        plantilla["coste_base"],
        aventurero["nivel"],
    )
    return aplicar_descuento_resurreccion(coste_contratacion)


def resucitar_aventurero(
    estado_clan: EstadoClan,
    datos_activos: list[AventureroActivo],
    aventurero_id: str,
) -> AventureroActivo:
    """Resucita un cuerpo recuperado y descuenta su coste al clan.

    Todas las condiciones se validan antes de modificar el dinero o el
    aventurero. El integrante conserva su identidad, plantilla, nivel y
    experiencia porque nunca abandona la lista de activos.

    Args:
        estado_clan: Estado persistente que contiene el dinero disponible.
        datos_activos: Integrantes vivos y muertos que actualmente ocupan
            cupo.
        aventurero_id: Identificador del muerto que se desea resucitar.

    Returns:
        El registro existente con su estado cambiado a ``"vivo"``.

    Raises:
        AventureroNoEncontradoError: Si el ID no pertenece a un integrante.
        AventureroNoEstaMuertoError: Si el integrante encontrado está vivo.
        DineroInsuficienteResurreccionError: Si el clan no alcanza a pagar.
    """

    aventurero: AventureroActivo = buscar_aventurero_muerto(
        datos_activos,
        aventurero_id,
    )
    coste: int = calcular_coste_resurreccion(aventurero)

    if estado_clan["dinero"] < coste:
        raise DineroInsuficienteResurreccionError(
            "El clan no posee dinero suficiente para esta resurrección."
        )

    estado_clan["dinero"] -= coste
    aventurero["estado"] = "vivo"
    return aventurero

