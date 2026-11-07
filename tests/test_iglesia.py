"""Pruebas de consulta, resurrección y entierro de aventureros."""

import unittest
from copy import deepcopy

from modelos.tipos import AventureroActivo, EstadoAventurero, EstadoClan
from servicios.calculos import aplicar_descuento_resurreccion
from servicios.clan import crear_estado_inicial_clan
from servicios.iglesia import (
    AventureroNoEncontradoError,
    AventureroNoEstaMuertoError,
    DineroInsuficienteResurreccionError,
    buscar_aventurero_muerto,
    calcular_coste_resurreccion,
    listar_aventureros_muertos,
    resucitar_aventurero,
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


class PruebasResurreccion(unittest.TestCase):
    """Comprueba la recuperación pagada de un aventurero muerto."""

    def setUp(self) -> None:
        """Prepara un muerto de nivel tres y un integrante vivo."""

        self.estado_clan: EstadoClan = crear_estado_inicial_clan(
            "Clan Alba",
        )
        self.estado_clan["dinero"] = 21
        self.muerto: AventureroActivo = crear_aventurero(
            "AV-0002",
            "muerto",
            nivel=3,
        )
        self.muerto["experiencia"] = 140
        self.vivo: AventureroActivo = crear_aventurero(
            "AV-0001",
            "vivo",
        )
        self.activos: list[AventureroActivo] = [self.vivo, self.muerto]

    def test_resucita_y_descuenta_el_coste_exacto(self) -> None:
        """Evita cambiar el estado sin cobrar el coste completo."""

        resultado = resucitar_aventurero(
            self.estado_clan,
            self.activos,
            "AV-0002",
        )

        self.assertIs(resultado, self.muerto)
        self.assertEqual(resultado["estado"], "vivo")
        self.assertEqual(self.estado_clan["dinero"], 0)
        self.assertEqual(len(self.activos), 2)

    def test_conserva_identidad_y_progresion(self) -> None:
        """Evita perder datos permanentes al devolver un muerto a la vida."""

        datos_esperados: tuple[str, str, str, int, int] = (
            self.muerto["id"],
            self.muerto["nombre"],
            self.muerto["plantilla_id"],
            self.muerto["nivel"],
            self.muerto["experiencia"],
        )

        resucitar_aventurero(
            self.estado_clan,
            self.activos,
            "AV-0002",
        )

        self.assertEqual(
            (
                self.muerto["id"],
                self.muerto["nombre"],
                self.muerto["plantilla_id"],
                self.muerto["nivel"],
                self.muerto["experiencia"],
            ),
            datos_esperados,
        )

    def test_rechaza_dinero_insuficiente_sin_mutaciones(self) -> None:
        """Evita cobrar o revivir parcialmente cuando falta dinero."""

        self.estado_clan["dinero"] = 20
        estado_antes: EstadoClan = deepcopy(self.estado_clan)
        activos_antes: list[AventureroActivo] = deepcopy(self.activos)

        with self.assertRaises(DineroInsuficienteResurreccionError):
            resucitar_aventurero(
                self.estado_clan,
                self.activos,
                "AV-0002",
            )

        self.assertEqual(self.estado_clan, estado_antes)
        self.assertEqual(self.activos, activos_antes)

    def test_reutiliza_error_para_id_inexistente(self) -> None:
        """Evita convertir una selección desconocida en otro error."""

        with self.assertRaises(AventureroNoEncontradoError):
            resucitar_aventurero(
                self.estado_clan,
                self.activos,
                "AV-9999",
            )

    def test_reutiliza_error_para_aventurero_vivo(self) -> None:
        """Impide pagar una resurrección para un integrante vivo."""

        with self.assertRaises(AventureroNoEstaMuertoError):
            resucitar_aventurero(
                self.estado_clan,
                self.activos,
                "AV-0001",
            )


if __name__ == "__main__":
    unittest.main()
