"""Pruebas de búsqueda y gestión de los aventureros del clan."""

import unittest
from copy import deepcopy

import servicios.aventureros as servicio_aventureros
from modelos.tipos import (
    AventureroActivo,
    AventureroEliminado,
    EstadoAventurero,
)


def crear_aventurero(
    identificador: str,
    estado: EstadoAventurero = "vivo",
) -> AventureroActivo:
    """Construye un aventurero controlado para las pruebas del servicio."""

    return {
        "id": identificador,
        "nombre": f"Integrante {identificador}",
        "plantilla_id": "PLANTILLA_SOLDADO",
        "nivel": 1,
        "experiencia": 0,
        "estado": estado,
    }


class PruebasBusquedaGeneral(unittest.TestCase):
    """Comprueba la normalización y localización común por ID."""

    def setUp(self) -> None:
        """Prepara una lista mínima con un integrante vivo."""

        self.aventurero: AventureroActivo = crear_aventurero("AV-0001")
        self.activos: list[AventureroActivo] = [self.aventurero]

    def test_normaliza_espacios_y_mayusculas(self) -> None:
        """Evita que el formato escrito por el usuario altere la búsqueda."""

        resultado: str = servicio_aventureros.normalizar_id_aventurero(
            " av-0001 "
        )

        self.assertEqual(resultado, "AV-0001")

    def test_busca_id_normalizado_y_devuelve_el_registro_original(self) -> None:
        """Evita crear una copia distinta al seleccionar un integrante."""

        resultado: AventureroActivo = (
            servicio_aventureros.buscar_aventurero_activo(
                self.activos,
                " av-0001 ",
            )
        )

        self.assertIs(resultado, self.aventurero)

    def test_rechaza_id_inexistente_sin_modificar_activos(self) -> None:
        """Evita alterar el clan cuando el identificador no existe."""

        activos_antes: list[AventureroActivo] = deepcopy(self.activos)

        with self.assertRaises(
            servicio_aventureros.AventureroNoEncontradoError
        ):
            servicio_aventureros.buscar_aventurero_activo(
                self.activos,
                " av-9999 ",
            )

        self.assertEqual(self.activos, activos_antes)


class PruebasConsultaDeVivos(unittest.TestCase):
    """Comprueba el listado y la búsqueda exclusiva de integrantes vivos."""

    def setUp(self) -> None:
        """Prepara vivos intercalados con un integrante muerto."""

        self.vivo_1: AventureroActivo = crear_aventurero("AV-0001")
        self.muerto: AventureroActivo = crear_aventurero(
            "AV-0002",
            "muerto",
        )
        self.vivo_2: AventureroActivo = crear_aventurero("AV-0003")
        self.activos: list[AventureroActivo] = [
            self.vivo_1,
            self.muerto,
            self.vivo_2,
        ]

    def test_lista_solo_vivos_en_orden_y_en_una_lista_nueva(self) -> None:
        """Evita incluir muertos, reordenar registros o exponer la lista base."""

        resultado: list[AventureroActivo] = (
            servicio_aventureros.listar_aventureros_vivos(self.activos)
        )

        self.assertEqual(resultado, [self.vivo_1, self.vivo_2])
        self.assertIsNot(resultado, self.activos)
        self.assertIs(resultado[0], self.vivo_1)
        self.assertIs(resultado[1], self.vivo_2)

    def test_busca_vivo_y_devuelve_el_registro_original(self) -> None:
        """Evita copiar el integrante seleccionado o ignorar la normalización."""

        resultado: AventureroActivo = (
            servicio_aventureros.buscar_aventurero_vivo(
                self.activos,
                " av-0003 ",
            )
        )

        self.assertIs(resultado, self.vivo_2)

    def test_rechaza_un_integrante_muerto(self) -> None:
        """Impide usar como vivo un cuerpo que todavía ocupa cupo."""

        with self.assertRaises(
            servicio_aventureros.AventureroNoEstaVivoError
        ):
            servicio_aventureros.buscar_aventurero_vivo(
                self.activos,
                "AV-0002",
            )


class PruebasExpulsion(unittest.TestCase):
    """Comprueba la expulsión segura de integrantes vivos."""

    def setUp(self) -> None:
        """Prepara dos vivos, un muerto y una baja histórica anterior."""

        self.vivo_1: AventureroActivo = crear_aventurero("AV-0001")
        self.vivo_1["nombre"] = "Aria"
        self.vivo_1["plantilla_id"] = "PLANTILLA_ARQUERO"
        self.vivo_1["nivel"] = 4
        self.vivo_1["experiencia"] = 175
        self.vivo_2: AventureroActivo = crear_aventurero("AV-0002")
        self.muerto: AventureroActivo = crear_aventurero(
            "AV-0003",
            "muerto",
        )
        self.activos: list[AventureroActivo] = [
            self.vivo_1,
            self.muerto,
            self.vivo_2,
        ]
        self.baja_anterior: AventureroEliminado = {
            "id": "AV-0000",
            "nombre": "Integrante anterior",
            "plantilla_id": "PLANTILLA_SOLDADO",
            "nivel": 1,
            "experiencia": 0,
            "estado": "muerto",
            "motivo_baja": "caido_no_recuperado",
        }
        self.eliminados: list[AventureroEliminado] = [self.baja_anterior]

    def test_expulsa_vivo_y_agrega_una_baja_independiente_al_final(self) -> None:
        """Evita perder datos, alterar el historial o contaminar el activo."""

        eliminado: AventureroEliminado = (
            servicio_aventureros.expulsar_aventurero(
                self.activos,
                self.eliminados,
                " av-0001 ",
            )
        )

        self.assertNotIn(self.vivo_1, self.activos)
        self.assertEqual(self.eliminados, [self.baja_anterior, eliminado])
        self.assertIsNot(eliminado, self.vivo_1)
        self.assertEqual(
            eliminado,
            {
                "id": "AV-0001",
                "nombre": "Aria",
                "plantilla_id": "PLANTILLA_ARQUERO",
                "nivel": 4,
                "experiencia": 175,
                "estado": "vivo",
                "motivo_baja": "servicios_finalizados",
            },
        )
        self.assertNotIn("motivo_baja", self.vivo_1)

    def test_rechaza_id_inexistente_sin_modificar_listas(self) -> None:
        """Evita una baja parcial cuando el identificador no pertenece al clan."""

        self._comprobar_error_atomico(
            servicio_aventureros.AventureroNoEncontradoError,
            "AV-9999",
        )

    def test_rechaza_muerto_sin_modificar_listas(self) -> None:
        """Reserva la salida de los muertos para el servicio de iglesia."""

        self._comprobar_error_atomico(
            servicio_aventureros.AventureroNoEstaVivoError,
            "AV-0003",
        )

    def test_rechaza_al_ultimo_vivo_aunque_haya_muertos(self) -> None:
        """Impide dejar al clan sin ningún integrante capaz de actuar."""

        self.activos.remove(self.vivo_2)

        self._comprobar_error_atomico(
            servicio_aventureros.UltimoAventureroVivoError,
            "AV-0001",
        )

    def _comprobar_error_atomico(
        self,
        error_esperado: type[ValueError],
        aventurero_id: str,
    ) -> None:
        """Verifica que una expulsión fallida no altere ninguna lista."""

        activos_antes: list[AventureroActivo] = deepcopy(self.activos)
        eliminados_antes: list[AventureroEliminado] = deepcopy(
            self.eliminados
        )

        with self.assertRaises(error_esperado):
            servicio_aventureros.expulsar_aventurero(
                self.activos,
                self.eliminados,
                aventurero_id,
            )

        self.assertEqual(self.activos, activos_antes)
        self.assertEqual(self.eliminados, eliminados_antes)


if __name__ == "__main__":
    unittest.main()
