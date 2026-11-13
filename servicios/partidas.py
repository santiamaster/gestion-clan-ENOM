"""Coordinación de la creación y el guardado de partidas."""

from copy import deepcopy
from pathlib import Path
from random import Random

from modelos.expediciones import EstadoExpedicion, ResumenCierreExpedicion
from modelos.tipos import AventureroActivo, AventureroEliminado, EstadoClan
from servicios.aventureros import crear_aventureros_iniciales
from servicios.clan import crear_estado_inicial_clan
from servicios.expediciones import (
    EstadoExpedicionInvalidoError,
    aplicar_consecuencias_expedicion,
    evaluar_derrota_definitiva,
)
from servicios.persistencia import (
    DIRECTORIO_PARTIDA,
    ErrorPersistencia,
    existe_partida_guardada,
    guardar_partida,
)
from servicios.reclutamiento import renovar_mercado


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
        generador: Fuente de azar opcional para controlar nombres y ofertas.

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
    renovar_mercado(estado_clan, generador_nombres)

    guardar_partida(
        estado_clan,
        datos_activos,
        datos_eliminados,
        directorio,
    )
    return estado_clan, datos_activos, datos_eliminados


def _publicar_estado_clan(
    destino: EstadoClan,
    origen: EstadoClan,
) -> None:
    """Reemplaza explícitamente todos los campos persistentes del clan."""

    destino["nombre"] = origen["nombre"]
    destino["nivel"] = origen["nivel"]
    destino["dinero"] = origen["dinero"]
    destino["siguiente_id_aventurero"] = origen["siguiente_id_aventurero"]
    destino["contrataciones_restantes"] = origen["contrataciones_restantes"]
    destino["estado_partida"] = origen["estado_partida"]
    destino["mazmorras_completadas"] = origen["mazmorras_completadas"]
    destino["ofertas_reclutamiento"] = origen["ofertas_reclutamiento"]


def cerrar_expedicion_y_guardar(
    expedicion: EstadoExpedicion,
    estado_clan: EstadoClan,
    datos_activos: list[AventureroActivo],
    datos_eliminados: list[AventureroEliminado],
    generador: Random,
    directorio: Path = DIRECTORIO_PARTIDA,
) -> ResumenCierreExpedicion:
    """Aplica, renueva y guarda una expedición como una única transacción.

    Todas las operaciones potencialmente fallidas trabajan sobre copias. El
    estado original y el generador se publican únicamente después de guardar
    correctamente los tres JSON. Esto permite reintentar un cierre fallido sin
    duplicar recompensas ni producir un mercado diferente.

    Args:
        expedicion: Flujo temporal finalizado y todavía no aplicado.
        estado_clan: Progreso persistente que será reemplazado tras el guardado.
        datos_activos: Integrantes que ocupan cupo antes del cierre.
        datos_eliminados: Historial anterior a las consecuencias.
        generador: Fuente de azar utilizada para renovar el mercado.
        directorio: Carpeta donde se guardarán los tres JSON.

    Returns:
        El resumen de consecuencias y estado final de la partida.

    Raises:
        ExpedicionYaAplicadaError: Si el cierre ya se publicó.
        EstadoExpedicionInvalidoError: Si el flujo o sus participantes son
            incompatibles con los datos persistentes.
        ErrorPersistencia: Si no es posible guardar la partida.
    """

    estado_generador = generador.getstate()
    try:
        expedicion_copia: EstadoExpedicion = deepcopy(expedicion)
        clan_copia: EstadoClan = deepcopy(estado_clan)
        activos_copia: list[AventureroActivo] = deepcopy(datos_activos)
        eliminados_copia: list[AventureroEliminado] = deepcopy(
            datos_eliminados
        )
        consecuencias = aplicar_consecuencias_expedicion(
            expedicion_copia,
            clan_copia,
            activos_copia,
            eliminados_copia,
        )
        resultado_final = expedicion_copia["resultado_final"]
        if resultado_final is None:
            raise EstadoExpedicionInvalidoError(
                "La expedición finalizada no posee un resultado."
            )

        renovar_mercado(clan_copia, generador)
        evaluar_derrota_definitiva(clan_copia, activos_copia)
        guardar_partida(
            clan_copia,
            activos_copia,
            eliminados_copia,
            directorio,
        )
    except Exception:
        generador.setstate(estado_generador)
        raise

    _publicar_estado_clan(estado_clan, clan_copia)
    datos_activos[:] = activos_copia
    datos_eliminados[:] = eliminados_copia
    expedicion["estado_flujo"] = "consecuencias_aplicadas"

    return {
        "dinero_entregado": consecuencias["dinero_entregado"],
        "experiencia_por_superviviente": consecuencias[
            "experiencia_por_superviviente"
        ],
        "supervivientes_ids": consecuencias["supervivientes_ids"],
        "muertos_ids": consecuencias["muertos_ids"],
        "mazmorra_completada": consecuencias["mazmorra_completada"],
        "resultado": resultado_final,
        "estado_partida": clan_copia["estado_partida"],
    }
