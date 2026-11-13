"""Pruebas del flujo temporal y las consecuencias de expediciones."""

import unittest
from copy import deepcopy
from unittest.mock import patch

from catalogos.mazmorras import CATALOGO_MAZMORRAS, MAZMORRA_LIMOS
from catalogos.plantillas import CATALOGO_PLANTILLAS
from modelos.combate import DefinicionMazmorra
from modelos.expediciones import EstadoExpedicion
from modelos.tipos import (
    AventureroActivo,
    EstadoAventurero,
    EstadoClan,
    EstadoPartida,
    NivelClan,
)
from servicios.aventureros import (
    AventureroNoEncontradoError,
    AventureroNoEstaVivoError,
    AventureroRepetidoEnGrupoError,
    GrupoExcedeLimiteError,
    GrupoVacioError,
)
from servicios.clan import crear_estado_inicial_clan
from servicios.expediciones import (
    EstadoExpedicionInvalidoError,
    MazmorraNoDisponibleError,
    MazmorraNoEncontradaError,
    iniciar_expedicion,
)


PLANTILLAS_PRUEBA: tuple[str, ...] = tuple(CATALOGO_PLANTILLAS)


def crear_aventurero(
    numero: int,
    *,
    estado: EstadoAventurero = "vivo",
) -> AventureroActivo:
    """Construye un integrante válido con un identificador correlativo."""

    return {
        "id": f"AV-{numero:04d}",
        "nombre": f"Aventurero {numero}",
        "plantilla_id": PLANTILLAS_PRUEBA[(numero - 1) % len(PLANTILLAS_PRUEBA)],
        "nivel": 1,
        "experiencia": 0,
        "estado": estado,
    }


def crear_clan(nivel: NivelClan = 1) -> EstadoClan:
    """Construye un estado en curso con el nivel indicado para las pruebas."""

    estado: EstadoClan = crear_estado_inicial_clan("Guardianes del Alba")
    estado["nivel"] = nivel
    return estado


class PruebasInicioExpedicion(unittest.TestCase):
    """Comprueba validaciones y construcción del estado temporal inicial."""

    def test_inicia_la_mazmorra_sin_modificar_la_partida(self) -> None:
        clan: EstadoClan = crear_clan()
        activos: list[AventureroActivo] = [
            crear_aventurero(1),
            crear_aventurero(2),
            crear_aventurero(3),
        ]
        clan_anterior: EstadoClan = deepcopy(clan)
        activos_anteriores: list[AventureroActivo] = deepcopy(activos)

        expedicion: EstadoExpedicion = iniciar_expedicion(
            clan,
            activos,
            ["AV-0001", "AV-0002", "AV-0003"],
            MAZMORRA_LIMOS["id"],
        )

        self.assertEqual(expedicion["mazmorra_id"], "MAZMORRA_LIMOS")
        self.assertEqual(expedicion["dificultad"], 1)
        self.assertEqual(expedicion["proxima_oleada"], 1)
        self.assertEqual(expedicion["oleadas_superadas"], 0)
        self.assertEqual(expedicion["experiencia_acumulada"], 0)
        self.assertEqual(expedicion["dinero_acumulado"], 0)
        self.assertEqual(expedicion["estado_flujo"], "lista_para_oleada")
        self.assertIsNone(expedicion["resultado_final"])
        self.assertIsNone(expedicion["ultima_oleada"])
        self.assertEqual(clan, clan_anterior)
        self.assertEqual(activos, activos_anteriores)

    def test_admite_uno_tres_y_el_maximo_de_siete_integrantes(self) -> None:
        activos: list[AventureroActivo] = [
            crear_aventurero(numero) for numero in range(1, 8)
        ]
        casos: tuple[tuple[NivelClan, int], ...] = ((1, 1), (1, 3), (5, 7))

        for nivel, cantidad in casos:
            with self.subTest(nivel=nivel, cantidad=cantidad):
                ids: list[str] = [
                    aventurero["id"] for aventurero in activos[:cantidad]
                ]
                expedicion: EstadoExpedicion = iniciar_expedicion(
                    crear_clan(nivel),
                    activos,
                    ids,
                    "MAZMORRA_LIMOS",
                )

                self.assertEqual(len(expedicion["aventureros"]), cantidad)

    def test_conserva_el_orden_e_independiza_los_estados_de_combate(
        self,
    ) -> None:
        activos: list[AventureroActivo] = [
            crear_aventurero(1),
            crear_aventurero(2),
            crear_aventurero(3),
        ]

        expedicion: EstadoExpedicion = iniciar_expedicion(
            crear_clan(),
            activos,
            [" av-0003 ", "AV-0001", "av-0002"],
            "MAZMORRA_LIMOS",
        )

        self.assertEqual(
            [aventurero["id"] for aventurero in expedicion["aventureros"]],
            ["AV-0003", "AV-0001", "AV-0002"],
        )
        for temporal in expedicion["aventureros"]:
            persistente: AventureroActivo = next(
                aventurero
                for aventurero in activos
                if aventurero["id"] == temporal["id"]
            )
            self.assertIsNot(temporal, persistente)

        expedicion["aventureros"][0]["nombre"] = "Nombre temporal"
        self.assertEqual(activos[2]["nombre"], "Aventurero 3")

    def test_reutiliza_los_errores_de_seleccion_del_grupo(self) -> None:
        activos: list[AventureroActivo] = [
            crear_aventurero(1),
            crear_aventurero(2, estado="muerto"),
            crear_aventurero(3),
            crear_aventurero(4),
        ]
        casos: tuple[tuple[type[ValueError], list[str]], ...] = (
            (GrupoVacioError, []),
            (AventureroRepetidoEnGrupoError, ["AV-0001", "av-0001"]),
            (AventureroNoEncontradoError, ["AV-9999"]),
            (AventureroNoEstaVivoError, ["AV-0002"]),
            (
                GrupoExcedeLimiteError,
                ["AV-0001", "AV-0002", "AV-0003", "AV-0004"],
            ),
        )

        for error, ids in casos:
            with self.subTest(error=error.__name__):
                with self.assertRaises(error):
                    iniciar_expedicion(
                        crear_clan(),
                        activos,
                        ids,
                        "MAZMORRA_LIMOS",
                    )

    def test_rechaza_una_partida_que_ya_finalizo(self) -> None:
        estados_finales: tuple[EstadoPartida, ...] = ("victoria", "derrota")
        for estado_partida in estados_finales:
            with self.subTest(estado_partida=estado_partida):
                clan: EstadoClan = crear_clan()
                clan["estado_partida"] = estado_partida

                with self.assertRaises(EstadoExpedicionInvalidoError):
                    iniciar_expedicion(
                        clan,
                        [crear_aventurero(1)],
                        ["AV-0001"],
                        "MAZMORRA_LIMOS",
                    )

    def test_diferencia_una_mazmorra_inexistente_de_una_no_disponible(
        self,
    ) -> None:
        with self.assertRaises(MazmorraNoEncontradaError):
            iniciar_expedicion(
                crear_clan(),
                [crear_aventurero(1)],
                ["AV-0001"],
                "MAZMORRA_INEXISTENTE",
            )

        mazmorra_futura: DefinicionMazmorra = {
            "id": "MAZMORRA_ROCAS",
            "nombre": "Mazmorra de las Rocas",
            "dificultad": 2,
            "oleadas": [],
        }
        with patch.dict(
            CATALOGO_MAZMORRAS,
            {mazmorra_futura["id"]: mazmorra_futura},
        ):
            with self.assertRaises(MazmorraNoDisponibleError):
                iniciar_expedicion(
                    crear_clan(),
                    [crear_aventurero(1)],
                    ["AV-0001"],
                    mazmorra_futura["id"],
                )


if __name__ == "__main__":
    unittest.main()
