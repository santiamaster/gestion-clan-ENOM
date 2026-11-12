"""Pruebas del catálogo de enemigos de la Mazmorra de los Limos."""

import unittest
from typing import cast

import catalogos.enemigos as enemigos
from modelos.combate import PlantillaEnemigo


def _catalogo() -> dict[str, PlantillaEnemigo]:
    """Obtiene el catálogo y falla claramente mientras no esté implementado."""

    catalogo: object | None = getattr(enemigos, "CATALOGO_ENEMIGOS", None)
    if catalogo is None:
        raise AssertionError("Falta definir CATALOGO_ENEMIGOS.")
    return cast(dict[str, PlantillaEnemigo], catalogo)


class PruebasCatalogoEnemigos(unittest.TestCase):
    """Comprueba identidad, valores representativos e invariantes."""

    def test_contiene_las_diez_plantillas_aprobadas(self) -> None:
        catalogo: dict[str, PlantillaEnemigo] = _catalogo()

        self.assertEqual(
            set(catalogo),
            {
                "LIMOS_LIMO",
                "LIMOS_LIME",
                "LIMOS_LIMA",
                "LIMOS_BRUJILIMO",
                "LIMOS_MEDULIMO",
                "LIMOS_METALIMO",
                "LIMOS_TRIO_LIMOSO",
                "LIMOS_LIMO_PRISMATICO",
                "LIMOS_MEDULIMO_GUERRERO",
                "LIMOS_REY_LIMO",
            },
        )
        self.assertEqual(len(catalogo), 10)

    def test_conserva_estadisticas_y_recompensas_representativas(self) -> None:
        catalogo: dict[str, PlantillaEnemigo] = _catalogo()

        self.assertEqual(catalogo["LIMOS_LIMO"]["estadisticas"]["vida"], 20)
        self.assertEqual(catalogo["LIMOS_METALIMO"]["dinero"], 18)
        self.assertEqual(
            catalogo["LIMOS_MEDULIMO_GUERRERO"]["estadisticas"],
            {"vida": 100, "dano": 25, "defensa": 40, "velocidad": 15},
        )

    def test_trio_limoso_utiliza_el_nombre_corregido(self) -> None:
        catalogo: dict[str, PlantillaEnemigo] = _catalogo()

        self.assertEqual(
            catalogo["LIMOS_TRIO_LIMOSO"]["nombre"],
            "Trío Limoso",
        )

    def test_solo_el_rey_limo_es_jefe(self) -> None:
        catalogo: dict[str, PlantillaEnemigo] = _catalogo()
        jefes: list[str] = [
            identificador
            for identificador, plantilla in catalogo.items()
            if plantilla["es_jefe"]
        ]

        self.assertEqual(jefes, ["LIMOS_REY_LIMO"])

    def test_las_claves_coinciden_con_los_identificadores(self) -> None:
        catalogo: dict[str, PlantillaEnemigo] = _catalogo()

        for identificador, plantilla in catalogo.items():
            with self.subTest(identificador=identificador):
                self.assertEqual(plantilla["id"], identificador)

    def test_todas_las_plantillas_tienen_valores_validos(self) -> None:
        catalogo: dict[str, PlantillaEnemigo] = _catalogo()

        for identificador, plantilla in catalogo.items():
            with self.subTest(identificador=identificador):
                estadisticas: dict[str, int] = plantilla["estadisticas"]
                self.assertGreater(estadisticas["vida"], 0)
                self.assertGreaterEqual(estadisticas["dano"], 0)
                self.assertGreaterEqual(estadisticas["defensa"], 0)
                self.assertGreaterEqual(estadisticas["velocidad"], 0)
                self.assertGreaterEqual(plantilla["experiencia"], 0)
                self.assertGreaterEqual(plantilla["dinero"], 0)
                self.assertEqual(
                    set(plantilla["efectividades"]),
                    {"cuerpo_a_cuerpo", "distancia", "magico"},
                )
                self.assertTrue(
                    set(plantilla["efectividades"].values())
                    <= {"efectivo", "neutral", "inefectivo"}
                )
                self.assertIsInstance(plantilla["imagen"], str)
                self.assertIsInstance(plantilla["descripcion"], str)


if __name__ == "__main__":
    unittest.main()
