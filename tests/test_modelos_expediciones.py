"""Pruebas de los contratos tipados del flujo de expediciones."""

import unittest
from typing import get_args

from modelos.combate import AventureroCombate, ResultadoOleada
from modelos.expediciones import (
    EstadoExpedicion,
    EstadoFlujoExpedicion,
    ResultadoConsecuenciasExpedicion,
    ResumenCierreExpedicion,
)


def crear_aventurero_combate() -> AventureroCombate:
    """Construye un estado temporal mínimo para probar los contratos."""

    return {
        "id": "AV-0001",
        "nombre": "Aldren",
        "plantilla_id": "PLANTILLA_SOLDADO",
        "vida_maxima": 100,
        "vida_actual": 80,
        "dano": 20,
        "defensa": 10,
        "velocidad": 5,
        "probabilidad_critica": 5,
        "esta_vivo": True,
        "tipo_ataque": "cuerpo_a_cuerpo",
        "estrategia_objetivo": "aleatorio",
    }


def crear_resultado_oleada(
    aventurero: AventureroCombate,
) -> ResultadoOleada:
    """Construye un resultado compatible con el motor de combate."""

    return {
        "resultado": "victoria",
        "rondas": 2,
        "aventureros": [aventurero],
        "enemigos": [],
        "enemigos_derrotados": ["LIMOS_LIMO-01"],
        "experiencia_obtenida": 10,
        "dinero_obtenido": 1,
    }


class PruebasModelosExpedicion(unittest.TestCase):
    """Comprueba nombres, estados y campos compartidos entre los servicios."""

    def test_flujo_contiene_los_cuatro_estados_acordados(self) -> None:
        self.assertEqual(
            get_args(EstadoFlujoExpedicion),
            (
                "lista_para_oleada",
                "esperando_decision",
                "finalizada",
                "consecuencias_aplicadas",
            ),
        )

    def test_construye_el_estado_temporal_completo(self) -> None:
        aventurero: AventureroCombate = crear_aventurero_combate()
        ultima_oleada: ResultadoOleada = crear_resultado_oleada(aventurero)
        expedicion: EstadoExpedicion = {
            "mazmorra_id": "MAZMORRA_LIMOS",
            "dificultad": 1,
            "proxima_oleada": 2,
            "oleadas_superadas": 1,
            "aventureros": [aventurero],
            "experiencia_acumulada": 10,
            "dinero_acumulado": 1,
            "estado_flujo": "esperando_decision",
            "resultado_final": None,
            "ultima_oleada": ultima_oleada,
        }

        self.assertEqual(expedicion["mazmorra_id"], "MAZMORRA_LIMOS")
        self.assertEqual(expedicion["dificultad"], 1)
        self.assertIs(expedicion["ultima_oleada"], ultima_oleada)

    def test_construye_resultados_de_consecuencias_y_cierre(self) -> None:
        consecuencias: ResultadoConsecuenciasExpedicion = {
            "dinero_entregado": 120,
            "experiencia_por_superviviente": 35,
            "supervivientes_ids": ["AV-0001"],
            "muertos_ids": ["AV-0002"],
            "mazmorra_completada": False,
        }
        cierre: ResumenCierreExpedicion = {
            **consecuencias,
            "resultado": "retirada",
            "estado_partida": "en_curso",
        }

        self.assertEqual(cierre["dinero_entregado"], 120)
        self.assertEqual(cierre["resultado"], "retirada")
        self.assertEqual(cierre["estado_partida"], "en_curso")


if __name__ == "__main__":
    unittest.main()
