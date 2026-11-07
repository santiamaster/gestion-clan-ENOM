"""Pruebas del mercado y el reclutamiento de aventureros."""

import unittest

from servicios.reclutamiento import (
    calcular_cantidad_ofertas,
    calcular_limite_contrataciones,
)


class PruebasProgresionMercado(unittest.TestCase):
    """Comprueba la progresión del mercado según el nivel del clan."""

    def test_calcula_cantidad_de_ofertas_para_cada_nivel(self) -> None:
        cantidades_esperadas: dict[int, int] = {
            1: 2,
            2: 4,
            3: 6,
            4: 8,
            5: 10,
        }

        for nivel, cantidad_esperada in cantidades_esperadas.items():
            with self.subTest(nivel=nivel):
                self.assertEqual(
                    calcular_cantidad_ofertas(nivel),
                    cantidad_esperada,
                )

    def test_calcula_limite_de_contrataciones_para_cada_nivel(self) -> None:
        limites_esperados: dict[int, int] = {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
        }

        for nivel, limite_esperado in limites_esperados.items():
            with self.subTest(nivel=nivel):
                self.assertEqual(
                    calcular_limite_contrataciones(nivel),
                    limite_esperado,
                )

    def test_rechaza_niveles_fuera_del_intervalo(self) -> None:
        for nivel in (0, 6):
            with self.subTest(nivel=nivel):
                with self.assertRaises(ValueError):
                    calcular_cantidad_ofertas(nivel)
                with self.assertRaises(ValueError):
                    calcular_limite_contrataciones(nivel)


if __name__ == "__main__":
    unittest.main()
