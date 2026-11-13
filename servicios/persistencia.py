"""Carga, validación y guardado de los archivos JSON."""

import json
from pathlib import Path
from shutil import copyfile
from typing import Callable, TypeVar, cast

from modelos.tipos import AventureroActivo, AventureroEliminado, EstadoClan
from servicios.validaciones import (
    ErrorValidacionDatos,
    validar_datos_activos,
    validar_datos_eliminados,
    validar_estado_clan,
)


DIRECTORIO_PROYECTO: Path = Path(__file__).resolve().parents[1]
DIRECTORIO_DATOS: Path = DIRECTORIO_PROYECTO / "datos"
DIRECTORIO_PARTIDA: Path = DIRECTORIO_DATOS / "partida"

NOMBRE_DATOS_ACTIVOS: str = "datos_activos.json"
NOMBRE_DATOS_ELIMINADOS: str = "datos_eliminados.json"
NOMBRE_ESTADO_CLAN: str = "estado_clan.json"

TipoValidado = TypeVar("TipoValidado")


class ErrorPersistencia(Exception):
    """Error base producido al leer o escribir la partida."""


class PartidaIncompletaError(ErrorPersistencia):
    """Indica que no están presentes los tres archivos requeridos."""


class PartidaInvalidaError(ErrorPersistencia):
    """Indica que un archivo no contiene una estructura válida."""


def crear_directorio_partida(
    directorio: Path = DIRECTORIO_PARTIDA,
) -> None:
    """Crea el directorio destinado a la partida cuando no existe.

    Args:
        directorio: Ubicación donde se guardarán los tres archivos JSON.
    """

    directorio.mkdir(parents=True, exist_ok=True)


def _rutas_partida(directorio: Path) -> dict[str, Path]:
    """Construye las tres rutas conocidas de una partida."""

    return {
        NOMBRE_ESTADO_CLAN: directorio / NOMBRE_ESTADO_CLAN,
        NOMBRE_DATOS_ACTIVOS: directorio / NOMBRE_DATOS_ACTIVOS,
        NOMBRE_DATOS_ELIMINADOS: directorio / NOMBRE_DATOS_ELIMINADOS,
    }


def _comprobar_archivos_completos(directorio: Path) -> dict[str, Path]:
    """Comprueba que estén presentes los tres archivos de la partida."""

    rutas: dict[str, Path] = _rutas_partida(directorio)
    faltantes: list[str] = [
        nombre for nombre, ruta in rutas.items() if not ruta.is_file()
    ]
    if faltantes:
        detalle: str = ", ".join(faltantes)
        raise PartidaIncompletaError(
            f"La partida está incompleta. Faltan: {detalle}."
        )
    return rutas


def _leer_y_validar(
    ruta: Path,
    validador: Callable[[object], TipoValidado],
) -> TipoValidado:
    """Lee un JSON y lo convierte mediante el validador indicado."""

    try:
        contenido: str = ruta.read_text(encoding="utf-8")
    except UnicodeError as error:
        raise PartidaInvalidaError(
            f"El archivo {ruta.name} no utiliza una codificación UTF-8 válida."
        ) from error
    except OSError as error:
        raise ErrorPersistencia(
            f"No fue posible leer el archivo {ruta.name}."
        ) from error

    try:
        datos: object = cast(object, json.loads(contenido))
    except json.JSONDecodeError as error:
        raise PartidaInvalidaError(
            f"El archivo {ruta.name} no contiene un JSON válido."
        ) from error

    try:
        return validador(datos)
    except ErrorValidacionDatos as error:
        raise PartidaInvalidaError(
            f"El archivo {ruta.name} contiene datos inválidos: {error}"
        ) from error


def cargar_partida(
    directorio: Path = DIRECTORIO_PARTIDA,
) -> tuple[EstadoClan, list[AventureroActivo], list[AventureroEliminado]]:
    """Carga y valida los tres archivos que forman una partida.

    Args:
        directorio: Carpeta donde se encuentran los archivos de la partida.

    Returns:
        El estado del clan, los aventureros activos y el historial eliminado.

    Raises:
        PartidaIncompletaError: Si falta al menos uno de los tres archivos.
        PartidaInvalidaError: Si un archivo no puede leerse o validarse.
    """

    rutas: dict[str, Path] = _comprobar_archivos_completos(directorio)
    estado: EstadoClan = _leer_y_validar(
        rutas[NOMBRE_ESTADO_CLAN],
        validar_estado_clan,
    )
    activos: list[AventureroActivo] = _leer_y_validar(
        rutas[NOMBRE_DATOS_ACTIVOS],
        validar_datos_activos,
    )
    eliminados: list[AventureroEliminado] = _leer_y_validar(
        rutas[NOMBRE_DATOS_ELIMINADOS],
        validar_datos_eliminados,
    )
    return estado, activos, eliminados


def existe_partida_guardada(
    directorio: Path = DIRECTORIO_PARTIDA,
) -> bool:
    """Indica si existe una partida completa y válida.

    La ausencia total es un estado normal. Una presencia parcial o inválida se
    informa mediante las excepciones de persistencia correspondientes.

    Args:
        directorio: Carpeta donde debería encontrarse la partida.

    Returns:
        `False` si no existe ningún archivo y `True` si los tres son válidos.
    """

    rutas: dict[str, Path] = _rutas_partida(directorio)
    if not any(ruta.exists() for ruta in rutas.values()):
        return False

    cargar_partida(directorio)
    return True


def _serializar_json(datos: object) -> str:
    """Convierte una estructura validada a JSON legible y UTF-8."""

    return json.dumps(datos, ensure_ascii=False, indent=4) + "\n"


def _limpiar_archivos_auxiliares(rutas: list[Path]) -> None:
    """Intenta eliminar temporales o respaldos sin ocultar el error original."""

    for ruta in rutas:
        try:
            ruta.unlink(missing_ok=True)
        except OSError:
            pass


def guardar_partida(
    estado_clan: EstadoClan,
    datos_activos: list[AventureroActivo],
    datos_eliminados: list[AventureroEliminado],
    directorio: Path = DIRECTORIO_PARTIDA,
) -> None:
    """Valida y guarda los tres archivos que forman una partida.

    La escritura se realiza primero sobre archivos temporales. Los destinos se
    reemplazan solamente después de que los tres temporales fueron escritos.

    Args:
        estado_clan: Progreso general de la partida.
        datos_activos: Aventureros que todavía ocupan cupo en el clan.
        datos_eliminados: Historial de aventureros que abandonaron el clan.
        directorio: Carpeta donde se almacenará la partida.

    Raises:
        PartidaInvalidaError: Si alguna estructura recibida no es válida.
        ErrorPersistencia: Si el sistema no puede escribir los archivos.
    """

    try:
        estado_validado: EstadoClan = validar_estado_clan(estado_clan)
        activos_validados: list[AventureroActivo] = validar_datos_activos(
            datos_activos
        )
        eliminados_validados: list[AventureroEliminado] = (
            validar_datos_eliminados(datos_eliminados)
        )
    except ErrorValidacionDatos as error:
        raise PartidaInvalidaError(
            f"No se puede guardar una partida con datos inválidos: {error}"
        ) from error

    rutas: dict[str, Path] = _rutas_partida(directorio)
    contenidos: dict[str, str] = {
        NOMBRE_ESTADO_CLAN: _serializar_json(estado_validado),
        NOMBRE_DATOS_ACTIVOS: _serializar_json(activos_validados),
        NOMBRE_DATOS_ELIMINADOS: _serializar_json(eliminados_validados),
    }
    temporales: dict[str, Path] = {
        nombre: ruta.with_name(f"{ruta.name}.tmp")
        for nombre, ruta in rutas.items()
    }
    respaldos: dict[str, Path] = {
        nombre: ruta.with_name(f"{ruta.name}.bak")
        for nombre, ruta in rutas.items()
    }
    existian: dict[str, bool] = {
        nombre: ruta.exists() for nombre, ruta in rutas.items()
    }
    auxiliares: list[Path] = [*temporales.values(), *respaldos.values()]

    try:
        crear_directorio_partida(directorio)
        _limpiar_archivos_auxiliares(auxiliares)

        for nombre, ruta in rutas.items():
            temporal: Path = temporales[nombre]
            temporal.write_text(contenidos[nombre], encoding="utf-8")

        for nombre, ruta in rutas.items():
            if existian[nombre]:
                copyfile(ruta, respaldos[nombre])

        for nombre, ruta in rutas.items():
            temporales[nombre].replace(ruta)
    except OSError as error:
        for nombre, ruta in rutas.items():
            try:
                respaldo: Path = respaldos[nombre]
                if existian[nombre] and respaldo.exists():
                    respaldo.replace(ruta)
                elif not existian[nombre]:
                    ruta.unlink(missing_ok=True)
            except OSError:
                pass
        _limpiar_archivos_auxiliares(auxiliares)
        raise ErrorPersistencia(
            "No fue posible guardar los archivos de la partida."
        ) from error
    else:
        _limpiar_archivos_auxiliares(auxiliares)


def eliminar_partida(
    directorio: Path = DIRECTORIO_PARTIDA,
) -> None:
    """Elimina exclusivamente los tres archivos conocidos de la partida.

    La operación no elimina el directorio ni otros archivos que pudiera
    contener. La ausencia previa de la partida se considera válida.

    Args:
        directorio: Carpeta donde se encuentra la partida.

    Raises:
        ErrorPersistencia: Si un archivo existente no puede eliminarse.
    """

    try:
        for ruta in _rutas_partida(directorio).values():
            ruta.unlink(missing_ok=True)
    except OSError as error:
        raise ErrorPersistencia(
            "No fue posible eliminar los archivos de la partida."
        ) from error

