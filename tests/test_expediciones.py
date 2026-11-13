"""Pruebas del flujo temporal y las consecuencias de expediciones."""

import unittest
from copy import deepcopy
from random import Random
from unittest.mock import patch

from catalogos.mazmorras import CATALOGO_MAZMORRAS, MAZMORRA_LIMOS
from catalogos.plantillas import CATALOGO_PLANTILLAS
from modelos.combate import (
    AventureroCombate,
    DefinicionMazmorra,
    EnemigoCombate,
    ResultadoCombate,
    ResultadoOleada,
)
from modelos.expediciones import (
    EstadoExpedicion,
    ResultadoConsecuenciasExpedicion,
)
from modelos.tipos import (
    AventureroActivo,
    AventureroEliminado,
    EstadoAventurero,
    EstadoClan,
    EstadoPartida,
    NivelClan,
    ResultadoExpedicion,
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
    ExpedicionYaAplicadaError,
    MazmorraNoDisponibleError,
    MazmorraNoEncontradaError,
    TransicionExpedicionInvalidaError,
    aplicar_consecuencias_expedicion,
    calcular_dinero_oleada,
    continuar_expedicion,
    evaluar_derrota_definitiva,
    iniciar_expedicion,
    resolver_siguiente_oleada,
    retirar_expedicion,
)


PLANTILLAS_PRUEBA: tuple[str, ...] = tuple(CATALOGO_PLANTILLAS)


def crear_aventurero(
    numero: int,
    *,
    estado: EstadoAventurero = "vivo",
    plantilla_id: str | None = None,
    nivel: int = 1,
    experiencia: int = 0,
) -> AventureroActivo:
    """Construye un integrante válido con un identificador correlativo."""

    return {
        "id": f"AV-{numero:04d}",
        "nombre": f"Aventurero {numero}",
        "plantilla_id": plantilla_id
        if plantilla_id is not None
        else PLANTILLAS_PRUEBA[(numero - 1) % len(PLANTILLAS_PRUEBA)],
        "nivel": nivel,
        "experiencia": experiencia,
        "estado": estado,
    }


def crear_clan(nivel: NivelClan = 1) -> EstadoClan:
    """Construye un estado en curso con el nivel indicado para las pruebas."""

    estado: EstadoClan = crear_estado_inicial_clan("Guardianes del Alba")
    estado["nivel"] = nivel
    return estado


def crear_expedicion_lista() -> EstadoExpedicion:
    """Inicia una expedición mínima preparada para resolver una oleada."""

    return iniciar_expedicion(
        crear_clan(),
        [crear_aventurero(1)],
        ["AV-0001"],
        "MAZMORRA_LIMOS",
    )


def crear_resultado_oleada(
    expedicion: EstadoExpedicion,
    resultado: ResultadoCombate,
    *,
    experiencia: int = 20,
    dinero: int = 10,
) -> ResultadoOleada:
    """Construye un resultado completo para controlar el motor en pruebas."""

    return {
        "resultado": resultado,
        "rondas": 2,
        "aventureros": expedicion["aventureros"],
        "enemigos": [],
        "enemigos_derrotados": ["LIMOS_LIMO-01"],
        "experiencia_obtenida": experiencia,
        "dinero_obtenido": dinero,
    }


def crear_expedicion_finalizada(
    clan: EstadoClan,
    activos: list[AventureroActivo],
    ids: list[str],
    resultado: ResultadoExpedicion,
    *,
    muertos_ids: tuple[str, ...] = (),
    experiencia: int = 0,
    dinero: int = 0,
) -> EstadoExpedicion:
    """Construye un final controlado partiendo de una selección real."""

    expedicion: EstadoExpedicion = iniciar_expedicion(
        clan,
        activos,
        ids,
        "MAZMORRA_LIMOS",
    )
    for aventurero in expedicion["aventureros"]:
        if aventurero["id"] in muertos_ids:
            aventurero["vida_actual"] = 0
            aventurero["esta_vivo"] = False

    expedicion["experiencia_acumulada"] = experiencia
    expedicion["dinero_acumulado"] = dinero
    expedicion["estado_flujo"] = "finalizada"
    expedicion["resultado_final"] = resultado
    return expedicion


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


class PruebasRecompensas(unittest.TestCase):
    """Comprueba la bonificación monetaria sin afectar la experiencia."""

    def test_calcula_bonificacion_y_redondea_hacia_abajo(self) -> None:
        self.assertEqual(calcular_dinero_oleada(100, 1), 100)
        self.assertEqual(calcular_dinero_oleada(101, 2), 111)
        self.assertEqual(calcular_dinero_oleada(3, 10), 5)

    def test_rechaza_dinero_negativo_y_oleadas_fuera_del_dominio(self) -> None:
        casos: tuple[tuple[int, int], ...] = (
            (-1, 1),
            (10, 0),
            (10, 11),
        )

        for dinero, oleada in casos:
            with self.subTest(dinero=dinero, oleada=oleada):
                with self.assertRaises(ValueError):
                    calcular_dinero_oleada(dinero, oleada)


class PruebasAvanceExpedicion(unittest.TestCase):
    """Comprueba resolución, decisiones y finales del estado temporal."""

    def test_victoria_intermedia_acumula_y_espera_decision(self) -> None:
        expedicion: EstadoExpedicion = crear_expedicion_lista()
        resultado: ResultadoOleada = crear_resultado_oleada(
            expedicion,
            "victoria",
            experiencia=27,
            dinero=101,
        )

        with patch(
            "servicios.expediciones.resolver_oleada",
            return_value=resultado,
        ):
            devuelto: ResultadoOleada = resolver_siguiente_oleada(
                expedicion,
                Random(1),
            )

        self.assertIs(devuelto, resultado)
        self.assertEqual(expedicion["experiencia_acumulada"], 27)
        self.assertEqual(expedicion["dinero_acumulado"], 101)
        self.assertEqual(expedicion["oleadas_superadas"], 1)
        self.assertEqual(expedicion["proxima_oleada"], 2)
        self.assertEqual(expedicion["estado_flujo"], "esperando_decision")
        self.assertIsNone(expedicion["resultado_final"])

    def test_ultima_oleada_es_una_copia_historica_profunda(self) -> None:
        expedicion: EstadoExpedicion = crear_expedicion_lista()
        vida_al_finalizar: int = expedicion["aventureros"][0]["vida_actual"]
        resultado: ResultadoOleada = crear_resultado_oleada(
            expedicion,
            "victoria",
        )

        with patch(
            "servicios.expediciones.resolver_oleada",
            return_value=resultado,
        ):
            resolver_siguiente_oleada(expedicion, Random(2))

        ultima: ResultadoOleada | None = expedicion["ultima_oleada"]
        self.assertIsNotNone(ultima)
        expedicion["aventureros"][0]["vida_actual"] -= 1
        if ultima is not None:
            self.assertEqual(
                ultima["aventureros"][0]["vida_actual"],
                vida_al_finalizar,
            )
            self.assertIsNot(
                ultima["aventureros"][0],
                expedicion["aventureros"][0],
            )

    def test_continuar_y_retirarse_respetan_el_estado_de_espera(self) -> None:
        expedicion: EstadoExpedicion = crear_expedicion_lista()
        resultado: ResultadoOleada = crear_resultado_oleada(
            expedicion,
            "victoria",
        )
        with patch(
            "servicios.expediciones.resolver_oleada",
            return_value=resultado,
        ):
            resolver_siguiente_oleada(expedicion, Random(3))

        continuar_expedicion(expedicion)
        self.assertEqual(expedicion["estado_flujo"], "lista_para_oleada")

        expedicion["estado_flujo"] = "esperando_decision"
        retirar_expedicion(expedicion)
        self.assertEqual(expedicion["estado_flujo"], "finalizada")
        self.assertEqual(expedicion["resultado_final"], "retirada")

    def test_transiciones_invalidas_no_modifican_el_estado(self) -> None:
        lista: EstadoExpedicion = crear_expedicion_lista()
        anterior_lista: EstadoExpedicion = deepcopy(lista)

        with self.assertRaises(TransicionExpedicionInvalidaError):
            continuar_expedicion(lista)
        self.assertEqual(lista, anterior_lista)

        with self.assertRaises(TransicionExpedicionInvalidaError):
            retirar_expedicion(lista)
        self.assertEqual(lista, anterior_lista)

        esperando: EstadoExpedicion = deepcopy(lista)
        esperando["estado_flujo"] = "esperando_decision"
        anterior_esperando: EstadoExpedicion = deepcopy(esperando)
        with self.assertRaises(TransicionExpedicionInvalidaError):
            resolver_siguiente_oleada(esperando, Random(4))
        self.assertEqual(esperando, anterior_esperando)

    def test_derrota_finaliza_con_recompensas_solamente_provisionales(
        self,
    ) -> None:
        expedicion: EstadoExpedicion = crear_expedicion_lista()
        resultado: ResultadoOleada = crear_resultado_oleada(
            expedicion,
            "derrota",
            experiencia=13,
            dinero=7,
        )
        resultado["aventureros"][0]["vida_actual"] = 0
        resultado["aventureros"][0]["esta_vivo"] = False

        with patch(
            "servicios.expediciones.resolver_oleada",
            return_value=resultado,
        ):
            resolver_siguiente_oleada(expedicion, Random(5))

        self.assertEqual(expedicion["estado_flujo"], "finalizada")
        self.assertEqual(expedicion["resultado_final"], "derrota_total")
        self.assertEqual(expedicion["experiencia_acumulada"], 13)
        self.assertEqual(expedicion["dinero_acumulado"], 7)
        self.assertEqual(expedicion["oleadas_superadas"], 0)
        self.assertEqual(expedicion["proxima_oleada"], 1)

    def test_limite_finaliza_y_conserva_recompensas_parciales(self) -> None:
        expedicion: EstadoExpedicion = crear_expedicion_lista()
        expedicion["proxima_oleada"] = 2
        expedicion["oleadas_superadas"] = 1
        resultado: ResultadoOleada = crear_resultado_oleada(
            expedicion,
            "limite_de_rondas",
            experiencia=19,
            dinero=9,
        )

        with patch(
            "servicios.expediciones.resolver_oleada",
            return_value=resultado,
        ):
            resolver_siguiente_oleada(expedicion, Random(6))

        self.assertEqual(expedicion["estado_flujo"], "finalizada")
        self.assertEqual(expedicion["resultado_final"], "limite_de_rondas")
        self.assertEqual(expedicion["experiencia_acumulada"], 19)
        self.assertEqual(expedicion["dinero_acumulado"], 9)
        self.assertEqual(expedicion["oleadas_superadas"], 1)
        self.assertEqual(expedicion["proxima_oleada"], 2)

    def test_victoria_en_decima_oleada_completa_y_agrega_cien(self) -> None:
        expedicion: EstadoExpedicion = crear_expedicion_lista()
        expedicion["proxima_oleada"] = 10
        expedicion["oleadas_superadas"] = 9
        resultado: ResultadoOleada = crear_resultado_oleada(
            expedicion,
            "victoria",
            experiencia=80,
            dinero=30,
        )

        with patch(
            "servicios.expediciones.resolver_oleada",
            return_value=resultado,
        ):
            resolver_siguiente_oleada(expedicion, Random(7))

        self.assertEqual(expedicion["proxima_oleada"], 11)
        self.assertEqual(expedicion["oleadas_superadas"], 10)
        self.assertEqual(expedicion["dinero_acumulado"], 157)
        self.assertEqual(expedicion["experiencia_acumulada"], 80)
        self.assertEqual(expedicion["estado_flujo"], "finalizada")
        self.assertEqual(
            expedicion["resultado_final"],
            "mazmorra_completada",
        )

    def test_derrota_o_limite_en_decima_no_agregan_cien(self) -> None:
        for desenlace in ("derrota", "limite_de_rondas"):
            with self.subTest(desenlace=desenlace):
                expedicion: EstadoExpedicion = crear_expedicion_lista()
                expedicion["proxima_oleada"] = 10
                expedicion["oleadas_superadas"] = 9
                resultado: ResultadoOleada = crear_resultado_oleada(
                    expedicion,
                    desenlace,
                    experiencia=0,
                    dinero=30,
                )

                with patch(
                    "servicios.expediciones.resolver_oleada",
                    return_value=resultado,
                ):
                    resolver_siguiente_oleada(expedicion, Random(8))

                self.assertEqual(expedicion["dinero_acumulado"], 57)
                self.assertNotEqual(
                    expedicion["resultado_final"],
                    "mazmorra_completada",
                )

    def test_recorre_diez_definiciones_reales_y_acumula_516(self) -> None:
        expedicion: EstadoExpedicion = crear_expedicion_lista()
        cantidades_enemigos: list[int] = []

        def victoria_controlada(
            aventureros: list[AventureroCombate],
            enemigos: list[EnemigoCombate],
            generador: Random,
        ) -> ResultadoOleada:
            del generador
            cantidades_enemigos.append(len(enemigos))
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
                self.assertEqual(expedicion["proxima_oleada"], numero)
                resolver_siguiente_oleada(expedicion, Random(numero))
                if numero < 10:
                    continuar_expedicion(expedicion)

        self.assertEqual(
            cantidades_enemigos,
            [3, 6, 5, 8, 10, 6, 5, 5, 5, 1],
        )
        self.assertEqual(expedicion["oleadas_superadas"], 10)
        self.assertEqual(expedicion["dinero_acumulado"], 516)
        self.assertEqual(
            expedicion["resultado_final"],
            "mazmorra_completada",
        )


class PruebasConsecuenciasExpedicion(unittest.TestCase):
    """Comprueba la publicación en memoria del desenlace de una incursión."""

    def test_reparte_pozos_solo_entre_supervivientes_y_recupera_muertos(
        self,
    ) -> None:
        clan: EstadoClan = crear_clan(2)
        clan["dinero"] = 10
        activos: list[AventureroActivo] = [
            crear_aventurero(1),
            crear_aventurero(2),
            crear_aventurero(3),
            crear_aventurero(4),
        ]
        no_participante_anterior: AventureroActivo = deepcopy(activos[3])
        eliminados: list[AventureroEliminado] = []
        expedicion: EstadoExpedicion = crear_expedicion_finalizada(
            clan,
            activos,
            ["AV-0001", "AV-0002", "AV-0003"],
            "retirada",
            muertos_ids=("AV-0003",),
            experiencia=701,
            dinero=120,
        )

        resumen: ResultadoConsecuenciasExpedicion = (
            aplicar_consecuencias_expedicion(
                expedicion,
                clan,
                activos,
                eliminados,
            )
        )

        self.assertEqual(clan["dinero"], 130)
        self.assertEqual(activos[0]["nivel"], 3)
        self.assertEqual(activos[0]["experiencia"], 50)
        self.assertEqual(activos[1]["nivel"], 3)
        self.assertEqual(activos[1]["experiencia"], 50)
        self.assertEqual(activos[2]["estado"], "muerto")
        self.assertEqual(activos[2]["nivel"], 1)
        self.assertEqual(activos[2]["experiencia"], 0)
        self.assertEqual(activos[3], no_participante_anterior)
        self.assertNotIn("vida_actual", activos[0])
        self.assertEqual(eliminados, [])
        self.assertFalse(clan["mazmorras_completadas"]["mazmorra_1"])
        self.assertEqual(expedicion["estado_flujo"], "consecuencias_aplicadas")
        self.assertEqual(
            resumen,
            {
                "dinero_entregado": 120,
                "experiencia_por_superviviente": 350,
                "supervivientes_ids": ["AV-0001", "AV-0002"],
                "muertos_ids": ["AV-0003"],
                "mazmorra_completada": False,
            },
        )

        estado_publicado = deepcopy((clan, activos, eliminados, expedicion))
        with self.assertRaises(ExpedicionYaAplicadaError):
            aplicar_consecuencias_expedicion(
                expedicion,
                clan,
                activos,
                eliminados,
            )
        self.assertEqual(
            (clan, activos, eliminados, expedicion),
            estado_publicado,
        )

    def test_entrega_nuevamente_el_bono_de_una_mazmorra_ya_completada(
        self,
    ) -> None:
        clan: EstadoClan = crear_clan()
        clan["dinero"] = 10
        clan["mazmorras_completadas"]["mazmorra_1"] = True
        activos: list[AventureroActivo] = [crear_aventurero(1)]
        expedicion: EstadoExpedicion = crear_expedicion_finalizada(
            clan,
            activos,
            ["AV-0001"],
            "mazmorra_completada",
            dinero=100,
        )

        resumen: ResultadoConsecuenciasExpedicion = (
            aplicar_consecuencias_expedicion(expedicion, clan, activos, [])
        )

        self.assertEqual(clan["dinero"], 110)
        self.assertTrue(clan["mazmorras_completadas"]["mazmorra_1"])
        self.assertTrue(resumen["mazmorra_completada"])
        self.assertEqual(clan["nivel"], 1)

    def test_derrota_total_pierde_pozos_y_registra_caidos_en_orden(
        self,
    ) -> None:
        clan: EstadoClan = crear_clan()
        clan["dinero"] = 25
        activos: list[AventureroActivo] = [
            crear_aventurero(1),
            crear_aventurero(2),
            crear_aventurero(3),
        ]
        no_participante_anterior: AventureroActivo = deepcopy(activos[2])
        eliminados: list[AventureroEliminado] = []
        expedicion: EstadoExpedicion = crear_expedicion_finalizada(
            clan,
            activos,
            ["AV-0002", "AV-0001"],
            "derrota_total",
            muertos_ids=("AV-0001", "AV-0002"),
            experiencia=900,
            dinero=500,
        )

        resumen: ResultadoConsecuenciasExpedicion = (
            aplicar_consecuencias_expedicion(
                expedicion,
                clan,
                activos,
                eliminados,
            )
        )

        self.assertEqual(clan["dinero"], 25)
        self.assertEqual(activos, [no_participante_anterior])
        self.assertEqual(
            [aventurero["id"] for aventurero in eliminados],
            ["AV-0002", "AV-0001"],
        )
        for caido in eliminados:
            self.assertEqual(caido["estado"], "muerto")
            self.assertEqual(caido["motivo_baja"], "caido_no_recuperado")
            self.assertEqual(caido["nivel"], 1)
            self.assertEqual(caido["experiencia"], 0)
        self.assertEqual(
            resumen,
            {
                "dinero_entregado": 0,
                "experiencia_por_superviviente": 0,
                "supervivientes_ids": [],
                "muertos_ids": ["AV-0002", "AV-0001"],
                "mazmorra_completada": False,
            },
        )

    def test_rechaza_estados_no_finalizados_y_prioriza_la_reaplicacion(
        self,
    ) -> None:
        clan: EstadoClan = crear_clan()
        activos: list[AventureroActivo] = [crear_aventurero(1)]
        expedicion: EstadoExpedicion = iniciar_expedicion(
            clan,
            activos,
            ["AV-0001"],
            "MAZMORRA_LIMOS",
        )
        estado_anterior = deepcopy((clan, activos, expedicion))

        with self.assertRaises(EstadoExpedicionInvalidoError):
            aplicar_consecuencias_expedicion(expedicion, clan, activos, [])
        self.assertEqual((clan, activos, expedicion), estado_anterior)

        expedicion["estado_flujo"] = "consecuencias_aplicadas"
        expedicion["resultado_final"] = None
        estado_aplicado = deepcopy((clan, activos, expedicion))
        with self.assertRaises(ExpedicionYaAplicadaError):
            aplicar_consecuencias_expedicion(expedicion, clan, activos, [])
        self.assertEqual((clan, activos, expedicion), estado_aplicado)

    def test_valida_todos_los_ids_y_plantillas_antes_de_mutar(self) -> None:
        for alteracion in ("ausente", "plantilla"):
            with self.subTest(alteracion=alteracion):
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
                    "retirada",
                    experiencia=300,
                    dinero=90,
                )
                if alteracion == "ausente":
                    activos.pop()
                else:
                    activos[1]["plantilla_id"] = "PLANTILLA_SOLDADO"
                anterior = deepcopy((clan, activos, eliminados, expedicion))

                with self.assertRaises(EstadoExpedicionInvalidoError):
                    aplicar_consecuencias_expedicion(
                        expedicion,
                        clan,
                        activos,
                        eliminados,
                    )

                self.assertEqual(
                    (clan, activos, eliminados, expedicion),
                    anterior,
                )


class PruebasDerrotaDefinitiva(unittest.TestCase):
    """Comprueba si el clan conserva alguna alternativa jugable."""

    def test_continua_si_queda_un_aventurero_vivo(self) -> None:
        clan: EstadoClan = crear_clan()
        activos: list[AventureroActivo] = [crear_aventurero(1)]

        evaluar_derrota_definitiva(clan, activos)

        self.assertEqual(clan["estado_partida"], "en_curso")

    def test_continua_si_alcanza_exactamente_para_resucitar(self) -> None:
        clan: EstadoClan = crear_clan()
        clan["dinero"] = 7
        activos: list[AventureroActivo] = [
            crear_aventurero(
                1,
                estado="muerto",
                plantilla_id="PLANTILLA_SOLDADO",
            )
        ]

        evaluar_derrota_definitiva(clan, activos)

        self.assertEqual(clan["estado_partida"], "en_curso")

    def test_continua_por_oferta_pagable_aunque_el_cupo_este_lleno(
        self,
    ) -> None:
        clan: EstadoClan = crear_clan()
        clan["dinero"] = 10
        clan["contrataciones_restantes"] = 1
        clan["ofertas_reclutamiento"] = [
            {
                "id_oferta": "OF-01",
                "nombre": "Liora",
                "plantilla_id": "PLANTILLA_SOLDADO",
                "nivel": 1,
                "coste": 10,
            }
        ]
        activos: list[AventureroActivo] = [
            crear_aventurero(
                numero,
                estado="muerto",
                plantilla_id="PLANTILLA_SOLDADO",
            )
            for numero in range(1, 6)
        ]

        evaluar_derrota_definitiva(clan, activos)

        self.assertEqual(clan["estado_partida"], "en_curso")

    def test_declara_derrota_sin_alternativas_pagables(self) -> None:
        casos: list[tuple[EstadoClan, list[AventureroActivo]]] = []

        sin_integrantes: EstadoClan = crear_clan()
        casos.append((sin_integrantes, []))

        resurreccion_cara: EstadoClan = crear_clan()
        resurreccion_cara["dinero"] = 6
        casos.append(
            (
                resurreccion_cara,
                [
                    crear_aventurero(
                        1,
                        estado="muerto",
                        plantilla_id="PLANTILLA_SOLDADO",
                    )
                ],
            )
        )

        oferta_cara: EstadoClan = crear_clan()
        oferta_cara["dinero"] = 9
        oferta_cara["contrataciones_restantes"] = 1
        oferta_cara["ofertas_reclutamiento"] = [
            {
                "id_oferta": "OF-01",
                "nombre": "Liora",
                "plantilla_id": "PLANTILLA_SOLDADO",
                "nivel": 1,
                "coste": 10,
            }
        ]
        casos.append((oferta_cara, []))

        mercado_agotado: EstadoClan = deepcopy(oferta_cara)
        mercado_agotado["dinero"] = 10
        mercado_agotado["contrataciones_restantes"] = 0
        casos.append((mercado_agotado, []))

        for numero, (clan, activos) in enumerate(casos, start=1):
            with self.subTest(caso=numero):
                evaluar_derrota_definitiva(clan, activos)
                self.assertEqual(clan["estado_partida"], "derrota")


if __name__ == "__main__":
    unittest.main()
