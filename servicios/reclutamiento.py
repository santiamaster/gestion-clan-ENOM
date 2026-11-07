"""Generación de ofertas y contratación de aventureros."""

from random import Random

from catalogos.nombres import elegir_nombre
from catalogos.plantillas import CATALOGO_PLANTILLAS
from configuracion import NIVEL_MAXIMO_CLAN
from modelos.tipos import EstadoClan, OfertaReclutamiento, PlantillaAventurero
from servicios.calculos import calcular_coste_contratacion


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


def generar_ofertas(
    nivel_clan: int,
    generador: Random,
) -> list[OfertaReclutamiento]:
    """Genera una lista nueva de candidatos para el gremio.

    Las plantillas se eligen con reemplazo, por lo que una misma profesión
    puede aparecer varias veces con distintos nombres o niveles.

    Args:
        nivel_clan: Nivel actual del clan, comprendido entre 1 y 5.
        generador: Fuente de azar inyectable para obtener resultados
            deterministas en las pruebas.

    Returns:
        Las ofertas completas de la nueva renovación.

    Raises:
        ValueError: Si el nivel del clan queda fuera del dominio permitido.
    """

    cantidad: int = calcular_cantidad_ofertas(nivel_clan)
    plantillas: tuple[PlantillaAventurero, ...] = tuple(
        CATALOGO_PLANTILLAS.values()
    )
    ofertas: list[OfertaReclutamiento] = []

    for numero in range(1, cantidad + 1):
        plantilla: PlantillaAventurero = generador.choice(plantillas)
        nivel: int = generador.randint(1, nivel_clan)
        oferta: OfertaReclutamiento = {
            "id_oferta": f"OF-{numero:02d}",
            "nombre": elegir_nombre(plantilla["sexo"], generador),
            "plantilla_id": plantilla["id"],
            "nivel": nivel,
            "coste": calcular_coste_contratacion(
                plantilla["coste_base"],
                nivel,
            ),
        }
        ofertas.append(oferta)

    return ofertas


def renovar_mercado(
    estado_clan: EstadoClan,
    generador: Random,
) -> None:
    """Reemplaza el mercado y habilita las contrataciones del nuevo ciclo.

    Args:
        estado_clan: Estado persistente que recibirá las ofertas nuevas.
        generador: Fuente de azar utilizada para generar los candidatos.

    Raises:
        ValueError: Si el nivel guardado del clan queda fuera del dominio.
    """

    nivel_clan: int = estado_clan["nivel"]
    ofertas_nuevas: list[OfertaReclutamiento] = generar_ofertas(
        nivel_clan,
        generador,
    )
    limite: int = calcular_limite_contrataciones(nivel_clan)

    estado_clan["ofertas_reclutamiento"] = ofertas_nuevas
    estado_clan["contrataciones_restantes"] = limite

