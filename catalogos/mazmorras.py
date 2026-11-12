"""Catálogo permanente de mazmorras y sus oleadas fijas."""

from modelos.combate import DefinicionMazmorra, GrupoEnemigosOleada


def _grupo(plantilla_id: str, cantidad: int) -> GrupoEnemigosOleada:
    """Construye un grupo de enemigos de una misma plantilla."""

    return {"plantilla_id": plantilla_id, "cantidad": cantidad}


MAZMORRA_LIMOS: DefinicionMazmorra = {
    "id": "MAZMORRA_LIMOS",
    "nombre": "Mazmorra de los Limos",
    "dificultad": 1,
    "oleadas": [
        {
            "numero": 1,
            "enemigos": [
                _grupo("LIMOS_LIMO", 1),
                _grupo("LIMOS_LIME", 1),
                _grupo("LIMOS_LIMA", 1),
            ],
        },
        {
            "numero": 2,
            "enemigos": [
                _grupo("LIMOS_LIMO", 2),
                _grupo("LIMOS_LIME", 2),
                _grupo("LIMOS_LIMA", 2),
            ],
        },
        {
            "numero": 3,
            "enemigos": [
                _grupo("LIMOS_LIMO", 1),
                _grupo("LIMOS_LIME", 1),
                _grupo("LIMOS_LIMA", 1),
                _grupo("LIMOS_BRUJILIMO", 1),
                _grupo("LIMOS_MEDULIMO", 1),
            ],
        },
        {
            "numero": 4,
            "enemigos": [
                _grupo("LIMOS_LIMO", 2),
                _grupo("LIMOS_LIME", 2),
                _grupo("LIMOS_LIMA", 2),
                _grupo("LIMOS_BRUJILIMO", 1),
                _grupo("LIMOS_MEDULIMO", 1),
            ],
        },
        {
            "numero": 5,
            "enemigos": [
                _grupo("LIMOS_LIMO", 2),
                _grupo("LIMOS_LIME", 2),
                _grupo("LIMOS_LIMA", 2),
                _grupo("LIMOS_BRUJILIMO", 2),
                _grupo("LIMOS_MEDULIMO", 2),
            ],
        },
        {
            "numero": 6,
            "enemigos": [
                _grupo("LIMOS_BRUJILIMO", 2),
                _grupo("LIMOS_MEDULIMO", 2),
                _grupo("LIMOS_TRIO_LIMOSO", 2),
            ],
        },
        {
            "numero": 7,
            "enemigos": [
                _grupo("LIMOS_BRUJILIMO", 1),
                _grupo("LIMOS_MEDULIMO", 1),
                _grupo("LIMOS_METALIMO", 1),
                _grupo("LIMOS_TRIO_LIMOSO", 1),
                _grupo("LIMOS_LIMO_PRISMATICO", 1),
            ],
        },
        {
            "numero": 8,
            "enemigos": [
                _grupo("LIMOS_METALIMO", 1),
                _grupo("LIMOS_TRIO_LIMOSO", 2),
                _grupo("LIMOS_LIMO_PRISMATICO", 1),
                _grupo("LIMOS_MEDULIMO_GUERRERO", 1),
            ],
        },
        {
            "numero": 9,
            "enemigos": [
                _grupo("LIMOS_TRIO_LIMOSO", 2),
                _grupo("LIMOS_LIMO_PRISMATICO", 2),
                _grupo("LIMOS_MEDULIMO_GUERRERO", 1),
            ],
        },
        {
            "numero": 10,
            "enemigos": [_grupo("LIMOS_REY_LIMO", 1)],
        },
    ],
}


CATALOGO_MAZMORRAS: dict[str, DefinicionMazmorra] = {
    MAZMORRA_LIMOS["id"]: MAZMORRA_LIMOS,
}

