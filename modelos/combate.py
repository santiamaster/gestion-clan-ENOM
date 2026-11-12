"""Tipos permanentes y temporales utilizados por el combate."""

from typing import Literal, TypeAlias, TypedDict

from modelos.tipos import (
    DificultadMazmorra,
    EfectividadAtaque,
    Estadisticas,
    EstrategiaObjetivo,
    TipoAtaque,
)


ResultadoTirada: TypeAlias = Literal["fallo", "impacto", "critico"]
ResultadoCombate: TypeAlias = Literal[
    "victoria",
    "derrota",
    "limite_de_rondas",
]


class EfectividadesRecibidas(TypedDict):
    """Relaciona cada tipo de ataque con su efecto sobre un enemigo."""

    cuerpo_a_cuerpo: EfectividadAtaque
    distancia: EfectividadAtaque
    magico: EfectividadAtaque


class PlantillaEnemigo(TypedDict):
    """Define los datos permanentes de una criatura enemiga."""

    id: str
    nombre: str
    estadisticas: Estadisticas
    tipo_ataque: TipoAtaque
    efectividades: EfectividadesRecibidas
    experiencia: int
    dinero: int
    es_jefe: bool
    imagen: str
    descripcion: str


class GrupoEnemigosOleada(TypedDict):
    """Indica cuántas instancias de una plantilla contiene una oleada."""

    plantilla_id: str
    cantidad: int


class DefinicionOleada(TypedDict):
    """Representa la composición fija de una oleada."""

    numero: int
    enemigos: list[GrupoEnemigosOleada]


class DefinicionMazmorra(TypedDict):
    """Agrupa las oleadas permanentes de una mazmorra."""

    id: str
    nombre: str
    dificultad: DificultadMazmorra
    oleadas: list[DefinicionOleada]


class CombatienteBase(TypedDict):
    """Contiene las estadísticas mutables compartidas durante una oleada."""

    nombre: str
    vida_maxima: int
    vida_actual: int
    dano: int
    defensa: int
    velocidad: int
    probabilidad_critica: int
    esta_vivo: bool


class AventureroCombate(CombatienteBase):
    """Representa temporalmente a un aventurero durante una expedición."""

    id: str
    plantilla_id: str
    tipo_ataque: TipoAtaque
    estrategia_objetivo: EstrategiaObjetivo


class EnemigoCombate(CombatienteBase):
    """Representa una instancia independiente de una plantilla enemiga."""

    id_instancia: str
    plantilla_id: str
    tipo_ataque: TipoAtaque
    efectividades: EfectividadesRecibidas
    experiencia: int
    dinero: int
    es_jefe: bool


class TurnoAventurero(TypedDict):
    """Conserva una referencia a un aventurero dentro del orden de turnos."""

    bando: Literal["aventureros"]
    combatiente: AventureroCombate


class TurnoEnemigo(TypedDict):
    """Conserva una referencia a un enemigo dentro del orden de turnos."""

    bando: Literal["enemigos"]
    combatiente: EnemigoCombate


ParticipanteTurno: TypeAlias = TurnoAventurero | TurnoEnemigo


class ResultadoAtaque(TypedDict):
    """Describe únicamente el efecto inmediato de un ataque."""

    resultado: ResultadoTirada
    dano_aplicado: int
    vida_restante: int
    objetivo_derrotado: bool


class ResultadoOleada(TypedDict):
    """Resume el estado y las recompensas provisionales de una oleada."""

    resultado: ResultadoCombate
    rondas: int
    aventureros: list[AventureroCombate]
    enemigos: list[EnemigoCombate]
    enemigos_derrotados: list[str]
    experiencia_obtenida: int
    dinero_obtenido: int

