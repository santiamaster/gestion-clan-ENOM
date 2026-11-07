"""Pruebas del catálogo de nombres aleatorios para aventureros."""

import unittest
from random import Random

from catalogos.nombres import (
    NOMBRES_FEMENINOS,
    NOMBRES_MASCULINOS,
    elegir_nombre,
)


class PruebasCatalogoNombres(unittest.TestCase):
    """Comprueba integridad y selección de los nombres disponibles."""

    def test_contiene_cien_nombres_limpios_y_sin_repeticiones(self) -> None:
        catalogo_completo: tuple[str, ...] = (
            NOMBRES_MASCULINOS + NOMBRES_FEMENINOS
        )

        self.assertEqual(len(catalogo_completo), 100)
        self.assertTrue(
            all(
                nombre != "" and nombre.strip() == nombre
                for nombre in catalogo_completo
            )
        )
        self.assertEqual(len(set(catalogo_completo)), len(catalogo_completo))

    def test_selecciona_un_nombre_del_catalogo_correspondiente(self) -> None:
        generador_masculino = Random(7)
        generador_femenino = Random(7)

        nombre_masculino: str = elegir_nombre("masculino", generador_masculino)
        nombre_femenino: str = elegir_nombre("femenino", generador_femenino)

        self.assertIn(nombre_masculino, NOMBRES_MASCULINOS)
        self.assertIn(nombre_femenino, NOMBRES_FEMENINOS)

    def test_una_semilla_repite_la_misma_seleccion(self) -> None:
        primera_seleccion: str = elegir_nombre("masculino", Random(19))
        segunda_seleccion: str = elegir_nombre("masculino", Random(19))

        self.assertEqual(primera_seleccion, segunda_seleccion)


if __name__ == "__main__":
    unittest.main()
