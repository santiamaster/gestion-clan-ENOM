"""Tipos compartidos y estructuras de datos del proyecto."""

from typing import Literal, TypeAlias, TypedDict


Sexo: TypeAlias = Literal["masculino", "femenino"]
EstadoAventurero: TypeAlias = Literal["vivo", "muerto"]
TipoAtaque: TypeAlias = Literal["cuerpo_a_cuerpo", "distancia", "magico"]
EfectividadAtaque: TypeAlias = Literal["efectivo", "neutral", "inefectivo"]
MotivoBaja: TypeAlias = Literal[
    "servicios_finalizados",
    "enterrado_con_honores",
    "caido_no_recuperado",
]
TipoHabilidad: TypeAlias = Literal[
    "dano_unico",
    "dano_area",
    "multigolpe",
    "dano_vida_faltante",
    "curacion_individual",
    "curacion_grupal",
    "escudo",
    "provocacion",
    "proteccion",
    "muerte_instantanea",
]
EstrategiaObjetivo: TypeAlias = Literal[
    "aleatorio",
    "menor_vida_actual",
    "mayor_vida_actual",
    "menor_porcentaje_vida",
    "todos_los_enemigos",
    "todos_los_aliados",
    "hasta_tres_enemigos",
]
EstadoPartida: TypeAlias = Literal["en_curso", "victoria", "derrota"]
ResultadoExpedicion: TypeAlias = Literal[
    "retirada",
    "mazmorra_completada",
    "derrota_total",
    "limite_de_rondas",
]
NivelClan: TypeAlias = Literal[1, 2, 3, 4, 5]
DificultadMazmorra: TypeAlias = Literal[1, 2, 3, 4, 5]


class Estadisticas(TypedDict):
    """Agrupa las cuatro estadísticas principales de un combatiente."""

    vida: int
    dano: int
    defensa: int
    velocidad: int


class MazmorrasCompletadas(TypedDict):
    """Registra las mazmorras completadas al menos una vez."""

    mazmorra_1: bool
    mazmorra_2: bool
    mazmorra_3: bool
    mazmorra_4: bool
    mazmorra_5: bool


class AventureroActivo(TypedDict):
    """Representa un aventurero que todavía ocupa un lugar en el clan."""

    id: str
    nombre: str
    plantilla_id: str
    nivel: int
    experiencia: int
    estado: EstadoAventurero


class AventureroEliminado(AventureroActivo):
    """Representa un aventurero que dejó de pertenecer al clan."""

    motivo_baja: MotivoBaja


class OfertaReclutamiento(TypedDict):
    """Representa un candidato disponible temporalmente en el gremio."""

    id_oferta: str
    nombre: str
    plantilla_id: str
    nivel: int
    coste: int


class EstadoClan(TypedDict):
    """Contiene el progreso general y persistente de la partida."""

    nombre: str
    nivel: NivelClan
    dinero: int
    siguiente_id_aventurero: int
    contrataciones_restantes: int
    estado_partida: EstadoPartida
    mazmorras_completadas: MazmorrasCompletadas
    ofertas_reclutamiento: list[OfertaReclutamiento]


class PlantillaAventurero(TypedDict):
    """Define los datos permanentes de una raza y profesión."""

    id: str
    raza: str
    profesion: str
    sexo: Sexo
    estadisticas_raza: Estadisticas
    crecimiento_profesion: Estadisticas
    critico_adicional: int
    tipo_ataque: TipoAtaque
    coste_base: int
    habilidad_id: str
    estrategia_ataque_basico: EstrategiaObjetivo
    imagen: str


class HabilidadBase(TypedDict):
    """Contiene los datos compartidos por todas las habilidades."""

    id: str
    nombre: str
    profesion: str
    enfriamiento: int
    descripcion: str
    estrategia_objetivo: EstrategiaObjetivo


class HabilidadDanoUnico(HabilidadBase):
    """Representa un ataque potenciado contra un enemigo."""

    tipo: Literal["dano_unico"]
    multiplicador_dano: float


class HabilidadDanoArea(HabilidadBase):
    """Representa un ataque que puede afectar a varios enemigos."""

    tipo: Literal["dano_area"]
    multiplicador_dano: float
    maximo_objetivos: int | None
    tiradas_individuales: bool


class HabilidadMultigolpe(HabilidadBase):
    """Representa varios ataques consecutivos contra un objetivo."""

    tipo: Literal["multigolpe"]
    cantidad_golpes: int
    multiplicador_por_golpe: float
    tiradas_individuales: bool


class HabilidadDanoVidaFaltante(HabilidadBase):
    """Agrega al daño la vida faltante del usuario."""

    tipo: Literal["dano_vida_faltante"]
    porcentaje_curacion_al_matar: float


class HabilidadCuracionIndividual(HabilidadBase):
    """Cura a un único aliado herido."""

    tipo: Literal["curacion_individual"]
    porcentaje_vida_maxima: float
    puede_elegirse_a_si_mismo: bool


class HabilidadCuracionGrupal(HabilidadBase):
    """Cura a todos los aliados vivos."""

    tipo: Literal["curacion_grupal"]
    porcentaje_vida_maxima: float
    incluye_usuario: bool


class HabilidadEscudo(HabilidadBase):
    """Reduce temporalmente el daño recibido por un aliado."""

    tipo: Literal["escudo"]
    reduccion_dano: float
    puede_elegirse_a_si_mismo: bool
    duracion: Literal["hasta_siguiente_turno_usuario"]


class HabilidadProvocacion(HabilidadBase):
    """Obliga a los enemigos a atacar al Defensor."""

    tipo: Literal["provocacion"]
    duracion: Literal["un_ataque_por_enemigo"]
    requiere_tirada: bool


class HabilidadProteccion(HabilidadBase):
    """Redirige hacia el Paladín los ataques dirigidos a un aliado."""

    tipo: Literal["proteccion"]
    duracion: Literal["hasta_siguiente_turno_usuario"]


class HabilidadMuerteInstantanea(HabilidadBase):
    """Puede eliminar inmediatamente a un enemigo sin causar daño."""

    tipo: Literal["muerte_instantanea"]
    probabilidad_normal: int
    probabilidad_jefe: int


Habilidad: TypeAlias = (
    HabilidadDanoUnico
    | HabilidadDanoArea
    | HabilidadMultigolpe
    | HabilidadDanoVidaFaltante
    | HabilidadCuracionIndividual
    | HabilidadCuracionGrupal
    | HabilidadEscudo
    | HabilidadProvocacion
    | HabilidadProteccion
    | HabilidadMuerteInstantanea
)

