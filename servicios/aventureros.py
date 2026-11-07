"""Creación, búsqueda, selección y eliminación de aventureros."""

from random import Random

from catalogos.nombres import elegir_nombre
from catalogos.plantillas import CATALOGO_PLANTILLAS, PLANTILLAS_INICIALES
from modelos.tipos import AventureroActivo, PlantillaAventurero


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

