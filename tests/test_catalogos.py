"""Pruebas iniciales de integridad de los catálogos."""

import unittest

from catalogos.habilidades import CATALOGO_HABILIDADES
from catalogos.plantillas import CATALOGO_PLANTILLAS, PLANTILLAS_INICIALES


class PruebasCatalogos(unittest.TestCase):
    """Comprueba que los catálogos estén completos y relacionados."""

    def test_existen_quince_habilidades(self) -> None:
        self.assertEqual(len(CATALOGO_HABILIDADES), 15)

    def test_existen_quince_plantillas(self) -> None:
        self.assertEqual(len(CATALOGO_PLANTILLAS), 15)

    def test_todas_las_habilidades_existen(self) -> None:
        for plantilla in CATALOGO_PLANTILLAS.values():
            self.assertIn(plantilla["habilidad_id"], CATALOGO_HABILIDADES)

    def test_las_claves_coinciden_con_los_identificadores(self) -> None:
        for identificador, plantilla in CATALOGO_PLANTILLAS.items():
            self.assertEqual(identificador, plantilla["id"])
        for identificador, habilidad in CATALOGO_HABILIDADES.items():
            self.assertEqual(identificador, habilidad["id"])

    def test_existen_las_tres_plantillas_iniciales(self) -> None:
        for identificador in PLANTILLAS_INICIALES:
            self.assertIn(identificador, CATALOGO_PLANTILLAS)


if __name__ == "__main__":
    unittest.main()

