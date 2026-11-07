"""Validaciones de datos externos, selecciones y reglas del juego."""

from typing import TypeGuard, cast

from catalogos.plantillas import CATALOGO_PLANTILLAS
from modelos.tipos import (
    AventureroActivo,
    AventureroEliminado,
    EstadoAventurero,
    EstadoClan,
    EstadoMercado,
    EstadoPartida,
    MazmorrasCompletadas,
    MotivoBaja,
    NivelClan,
    OfertaReclutamiento,
)


class ErrorValidacionDatos(ValueError):
    """Indica que una estructura no coincide con el modelo esperado."""


def _es_diccionario_cadena_objeto(
    valor: object,
) -> TypeGuard[dict[str, object]]:
    """Indica si un objeto es un diccionario con claves de texto."""

    if not isinstance(valor, dict):
        return False
    diccionario: dict[object, object] = cast(dict[object, object], valor)
    return all(isinstance(clave, str) for clave in diccionario)


def _obtener_cadena(
    registro: dict[str, object],
    campo: str,
) -> str:
    """Obtiene una cadena obligatoria y no vacía de un registro."""

    valor: object | None = registro.get(campo)
    if not isinstance(valor, str) or valor.strip() == "":
        raise ErrorValidacionDatos(
            f"El campo '{campo}' debe ser una cadena no vacía."
        )
    return valor


def _obtener_entero(
    registro: dict[str, object],
    campo: str,
) -> int:
    """Obtiene un entero obligatorio, rechazando valores booleanos."""

    valor: object | None = registro.get(campo)
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise ErrorValidacionDatos(f"El campo '{campo}' debe ser un entero.")
    return valor


def _validar_aventurero_activo(
    valor: object,
    posicion: int,
) -> AventureroActivo:
    """Valida y copia un aventurero activo individual."""

    if not _es_diccionario_cadena_objeto(valor):
        raise ErrorValidacionDatos(
            f"El aventurero de la posición {posicion} debe ser un objeto."
        )

    identificador: str = _obtener_cadena(valor, "id")
    nombre: str = _obtener_cadena(valor, "nombre")
    plantilla_id: str = _obtener_cadena(valor, "plantilla_id")
    nivel: int = _obtener_entero(valor, "nivel")
    experiencia: int = _obtener_entero(valor, "experiencia")
    estado_texto: str = _obtener_cadena(valor, "estado")

    if plantilla_id not in CATALOGO_PLANTILLAS:
        raise ErrorValidacionDatos(
            f"La plantilla '{plantilla_id}' no está registrada."
        )
    if not 1 <= nivel <= 10:
        raise ErrorValidacionDatos("El nivel debe estar entre 1 y 10.")
    if experiencia < 0:
        raise ErrorValidacionDatos("La experiencia no puede ser negativa.")
    if nivel == 10 and experiencia != 0:
        raise ErrorValidacionDatos(
            "Un aventurero de nivel 10 debe tener experiencia igual a cero."
        )
    if estado_texto not in ("vivo", "muerto"):
        raise ErrorValidacionDatos(
            "El estado del aventurero debe ser 'vivo' o 'muerto'."
        )

    estado: EstadoAventurero = estado_texto
    return {
        "id": identificador,
        "nombre": nombre,
        "plantilla_id": plantilla_id,
        "nivel": nivel,
        "experiencia": experiencia,
        "estado": estado,
    }


def validar_datos_activos(datos: object) -> list[AventureroActivo]:
    """Valida y copia la lista de aventureros que todavía ocupan cupo.

    Args:
        datos: Objeto desconocido obtenido desde un archivo JSON.

    Returns:
        Una lista nueva de registros fuertemente tipados.

    Raises:
        ErrorValidacionDatos: Si el contenedor o algún registro es inválido.
    """

    if not isinstance(datos, list):
        raise ErrorValidacionDatos("Los datos activos deben ser una lista.")

    elementos: list[object] = cast(list[object], datos)
    return [
        _validar_aventurero_activo(valor, posicion)
        for posicion, valor in enumerate(elementos)
    ]


def validar_datos_eliminados(datos: object) -> list[AventureroEliminado]:
    """Valida y copia la lista histórica de aventureros eliminados.

    Args:
        datos: Objeto desconocido obtenido desde un archivo JSON.

    Returns:
        Una lista nueva de registros eliminados fuertemente tipados.

    Raises:
        ErrorValidacionDatos: Si el contenedor o algún registro es inválido.
    """

    if not isinstance(datos, list):
        raise ErrorValidacionDatos("Los datos eliminados deben ser una lista.")

    eliminados: list[AventureroEliminado] = []
    elementos: list[object] = cast(list[object], datos)
    for posicion, valor in enumerate(elementos):
        activo: AventureroActivo = _validar_aventurero_activo(valor, posicion)
        if not _es_diccionario_cadena_objeto(valor):
            raise ErrorValidacionDatos(
                f"El registro eliminado de la posición {posicion} es inválido."
            )

        motivo_texto: str = _obtener_cadena(valor, "motivo_baja")
        if motivo_texto not in (
            "servicios_finalizados",
            "enterrado_con_honores",
            "caido_no_recuperado",
        ):
            raise ErrorValidacionDatos("El motivo de baja no es válido.")

        motivo: MotivoBaja = motivo_texto
        eliminado: AventureroEliminado = {
            **activo,
            "motivo_baja": motivo,
        }
        eliminados.append(eliminado)

    return eliminados


def _validar_mazmorras(valor: object) -> MazmorrasCompletadas:
    """Valida las cinco banderas de progreso de las mazmorras."""

    if not _es_diccionario_cadena_objeto(valor):
        raise ErrorValidacionDatos(
            "El campo 'mazmorras_completadas' debe ser un objeto."
        )

    claves_esperadas: set[str] = {
        "mazmorra_1",
        "mazmorra_2",
        "mazmorra_3",
        "mazmorra_4",
        "mazmorra_5",
    }
    if set(valor) != claves_esperadas:
        raise ErrorValidacionDatos(
            "Deben existir exactamente las cinco banderas de mazmorras."
        )
    if not all(isinstance(valor[clave], bool) for clave in claves_esperadas):
        raise ErrorValidacionDatos(
            "Las banderas de mazmorras deben ser valores booleanos."
        )

    return {
        "mazmorra_1": cast(bool, valor["mazmorra_1"]),
        "mazmorra_2": cast(bool, valor["mazmorra_2"]),
        "mazmorra_3": cast(bool, valor["mazmorra_3"]),
        "mazmorra_4": cast(bool, valor["mazmorra_4"]),
        "mazmorra_5": cast(bool, valor["mazmorra_5"]),
    }


def _validar_oferta(valor: object, posicion: int) -> OfertaReclutamiento:
    """Valida y copia una oferta individual del gremio."""

    if not _es_diccionario_cadena_objeto(valor):
        raise ErrorValidacionDatos(
            f"La oferta de la posición {posicion} debe ser un objeto."
        )

    identificador: str = _obtener_cadena(valor, "id_oferta")
    nombre: str = _obtener_cadena(valor, "nombre")
    plantilla_id: str = _obtener_cadena(valor, "plantilla_id")
    nivel: int = _obtener_entero(valor, "nivel")
    coste: int = _obtener_entero(valor, "coste")

    if plantilla_id not in CATALOGO_PLANTILLAS:
        raise ErrorValidacionDatos(
            f"La plantilla '{plantilla_id}' no está registrada."
        )
    if not 1 <= nivel <= 10:
        raise ErrorValidacionDatos("El nivel de la oferta debe estar entre 1 y 10.")
    if coste < 0:
        raise ErrorValidacionDatos("El coste de la oferta no puede ser negativo.")

    return {
        "id_oferta": identificador,
        "nombre": nombre,
        "plantilla_id": plantilla_id,
        "nivel": nivel,
        "coste": coste,
    }


def validar_estado_clan(datos: object) -> EstadoClan:
    """Valida y copia el estado general persistente de una partida.

    Args:
        datos: Objeto desconocido obtenido desde un archivo JSON.

    Returns:
        Un estado nuevo y completamente tipado.

    Raises:
        ErrorValidacionDatos: Si falta un campo o contiene un valor inválido.
    """

    if not _es_diccionario_cadena_objeto(datos):
        raise ErrorValidacionDatos("El estado del clan debe ser un objeto.")

    nombre: str = _obtener_cadena(datos, "nombre")
    nivel_entero: int = _obtener_entero(datos, "nivel")
    dinero: int = _obtener_entero(datos, "dinero")
    siguiente_id: int = _obtener_entero(datos, "siguiente_id_aventurero")
    mercado_texto: str = _obtener_cadena(datos, "estado_mercado")
    partida_texto: str = _obtener_cadena(datos, "estado_partida")

    if not 1 <= nivel_entero <= 5:
        raise ErrorValidacionDatos("El nivel del clan debe estar entre 1 y 5.")
    if dinero < 0:
        raise ErrorValidacionDatos("El dinero no puede ser negativo.")
    if siguiente_id < 1:
        raise ErrorValidacionDatos(
            "El siguiente identificador de aventurero debe ser positivo."
        )
    if mercado_texto not in ("disponible", "contratacion_realizada"):
        raise ErrorValidacionDatos("El estado del mercado no es válido.")
    if partida_texto not in ("en_curso", "victoria", "derrota"):
        raise ErrorValidacionDatos("El estado de la partida no es válido.")

    mazmorras: MazmorrasCompletadas = _validar_mazmorras(
        datos.get("mazmorras_completadas")
    )
    ofertas_sin_validar: object | None = datos.get("ofertas_reclutamiento")
    if not isinstance(ofertas_sin_validar, list):
        raise ErrorValidacionDatos(
            "El campo 'ofertas_reclutamiento' debe ser una lista."
        )
    elementos: list[object] = cast(list[object], ofertas_sin_validar)
    ofertas: list[OfertaReclutamiento] = [
        _validar_oferta(valor, posicion)
        for posicion, valor in enumerate(elementos)
    ]

    nivel: NivelClan = cast(NivelClan, nivel_entero)
    mercado: EstadoMercado = mercado_texto
    estado_partida: EstadoPartida = partida_texto
    return {
        "nombre": nombre,
        "nivel": nivel,
        "dinero": dinero,
        "siguiente_id_aventurero": siguiente_id,
        "estado_mercado": mercado,
        "estado_partida": estado_partida,
        "mazmorras_completadas": mazmorras,
        "ofertas_reclutamiento": ofertas,
    }

