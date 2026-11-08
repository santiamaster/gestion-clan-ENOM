"""Pruebas de consulta, resurrección y entierro de aventureros."""

import unittest
from copy import deepcopy

from modelos.tipos import (
    AventureroActivo,
    AventureroEliminado,
    EstadoAventurero,
    EstadoClan,
    MotivoBaja,
)
from servicios.calculos import aplicar_descuento_resurreccion
from servicios.clan import crear_estado_inicial_clan
from servicios.iglesia import (
    AventureroNoEncontradoError,
    AventureroNoEstaMuertoError,
    DineroInsuficienteResurreccionError,
    buscar_aventurero_muerto,
    calcular_coste_resurreccion,
    enterrar_aventurero,
    listar_caidos_historicos,
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


def crear_eliminado(
    identificador: str,
    motivo_baja: MotivoBaja,
) -> AventureroEliminado:
    """Construye un registro histórico controlado para las pruebas."""

    estado: EstadoAventurero = (
        "vivo" if motivo_baja == "servicios_finalizados" else "muerto"
    )

    return {
        "id": identificador,
        "nombre": f"Integrante {identificador}",
        "plantilla_id": "PLANTILLA_SOLDADO",
        "nivel": 1,
        "experiencia": 0,
        "estado": estado,
        "motivo_baja": motivo_baja,
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


class PruebasEntierro(unittest.TestCase):
    """Comprueba la baja definitiva de los cuerpos recuperados."""

    def setUp(self) -> None:
        """Prepara dos muertos, un vivo y un registro histórico anterior."""

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
        self.caido_anterior: AventureroEliminado = crear_eliminado(
            "AV-0000",
            "caido_no_recuperado",
        )
        self.eliminados: list[AventureroEliminado] = [
            self.caido_anterior,
        ]

    def test_entierra_muerto_y_libera_cupo(self) -> None:
        """Evita conservar en activos un cuerpo que ya fue enterrado."""

        eliminado = enterrar_aventurero(
            self.activos,
            self.eliminados,
            "AV-0002",
        )

        self.assertNotIn(self.muerto_1, self.activos)
        self.assertEqual(len(self.activos), 2)
        self.assertEqual(eliminado["motivo_baja"], "enterrado_con_honores")
        self.assertEqual(self.eliminados[-1], eliminado)
        self.assertNotIn("motivo_baja", self.muerto_1)

    def test_conserva_orden_historico_de_entierros(self) -> None:
        """Evita insertar entierros nuevos antes de registros anteriores."""

        enterrar_aventurero(self.activos, self.eliminados, "AV-0002")
        enterrar_aventurero(self.activos, self.eliminados, "AV-0003")

        self.assertEqual(
            [registro["id"] for registro in self.eliminados],
            ["AV-0000", "AV-0002", "AV-0003"],
        )

    def test_rechaza_vivo_sin_modificar_listas(self) -> None:
        """Impide enterrar a un integrante vivo o alterar los registros."""

        activos_antes: list[AventureroActivo] = deepcopy(self.activos)
        eliminados_antes: list[AventureroEliminado] = deepcopy(
            self.eliminados
        )

        with self.assertRaises(AventureroNoEstaMuertoError):
            enterrar_aventurero(
                self.activos,
                self.eliminados,
                "AV-0001",
            )

        self.assertEqual(self.activos, activos_antes)
        self.assertEqual(self.eliminados, eliminados_antes)

    def test_rechaza_id_inexistente_sin_modificar_listas(self) -> None:
        """Impide crear una baja cuando el identificador no existe."""

        activos_antes: list[AventureroActivo] = deepcopy(self.activos)
        eliminados_antes: list[AventureroEliminado] = deepcopy(
            self.eliminados
        )

        with self.assertRaises(AventureroNoEncontradoError):
            enterrar_aventurero(
                self.activos,
                self.eliminados,
                "AV-9999",
            )

        self.assertEqual(self.activos, activos_antes)
        self.assertEqual(self.eliminados, eliminados_antes)


class PruebasMemorial(unittest.TestCase):
    """Comprueba el historial de aventureros muertos fuera del clan."""

    def test_filtra_caidos_en_orden_y_devuelve_lista_nueva(self) -> None:
        """Evita mostrar expulsados vivos o alterar el historial original."""

        enterrado: AventureroEliminado = crear_eliminado(
            "AV-0002",
            "enterrado_con_honores",
        )
        expulsado: AventureroEliminado = crear_eliminado(
            "AV-0003",
            "servicios_finalizados",
        )
        no_recuperado: AventureroEliminado = crear_eliminado(
            "AV-0004",
            "caido_no_recuperado",
        )
        eliminados: list[AventureroEliminado] = [
            enterrado,
            expulsado,
            no_recuperado,
        ]

        resultado = listar_caidos_historicos(eliminados)

        self.assertEqual(resultado, [enterrado, no_recuperado])
        self.assertIsNot(resultado, eliminados)
        self.assertIs(resultado[0], enterrado)


if __name__ == "__main__":
    unittest.main()
