"""Pruebas de la composición fija de la Mazmorra de los Limos."""

import unittest
from typing import cast

from catalogos.enemigos import CATALOGO_ENEMIGOS
import catalogos.mazmorras as mazmorras
from modelos.combate import DefinicionMazmorra, DefinicionOleada


def _mazmorra_limos() -> DefinicionMazmorra:
    """Obtiene la mazmorra y falla claramente mientras no esté implementada."""

    mazmorra: object | None = getattr(mazmorras, "MAZMORRA_LIMOS", None)
    if mazmorra is None:
        raise AssertionError("Falta definir MAZMORRA_LIMOS.")
    return cast(DefinicionMazmorra, mazmorra)


def _oleada(numero: int) -> DefinicionOleada:
    """Devuelve una oleada por su número dentro de la mazmorra aprobada."""

    return _mazmorra_limos()["oleadas"][numero - 1]


class PruebasMazmorraLimos(unittest.TestCase):
    """Comprueba identidad, composiciones y recompensas potenciales."""

    def test_contiene_diez_oleadas_consecutivas(self) -> None:
        numeros: list[int] = [
            oleada["numero"] for oleada in _mazmorra_limos()["oleadas"]
        ]

        self.assertEqual(numeros, list(range(1, 11)))

    def test_todas_las_referencias_y_cantidades_son_validas(self) -> None:
        for oleada in _mazmorra_limos()["oleadas"]:
            identificadores: list[str] = []
            for grupo in oleada["enemigos"]:
                identificadores.append(grupo["plantilla_id"])
                self.assertIn(grupo["plantilla_id"], CATALOGO_ENEMIGOS)
                self.assertGreater(grupo["cantidad"], 0)

            self.assertEqual(len(identificadores), len(set(identificadores)))

    def test_conserva_la_composicion_corregida_de_la_oleada_seis(self) -> None:
        self.assertEqual(
            _oleada(6)["enemigos"],
            [
                {"plantilla_id": "LIMOS_BRUJILIMO", "cantidad": 2},
                {"plantilla_id": "LIMOS_MEDULIMO", "cantidad": 2},
                {"plantilla_id": "LIMOS_TRIO_LIMOSO", "cantidad": 2},
            ],
        )

    def test_la_ultima_oleada_contiene_solo_al_rey_limo(self) -> None:
        self.assertEqual(
            _oleada(10)["enemigos"],
            [{"plantilla_id": "LIMOS_REY_LIMO", "cantidad": 1}],
        )

    def test_totales_potenciales_coinciden_con_la_composicion(self) -> None:
        cantidad_total: int = 0
        experiencia_total: int = 0
        dinero_total: int = 0

        for oleada in _mazmorra_limos()["oleadas"]:
            for grupo in oleada["enemigos"]:
                cantidad: int = grupo["cantidad"]
                plantilla = CATALOGO_ENEMIGOS[grupo["plantilla_id"]]
                cantidad_total += cantidad
                experiencia_total += plantilla["experiencia"] * cantidad
                dinero_total += plantilla["dinero"] * cantidad

        self.assertEqual(cantidad_total, 54)
        self.assertEqual(experiencia_total, 890)
        self.assertEqual(dinero_total, 258)

    def test_el_catalogo_usa_el_identificador_de_la_mazmorra(self) -> None:
        catalogo: object | None = getattr(
            mazmorras,
            "CATALOGO_MAZMORRAS",
            None,
        )
        if catalogo is None:
            self.fail("Falta definir CATALOGO_MAZMORRAS.")

        catalogo_tipado = cast(dict[str, DefinicionMazmorra], catalogo)
        definicion: DefinicionMazmorra = _mazmorra_limos()
        self.assertEqual(catalogo_tipado, {definicion["id"]: definicion})


if __name__ == "__main__":
    unittest.main()
