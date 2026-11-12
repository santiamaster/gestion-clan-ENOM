"""Catálogo permanente de enemigos disponibles en las mazmorras."""

from modelos.combate import PlantillaEnemigo
from modelos.tipos import EfectividadAtaque, TipoAtaque


def _enemigo(
    identificador: str,
    nombre: str,
    estadisticas: tuple[int, int, int, int],
    tipo_ataque: TipoAtaque,
    efectividades: tuple[
        EfectividadAtaque,
        EfectividadAtaque,
        EfectividadAtaque,
    ],
    experiencia: int,
    dinero: int,
    es_jefe: bool = False,
) -> PlantillaEnemigo:
    """Construye una plantilla enemiga manteniendo el catálogo compacto."""

    vida, dano, defensa, velocidad = estadisticas
    cuerpo_a_cuerpo, distancia, magico = efectividades
    return {
        "id": identificador,
        "nombre": nombre,
        "estadisticas": {
            "vida": vida,
            "dano": dano,
            "defensa": defensa,
            "velocidad": velocidad,
        },
        "tipo_ataque": tipo_ataque,
        "efectividades": {
            "cuerpo_a_cuerpo": cuerpo_a_cuerpo,
            "distancia": distancia,
            "magico": magico,
        },
        "experiencia": experiencia,
        "dinero": dinero,
        "es_jefe": es_jefe,
        "imagen": "",
        "descripcion": "",
    }


LIMO: PlantillaEnemigo = _enemigo(
    "LIMOS_LIMO",
    "Limo",
    (20, 20, 1, 1),
    "magico",
    ("efectivo", "efectivo", "inefectivo"),
    10,
    1,
)

LIME: PlantillaEnemigo = _enemigo(
    "LIMOS_LIME",
    "Lime",
    (40, 15, 5, 2),
    "cuerpo_a_cuerpo",
    ("inefectivo", "neutral", "efectivo"),
    10,
    1,
)

LIMA: PlantillaEnemigo = _enemigo(
    "LIMOS_LIMA",
    "Lima",
    (30, 17, 3, 3),
    "distancia",
    ("efectivo", "inefectivo", "efectivo"),
    10,
    1,
)

BRUJILIMO: PlantillaEnemigo = _enemigo(
    "LIMOS_BRUJILIMO",
    "Brujilimo",
    (20, 30, 5, 5),
    "magico",
    ("efectivo", "neutral", "inefectivo"),
    15,
    3,
)

MEDULIMO: PlantillaEnemigo = _enemigo(
    "LIMOS_MEDULIMO",
    "Medulimo",
    (50, 20, 9, 6),
    "cuerpo_a_cuerpo",
    ("neutral", "neutral", "efectivo"),
    15,
    3,
)

METALIMO: PlantillaEnemigo = _enemigo(
    "LIMOS_METALIMO",
    "Metalimo",
    (15, 20, 20, 15),
    "cuerpo_a_cuerpo",
    ("inefectivo", "inefectivo", "inefectivo"),
    20,
    18,
)

TRIO_LIMOSO: PlantillaEnemigo = _enemigo(
    "LIMOS_TRIO_LIMOSO",
    "Trío Limoso",
    (90, 25, 9, 6),
    "cuerpo_a_cuerpo",
    ("efectivo", "efectivo", "efectivo"),
    20,
    8,
)

LIMO_PRISMATICO: PlantillaEnemigo = _enemigo(
    "LIMOS_LIMO_PRISMATICO",
    "Limo Prismático",
    (60, 30, 30, 30),
    "cuerpo_a_cuerpo",
    ("neutral", "neutral", "neutral"),
    30,
    10,
)

MEDULIMO_GUERRERO: PlantillaEnemigo = _enemigo(
    "LIMOS_MEDULIMO_GUERRERO",
    "Medulimo Guerrero",
    (100, 25, 40, 15),
    "cuerpo_a_cuerpo",
    ("neutral", "neutral", "efectivo"),
    40,
    15,
)

REY_LIMO: PlantillaEnemigo = _enemigo(
    "LIMOS_REY_LIMO",
    "Rey Limo",
    (120, 40, 50, 20),
    "magico",
    ("inefectivo", "neutral", "neutral"),
    60,
    30,
    True,
)


CATALOGO_ENEMIGOS: dict[str, PlantillaEnemigo] = {
    plantilla["id"]: plantilla
    for plantilla in (
        LIMO,
        LIME,
        LIMA,
        BRUJILIMO,
        MEDULIMO,
        METALIMO,
        TRIO_LIMOSO,
        LIMO_PRISMATICO,
        MEDULIMO_GUERRERO,
        REY_LIMO,
    )
}

