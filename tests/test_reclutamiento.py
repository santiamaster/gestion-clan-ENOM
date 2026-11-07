"""Pruebas del mercado y el reclutamiento de aventureros."""

import unittest
from collections.abc import Sequence
from copy import deepcopy
from random import Random
from typing import TypeVar

from catalogos.nombres import NOMBRES_FEMENINOS, NOMBRES_MASCULINOS
from catalogos.plantillas import CATALOGO_PLANTILLAS
from modelos.tipos import (
    AventureroActivo,
    EstadoAventurero,
    EstadoClan,
    OfertaReclutamiento,
)
from servicios.aventureros import crear_aventureros_iniciales
from servicios.clan import crear_estado_inicial_clan
from servicios.reclutamiento import (
    CupoClanCompletoError,
    DineroInsuficienteError,
    MercadoAgotadoError,
    OfertaNoEncontradaError,
    calcular_cantidad_ofertas,
    calcular_limite_contrataciones,
    contratar_aventurero,
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


def crear_mercado_para_contratar() -> tuple[EstadoClan, list[AventureroActivo]]:
    """Crea un clan de nivel dos con dos contrataciones disponibles."""

    estado: EstadoClan = crear_estado_inicial_clan("Clan Alba")
    estado["nivel"] = 2
    estado["dinero"] = 100
    estado["contrataciones_restantes"] = 2
    estado["ofertas_reclutamiento"] = [
        {
            "id_oferta": "OF-01",
            "nombre": "Aldren",
            "plantilla_id": "PLANTILLA_SOLDADO",
            "nivel": 2,
            "coste": 20,
        },
        {
            "id_oferta": "OF-02",
            "nombre": "Aelira",
            "plantilla_id": "PLANTILLA_ARQUERO",
            "nivel": 1,
            "coste": 10,
        },
    ]
    activos: list[AventureroActivo] = crear_aventureros_iniciales(Random(3))
    return estado, activos


def crear_clan_con_cupo_completo(
    estado_aventurero: EstadoAventurero,
) -> tuple[EstadoClan, list[AventureroActivo]]:
    """Crea diez aventureros vivos o muertos en un clan de nivel dos."""

    estado, _ = crear_mercado_para_contratar()
    estado["siguiente_id_aventurero"] = 11
    activos: list[AventureroActivo] = []
    for numero in range(1, 11):
        aventurero: AventureroActivo = {
            "id": f"AV-{numero:04d}",
            "nombre": f"Integrante {numero}",
            "plantilla_id": "PLANTILLA_SOLDADO",
            "nivel": 1,
            "experiencia": 0,
            "estado": estado_aventurero,
        }
        activos.append(aventurero)
    return estado, activos


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


class PruebasContratacionCorrecta(unittest.TestCase):
    """Comprueba todos los cambios producidos por una contratación válida."""

    def test_contrata_y_actualiza_el_estado_completo(self) -> None:
        estado, activos = crear_mercado_para_contratar()

        contratado = contratar_aventurero(estado, activos, "OF-01")

        esperado: AventureroActivo = {
            "id": "AV-0004",
            "nombre": "Aldren",
            "plantilla_id": "PLANTILLA_SOLDADO",
            "nivel": 2,
            "experiencia": 0,
            "estado": "vivo",
        }
        self.assertEqual(contratado, esperado)
        self.assertEqual(activos[-1], esperado)
        self.assertEqual(len(activos), 4)
        self.assertEqual(estado["dinero"], 80)
        self.assertEqual(estado["siguiente_id_aventurero"], 5)
        self.assertEqual(estado["contrataciones_restantes"], 1)
        self.assertEqual(
            [
                oferta["id_oferta"]
                for oferta in estado["ofertas_reclutamiento"]
            ],
            ["OF-02"],
        )

    def test_permite_una_segunda_contratacion_disponible(self) -> None:
        estado, activos = crear_mercado_para_contratar()

        primero = contratar_aventurero(estado, activos, "OF-01")
        segundo = contratar_aventurero(estado, activos, "OF-02")

        self.assertEqual(primero["id"], "AV-0004")
        self.assertEqual(segundo["id"], "AV-0005")
        self.assertEqual(len(activos), 5)
        self.assertEqual(estado["dinero"], 70)
        self.assertEqual(estado["siguiente_id_aventurero"], 6)
        self.assertEqual(estado["contrataciones_restantes"], 0)
        self.assertEqual(estado["ofertas_reclutamiento"], [])


class PruebasErroresContratacion(unittest.TestCase):
    """Comprueba los errores de dominio y la ausencia de cambios parciales."""

    def comprobar_error_sin_mutaciones(
        self,
        tipo_error: type[Exception],
        estado: EstadoClan,
        activos: list[AventureroActivo],
        id_oferta: str = "OF-01",
    ) -> None:
        """Verifica que un error conserve exactamente ambas estructuras."""

        estado_anterior: EstadoClan = deepcopy(estado)
        activos_anteriores: list[AventureroActivo] = deepcopy(activos)

        with self.assertRaises(tipo_error):
            contratar_aventurero(estado, activos, id_oferta)

        self.assertEqual(estado, estado_anterior)
        self.assertEqual(activos, activos_anteriores)

    def test_rechaza_una_oferta_inexistente_sin_consumir_recursos(self) -> None:
        estado, activos = crear_mercado_para_contratar()
        estado["contrataciones_restantes"] = 0

        self.comprobar_error_sin_mutaciones(
            OfertaNoEncontradaError,
            estado,
            activos,
            "OF-INEXISTENTE",
        )

    def test_rechaza_un_mercado_agotado_sin_consumir_recursos(self) -> None:
        estado, activos = crear_mercado_para_contratar()
        estado["contrataciones_restantes"] = 0

        self.comprobar_error_sin_mutaciones(
            MercadoAgotadoError,
            estado,
            activos,
        )

    def test_rechaza_dinero_insuficiente_sin_consumir_recursos(self) -> None:
        estado, activos = crear_mercado_para_contratar()
        estado["dinero"] = 19

        self.comprobar_error_sin_mutaciones(
            DineroInsuficienteError,
            estado,
            activos,
        )

    def test_rechaza_cupo_lleno_con_vivos_o_muertos_sin_mutaciones(self) -> None:
        for estado_aventurero in ("vivo", "muerto"):
            with self.subTest(estado_aventurero=estado_aventurero):
                estado, activos = crear_clan_con_cupo_completo(
                    estado_aventurero
                )

                self.comprobar_error_sin_mutaciones(
                    CupoClanCompletoError,
                    estado,
                    activos,
                )

    def test_permite_contratar_la_misma_oferta_tras_liberar_cupo(self) -> None:
        estado, activos = crear_clan_con_cupo_completo("muerto")
        self.comprobar_error_sin_mutaciones(
            CupoClanCompletoError,
            estado,
            activos,
        )

        activos.pop()
        contratado = contratar_aventurero(estado, activos, "OF-01")

        self.assertEqual(contratado["id"], "AV-0011")
        self.assertEqual(len(activos), 10)
        self.assertEqual(estado["dinero"], 80)
        self.assertEqual(estado["contrataciones_restantes"], 1)
        self.assertEqual(
            [
                oferta["id_oferta"]
                for oferta in estado["ofertas_reclutamiento"]
            ],
            ["OF-02"],
        )


if __name__ == "__main__":
    unittest.main()
