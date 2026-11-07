"""Pruebas de construcción y guardado de una partida nueva."""

import unittest
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory

from catalogos.nombres import NOMBRES_FEMENINOS, NOMBRES_MASCULINOS
from catalogos.plantillas import CATALOGO_PLANTILLAS, PLANTILLAS_INICIALES
from modelos.tipos import AventureroActivo, EstadoClan
from servicios.aventureros import (
    crear_aventureros_iniciales,
    formatear_id_aventurero,
)
from servicios.clan import NombreClanInvalidoError, crear_estado_inicial_clan
from servicios.partidas import PartidaExistenteError, crear_nueva_partida
from servicios.persistencia import (
    PartidaIncompletaError,
    PartidaInvalidaError,
    cargar_partida,
)


class PruebasConstruccionClan(unittest.TestCase):
    """Comprueba los valores iniciales del estado general del clan."""

    def test_normaliza_y_construye_el_estado_inicial(self) -> None:
        estado: EstadoClan = crear_estado_inicial_clan(
            "  Guardianes del Alba  "
        )

        self.assertEqual(
            estado,
            {
                "nombre": "Guardianes del Alba",
                "nivel": 1,
                "dinero": 0,
                "siguiente_id_aventurero": 4,
                "contrataciones_restantes": 0,
                "estado_partida": "en_curso",
                "mazmorras_completadas": {
                    "mazmorra_1": False,
                    "mazmorra_2": False,
                    "mazmorra_3": False,
                    "mazmorra_4": False,
                    "mazmorra_5": False,
                },
                "ofertas_reclutamiento": [],
            },
        )

    def test_rechaza_un_nombre_vacio_o_compuesto_por_espacios(self) -> None:
        for nombre in ("", "   "):
            with self.subTest(nombre=nombre):
                with self.assertRaises(NombreClanInvalidoError):
                    crear_estado_inicial_clan(nombre)


class PruebasConstruccionAventureros(unittest.TestCase):
    """Comprueba los tres integrantes fijos de la partida inicial."""

    def test_formatea_identificadores_y_rechaza_numeros_invalidos(self) -> None:
        self.assertEqual(formatear_id_aventurero(1), "AV-0001")
        with self.assertRaises(ValueError):
            formatear_id_aventurero(0)

    def test_crea_la_terna_inicial_en_el_orden_acordado(self) -> None:
        integrantes: list[AventureroActivo] = crear_aventureros_iniciales(
            Random(7)
        )

        self.assertEqual(
            [integrante["id"] for integrante in integrantes],
            ["AV-0001", "AV-0002", "AV-0003"],
        )
        self.assertEqual(
            [integrante["plantilla_id"] for integrante in integrantes],
            list(PLANTILLAS_INICIALES),
        )
        for integrante in integrantes:
            self.assertEqual(integrante["nivel"], 1)
            self.assertEqual(integrante["experiencia"], 0)
            self.assertEqual(integrante["estado"], "vivo")

    def test_asigna_nombres_segun_el_sexo_de_cada_plantilla(self) -> None:
        integrantes: list[AventureroActivo] = crear_aventureros_iniciales(
            Random(11)
        )

        for integrante in integrantes:
            plantilla = CATALOGO_PLANTILLAS[integrante["plantilla_id"]]
            catalogo: tuple[str, ...] = (
                NOMBRES_MASCULINOS
                if plantilla["sexo"] == "masculino"
                else NOMBRES_FEMENINOS
            )
            self.assertIn(integrante["nombre"], catalogo)


class PruebasCreacionPartida(unittest.TestCase):
    """Comprueba la coordinación y la protección de los archivos guardados."""

    def test_crea_y_persiste_el_mercado_inicial(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"

            creada = crear_nueva_partida(
                "Guardianes del Alba",
                False,
                directorio,
                Random(7),
            )
            estado = creada[0]
            estado_recargado = cargar_partida(directorio)[0]

            self.assertEqual(estado["contrataciones_restantes"], 1)
            self.assertEqual(len(estado["ofertas_reclutamiento"]), 2)
            self.assertEqual(
                [
                    oferta["id_oferta"]
                    for oferta in estado["ofertas_reclutamiento"]
                ],
                ["OF-01", "OF-02"],
            )
            self.assertEqual(estado_recargado, estado)

    def test_guarda_y_recarga_los_tres_archivos_iniciales(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"

            creada = crear_nueva_partida(
                "Guardianes del Alba",
                False,
                directorio,
                Random(7),
            )

            self.assertEqual(cargar_partida(directorio), creada)
            self.assertEqual(
                {ruta.name for ruta in directorio.glob("*.json")},
                {
                    "estado_clan.json",
                    "datos_activos.json",
                    "datos_eliminados.json",
                },
            )

    def test_crea_nombres_validos_sin_recibir_un_generador(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"

            _, activos, _ = crear_nueva_partida(
                "Vigías de ENOM",
                False,
                directorio,
                None,
            )

            catalogo_completo: tuple[str, ...] = (
                NOMBRES_MASCULINOS + NOMBRES_FEMENINOS
            )
            self.assertEqual(len(activos), 3)
            for activo in activos:
                self.assertIn(activo["nombre"], catalogo_completo)

    def test_bloquea_una_sobrescritura_no_autorizada(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"
            crear_nueva_partida("Clan Original", False, directorio, Random(1))
            contenidos_anteriores: dict[str, bytes] = {
                ruta.name: ruta.read_bytes() for ruta in directorio.glob("*.json")
            }

            with self.assertRaises(PartidaExistenteError):
                crear_nueva_partida(
                    "Clan Nuevo",
                    False,
                    directorio,
                    Random(2),
                )

            contenidos_actuales: dict[str, bytes] = {
                ruta.name: ruta.read_bytes() for ruta in directorio.glob("*.json")
            }
            self.assertEqual(contenidos_actuales, contenidos_anteriores)

    def test_reemplaza_una_partida_valida_con_autorizacion(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"
            crear_nueva_partida("Clan Original", False, directorio, Random(1))

            nueva = crear_nueva_partida(
                "Clan Nuevo",
                True,
                directorio,
                Random(2),
            )

            self.assertEqual(nueva[0]["nombre"], "Clan Nuevo")
            self.assertEqual(cargar_partida(directorio), nueva)

    def test_conserva_una_partida_incompleta_aunque_se_autorice(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"
            directorio.mkdir(parents=True)
            archivo_existente = directorio / "datos_activos.json"
            archivo_existente.write_text("[]\n", encoding="utf-8")
            contenido_anterior: bytes = archivo_existente.read_bytes()

            with self.assertRaises(PartidaIncompletaError):
                crear_nueva_partida(
                    "Clan Nuevo",
                    True,
                    directorio,
                    Random(2),
                )

            self.assertEqual(archivo_existente.read_bytes(), contenido_anterior)
            self.assertEqual(list(directorio.glob("*.json")), [archivo_existente])

    def test_conserva_una_partida_invalida_aunque_se_autorice(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"
            crear_nueva_partida("Clan Original", False, directorio, Random(1))
            (directorio / "estado_clan.json").write_text("{", encoding="utf-8")
            contenidos_anteriores: dict[str, bytes] = {
                ruta.name: ruta.read_bytes() for ruta in directorio.glob("*.json")
            }

            with self.assertRaises(PartidaInvalidaError):
                crear_nueva_partida(
                    "Clan Nuevo",
                    True,
                    directorio,
                    Random(2),
                )

            contenidos_actuales: dict[str, bytes] = {
                ruta.name: ruta.read_bytes() for ruta in directorio.glob("*.json")
            }
            self.assertEqual(contenidos_actuales, contenidos_anteriores)


if __name__ == "__main__":
    unittest.main()
