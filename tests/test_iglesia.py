"""Pruebas de consulta, resurrección y entierro de aventureros."""

import unittest

from modelos.tipos import AventureroActivo, EstadoAventurero
from servicios.calculos import aplicar_descuento_resurreccion
from servicios.iglesia import (
    AventureroNoEncontradoError,
    AventureroNoEstaMuertoError,
    buscar_aventurero_muerto,
    calcular_coste_resurreccion,
    listar_aventureros_muertos,
)


def crear_aventurero(
    identificador: str,
    estado: EstadoAventurero,
    nivel: int = 1,
) -> AventureroActivo:
    """Construye un aventurero controlado para las pruebas de la iglesia."""

    return {
        "id": identificador,
        "nombre": f"Integrante {identificador}",
        "plantilla_id": "PLANTILLA_SOLDADO",
        "nivel": nivel,
        "experiencia": 0,
        "estado": estado,
    }


class PruebasConsultaCuerpos(unittest.TestCase):
    """Comprueba el listado y la selección de muertos recuperados."""

    def setUp(self) -> None:
        """Prepara un clan con un vivo y dos muertos."""

        self.vivo: AventureroActivo = crear_aventurero(
            "AV-0001",
            "vivo",
        )
        self.muerto_1: AventureroActivo = crear_aventurero(
            "AV-0002",
            "muerto",
        )
        self.muerto_2: AventureroActivo = crear_aventurero(
            "AV-0003",
            "muerto",
        )
        self.activos: list[AventureroActivo] = [
            self.vivo,
            self.muerto_1,
            self.muerto_2,
        ]

    def test_lista_solo_muertos_en_una_lista_nueva(self) -> None:
        """Evita incluir vivos o devolver la lista activa original."""

        resultado = listar_aventureros_muertos(self.activos)

        self.assertEqual(resultado, [self.muerto_1, self.muerto_2])
        self.assertIsNot(resultado, self.activos)
        self.assertIs(resultado[0], self.muerto_1)

    def test_busca_id_normalizado(self) -> None:
        """Evita que espacios o minúsculas impidan seleccionar un cuerpo."""

        resultado = buscar_aventurero_muerto(
            self.activos,
            "  av-0002  ",
        )

        self.assertIs(resultado, self.muerto_1)

    def test_rechaza_id_inexistente(self) -> None:
        """Distingue un identificador desconocido de otros errores."""

        with self.assertRaises(AventureroNoEncontradoError):
            buscar_aventurero_muerto(self.activos, "AV-9999")

    def test_rechaza_aventurero_vivo(self) -> None:
        """Impide tratar como cuerpo a un integrante que sigue vivo."""

        with self.assertRaises(AventureroNoEstaMuertoError):
            buscar_aventurero_muerto(self.activos, "AV-0001")


class PruebasCosteResurreccion(unittest.TestCase):
    """Comprueba el descuento y el coste final de la resurrección."""

    def test_redondea_descuento_hacia_abajo(self) -> None:
        """Evita redondear hacia arriba un setenta por ciento decimal."""

        self.assertEqual(aplicar_descuento_resurreccion(11), 7)

    def test_rechaza_coste_de_contratacion_negativo(self) -> None:
        """Evita convertir un coste inválido en una resurrección negativa."""

        with self.assertRaises(ValueError):
            aplicar_descuento_resurreccion(-1)

    def test_calcula_coste_desde_plantilla_y_nivel(self) -> None:
        """Evita ignorar la profesión o el nivel del muerto."""

        muerto: AventureroActivo = crear_aventurero(
            "AV-0002",
            "muerto",
            nivel=3,
        )

        self.assertEqual(calcular_coste_resurreccion(muerto), 21)


if __name__ == "__main__":
    unittest.main()
