"""Catálogo permanente de las quince plantillas de aventureros."""

from modelos.tipos import (
    EstrategiaObjetivo,
    PlantillaAventurero,
    Sexo,
    TipoAtaque,
)


def _plantilla(
    identificador: str,
    raza: str,
    profesion: str,
    sexo: Sexo,
    estadisticas_raza: tuple[int, int, int, int],
    crecimiento: tuple[int, int, int, int],
    critico_adicional: int,
    tipo_ataque: TipoAtaque,
    coste_base: int,
    habilidad_id: str,
    estrategia: EstrategiaObjetivo,
    imagen: str,
) -> PlantillaAventurero:
    """Construye una plantilla manteniendo una tabla de datos compacta."""

    vida_raza, dano_raza, defensa_raza, velocidad_raza = estadisticas_raza
    vida_profesion, dano_profesion, defensa_profesion, velocidad_profesion = crecimiento
    return {
        "id": identificador,
        "raza": raza,
        "profesion": profesion,
        "sexo": sexo,
        "estadisticas_raza": {
            "vida": vida_raza,
            "dano": dano_raza,
            "defensa": defensa_raza,
            "velocidad": velocidad_raza,
        },
        "crecimiento_profesion": {
            "vida": vida_profesion,
            "dano": dano_profesion,
            "defensa": defensa_profesion,
            "velocidad": velocidad_profesion,
        },
        "critico_adicional": critico_adicional,
        "tipo_ataque": tipo_ataque,
        "coste_base": coste_base,
        "habilidad_id": habilidad_id,
        "estrategia_ataque_basico": estrategia,
        "imagen": imagen,
    }


MAGO_ARCANO = _plantilla(
    "PLANTILLA_MAGO_ARCANO", "Draia’seikan", "Mago Arcano", "masculino",
    (5, 15, 6, 3), (3, 15, 1, 1), 0, "magico", 50,
    "HAB_EXPLOSION_ARCANA", "mayor_vida_actual", "assets/aventureros/mago_arcano.png",
)
HECHICERO = _plantilla(
    "PLANTILLA_HECHICERO", "Alh-Zarqai", "Hechicero", "femenino",
    (6, 9, 8, 3), (4, 11, 2, 2), 0, "magico", 10,
    "HAB_RAYO", "mayor_vida_actual", "assets/aventureros/hechicero.png",
)
ARQUERO = _plantilla(
    "PLANTILLA_ARQUERO", "Baz-Zarqai", "Arquero", "femenino",
    (9, 10, 8, 10), (7, 10, 4, 6), 5, "distancia", 10,
    "HAB_MULTIDISPAROS", "menor_vida_actual", "assets/aventureros/arquero.png",
)
NINJA = _plantilla(
    "PLANTILLA_NINJA", "Dac-Zarqai", "Ninja", "femenino",
    (10, 9, 10, 14), (6, 11, 4, 5), 10, "cuerpo_a_cuerpo", 20,
    "HAB_CAOS_LIBERADO", "aleatorio", "assets/aventureros/ninja.png",
)
BARBARO = _plantilla(
    "PLANTILLA_BARBARO", "Uk-Haaie", "Bárbaro", "masculino",
    (15, 10, 10, 10), (14, 8, 5, 3), 0, "cuerpo_a_cuerpo", 30,
    "HAB_COMPARTIR_DOLOR", "aleatorio", "assets/aventureros/barbaro.png",
)
DEFENSOR = _plantilla(
    "PLANTILLA_DEFENSOR", "Dangabaruk", "Defensor", "masculino",
    (18, 5, 20, 5), (15, 3, 10, 1), 0, "cuerpo_a_cuerpo", 40,
    "HAB_PROVOCAR", "aleatorio", "assets/aventureros/defensor.png",
)
ALABARDERO = _plantilla(
    "PLANTILLA_ALABARDERO", "Rapzil", "Alabardero", "masculino",
    (12, 10, 10, 5), (9, 8, 6, 5), 0, "cuerpo_a_cuerpo", 40,
    "HAB_GOLPE_TEMBLOR", "aleatorio", "assets/aventureros/alabardero.png",
)
CAZADOR = _plantilla(
    "PLANTILLA_CAZADOR", "Garonido", "Cazador", "masculino",
    (8, 13, 8, 10), (8, 7, 5, 4), 10, "distancia", 30,
    "HAB_FLECHA_PESADA", "aleatorio", "assets/aventureros/cazador.png",
)
CURADOR = _plantilla(
    "PLANTILLA_CURADOR", "Dri’wing", "Curador", "femenino",
    (6, 5, 6, 4), (6, 3, 4, 3), 0, "magico", 20,
    "HAB_GRAN_CURA", "aleatorio", "assets/aventureros/curador.png",
)
ASESINO = _plantilla(
    "PLANTILLA_ASESINO", "Kitsu", "Asesino", "femenino",
    (10, 12, 6, 15), (6, 10, 5, 5), 15, "distancia", 50,
    "HAB_MUERTE", "menor_vida_actual", "assets/aventureros/asesino.png",
)
SOLDADO = _plantilla(
    "PLANTILLA_SOLDADO", "Doker", "Soldado", "masculino",
    (12, 6, 10, 5), (8, 6, 6, 2), 0, "cuerpo_a_cuerpo", 10,
    "HAB_GOLPE_POTENCIADO", "aleatorio", "assets/aventureros/soldado.png",
)
PSIQUICO = _plantilla(
    "PLANTILLA_PSIQUICO", "Soul’viraph", "Psíquico", "masculino",
    (10, 8, 8, 7), (6, 4, 6, 2), 0, "distancia", 20,
    "HAB_ESCUDO_MENTAL", "aleatorio", "assets/aventureros/psiquico.png",
)
INFERNAL = _plantilla(
    "PLANTILLA_INFERNAL", "Kormak", "Infernal", "masculino",
    (13, 11, 9, 5), (7, 8, 4, 3), 0, "cuerpo_a_cuerpo", 40,
    "HAB_BOLA_OSCURA", "aleatorio", "assets/aventureros/infernal.png",
)
CONJURADOR_MAREAS = _plantilla(
    "PLANTILLA_CONJURADOR_MAREAS", "Bransha’kana", "Conjurador de Mareas", "masculino",
    (5, 15, 6, 4), (3, 11, 2, 2), 0, "magico", 50,
    "HAB_FUENTE_DE_VIDA", "aleatorio", "assets/aventureros/conjurador_mareas.png",
)
PALADIN = _plantilla(
    "PLANTILLA_PALADIN", "Wirmann", "Paladín", "masculino",
    (16, 7, 10, 5), (10, 5, 7, 2), 0, "cuerpo_a_cuerpo", 30,
    "HAB_PROTEGER", "aleatorio", "assets/aventureros/paladin.png",
)


CATALOGO_PLANTILLAS: dict[str, PlantillaAventurero] = {
    plantilla["id"]: plantilla
    for plantilla in (
        MAGO_ARCANO, HECHICERO, ARQUERO, NINJA, BARBARO,
        DEFENSOR, ALABARDERO, CAZADOR, CURADOR, ASESINO,
        SOLDADO, PSIQUICO, INFERNAL, CONJURADOR_MAREAS, PALADIN,
    )
}

PLANTILLAS_INICIALES: tuple[str, str, str] = (
    "PLANTILLA_SOLDADO",
    "PLANTILLA_ARQUERO",
    "PLANTILLA_HECHICERO",
)

