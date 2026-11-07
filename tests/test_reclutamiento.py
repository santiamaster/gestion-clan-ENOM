"""Pruebas del mercado y el reclutamiento de aventureros."""

import unittest
from collections.abc import Sequence
from random import Random
from typing import TypeVar

from catalogos.nombres import NOMBRES_FEMENINOS, NOMBRES_MASCULINOS
from catalogos.plantillas import CATALOGO_PLANTILLAS
from modelos.tipos import OfertaReclutamiento
from servicios.clan import crear_estado_inicial_clan
from servicios.reclutamiento import (
    calcular_cantidad_ofertas,
    calcular_limite_contrataciones,
    generar_ofertas,
    renovar_mercado,
)


T = TypeVar("T")


class GeneradorPrimerElemento(Random):
    """Generador controlado que siempre selecciona el primer elemento."""

    def choice(self, seq: Sequence[T]) -> T:
        """Devuelve siempre el primer elemento de una secuencia no vacía."""

        return seq[0]

    def randint(self, a: int, b: int) -> int:
        """Devuelve siempre el límite inferior recibido."""

        return a


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


class PruebasGeneracionOfertas(unittest.TestCase):
    """Comprueba el contenido generado para cada renovación del mercado."""

    def test_genera_ofertas_validas_para_cada_nivel_del_clan(self) -> None:
        cantidades_esperadas: dict[int, int] = {
            1: 2,
            2: 4,
            3: 6,
            4: 8,
            5: 10,
        }

        for nivel_clan, cantidad_esperada in cantidades_esperadas.items():
            with self.subTest(nivel_clan=nivel_clan):
                ofertas = generar_ofertas(nivel_clan, Random(nivel_clan))

                self.assertEqual(len(ofertas), cantidad_esperada)
                self.assertEqual(
                    [oferta["id_oferta"] for oferta in ofertas],
                    [
                        f"OF-{numero:02d}"
                        for numero in range(1, cantidad_esperada + 1)
                    ],
                )

                for oferta in ofertas:
                    plantilla = CATALOGO_PLANTILLAS[oferta["plantilla_id"]]
                    nombres_validos: tuple[str, ...] = (
                        NOMBRES_MASCULINOS
                        if plantilla["sexo"] == "masculino"
                        else NOMBRES_FEMENINOS
                    )
                    self.assertGreaterEqual(oferta["nivel"], 1)
                    self.assertLessEqual(oferta["nivel"], nivel_clan)
                    self.assertIn(oferta["nombre"], nombres_validos)
                    self.assertEqual(
                        oferta["coste"],
                        plantilla["coste_base"] * oferta["nivel"],
                    )

    def test_conserva_plantillas_repetidas(self) -> None:
        ofertas = generar_ofertas(2, GeneradorPrimerElemento())

        self.assertEqual(len(ofertas), 4)
        self.assertEqual(
            {oferta["plantilla_id"] for oferta in ofertas},
            {"PLANTILLA_MAGO_ARCANO"},
        )


class PruebasRenovacionMercado(unittest.TestCase):
    """Comprueba el reemplazo completo de una renovación anterior."""

    def test_reemplaza_ofertas_y_restablece_limite_del_nivel(self) -> None:
        estado = crear_estado_inicial_clan("Clan Alba")
        estado["nivel"] = 3
        oferta_anterior: OfertaReclutamiento = {
            "id_oferta": "OF-ANTIGUA",
            "nombre": "Candidato anterior",
            "plantilla_id": "PLANTILLA_SOLDADO",
            "nivel": 1,
            "coste": 10,
        }
        estado["ofertas_reclutamiento"] = [oferta_anterior]
        ofertas_anteriores = estado["ofertas_reclutamiento"]

        renovar_mercado(estado, Random(7))

        self.assertIsNot(estado["ofertas_reclutamiento"], ofertas_anteriores)
        self.assertEqual(estado["contrataciones_restantes"], 3)
        self.assertEqual(len(estado["ofertas_reclutamiento"]), 6)
        self.assertEqual(
            [
                oferta["id_oferta"]
                for oferta in estado["ofertas_reclutamiento"]
            ],
            ["OF-01", "OF-02", "OF-03", "OF-04", "OF-05", "OF-06"],
        )


if __name__ == "__main__":
    unittest.main()
