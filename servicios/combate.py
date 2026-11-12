"""Creación de estados, turnos, ataques y resolución de rondas."""

from collections.abc import Mapping, Sequence
from random import Random
from typing import TypeVar

from configuracion import (
    CANTIDAD_OLEADAS_MAZMORRA,
    LIMITE_IMPACTO_NORMAL,
    LIMITE_RONDAS_OLEADA,
    PROBABILIDAD_CRITICA_MAXIMA,
)
from modelos.combate import (
    AventureroCombate,
    CombatienteBase,
    DefinicionOleada,
    EnemigoCombate,
    ParticipanteTurno,
    PlantillaEnemigo,
    ResultadoAtaque,
    ResultadoCombate,
    ResultadoOleada,
    ResultadoTirada,
    TurnoAventurero,
    TurnoEnemigo,
)
from modelos.tipos import (
    AventureroActivo,
    EfectividadAtaque,
    PlantillaAventurero,
)
from servicios.calculos import (
    calcular_dano_final,
    calcular_estadisticas,
    calcular_probabilidad_critico,
)


T = TypeVar("T")


class EstadoCombateInvalidoError(ValueError):
    """Indica que un estado temporal no puede participar del combate."""


class DefinicionOleadaInvalidaError(ValueError):
    """Indica que una oleada no permite crear enemigos independientes."""


def _validar_combatiente(combatiente: CombatienteBase) -> None:
    """Comprueba las invariantes comunes de un estado temporal."""

    vida_maxima: int = combatiente["vida_maxima"]
    vida_actual: int = combatiente["vida_actual"]

    if vida_maxima < 1:
        raise EstadoCombateInvalidoError(
            "La vida máxima debe ser mayor que cero."
        )
    if not 0 <= vida_actual <= vida_maxima:
        raise EstadoCombateInvalidoError(
            "La vida actual debe estar entre cero y la vida máxima."
        )
    if combatiente["esta_vivo"] != (vida_actual > 0):
        raise EstadoCombateInvalidoError(
            "El estado de vida no coincide con la vida actual."
        )
    if any(
        valor < 0
        for valor in (
            combatiente["dano"],
            combatiente["defensa"],
            combatiente["velocidad"],
        )
    ):
        raise EstadoCombateInvalidoError(
            "El daño, la defensa y la velocidad no pueden ser negativos."
        )
    if not 0 <= combatiente["probabilidad_critica"] <= 90:
        raise EstadoCombateInvalidoError(
            "La probabilidad crítica debe estar entre cero y noventa."
        )


def _validar_estados_combate(
    aventureros: Sequence[AventureroCombate],
    enemigos: Sequence[EnemigoCombate],
) -> None:
    """Valida los dos grupos antes de comenzar o continuar una oleada.

    Los aventureros muertos pueden permanecer en la lista, pero debe quedar
    al menos un superviviente. Los enemigos se reciben como instancias de una
    oleada todavía disputable, por lo que la lista no puede estar vacía.
    """

    if not aventureros:
        raise EstadoCombateInvalidoError(
            "El grupo debe contener al menos un aventurero."
        )
    if not enemigos:
        raise EstadoCombateInvalidoError(
            "La oleada debe contener al menos un enemigo."
        )

    for aventurero in aventureros:
        _validar_combatiente(aventurero)
    for enemigo in enemigos:
        _validar_combatiente(enemigo)

    if not any(aventurero["esta_vivo"] for aventurero in aventureros):
        raise EstadoCombateInvalidoError(
            "El grupo debe conservar al menos un aventurero vivo."
        )

    ids_instancia: list[str] = [
        enemigo["id_instancia"] for enemigo in enemigos
    ]
    if len(ids_instancia) != len(set(ids_instancia)):
        raise DefinicionOleadaInvalidaError(
            "Los identificadores de instancia enemiga no pueden repetirse."
        )


def crear_aventurero_combate(
    aventurero: AventureroActivo,
    catalogo: Mapping[str, PlantillaAventurero],
) -> AventureroCombate:
    """Crea un estado mutable sin alterar el registro persistente.

    Args:
        aventurero: Integrante del clan que participará de la expedición.
        catalogo: Plantillas permanentes disponibles.

    Returns:
        Una representación temporal con estadísticas calculadas por nivel.

    Raises:
        EstadoCombateInvalidoError: Si la plantilla no existe o el estado
            temporal resultante no cumple las invariantes de combate.
    """

    plantilla_id: str = aventurero["plantilla_id"]
    if plantilla_id not in catalogo:
        raise EstadoCombateInvalidoError(
            f"No existe la plantilla de aventurero {plantilla_id}."
        )

    plantilla: PlantillaAventurero = catalogo[plantilla_id]
    estadisticas = calcular_estadisticas(plantilla, aventurero["nivel"])
    esta_vivo: bool = aventurero["estado"] == "vivo"
    resultado: AventureroCombate = {
        "id": aventurero["id"],
        "nombre": aventurero["nombre"],
        "plantilla_id": plantilla_id,
        "vida_maxima": estadisticas["vida"],
        "vida_actual": estadisticas["vida"] if esta_vivo else 0,
        "dano": estadisticas["dano"],
        "defensa": estadisticas["defensa"],
        "velocidad": estadisticas["velocidad"],
        "probabilidad_critica": calcular_probabilidad_critico(
            plantilla["critico_adicional"]
        ),
        "esta_vivo": esta_vivo,
        "tipo_ataque": plantilla["tipo_ataque"],
        "estrategia_objetivo": plantilla["estrategia_ataque_basico"],
    }
    _validar_combatiente(resultado)
    return resultado


def crear_enemigos_oleada(
    oleada: DefinicionOleada,
    catalogo: Mapping[str, PlantillaEnemigo],
) -> list[EnemigoCombate]:
    """Crea estados independientes para todos los enemigos de una oleada.

    Los contadores de instancia comienzan nuevamente en uno para cada
    plantilla y cada oleada. La definición completa se valida antes de crear
    el primer estado para evitar resultados parciales.

    Args:
        oleada: Composición fija que se desea instanciar.
        catalogo: Plantillas enemigas permanentes disponibles.

    Returns:
        Los estados temporales en el orden definido por la oleada.

    Raises:
        DefinicionOleadaInvalidaError: Si el número, los grupos, las
            cantidades o las referencias de plantilla son inválidos.
    """

    if not 1 <= oleada["numero"] <= CANTIDAD_OLEADAS_MAZMORRA:
        raise DefinicionOleadaInvalidaError(
            "El número de oleada debe estar entre uno y diez."
        )
    if not oleada["enemigos"]:
        raise DefinicionOleadaInvalidaError(
            "La oleada debe definir al menos un grupo enemigo."
        )

    ids_plantilla: list[str] = [
        grupo["plantilla_id"] for grupo in oleada["enemigos"]
    ]
    if len(ids_plantilla) != len(set(ids_plantilla)):
        raise DefinicionOleadaInvalidaError(
            "Una plantilla enemiga no puede repetirse dentro de la oleada."
        )

    for grupo in oleada["enemigos"]:
        plantilla_id: str = grupo["plantilla_id"]
        if plantilla_id not in catalogo:
            raise DefinicionOleadaInvalidaError(
                f"No existe la plantilla enemiga {plantilla_id}."
            )
        if grupo["cantidad"] < 1:
            raise DefinicionOleadaInvalidaError(
                "Cada grupo debe contener al menos un enemigo."
            )

    enemigos: list[EnemigoCombate] = []
    for grupo in oleada["enemigos"]:
        plantilla: PlantillaEnemigo = catalogo[grupo["plantilla_id"]]
        for numero in range(1, grupo["cantidad"] + 1):
            estadisticas = plantilla["estadisticas"]
            enemigo: EnemigoCombate = {
                "id_instancia": f"{plantilla['id']}-{numero:02d}",
                "plantilla_id": plantilla["id"],
                "nombre": plantilla["nombre"],
                "vida_maxima": estadisticas["vida"],
                "vida_actual": estadisticas["vida"],
                "dano": estadisticas["dano"],
                "defensa": estadisticas["defensa"],
                "velocidad": estadisticas["velocidad"],
                "probabilidad_critica": calcular_probabilidad_critico(0),
                "esta_vivo": True,
                "tipo_ataque": plantilla["tipo_ataque"],
                "efectividades": {
                    "cuerpo_a_cuerpo": plantilla["efectividades"][
                        "cuerpo_a_cuerpo"
                    ],
                    "distancia": plantilla["efectividades"]["distancia"],
                    "magico": plantilla["efectividades"]["magico"],
                },
                "experiencia": plantilla["experiencia"],
                "dinero": plantilla["dinero"],
                "es_jefe": plantilla["es_jefe"],
            }
            _validar_combatiente(enemigo)
            enemigos.append(enemigo)

    ids_instancia: list[str] = [
        enemigo["id_instancia"] for enemigo in enemigos
    ]
    if len(ids_instancia) != len(set(ids_instancia)):
        raise DefinicionOleadaInvalidaError(
            "Los identificadores de instancia enemiga no pueden repetirse."
        )
    return enemigos


def resolver_desempate_d100(
    participantes: Sequence[T],
    generador: Random,
) -> list[T]:
    """Ordena participantes por d100 y repite solamente los empates.

    El resultado mayor obtiene prioridad. Cuando dos o más participantes
    consiguen la misma tirada, solo ese subgrupo vuelve a tirar hasta quedar
    completamente ordenado.

    Args:
        participantes: Elementos empatados que necesitan un orden definitivo.
        generador: Fuente de azar inyectada para permitir pruebas repetibles.

    Returns:
        Una lista nueva ordenada de mayor a menor resultado.
    """

    if len(participantes) <= 1:
        return list(participantes)

    grupos_por_tirada: dict[int, list[T]] = {}
    for participante in participantes:
        tirada: int = generador.randint(1, 100)
        grupos_por_tirada.setdefault(tirada, []).append(participante)

    resultado: list[T] = []
    for tirada in sorted(grupos_por_tirada, reverse=True):
        grupo: list[T] = grupos_por_tirada[tirada]
        if len(grupo) == 1:
            resultado.extend(grupo)
        else:
            resultado.extend(resolver_desempate_d100(grupo, generador))
    return resultado


def resolver_tirada_ataque(
    probabilidad_critica: int,
    generador: Random,
) -> ResultadoTirada:
    """Resuelve crítico, impacto o fallo mediante una única tirada d100.

    La probabilidad recibida debe haber sido normalizada previamente. Esta
    operación la valida, pero no la corrige silenciosamente.

    Args:
        probabilidad_critica: Umbral crítico entre cero y noventa.
        generador: Fuente de azar inyectada.

    Returns:
        ``critico``, ``impacto`` o ``fallo`` según la tirada.

    Raises:
        ValueError: Si la probabilidad recibida está fuera del dominio.
    """

    if not 0 <= probabilidad_critica <= PROBABILIDAD_CRITICA_MAXIMA:
        raise ValueError(
            "La probabilidad crítica debe estar entre cero y noventa."
        )

    tirada: int = generador.randint(1, 100)
    if tirada <= probabilidad_critica:
        return "critico"
    if tirada <= LIMITE_IMPACTO_NORMAL:
        return "impacto"
    return "fallo"


def seleccionar_objetivo_aventurero(
    atacante: AventureroCombate,
    enemigos: Sequence[EnemigoCombate],
    generador: Random,
) -> EnemigoCombate:
    """Selecciona un enemigo vivo según la estrategia del aventurero.

    Los empates de vida se resuelven con el desempate general de d100 y no
    mediante el orden recibido.

    Raises:
        EstadoCombateInvalidoError: Si no quedan enemigos vivos.
        ValueError: Si la estrategia no pertenece al combate básico.
    """

    vivos: list[EnemigoCombate] = [
        enemigo for enemigo in enemigos if enemigo["esta_vivo"]
    ]
    if not vivos:
        raise EstadoCombateInvalidoError(
            "No quedan enemigos vivos para seleccionar."
        )

    estrategia = atacante["estrategia_objetivo"]
    if estrategia == "aleatorio":
        return generador.choice(vivos)
    if estrategia == "menor_vida_actual":
        vida_objetivo: int = min(enemigo["vida_actual"] for enemigo in vivos)
    elif estrategia == "mayor_vida_actual":
        vida_objetivo = max(enemigo["vida_actual"] for enemigo in vivos)
    else:
        raise ValueError(
            f"La estrategia {estrategia} no selecciona un objetivo básico."
        )

    empatados: list[EnemigoCombate] = [
        enemigo
        for enemigo in vivos
        if enemigo["vida_actual"] == vida_objetivo
    ]
    return resolver_desempate_d100(empatados, generador)[0]


def seleccionar_objetivo_enemigo(
    aventureros: Sequence[AventureroCombate],
    generador: Random,
) -> AventureroCombate:
    """Selecciona aleatoriamente un aventurero vivo como objetivo enemigo.

    Raises:
        EstadoCombateInvalidoError: Si el grupo ya no tiene supervivientes.
    """

    vivos: list[AventureroCombate] = [
        aventurero
        for aventurero in aventureros
        if aventurero["esta_vivo"]
    ]
    if not vivos:
        raise EstadoCombateInvalidoError(
            "No quedan aventureros vivos para seleccionar."
        )
    return generador.choice(vivos)


def obtener_efectividad_ataque(
    atacante: ParticipanteTurno,
    objetivo: ParticipanteTurno,
) -> EfectividadAtaque:
    """Determina la efectividad aplicable entre dos bandos distintos.

    Los ataques enemigos son neutrales en esta versión simplificada. Los
    aventureros consultan en el enemigo la efectividad correspondiente a su
    tipo de ataque.

    Raises:
        ValueError: Si atacante y objetivo pertenecen al mismo bando.
    """

    if atacante["bando"] == objetivo["bando"]:
        raise ValueError("Un ataque básico debe dirigirse al bando contrario.")
    if atacante["bando"] == "enemigos":
        return "neutral"
    if objetivo["bando"] != "enemigos":
        raise ValueError("El objetivo del aventurero debe ser un enemigo.")

    aventurero: AventureroCombate = atacante["combatiente"]
    enemigo: EnemigoCombate = objetivo["combatiente"]
    return enemigo["efectividades"][aventurero["tipo_ataque"]]


def calcular_dano_recibido(dano_modificado: int, defensa: int) -> int:
    """Resta la defensa y conserva un mínimo de un punto por impacto.

    Args:
        dano_modificado: Daño posterior a efectividad y posible crítico.
        defensa: Defensa actual del objetivo.

    Returns:
        El daño que debe descontarse de la vida.

    Raises:
        ValueError: Si alguno de los valores recibidos es negativo.
    """

    if dano_modificado < 0 or defensa < 0:
        raise ValueError("El daño y la defensa no pueden ser negativos.")
    return max(1, dano_modificado - defensa)


def ejecutar_ataque_basico(
    atacante: CombatienteBase,
    objetivo: CombatienteBase,
    efectividad: EfectividadAtaque,
    generador: Random,
) -> ResultadoAtaque:
    """Resuelve un ataque y muta solamente la vida temporal del objetivo.

    El ataque usa una sola tirada. Si impacta, aplica primero efectividad y
    crítico, luego defensa y finalmente limita la vida resultante a cero.

    Raises:
        EstadoCombateInvalidoError: Si atacante u objetivo son incoherentes,
            o si alguno ya está muerto antes del ataque.
    """

    _validar_combatiente(atacante)
    _validar_combatiente(objetivo)
    if not atacante["esta_vivo"]:
        raise EstadoCombateInvalidoError(
            "Un combatiente muerto no puede realizar un ataque."
        )
    if not objetivo["esta_vivo"]:
        raise EstadoCombateInvalidoError(
            "No se puede atacar a un objetivo que ya está muerto."
        )

    resultado_tirada: ResultadoTirada = resolver_tirada_ataque(
        atacante["probabilidad_critica"],
        generador,
    )
    if resultado_tirada == "fallo":
        return {
            "resultado": "fallo",
            "dano_aplicado": 0,
            "vida_restante": objetivo["vida_actual"],
            "objetivo_derrotado": False,
        }

    dano_modificado: int = calcular_dano_final(
        atacante["dano"],
        efectividad,
        resultado_tirada == "critico",
    )
    dano_aplicado: int = calcular_dano_recibido(
        dano_modificado,
        objetivo["defensa"],
    )
    objetivo["vida_actual"] = max(
        0,
        objetivo["vida_actual"] - dano_aplicado,
    )
    objetivo_derrotado: bool = objetivo["vida_actual"] == 0
    objetivo["esta_vivo"] = not objetivo_derrotado

    return {
        "resultado": resultado_tirada,
        "dano_aplicado": dano_aplicado,
        "vida_restante": objetivo["vida_actual"],
        "objetivo_derrotado": objetivo_derrotado,
    }


def calcular_orden_turnos(
    aventureros: Sequence[AventureroCombate],
    enemigos: Sequence[EnemigoCombate],
    generador: Random,
) -> list[ParticipanteTurno]:
    """Crea el orden de la oleada por velocidad descendente.

    Los combatientes muertos quedan excluidos. Cada empate de velocidad se
    resuelve con d100 y las estructuras del orden conservan referencias a los
    estados temporales originales.
    """

    participantes: list[ParticipanteTurno] = []
    for aventurero in aventureros:
        _validar_combatiente(aventurero)
        if aventurero["esta_vivo"]:
            participantes.append(
                {"bando": "aventureros", "combatiente": aventurero}
            )
    for enemigo in enemigos:
        _validar_combatiente(enemigo)
        if enemigo["esta_vivo"]:
            participantes.append(
                {"bando": "enemigos", "combatiente": enemigo}
            )

    grupos_por_velocidad: dict[int, list[ParticipanteTurno]] = {}
    for participante in participantes:
        velocidad: int = participante["combatiente"]["velocidad"]
        grupos_por_velocidad.setdefault(velocidad, []).append(participante)

    orden: list[ParticipanteTurno] = []
    for velocidad in sorted(grupos_por_velocidad, reverse=True):
        empatados: list[ParticipanteTurno] = grupos_por_velocidad[velocidad]
        orden.extend(resolver_desempate_d100(empatados, generador))
    return orden


def resolver_ronda(
    orden_turnos: Sequence[ParticipanteTurno],
    aventureros: list[AventureroCombate],
    enemigos: list[EnemigoCombate],
    generador: Random,
) -> list[str]:
    """Ejecuta como máximo un turno por participante vivo.

    El recorrido se detiene en cuanto uno de los bandos deja de tener
    supervivientes. Los enemigos derrotados se devuelven en el orden exacto
    en que cayeron para que la oleada acumule sus recompensas una sola vez.
    """

    _validar_estados_combate(aventureros, enemigos)
    derrotados: list[str] = []
    participantes_procesados: set[int] = set()

    for turno in orden_turnos:
        if not any(aventurero["esta_vivo"] for aventurero in aventureros):
            break
        if not any(enemigo["esta_vivo"] for enemigo in enemigos):
            break

        identidad: int = id(turno["combatiente"])
        if identidad in participantes_procesados:
            continue
        participantes_procesados.add(identidad)

        if not turno["combatiente"]["esta_vivo"]:
            continue

        if turno["bando"] == "aventureros":
            atacante: AventureroCombate = turno["combatiente"]
            objetivo: EnemigoCombate = seleccionar_objetivo_aventurero(
                atacante,
                enemigos,
                generador,
            )
            turno_objetivo: TurnoEnemigo = {
                "bando": "enemigos",
                "combatiente": objetivo,
            }
            efectividad: EfectividadAtaque = obtener_efectividad_ataque(
                turno,
                turno_objetivo,
            )
            resultado: ResultadoAtaque = ejecutar_ataque_basico(
                atacante,
                objetivo,
                efectividad,
                generador,
            )
            if resultado["objetivo_derrotado"]:
                derrotados.append(objetivo["id_instancia"])
        else:
            atacante_enemigo: EnemigoCombate = turno["combatiente"]
            objetivo_aventurero: AventureroCombate = (
                seleccionar_objetivo_enemigo(aventureros, generador)
            )
            turno_objetivo_aventurero: TurnoAventurero = {
                "bando": "aventureros",
                "combatiente": objetivo_aventurero,
            }
            efectividad_enemiga: EfectividadAtaque = (
                obtener_efectividad_ataque(
                    turno,
                    turno_objetivo_aventurero,
                )
            )
            ejecutar_ataque_basico(
                atacante_enemigo,
                objetivo_aventurero,
                efectividad_enemiga,
                generador,
            )

    return derrotados


def resolver_oleada(
    aventureros: list[AventureroCombate],
    enemigos: list[EnemigoCombate],
    generador: Random,
) -> ResultadoOleada:
    """Resuelve una oleada hasta victoria, derrota o límite de rondas.

    El orden de turnos se calcula una sola vez y se conserva durante toda la
    oleada. Las recompensas devueltas son provisionales: el futuro servicio de
    expediciones decidirá si se entregan o se pierden.

    Args:
        aventureros: Estados temporales del grupo, incluidos muertos previos.
        enemigos: Instancias independientes creadas para esta oleada.
        generador: Fuente de azar compartida por toda la resolución.

    Returns:
        El resultado, las rondas disputadas, los estados finales y el botín
        provisional de las instancias derrotadas.

    Raises:
        EstadoCombateInvalidoError: Si los grupos o estados son inválidos.
        DefinicionOleadaInvalidaError: Si hay IDs enemigos duplicados.
    """

    _validar_estados_combate(aventureros, enemigos)
    orden_turnos: list[ParticipanteTurno] = calcular_orden_turnos(
        aventureros,
        enemigos,
        generador,
    )
    enemigos_derrotados: list[str] = []
    ids_contabilizados: set[str] = set()
    resultado_combate: ResultadoCombate = "limite_de_rondas"
    rondas_disputadas: int = 0

    for ronda in range(1, LIMITE_RONDAS_OLEADA + 1):
        rondas_disputadas = ronda
        derrotados_ronda: list[str] = resolver_ronda(
            orden_turnos,
            aventureros,
            enemigos,
            generador,
        )
        for identificador in derrotados_ronda:
            if identificador not in ids_contabilizados:
                ids_contabilizados.add(identificador)
                enemigos_derrotados.append(identificador)

        quedan_aventureros: bool = any(
            aventurero["esta_vivo"] for aventurero in aventureros
        )
        quedan_enemigos: bool = any(
            enemigo["esta_vivo"] for enemigo in enemigos
        )
        if not quedan_aventureros:
            resultado_combate = "derrota"
            break
        if not quedan_enemigos:
            resultado_combate = "victoria"
            break

    enemigos_por_id: dict[str, EnemigoCombate] = {
        enemigo["id_instancia"]: enemigo for enemigo in enemigos
    }
    experiencia_obtenida: int = sum(
        enemigos_por_id[identificador]["experiencia"]
        for identificador in enemigos_derrotados
    )
    dinero_obtenido: int = sum(
        enemigos_por_id[identificador]["dinero"]
        for identificador in enemigos_derrotados
    )

    return {
        "resultado": resultado_combate,
        "rondas": rondas_disputadas,
        "aventureros": aventureros,
        "enemigos": enemigos,
        "enemigos_derrotados": enemigos_derrotados,
        "experiencia_obtenida": experiencia_obtenida,
        "dinero_obtenido": dinero_obtenido,
    }

