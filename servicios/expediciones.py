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
from modelos.expediciones import (
    EstadoExpedicion,
    ResultadoConsecuenciasExpedicion,
)
from modelos.tipos import AventureroActivo, AventureroEliminado, EstadoClan
from servicios.aventureros import seleccionar_grupo
from servicios.calculos import aplicar_experiencia
from servicios.combate import (
    crear_aventurero_combate,
    crear_enemigos_oleada,
    resolver_oleada,
)
from servicios.iglesia import calcular_coste_resurreccion


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


def _validar_cierre_en_memoria(
    expedicion: EstadoExpedicion,
    datos_activos: list[AventureroActivo],
) -> dict[str, AventureroActivo]:
    """Valida estado, IDs y plantillas antes de aplicar consecuencias."""

    if expedicion["estado_flujo"] == "consecuencias_aplicadas":
        raise ExpedicionYaAplicadaError(
            "Las consecuencias de esta expedición ya fueron aplicadas."
        )
    if (
        expedicion["estado_flujo"] != "finalizada"
        or expedicion["resultado_final"] is None
    ):
        raise EstadoExpedicionInvalidoError(
            "La expedición debe estar finalizada antes de aplicar consecuencias."
        )
    if not expedicion["aventureros"]:
        raise EstadoExpedicionInvalidoError(
            "La expedición no contiene integrantes para procesar."
        )

    activos_por_id: dict[str, AventureroActivo] = {
        aventurero["id"]: aventurero for aventurero in datos_activos
    }
    ids_expedicion: set[str] = set()
    for temporal in expedicion["aventureros"]:
        identificador: str = temporal["id"]
        if identificador in ids_expedicion:
            raise EstadoExpedicionInvalidoError(
                "La expedición contiene identificadores repetidos."
            )
        ids_expedicion.add(identificador)

        persistente: AventureroActivo | None = activos_por_id.get(identificador)
        if persistente is None:
            raise EstadoExpedicionInvalidoError(
                f"El aventurero '{identificador}' ya no pertenece al clan."
            )
        if persistente["plantilla_id"] != temporal["plantilla_id"]:
            raise EstadoExpedicionInvalidoError(
                f"La plantilla del aventurero '{identificador}' cambió."
            )

    return activos_por_id


def aplicar_consecuencias_expedicion(
    expedicion: EstadoExpedicion,
    estado_clan: EstadoClan,
    datos_activos: list[AventureroActivo],
    datos_eliminados: list[AventureroEliminado],
) -> ResultadoConsecuenciasExpedicion:
    """Publica en memoria las consecuencias de una expedición finalizada.

    Si regresa al menos un integrante, el clan recibe el dinero y la
    experiencia se divide entre los supervivientes. Si nadie regresa, el
    grupo completo pasa al historial como caído no recuperado y pierde ambos
    pozos. La operación no renueva el mercado ni guarda archivos.

    Args:
        expedicion: Estado temporal con un resultado final todavía no aplicado.
        estado_clan: Progreso general que recibirá dinero y marcas de avance.
        datos_activos: Integrantes que actualmente ocupan cupo en el clan.
        datos_eliminados: Historial ordenado de integrantes fuera del clan.

    Returns:
        Un resumen de dinero, experiencia y participantes afectados.

    Raises:
        ExpedicionYaAplicadaError: Si el cierre ya fue publicado.
        EstadoExpedicionInvalidoError: Si el flujo, los IDs o las plantillas
            son incompatibles con el estado persistente.
    """

    activos_por_id: dict[str, AventureroActivo] = _validar_cierre_en_memoria(
        expedicion,
        datos_activos,
    )
    supervivientes: list[AventureroCombate] = [
        aventurero
        for aventurero in expedicion["aventureros"]
        if aventurero["esta_vivo"]
    ]
    muertos: list[AventureroCombate] = [
        aventurero
        for aventurero in expedicion["aventureros"]
        if not aventurero["esta_vivo"]
    ]
    experiencia_individual: int = 0
    dinero_entregado: int = 0
    mazmorra_completada: bool = False

    if supervivientes:
        dinero_entregado = expedicion["dinero_acumulado"]
        estado_clan["dinero"] += dinero_entregado
        experiencia_individual = (
            expedicion["experiencia_acumulada"] // len(supervivientes)
        )

        for temporal in expedicion["aventureros"]:
            persistente: AventureroActivo = activos_por_id[temporal["id"]]
            if temporal["esta_vivo"]:
                nivel, experiencia = aplicar_experiencia(
                    persistente["nivel"],
                    persistente["experiencia"],
                    experiencia_individual,
                )
                persistente["nivel"] = nivel
                persistente["experiencia"] = experiencia
                persistente["estado"] = "vivo"
            else:
                persistente["estado"] = "muerto"

        if expedicion["resultado_final"] == "mazmorra_completada":
            estado_clan["mazmorras_completadas"]["mazmorra_1"] = True
            mazmorra_completada = True
    else:
        for temporal in expedicion["aventureros"]:
            persistente = activos_por_id[temporal["id"]]
            eliminado: AventureroEliminado = {
                "id": persistente["id"],
                "nombre": persistente["nombre"],
                "plantilla_id": persistente["plantilla_id"],
                "nivel": persistente["nivel"],
                "experiencia": persistente["experiencia"],
                "estado": "muerto",
                "motivo_baja": "caido_no_recuperado",
            }
            datos_eliminados.append(eliminado)
            datos_activos.remove(persistente)

    expedicion["estado_flujo"] = "consecuencias_aplicadas"
    return {
        "dinero_entregado": dinero_entregado,
        "experiencia_por_superviviente": experiencia_individual,
        "supervivientes_ids": [
            aventurero["id"] for aventurero in supervivientes
        ],
        "muertos_ids": [aventurero["id"] for aventurero in muertos],
        "mazmorra_completada": mazmorra_completada,
    }


def evaluar_derrota_definitiva(
    estado_clan: EstadoClan,
    datos_activos: list[AventureroActivo],
) -> None:
    """Declara la derrota si el clan no conserva una alternativa jugable.

    La evaluación no ejecuta resurrecciones, entierros ni contrataciones. Un
    cupo lleno de muertos no bloquea el mercado porque el jugador puede
    enterrarlos gratuitamente antes de contratar.

    Args:
        estado_clan: Estado con dinero, mercado y contrataciones disponibles.
        datos_activos: Integrantes vivos y cuerpos recuperados del clan.
    """

    if estado_clan["estado_partida"] != "en_curso":
        return
    if any(aventurero["estado"] == "vivo" for aventurero in datos_activos):
        return
    if any(
        estado_clan["dinero"] >= calcular_coste_resurreccion(aventurero)
        for aventurero in datos_activos
        if aventurero["estado"] == "muerto"
    ):
        return
    if (
        estado_clan["contrataciones_restantes"] > 0
        and any(
            estado_clan["dinero"] >= oferta["coste"]
            for oferta in estado_clan["ofertas_reclutamiento"]
        )
    ):
        return

    estado_clan["estado_partida"] = "derrota"

