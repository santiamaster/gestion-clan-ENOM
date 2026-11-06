"""Pruebas de las reglas matemáticas compartidas del juego."""

import unittest

from configuracion import (
    BONO_ESTADISTICAS_NIVEL_MAXIMO,
    MULTIPLICADOR_ATAQUE_EFECTIVO,
    MULTIPLICADOR_ATAQUE_INEFECTIVO,
    MULTIPLICADOR_ATAQUE_NEUTRAL,
)
from modelos.tipos import EfectividadAtaque
from catalogos.plantillas import SOLDADO
from servicios.calculos import (
    aplicar_experiencia,
    calcular_coste_contratacion,
    calcular_cupo_clan,
    calcular_dano_final,
    calcular_estadisticas,
    calcular_experiencia_necesaria,
    calcular_probabilidad_critico,
)


class PruebasConfiguracion(unittest.TestCase):
    """Comprueba los valores constantes acordados para los cálculos."""

    def test_multiplicadores_de_efectividad(self) -> None:
        self.assertEqual(MULTIPLICADOR_ATAQUE_EFECTIVO, 1.50)
        self.assertEqual(MULTIPLICADOR_ATAQUE_NEUTRAL, 1.00)
        self.assertEqual(MULTIPLICADOR_ATAQUE_INEFECTIVO, 0.50)

    def test_bono_de_nivel_maximo(self) -> None:
        self.assertEqual(BONO_ESTADISTICAS_NIVEL_MAXIMO, 1.20)

    def test_tipo_efectividad_acepta_valores_acordados(self) -> None:
        valores: tuple[EfectividadAtaque, ...] = (
            "efectivo",
            "neutral",
            "inefectivo",
        )
        self.assertEqual(len(valores), 3)


class PruebasEstadisticas(unittest.TestCase):
    """Comprueba el crecimiento y el bono de nivel máximo."""

    def test_calcula_estadisticas_desde_nivel_uno(self) -> None:
        resultado = calcular_estadisticas(SOLDADO, 1)

        self.assertEqual(
            resultado,
            {"vida": 20, "dano": 12, "defensa": 16, "velocidad": 7},
        )

    def test_calcula_estadisticas_de_nivel_nueve_sin_bono(self) -> None:
        resultado = calcular_estadisticas(SOLDADO, 9)

        self.assertEqual(
            resultado,
            {"vida": 84, "dano": 60, "defensa": 64, "velocidad": 23},
        )

    def test_aplica_bono_y_redondea_hacia_abajo_en_nivel_diez(self) -> None:
        resultado = calcular_estadisticas(SOLDADO, 10)

        self.assertEqual(
            resultado,
            {"vida": 110, "dano": 79, "defensa": 84, "velocidad": 30},
        )

    def test_rechaza_niveles_fuera_del_intervalo(self) -> None:
        for nivel in (0, 11):
            with self.subTest(nivel=nivel):
                with self.assertRaises(ValueError):
                    calcular_estadisticas(SOLDADO, nivel)


class PruebasExperiencia(unittest.TestCase):
    """Comprueba umbrales, ascensos y experiencia sobrante."""

    def test_calcula_experiencia_necesaria_segun_nivel(self) -> None:
        self.assertEqual(calcular_experiencia_necesaria(1), 100)
        self.assertEqual(calcular_experiencia_necesaria(9), 900)
        self.assertEqual(calcular_experiencia_necesaria(10), 0)

    def test_aplica_un_ascenso_y_conserva_el_sobrante(self) -> None:
        self.assertEqual(aplicar_experiencia(1, 0, 104), (2, 4))
        self.assertEqual(aplicar_experiencia(2, 150, 75), (3, 25))

    def test_permite_subir_varios_niveles(self) -> None:
        self.assertEqual(aplicar_experiencia(1, 0, 650), (4, 50))

    def test_descarta_experiencia_al_alcanzar_nivel_diez(self) -> None:
        self.assertEqual(aplicar_experiencia(9, 0, 1_000), (10, 0))
        self.assertEqual(aplicar_experiencia(10, 900, 100), (10, 0))

    def test_rechaza_niveles_invalidos(self) -> None:
        for nivel in (0, 11):
            with self.subTest(nivel=nivel):
                with self.assertRaises(ValueError):
                    calcular_experiencia_necesaria(nivel)
                with self.assertRaises(ValueError):
                    aplicar_experiencia(nivel, 0, 0)

    def test_rechaza_experiencia_negativa(self) -> None:
        with self.assertRaises(ValueError):
            aplicar_experiencia(1, -1, 0)
        with self.assertRaises(ValueError):
            aplicar_experiencia(1, 0, -1)


class PruebasClanYContratacion(unittest.TestCase):
    """Comprueba el cupo del clan y los costes de contratación."""

    def test_calcula_cupo_para_niveles_limite(self) -> None:
        self.assertEqual(calcular_cupo_clan(1), 5)
        self.assertEqual(calcular_cupo_clan(5), 25)

    def test_rechaza_nivel_de_clan_invalido(self) -> None:
        for nivel in (0, 6):
            with self.subTest(nivel=nivel):
                with self.assertRaises(ValueError):
                    calcular_cupo_clan(nivel)

    def test_calcula_coste_por_nivel(self) -> None:
        self.assertEqual(calcular_coste_contratacion(10, 1), 10)
        self.assertEqual(calcular_coste_contratacion(10, 10), 100)
        self.assertEqual(calcular_coste_contratacion(0, 5), 0)

    def test_rechaza_coste_negativo_o_nivel_invalido(self) -> None:
        with self.assertRaises(ValueError):
            calcular_coste_contratacion(-1, 1)
        for nivel in (0, 11):
            with self.subTest(nivel=nivel):
                with self.assertRaises(ValueError):
                    calcular_coste_contratacion(10, nivel)


class PruebasCombateBase(unittest.TestCase):
    """Comprueba la probabilidad crítica y los multiplicadores de daño."""

    def test_calcula_probabilidad_critica_total(self) -> None:
        self.assertEqual(calcular_probabilidad_critico(0), 5)
        self.assertEqual(calcular_probabilidad_critico(15), 20)

    def test_limita_probabilidad_critica_entre_cero_y_cien(self) -> None:
        self.assertEqual(calcular_probabilidad_critico(-10), 0)
        self.assertEqual(calcular_probabilidad_critico(200), 100)

    def test_calcula_dano_segun_efectividad(self) -> None:
        self.assertEqual(calcular_dano_final(15, "neutral", False), 15)
        self.assertEqual(calcular_dano_final(15, "efectivo", False), 22)
        self.assertEqual(calcular_dano_final(15, "inefectivo", False), 7)

    def test_aplica_multiplicador_critico(self) -> None:
        self.assertEqual(calcular_dano_final(15, "neutral", True), 22)

    def test_combina_efectividad_y_critico_antes_de_redondear(self) -> None:
        self.assertEqual(calcular_dano_final(15, "efectivo", True), 33)

    def test_acepta_dano_cero_y_rechaza_dano_negativo(self) -> None:
        self.assertEqual(calcular_dano_final(0, "efectivo", True), 0)
        with self.assertRaises(ValueError):
            calcular_dano_final(-1, "neutral", False)


if __name__ == "__main__":
    unittest.main()
