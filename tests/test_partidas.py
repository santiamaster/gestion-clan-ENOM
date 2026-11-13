"""Pruebas de construcción y guardado de una partida nueva."""

import unittest
from copy import deepcopy
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory
from unittest.mock import patch

from catalogos.nombres import NOMBRES_FEMENINOS, NOMBRES_MASCULINOS
from catalogos.plantillas import CATALOGO_PLANTILLAS, PLANTILLAS_INICIALES
from modelos.combate import AventureroCombate, EnemigoCombate, ResultadoOleada
from modelos.expediciones import EstadoExpedicion, ResumenCierreExpedicion
from modelos.tipos import (
    AventureroActivo,
    AventureroEliminado,
    EstadoClan,
    ResultadoExpedicion,
)
from servicios.aventureros import (
    crear_aventureros_iniciales,
    formatear_id_aventurero,
)
from servicios.clan import NombreClanInvalidoError, crear_estado_inicial_clan
from servicios.expediciones import (
    EstadoExpedicionInvalidoError,
    ExpedicionYaAplicadaError,
    continuar_expedicion,
    iniciar_expedicion,
    resolver_siguiente_oleada,
)
from servicios.partidas import (
    PartidaExistenteError,
    cerrar_expedicion_y_guardar,
    crear_nueva_partida,
)
from servicios.persistencia import (
    ErrorPersistencia,
    PartidaIncompletaError,
    PartidaInvalidaError,
    cargar_partida,
)
from tests.test_expediciones import (
    crear_aventurero,
    crear_clan,
    crear_expedicion_finalizada,
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


class PruebasCierreExpedicion(unittest.TestCase):
    """Comprueba publicación, guardado, reintento e integración del cierre."""

    def test_cierra_y_recarga_cada_resultado_con_supervivientes(self) -> None:
        casos: tuple[tuple[ResultadoExpedicion, bool], ...] = (
            ("retirada", False),
            ("limite_de_rondas", False),
            ("mazmorra_completada", True),
        )

        for resultado_final, completa in casos:
            with self.subTest(resultado_final=resultado_final):
                with TemporaryDirectory() as temporal:
                    directorio = Path(temporal) / "partida"
                    clan: EstadoClan = crear_clan()
                    activos: list[AventureroActivo] = [crear_aventurero(1)]
                    eliminados: list[AventureroEliminado] = []
                    expedicion: EstadoExpedicion = crear_expedicion_finalizada(
                        clan,
                        activos,
                        ["AV-0001"],
                        resultado_final,
                        experiencia=100,
                        dinero=50,
                    )

                    resumen: ResumenCierreExpedicion = (
                        cerrar_expedicion_y_guardar(
                            expedicion,
                            clan,
                            activos,
                            eliminados,
                            Random(7),
                            directorio,
                        )
                    )

                    self.assertEqual(
                        expedicion["estado_flujo"],
                        "consecuencias_aplicadas",
                    )
                    self.assertEqual(clan["dinero"], 50)
                    self.assertEqual(clan["contrataciones_restantes"], 1)
                    self.assertEqual(len(clan["ofertas_reclutamiento"]), 2)
                    self.assertEqual(activos[0]["nivel"], 2)
                    self.assertEqual(activos[0]["experiencia"], 0)
                    self.assertEqual(clan["estado_partida"], "en_curso")
                    self.assertEqual(
                        clan["mazmorras_completadas"]["mazmorra_1"],
                        completa,
                    )
                    self.assertEqual(
                        resumen,
                        {
                            "dinero_entregado": 50,
                            "experiencia_por_superviviente": 100,
                            "supervivientes_ids": ["AV-0001"],
                            "muertos_ids": [],
                            "mazmorra_completada": completa,
                            "resultado": resultado_final,
                            "estado_partida": "en_curso",
                        },
                    )
                    self.assertEqual(
                        cargar_partida(directorio),
                        (clan, activos, eliminados),
                    )

    def test_derrota_total_renueva_mercado_y_guarda_derrota(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"
            clan: EstadoClan = crear_clan()
            activos: list[AventureroActivo] = [
                crear_aventurero(1),
                crear_aventurero(2),
            ]
            eliminados: list[AventureroEliminado] = []
            expedicion: EstadoExpedicion = crear_expedicion_finalizada(
                clan,
                activos,
                ["AV-0001", "AV-0002"],
                "derrota_total",
                muertos_ids=("AV-0001", "AV-0002"),
                experiencia=900,
                dinero=500,
            )

            resumen: ResumenCierreExpedicion = cerrar_expedicion_y_guardar(
                expedicion,
                clan,
                activos,
                eliminados,
                Random(11),
                directorio,
            )

            self.assertEqual(activos, [])
            self.assertEqual(
                [aventurero["id"] for aventurero in eliminados],
                ["AV-0001", "AV-0002"],
            )
            self.assertEqual(clan["dinero"], 0)
            self.assertEqual(clan["estado_partida"], "derrota")
            self.assertEqual(clan["contrataciones_restantes"], 1)
            self.assertEqual(len(clan["ofertas_reclutamiento"]), 2)
            self.assertEqual(resumen["dinero_entregado"], 0)
            self.assertEqual(resumen["experiencia_por_superviviente"], 0)
            self.assertEqual(resumen["resultado"], "derrota_total")
            self.assertEqual(resumen["estado_partida"], "derrota")
            self.assertEqual(
                cargar_partida(directorio),
                (clan, activos, eliminados),
            )

    def test_rechaza_segundo_cierre_sin_modificar_datos_ni_azar(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"
            clan: EstadoClan = crear_clan()
            activos: list[AventureroActivo] = [crear_aventurero(1)]
            eliminados: list[AventureroEliminado] = []
            expedicion: EstadoExpedicion = crear_expedicion_finalizada(
                clan,
                activos,
                ["AV-0001"],
                "retirada",
                dinero=20,
            )
            generador = Random(13)
            cerrar_expedicion_y_guardar(
                expedicion,
                clan,
                activos,
                eliminados,
                generador,
                directorio,
            )
            anterior = deepcopy((expedicion, clan, activos, eliminados))
            estado_azar = generador.getstate()

            with self.assertRaises(ExpedicionYaAplicadaError):
                cerrar_expedicion_y_guardar(
                    expedicion,
                    clan,
                    activos,
                    eliminados,
                    generador,
                    directorio,
                )

            self.assertEqual((expedicion, clan, activos, eliminados), anterior)
            self.assertEqual(generador.getstate(), estado_azar)

    def test_rechaza_id_o_plantilla_incompatible_antes_de_guardar(self) -> None:
        for alteracion in ("id", "plantilla"):
            with self.subTest(alteracion=alteracion):
                with TemporaryDirectory() as temporal:
                    directorio = Path(temporal) / "partida"
                    clan: EstadoClan = crear_clan()
                    activos: list[AventureroActivo] = [crear_aventurero(1)]
                    eliminados: list[AventureroEliminado] = []
                    expedicion: EstadoExpedicion = crear_expedicion_finalizada(
                        clan,
                        activos,
                        ["AV-0001"],
                        "retirada",
                        dinero=50,
                    )
                    if alteracion == "id":
                        activos.clear()
                    else:
                        activos[0]["plantilla_id"] = "PLANTILLA_SOLDADO"
                    anterior = deepcopy((expedicion, clan, activos, eliminados))
                    generador = Random(17)
                    estado_azar = generador.getstate()

                    with self.assertRaises(EstadoExpedicionInvalidoError):
                        cerrar_expedicion_y_guardar(
                            expedicion,
                            clan,
                            activos,
                            eliminados,
                            generador,
                            directorio,
                        )

                    self.assertEqual(
                        (expedicion, clan, activos, eliminados),
                        anterior,
                    )
                    self.assertEqual(generador.getstate(), estado_azar)
                    self.assertFalse(directorio.exists())

    def test_reintenta_guardado_sin_duplicar_recompensas_ni_mercado(
        self,
    ) -> None:
        with TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            clan: EstadoClan = crear_clan()
            activos: list[AventureroActivo] = [crear_aventurero(1)]
            eliminados: list[AventureroEliminado] = []
            expedicion: EstadoExpedicion = crear_expedicion_finalizada(
                clan,
                activos,
                ["AV-0001"],
                "retirada",
                experiencia=100,
                dinero=50,
            )
            clan_directo: EstadoClan = deepcopy(clan)
            activos_directos: list[AventureroActivo] = deepcopy(activos)
            eliminados_directos: list[AventureroEliminado] = []
            expedicion_directa: EstadoExpedicion = deepcopy(expedicion)
            generador_reintento = Random(23)
            generador_directo = Random(23)
            anterior = deepcopy((expedicion, clan, activos, eliminados))
            estado_azar = generador_reintento.getstate()

            with patch(
                "servicios.partidas.guardar_partida",
                side_effect=ErrorPersistencia("fallo controlado"),
            ):
                with self.assertRaises(ErrorPersistencia):
                    cerrar_expedicion_y_guardar(
                        expedicion,
                        clan,
                        activos,
                        eliminados,
                        generador_reintento,
                        raiz / "reintento",
                    )

            self.assertEqual((expedicion, clan, activos, eliminados), anterior)
            self.assertEqual(generador_reintento.getstate(), estado_azar)

            resumen_reintento: ResumenCierreExpedicion = (
                cerrar_expedicion_y_guardar(
                    expedicion,
                    clan,
                    activos,
                    eliminados,
                    generador_reintento,
                    raiz / "reintento",
                )
            )
            resumen_directo: ResumenCierreExpedicion = (
                cerrar_expedicion_y_guardar(
                    expedicion_directa,
                    clan_directo,
                    activos_directos,
                    eliminados_directos,
                    generador_directo,
                    raiz / "directo",
                )
            )

            self.assertEqual(resumen_reintento, resumen_directo)
            self.assertEqual(clan, clan_directo)
            self.assertEqual(activos, activos_directos)
            self.assertEqual(eliminados, eliminados_directos)
            self.assertEqual(
                generador_reintento.getstate(),
                generador_directo.getstate(),
            )
            self.assertEqual(clan["dinero"], 50)
            self.assertEqual(activos[0]["nivel"], 2)

    def test_integra_diez_oleadas_cierre_y_recarga(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"
            clan: EstadoClan = crear_estado_inicial_clan("Guardianes del Alba")
            activos: list[AventureroActivo] = crear_aventureros_iniciales(
                Random(29)
            )
            eliminados: list[AventureroEliminado] = []
            expedicion: EstadoExpedicion = iniciar_expedicion(
                clan,
                activos,
                ["AV-0001", "AV-0002", "AV-0003"],
                "MAZMORRA_LIMOS",
            )

            def victoria_controlada(
                aventureros: list[AventureroCombate],
                enemigos: list[EnemigoCombate],
                generador: Random,
            ) -> ResultadoOleada:
                del generador
                ids: list[str] = []
                for enemigo in enemigos:
                    enemigo["vida_actual"] = 0
                    enemigo["esta_vivo"] = False
                    ids.append(enemigo["id_instancia"])
                return {
                    "resultado": "victoria",
                    "rondas": 1,
                    "aventureros": aventureros,
                    "enemigos": enemigos,
                    "enemigos_derrotados": ids,
                    "experiencia_obtenida": sum(
                        enemigo["experiencia"] for enemigo in enemigos
                    ),
                    "dinero_obtenido": sum(
                        enemigo["dinero"] for enemigo in enemigos
                    ),
                }

            with patch(
                "servicios.expediciones.resolver_oleada",
                side_effect=victoria_controlada,
            ):
                for numero in range(1, 11):
                    resolver_siguiente_oleada(expedicion, Random(numero))
                    if numero < 10:
                        continuar_expedicion(expedicion)

            resumen: ResumenCierreExpedicion = cerrar_expedicion_y_guardar(
                expedicion,
                clan,
                activos,
                eliminados,
                Random(31),
                directorio,
            )

            self.assertEqual(resumen["resultado"], "mazmorra_completada")
            self.assertEqual(resumen["dinero_entregado"], 516)
            self.assertEqual(resumen["experiencia_por_superviviente"], 296)
            self.assertEqual(clan["dinero"], 516)
            self.assertTrue(clan["mazmorras_completadas"]["mazmorra_1"])
            for aventurero in activos:
                self.assertEqual(aventurero["nivel"], 2)
                self.assertEqual(aventurero["experiencia"], 196)
            self.assertEqual(
                cargar_partida(directorio),
                (clan, activos, eliminados),
            )
            self.assertEqual(
                {ruta.name for ruta in directorio.glob("*.json")},
                {
                    "estado_clan.json",
                    "datos_activos.json",
                    "datos_eliminados.json",
                },
            )

if __name__ == "__main__":
    unittest.main()
