"""Nombres disponibles para la creación aleatoria de aventureros."""

from random import Random

from modelos.tipos import Sexo


NOMBRES_MASCULINOS: tuple[str, ...] = (
    "Aldren", "Bastian", "Caelan", "Darian", "Edrik",
    "Faelar", "Garen", "Hadrian", "Ivar", "Jarek",
    "Kael", "Leoric", "Maelor", "Narek", "Oren",
    "Perrin", "Quinlan", "Ronan", "Soren", "Theron",
    "Ulric", "Vaelor", "Wulfric", "Xander", "Yorik",
    "Zarek", "Alaric", "Brenner", "Cedric", "Dorian",
    "Evander", "Fenric", "Galen", "Hector", "Isandro",
    "Julian", "Kieran", "Lucan", "Magnus", "Nolan",
    "Orion", "Rowan", "Silas", "Tristan", "Uriel",
    "Viktor", "Wendel", "Xavian", "Yago", "Zephyr",
)

NOMBRES_FEMENINOS: tuple[str, ...] = (
    "Aelira", "Brienne", "Calista", "Delia", "Elowen",
    "Freya", "Gwyneth", "Helena", "Isolde", "Jaina",
    "Kaela", "Lyanna", "Mireya", "Nyssa", "Oriana",
    "Petra", "Quilla", "Rhea", "Selene", "Thalia",
    "Una", "Valeria", "Wenda", "Xenia", "Ylva",
    "Zelda", "Amara", "Beatriz", "Celine", "Diana",
    "Elara", "Fiona", "Giselle", "Hana", "Iliana",
    "Julieta", "Kiara", "Liora", "Mara", "Nadia",
    "Ophelia", "Renata", "Serena", "Tessa", "Ursula",
    "Vera", "Winona", "Ximena", "Yara", "Zoe",
)


def elegir_nombre(sexo: Sexo, generador: Random) -> str:
    """Elige un nombre aleatorio compatible con el sexo de la plantilla.

    Args:
        sexo: Sexo definido por la plantilla del aventurero.
        generador: Fuente de azar; puede sembrarse para obtener pruebas
            deterministas.

    Returns:
        Un nombre perteneciente al catálogo correspondiente.
    """

    catalogo: tuple[str, ...] = (
        NOMBRES_MASCULINOS if sexo == "masculino" else NOMBRES_FEMENINOS
    )
    return generador.choice(catalogo)

