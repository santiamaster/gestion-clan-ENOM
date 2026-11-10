"""Pruebas de búsqueda y gestión de los aventureros del clan."""

import unittest
from copy import deepcopy

import servicios.aventureros as servicio_aventureros
from modelos.tipos import AventureroActivo, EstadoAventurero


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


if __name__ == "__main__":
    unittest.main()
