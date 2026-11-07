"""Pruebas de validación de las estructuras cargadas desde JSON."""

import unittest
from typing import cast

from servicios.validaciones import (
    ErrorValidacionDatos,
    validar_datos_activos,
    validar_datos_eliminados,
    validar_estado_clan,
)


def crear_aventurero_activo() -> dict[str, object]:
    """Crea un registro válido que cada prueba puede modificar."""

    return {
        "id": "AV-0001",
        "nombre": "Áurea",
        "plantilla_id": "PLANTILLA_SOLDADO",
        "nivel": 1,
        "experiencia": 0,
        "estado": "vivo",
    }


def crear_estado_clan() -> dict[str, object]:
    """Crea un estado persistente válido para las pruebas."""

    return {
        "nombre": "Clan Alba",
        "nivel": 1,
        "dinero": 0,
        "siguiente_id_aventurero": 4,
        "contrataciones_restantes": 1,
        "estado_partida": "en_curso",
        "mazmorras_completadas": {
            "mazmorra_1": False,
            "mazmorra_2": False,
            "mazmorra_3": False,
            "mazmorra_4": False,
            "mazmorra_5": False,
        },
        "ofertas_reclutamiento": [
            {
                "id_oferta": "OF-01",
                "nombre": "Bruno",
                "plantilla_id": "PLANTILLA_SOLDADO",
                "nivel": 1,
                "coste": 10,
            },
            {
                "id_oferta": "OF-02",
                "nombre": "Aelira",
                "plantilla_id": "PLANTILLA_ARQUERO",
                "nivel": 1,
                "coste": 10,
            },
        ],
    }


class PruebasValidacionAventureros(unittest.TestCase):
    """Comprueba aventureros activos y registros eliminados."""

    def test_valida_lista_de_aventureros_activos_y_devuelve_copia(self) -> None:
        registro = crear_aventurero_activo()

        resultado = validar_datos_activos([registro])

        self.assertEqual(resultado, [registro])
        self.assertIsNot(resultado[0], registro)

    def test_rechaza_contenedor_que_no_es_lista(self) -> None:
        with self.assertRaises(ErrorValidacionDatos):
            validar_datos_activos({})

    def test_rechaza_campo_ausente_o_tipo_incorrecto(self) -> None:
        sin_nombre = crear_aventurero_activo()
        del sin_nombre["nombre"]
        id_incorrecto = crear_aventurero_activo()
        id_incorrecto["id"] = 10

        for registro in (sin_nombre, id_incorrecto):
            with self.subTest(registro=registro):
                with self.assertRaises(ErrorValidacionDatos):
                    validar_datos_activos([registro])

    def test_rechaza_valores_fuera_del_dominio(self) -> None:
        casos: list[tuple[str, object]] = [
            ("nivel", 0),
            ("nivel", 11),
            ("experiencia", -1),
            ("estado", "herido"),
            ("plantilla_id", "PLANTILLA_INEXISTENTE"),
        ]

        for campo, valor in casos:
            with self.subTest(campo=campo, valor=valor):
                registro = crear_aventurero_activo()
                registro[campo] = valor
                with self.assertRaises(ErrorValidacionDatos):
                    validar_datos_activos([registro])

    def test_nivel_diez_exige_experiencia_cero(self) -> None:
        registro = crear_aventurero_activo()
        registro["nivel"] = 10
        registro["experiencia"] = 1

        with self.assertRaises(ErrorValidacionDatos):
            validar_datos_activos([registro])

    def test_valida_aventurero_eliminado(self) -> None:
        registro = crear_aventurero_activo()
        registro["motivo_baja"] = "enterrado_con_honores"

        resultado = validar_datos_eliminados([registro])

        self.assertEqual(resultado, [registro])
        self.assertIsNot(resultado[0], registro)

    def test_rechaza_motivo_de_baja_invalido(self) -> None:
        registro = crear_aventurero_activo()
        registro["motivo_baja"] = "desconocido"

        with self.assertRaises(ErrorValidacionDatos):
            validar_datos_eliminados([registro])


class PruebasValidacionEstadoClan(unittest.TestCase):
    """Comprueba el estado general, las mazmorras y las ofertas."""

    def test_valida_estado_completo_y_devuelve_copia_profunda(self) -> None:
        estado = crear_estado_clan()

        resultado = validar_estado_clan(estado)

        self.assertEqual(resultado, estado)
        self.assertIsNot(resultado, estado)
        self.assertIsNot(
            resultado["mazmorras_completadas"],
            estado["mazmorras_completadas"],
        )
        self.assertIsNot(
            resultado["ofertas_reclutamiento"],
            estado["ofertas_reclutamiento"],
        )

    def test_rechaza_campos_generales_invalidos(self) -> None:
        casos: list[tuple[str, object]] = [
            ("nombre", " "),
            ("nivel", 0),
            ("nivel", 6),
            ("dinero", -1),
            ("siguiente_id_aventurero", 0),
            ("estado_partida", "desconocido"),
        ]

        for campo, valor in casos:
            with self.subTest(campo=campo, valor=valor):
                estado = crear_estado_clan()
                estado[campo] = valor
                with self.assertRaises(ErrorValidacionDatos):
                    validar_estado_clan(estado)

    def test_rechaza_contador_de_contrataciones_invalido(self) -> None:
        casos: tuple[object, ...] = (True, -1, 2)

        for valor in casos:
            with self.subTest(valor=valor):
                estado = crear_estado_clan()
                estado["contrataciones_restantes"] = valor
                with self.assertRaisesRegex(
                    ErrorValidacionDatos,
                    "contrataciones_restantes|contrataciones restantes",
                ):
                    validar_estado_clan(estado)

    def test_rechaza_estado_del_esquema_anterior(self) -> None:
        estado = crear_estado_clan()
        del estado["contrataciones_restantes"]
        estado["estado_mercado"] = "disponible"

        with self.assertRaisesRegex(
            ErrorValidacionDatos,
            "contrataciones_restantes",
        ):
            validar_estado_clan(estado)

    def test_rechaza_mas_ofertas_que_el_maximo_del_nivel(self) -> None:
        estado = crear_estado_clan()
        ofertas = cast(list[object], estado["ofertas_reclutamiento"])
        ofertas.append(
            {
                "id_oferta": "OF-03",
                "nombre": "Ciro",
                "plantilla_id": "PLANTILLA_SOLDADO",
                "nivel": 1,
                "coste": 10,
            }
        )

        with self.assertRaisesRegex(ErrorValidacionDatos, "cantidad de ofertas"):
            validar_estado_clan(estado)

    def test_rechaza_menos_ofertas_que_contrataciones_restantes(self) -> None:
        estado = crear_estado_clan()
        estado["nivel"] = 2
        estado["contrataciones_restantes"] = 2
        estado["ofertas_reclutamiento"] = [
            cast(list[object], estado["ofertas_reclutamiento"])[0]
        ]

        with self.assertRaisesRegex(
            ErrorValidacionDatos,
            "ofertas.*contrataciones restantes",
        ):
            validar_estado_clan(estado)

    def test_rechaza_identificadores_de_oferta_repetidos(self) -> None:
        estado = crear_estado_clan()
        ofertas = cast(list[dict[str, object]], estado["ofertas_reclutamiento"])
        ofertas[1]["id_oferta"] = ofertas[0]["id_oferta"]

        with self.assertRaisesRegex(ErrorValidacionDatos, "identificadores"):
            validar_estado_clan(estado)

    def test_rechaza_oferta_superior_al_nivel_del_clan(self) -> None:
        estado = crear_estado_clan()
        ofertas = cast(list[dict[str, object]], estado["ofertas_reclutamiento"])
        ofertas[0]["nivel"] = 2
        ofertas[0]["coste"] = 20

        with self.assertRaisesRegex(ErrorValidacionDatos, "nivel de la oferta"):
            validar_estado_clan(estado)

    def test_rechaza_oferta_con_coste_incorrecto(self) -> None:
        estado = crear_estado_clan()
        ofertas = cast(list[dict[str, object]], estado["ofertas_reclutamiento"])
        ofertas[0]["coste"] = 11

        with self.assertRaisesRegex(ErrorValidacionDatos, "coste de la oferta"):
            validar_estado_clan(estado)

    def test_rechaza_banderas_de_mazmorras_invalidas(self) -> None:
        estado_incompleto = crear_estado_clan()
        mazmorras = estado_incompleto["mazmorras_completadas"]
        self.assertIsInstance(mazmorras, dict)
        if isinstance(mazmorras, dict):
            del mazmorras["mazmorra_5"]

        estado_no_booleano = crear_estado_clan()
        mazmorras_no_booleanas = estado_no_booleano["mazmorras_completadas"]
        self.assertIsInstance(mazmorras_no_booleanas, dict)
        if isinstance(mazmorras_no_booleanas, dict):
            mazmorras_no_booleanas["mazmorra_1"] = 1

        for estado in (estado_incompleto, estado_no_booleano):
            with self.subTest(estado=estado):
                with self.assertRaises(ErrorValidacionDatos):
                    validar_estado_clan(estado)

    def test_rechaza_lista_u_oferta_invalida(self) -> None:
        ofertas_no_lista = crear_estado_clan()
        ofertas_no_lista["ofertas_reclutamiento"] = {}

        oferta_invalida = crear_estado_clan()
        ofertas_objeto: object = oferta_invalida["ofertas_reclutamiento"]
        self.assertIsInstance(ofertas_objeto, list)
        ofertas = cast(list[object], ofertas_objeto)
        oferta_objeto: object = ofertas[0]
        self.assertIsInstance(oferta_objeto, dict)
        oferta = cast(dict[str, object], oferta_objeto)
        oferta["plantilla_id"] = "PLANTILLA_INEXISTENTE"

        for estado in (ofertas_no_lista, oferta_invalida):
            with self.subTest(estado=estado):
                with self.assertRaises(ErrorValidacionDatos):
                    validar_estado_clan(estado)


if __name__ == "__main__":
    unittest.main()
