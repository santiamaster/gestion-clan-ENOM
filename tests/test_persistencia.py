"""Pruebas del acceso a los archivos locales de la partida."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast
from unittest.mock import patch

from modelos.tipos import EstadoClan
from servicios.persistencia import (
    DIRECTORIO_DATOS,
    DIRECTORIO_PARTIDA,
    ErrorPersistencia,
    PartidaIncompletaError,
    PartidaInvalidaError,
    cargar_partida,
    crear_directorio_partida,
    eliminar_partida,
    existe_partida_guardada,
    guardar_partida,
)
from servicios.validaciones import (
    validar_datos_activos,
    validar_datos_eliminados,
    validar_estado_clan,
)
from tests.test_validaciones import crear_aventurero_activo, crear_estado_clan


REEMPLAZAR_REAL = Path.replace


def escribir_json(directorio: Path, nombre: str, datos: object) -> None:
    """Escribe un JSON de prueba dentro de un directorio temporal."""

    directorio.mkdir(parents=True, exist_ok=True)
    contenido: str = json.dumps(datos, ensure_ascii=False, indent=4)
    (directorio / nombre).write_text(contenido, encoding="utf-8")


def escribir_partida_valida(directorio: Path) -> None:
    """Crea los tres archivos válidos requeridos para cargar una partida."""

    escribir_json(directorio, "estado_clan.json", crear_estado_clan())
    escribir_json(
        directorio,
        "datos_activos.json",
        [crear_aventurero_activo()],
    )
    escribir_json(directorio, "datos_eliminados.json", [])


class PruebasRutasPersistencia(unittest.TestCase):
    """Comprueba que las rutas no dependan de la terminal utilizada."""

    def test_directorios_se_resuelven_desde_la_raiz_del_proyecto(self) -> None:
        self.assertTrue(DIRECTORIO_DATOS.is_absolute())
        self.assertEqual(DIRECTORIO_DATOS.name, "datos")
        self.assertEqual(DIRECTORIO_PARTIDA, DIRECTORIO_DATOS / "partida")

    def test_no_quedan_json_directamente_en_datos(self) -> None:
        self.assertEqual(list(DIRECTORIO_DATOS.glob("*.json")), [])

    def test_crea_el_directorio_de_partida_si_no_existe(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "datos" / "partida"

            crear_directorio_partida(directorio)

            self.assertTrue(directorio.is_dir())


class PruebasCargaPersistencia(unittest.TestCase):
    """Comprueba existencia, integridad y carga de la partida."""

    def test_ausencia_total_indica_que_no_hay_partida(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"

            self.assertFalse(existe_partida_guardada(directorio))

    def test_carga_partida_completa_y_valida(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"
            escribir_partida_valida(directorio)

            self.assertTrue(existe_partida_guardada(directorio))
            estado, activos, eliminados = cargar_partida(directorio)

            self.assertEqual(estado, crear_estado_clan())
            self.assertEqual(activos, [crear_aventurero_activo()])
            self.assertEqual(eliminados, [])

    def test_presencia_parcial_produce_error_controlado(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"
            escribir_json(directorio, "datos_activos.json", [])

            with self.assertRaises(PartidaIncompletaError):
                existe_partida_guardada(directorio)
            with self.assertRaises(PartidaIncompletaError):
                cargar_partida(directorio)

    def test_json_malformado_identifica_el_archivo(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"
            escribir_partida_valida(directorio)
            (directorio / "estado_clan.json").write_text("{", encoding="utf-8")

            with self.assertRaisesRegex(
                PartidaInvalidaError,
                "estado_clan.json",
            ):
                cargar_partida(directorio)

    def test_estructura_invalida_identifica_el_archivo(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"
            escribir_partida_valida(directorio)
            datos_invalidos: list[object] = [{}]
            escribir_json(directorio, "datos_activos.json", datos_invalidos)

            with self.assertRaisesRegex(
                PartidaInvalidaError,
                "datos_activos.json",
            ):
                cargar_partida(directorio)

    def test_error_de_lectura_no_se_confunde_con_json_invalido(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"
            escribir_partida_valida(directorio)

            with patch.object(Path, "read_text", side_effect=OSError("bloqueado")):
                with self.assertRaises(ErrorPersistencia) as contexto:
                    cargar_partida(directorio)

            self.assertNotIsInstance(contexto.exception, PartidaInvalidaError)

class PruebasGuardadoPersistencia(unittest.TestCase):
    """Comprueba escritura segura, sustitución y eliminación limitada."""

    def test_guarda_unicode_con_sangria_y_permite_recargar(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"
            estado = validar_estado_clan(crear_estado_clan())
            activos = validar_datos_activos([crear_aventurero_activo()])
            eliminados = validar_datos_eliminados([])

            guardar_partida(estado, activos, eliminados, directorio)

            contenido = (directorio / "datos_activos.json").read_text(
                encoding="utf-8"
            )
            self.assertIn("Áurea", contenido)
            self.assertNotIn("\\u00c1", contenido)
            self.assertIn('    "nombre"', contenido)
            self.assertEqual(cargar_partida(directorio), (estado, activos, []))
            self.assertEqual(list(directorio.glob("*.tmp")), [])
            self.assertEqual(list(directorio.glob("*.bak")), [])

    def test_sustituye_una_partida_anterior(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"
            estado = validar_estado_clan(crear_estado_clan())
            guardar_partida(estado, [], [], directorio)
            estado["dinero"] = 250

            guardar_partida(estado, [], [], directorio)

            estado_cargado, _, _ = cargar_partida(directorio)
            self.assertEqual(estado_cargado["dinero"], 250)

    def test_no_crea_archivos_si_los_datos_son_invalidos(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"
            estado_invalido = cast(EstadoClan, {"nombre": ""})

            with self.assertRaises(PartidaInvalidaError):
                guardar_partida(estado_invalido, [], [], directorio)

            self.assertFalse(directorio.exists())

    def test_restaura_los_tres_json_si_falla_cualquier_reemplazo(
        self,
    ) -> None:
        for reemplazo_fallido in (1, 2, 3):
            with self.subTest(reemplazo_fallido=reemplazo_fallido):
                with TemporaryDirectory() as temporal:
                    directorio = Path(temporal) / "partida"
                    estado_anterior = validar_estado_clan(crear_estado_clan())
                    activos_anteriores = validar_datos_activos(
                        [crear_aventurero_activo()]
                    )
                    eliminados_anteriores = validar_datos_eliminados([])
                    guardar_partida(
                        estado_anterior,
                        activos_anteriores,
                        eliminados_anteriores,
                        directorio,
                    )
                    bytes_anteriores: dict[str, bytes] = {
                        ruta.name: ruta.read_bytes()
                        for ruta in directorio.glob("*.json")
                    }
                    estado_nuevo: EstadoClan = validar_estado_clan(
                        crear_estado_clan()
                    )
                    estado_nuevo["dinero"] = 250
                    contador: int = 0

                    def reemplazar_con_fallo(
                        origen: Path,
                        destino: Path,
                    ) -> Path:
                        nonlocal contador
                        if origen.name.endswith(".tmp"):
                            contador += 1
                            if contador == reemplazo_fallido:
                                raise OSError("reemplazo bloqueado")
                        return REEMPLAZAR_REAL(origen, destino)

                    with patch.object(
                        Path,
                        "replace",
                        new=reemplazar_con_fallo,
                    ):
                        with self.assertRaises(ErrorPersistencia):
                            guardar_partida(
                                estado_nuevo,
                                activos_anteriores,
                                eliminados_anteriores,
                                directorio,
                            )

                    bytes_actuales: dict[str, bytes] = {
                        ruta.name: ruta.read_bytes()
                        for ruta in directorio.glob("*.json")
                    }
                    self.assertEqual(bytes_actuales, bytes_anteriores)
                    self.assertEqual(
                        cargar_partida(directorio),
                        (
                            estado_anterior,
                            activos_anteriores,
                            eliminados_anteriores,
                        ),
                    )
                    self.assertEqual(list(directorio.glob("*.tmp")), [])
                    self.assertEqual(list(directorio.glob("*.bak")), [])

    def test_no_deja_partida_parcial_en_un_directorio_nuevo(self) -> None:
        for reemplazo_fallido in (1, 2, 3):
            with self.subTest(reemplazo_fallido=reemplazo_fallido):
                with TemporaryDirectory() as temporal:
                    directorio = Path(temporal) / "partida"
                    estado = validar_estado_clan(crear_estado_clan())
                    contador: int = 0

                    def reemplazar_con_fallo(
                        origen: Path,
                        destino: Path,
                    ) -> Path:
                        nonlocal contador
                        if origen.name.endswith(".tmp"):
                            contador += 1
                            if contador == reemplazo_fallido:
                                raise OSError("reemplazo bloqueado")
                        return REEMPLAZAR_REAL(origen, destino)

                    with patch.object(
                        Path,
                        "replace",
                        new=reemplazar_con_fallo,
                    ):
                        with self.assertRaises(ErrorPersistencia):
                            guardar_partida(estado, [], [], directorio)

                    self.assertEqual(list(directorio.glob("*.json")), [])
                    self.assertEqual(list(directorio.glob("*.tmp")), [])
                    self.assertEqual(list(directorio.glob("*.bak")), [])

    def test_eliminar_partida_inexistente_no_falla(self) -> None:
        with TemporaryDirectory() as temporal:
            eliminar_partida(Path(temporal) / "partida")

    def test_elimina_solo_los_tres_archivos_conocidos(self) -> None:
        with TemporaryDirectory() as temporal:
            directorio = Path(temporal) / "partida"
            estado = validar_estado_clan(crear_estado_clan())
            guardar_partida(estado, [], [], directorio)
            desconocido = directorio / "notas.txt"
            desconocido.write_text("conservar", encoding="utf-8")

            eliminar_partida(directorio)

            self.assertTrue(desconocido.is_file())
            self.assertFalse((directorio / "estado_clan.json").exists())
            self.assertFalse((directorio / "datos_activos.json").exists())
            self.assertFalse((directorio / "datos_eliminados.json").exists())


if __name__ == "__main__":
    unittest.main()
