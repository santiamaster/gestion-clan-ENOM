"""Preparación, avance y cierre temporal de expediciones."""

from copy import deepcopy
from random import Random

from catalogos.enemigos import CATALOGO_ENEMIGOS
from catalogos.mazmorras import CATALOGO_MAZMORRAS, MAZMORRA_LIMOS
from catalogos.plantillas import CATALOGO_PLANTILLAS
from configuracion import (
    BONIFICACION_COMPLETAR_MAZMORRA_LIMOS,
    BONIFICACION_DINERO_POR_OLEADA,
    CANTIDAD_OLEADAS_MAZMORRA,
)
from modelos.combate import (
    AventureroCombate,
    DefinicionMazmorra,
    DefinicionOleada,
    EnemigoCombate,
    ResultadoOleada,
)
from modelos.expediciones import EstadoExpedicion
from modelos.tipos import AventureroActivo, EstadoClan
from servicios.aventureros import seleccionar_grupo
from servicios.combate import (
    crear_aventurero_combate,
    crear_enemigos_oleada,
    resolver_oleada,
)


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


def calcular_dinero_oleada(dinero_base: int, numero_oleada: int) -> int:
    """Aplica la bonificación progresiva al dinero de una oleada.

    Args:
        dinero_base: Suma sin bonificación de los enemigos derrotados.
        numero_oleada: Posición de la oleada, comprendida entre uno y diez.

    Returns:
        El dinero bonificado y redondeado hacia abajo.

    Raises:
        ValueError: Si el dinero es negativo o la oleada queda fuera del
            dominio de la mazmorra.
    """

    if dinero_base < 0:
        raise ValueError("El dinero base de una oleada no puede ser negativo.")
    if not 1 <= numero_oleada <= CANTIDAD_OLEADAS_MAZMORRA:
        raise ValueError(
            "El número de oleada debe estar entre 1 y "
            f"{CANTIDAD_OLEADAS_MAZMORRA}."
        )

    porcentaje: int = 100 + (
        BONIFICACION_DINERO_POR_OLEADA * (numero_oleada - 1)
    )
    return dinero_base * porcentaje // 100


def _obtener_oleada(expedicion: EstadoExpedicion) -> DefinicionOleada:
    """Obtiene la definición correspondiente al avance temporal recibido."""

    mazmorra: DefinicionMazmorra | None = CATALOGO_MAZMORRAS.get(
        expedicion["mazmorra_id"]
    )
    if mazmorra is None:
        raise EstadoExpedicionInvalidoError(
            "La expedición referencia una mazmorra inexistente."
        )

    numero: int = expedicion["proxima_oleada"]
    oleada: DefinicionOleada | None = next(
        (
            definicion
            for definicion in mazmorra["oleadas"]
            if definicion["numero"] == numero
        ),
        None,
    )
    if oleada is None:
        raise EstadoExpedicionInvalidoError(
            f"La mazmorra no contiene la oleada {numero}."
        )
    return oleada


def resolver_siguiente_oleada(
    expedicion: EstadoExpedicion,
    generador: Random,
) -> ResultadoOleada:
    """Resuelve la próxima oleada y actualiza solamente el estado temporal.

    Las recompensas permanecen en pozos provisionales hasta que otro servicio
    cierre la expedición. La vida de los aventureros se conserva entre
    oleadas y el último resultado se guarda como una copia histórica.

    Args:
        expedicion: Flujo temporal preparado para combatir.
        generador: Fuente de azar compartida con el motor de combate.

    Returns:
        El resultado inmediato producido por el motor de combate.

    Raises:
        TransicionExpedicionInvalidaError: Si el flujo no admite combatir.
        EstadoExpedicionInvalidoError: Si falta la definición de la oleada.
    """

    if expedicion["estado_flujo"] != "lista_para_oleada":
        raise TransicionExpedicionInvalidaError(
            "La expedición no está preparada para resolver una oleada."
        )

    numero_oleada: int = expedicion["proxima_oleada"]
    definicion: DefinicionOleada = _obtener_oleada(expedicion)
    enemigos: list[EnemigoCombate] = crear_enemigos_oleada(
        definicion,
        CATALOGO_ENEMIGOS,
    )
    resultado: ResultadoOleada = resolver_oleada(
        expedicion["aventureros"],
        enemigos,
        generador,
    )

    dinero_oleada: int = calcular_dinero_oleada(
        resultado["dinero_obtenido"],
        numero_oleada,
    )
    expedicion["aventureros"] = resultado["aventureros"]
    expedicion["experiencia_acumulada"] += resultado["experiencia_obtenida"]
    expedicion["dinero_acumulado"] += dinero_oleada
    expedicion["ultima_oleada"] = deepcopy(resultado)

    if resultado["resultado"] == "victoria":
        expedicion["oleadas_superadas"] += 1
        expedicion["proxima_oleada"] += 1
        if numero_oleada == CANTIDAD_OLEADAS_MAZMORRA:
            expedicion["dinero_acumulado"] += (
                BONIFICACION_COMPLETAR_MAZMORRA_LIMOS
            )
            expedicion["estado_flujo"] = "finalizada"
            expedicion["resultado_final"] = "mazmorra_completada"
        else:
            expedicion["estado_flujo"] = "esperando_decision"
    elif resultado["resultado"] == "derrota":
        expedicion["estado_flujo"] = "finalizada"
        expedicion["resultado_final"] = "derrota_total"
    else:
        expedicion["estado_flujo"] = "finalizada"
        expedicion["resultado_final"] = "limite_de_rondas"

    return resultado


def continuar_expedicion(expedicion: EstadoExpedicion) -> None:
    """Habilita la siguiente oleada después de una victoria intermedia.

    Args:
        expedicion: Estado temporal que espera la decisión del jugador.

    Raises:
        TransicionExpedicionInvalidaError: Si no corresponde continuar.
    """

    if expedicion["estado_flujo"] != "esperando_decision":
        raise TransicionExpedicionInvalidaError(
            "Solo puede continuarse después de superar una oleada."
        )
    expedicion["estado_flujo"] = "lista_para_oleada"


def retirar_expedicion(expedicion: EstadoExpedicion) -> None:
    """Finaliza voluntariamente una expedición entre dos oleadas.

    Args:
        expedicion: Estado temporal que espera la decisión del jugador.

    Raises:
        TransicionExpedicionInvalidaError: Si no corresponde retirarse.
    """

    if expedicion["estado_flujo"] != "esperando_decision":
        raise TransicionExpedicionInvalidaError(
            "Solo puede retirarse después de superar una oleada."
        )
    expedicion["estado_flujo"] = "finalizada"
    expedicion["resultado_final"] = "retirada"

