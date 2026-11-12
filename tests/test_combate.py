"""Pruebas del motor de combate básico y sus estados temporales."""

import unittest
from collections.abc import Sequence
from random import Random
from typing import Callable, TypeVar, cast

from catalogos.enemigos import CATALOGO_ENEMIGOS
from catalogos.mazmorras import MAZMORRA_LIMOS
from catalogos.plantillas import CATALOGO_PLANTILLAS
from modelos.combate import (
    AventureroCombate,
    DefinicionOleada,
    EnemigoCombate,
    ParticipanteTurno,
    TurnoAventurero,
    TurnoEnemigo,
)
from modelos.tipos import (
    AventureroActivo,
    EfectividadAtaque,
    EstrategiaObjetivo,
    PlantillaAventurero,
    TipoAtaque,
)
import servicios.combate as combate


T = TypeVar("T")


class RandomControlado(Random):
    """Entrega valores prefijados y falla ante cualquier consumo adicional."""

    def __init__(
        self,
        tiradas: list[int] | None = None,
        elecciones: list[int] | None = None,
    ) -> None:
        super().__init__(0)
        self.tiradas: list[int] = list(tiradas or [])
        self.elecciones: list[int] = list(elecciones or [])

    def randint(self, inicio: int, fin: int) -> int:
        """Consume la siguiente tirada y comprueba el intervalo solicitado."""

        if not self.tiradas:
            raise AssertionError("No quedan tiradas d100 configuradas.")
        valor: int = self.tiradas.pop(0)
        if not inicio <= valor <= fin:
            raise AssertionError(
                f"La tirada {valor} no pertenece a {inicio}..{fin}."
            )
        return valor

    def choice(self, secuencia: Sequence[T]) -> T:
        """Consume el siguiente índice de elección controlada."""

        if not self.elecciones:
            raise AssertionError("No quedan elecciones configuradas.")
        indice: int = self.elecciones.pop(0)
        try:
            return secuencia[indice]
        except IndexError as error:
            raise AssertionError(
                f"El índice controlado {indice} no existe."
            ) from error


def _operacion(nombre: str) -> Callable[..., object]:
    """Obtiene una operación y falla claramente si todavía no existe."""

    operacion: object | None = getattr(combate, nombre, None)
    if not callable(operacion):
        raise AssertionError(f"Falta implementar {nombre}().")
    return cast(Callable[..., object], operacion)


def _aventurero(
    *,
    identificador: str = "AV-0001",
    plantilla_id: str = "PLANTILLA_SOLDADO",
    nivel: int = 1,
    estado: str = "vivo",
) -> AventureroActivo:
    """Construye un registro persistente mínimo para las pruebas."""

    return cast(
        AventureroActivo,
        {
            "id": identificador,
            "nombre": "Aldric",
            "plantilla_id": plantilla_id,
            "nivel": nivel,
            "experiencia": 0,
            "estado": estado,
        },
    )


def _estado_aventurero(
    *,
    identificador: str = "AV-0001",
    vida_actual: int = 20,
    esta_vivo: bool = True,
    estrategia: EstrategiaObjetivo = "aleatorio",
) -> AventureroCombate:
    """Crea un estado temporal controlado para validar grupos."""

    return {
        "id": identificador,
        "nombre": "Aldric",
        "plantilla_id": "PLANTILLA_SOLDADO",
        "vida_maxima": 20,
        "vida_actual": vida_actual,
        "dano": 12,
        "defensa": 16,
        "velocidad": 7,
        "probabilidad_critica": 5,
        "esta_vivo": esta_vivo,
        "tipo_ataque": "cuerpo_a_cuerpo",
        "estrategia_objetivo": estrategia,
    }


def _estado_enemigo(
    *,
    identificador: str = "LIMOS_LIMO-01",
    vida_actual: int = 20,
    esta_vivo: bool = True,
) -> EnemigoCombate:
    """Crea un estado enemigo controlado para validar grupos."""

    return {
        "id_instancia": identificador,
        "plantilla_id": "LIMOS_LIMO",
        "nombre": "Limo",
        "vida_maxima": 20,
        "vida_actual": vida_actual,
        "dano": 20,
        "defensa": 1,
        "velocidad": 1,
        "probabilidad_critica": 5,
        "esta_vivo": esta_vivo,
        "tipo_ataque": "magico",
        "efectividades": {
            "cuerpo_a_cuerpo": "efectivo",
            "distancia": "efectivo",
            "magico": "inefectivo",
        },
        "experiencia": 10,
        "dinero": 1,
        "es_jefe": False,
    }


def _turno_aventurero(
    combatiente: AventureroCombate,
) -> TurnoAventurero:
    """Envuelve un aventurero conservando la referencia original."""

    return {"bando": "aventureros", "combatiente": combatiente}


def _turno_enemigo(combatiente: EnemigoCombate) -> TurnoEnemigo:
    """Envuelve un enemigo conservando la referencia original."""

    return {"bando": "enemigos", "combatiente": combatiente}


class PruebasCreacionEstados(unittest.TestCase):
    """Comprueba la creación independiente y las validaciones previas."""

    def test_crea_aventurero_con_estadisticas_calculadas(self) -> None:
        crear = _operacion("crear_aventurero_combate")
        registro: AventureroActivo = _aventurero()

        resultado = cast(
            AventureroCombate,
            crear(registro, CATALOGO_PLANTILLAS),
        )

        self.assertEqual(resultado["vida_maxima"], 20)
        self.assertEqual(resultado["vida_actual"], 20)
        self.assertEqual(resultado["dano"], 12)
        self.assertEqual(resultado["defensa"], 16)
        self.assertEqual(resultado["velocidad"], 7)
        self.assertEqual(resultado["probabilidad_critica"], 5)
        self.assertEqual(resultado["tipo_ataque"], "cuerpo_a_cuerpo")
        self.assertEqual(resultado["estrategia_objetivo"], "aleatorio")
        self.assertTrue(resultado["esta_vivo"])

    def test_estado_de_aventurero_no_modifica_registro_ni_catalogo(self) -> None:
        crear = _operacion("crear_aventurero_combate")
        registro: AventureroActivo = _aventurero()
        plantilla: PlantillaAventurero = CATALOGO_PLANTILLAS[
            "PLANTILLA_SOLDADO"
        ]

        resultado = cast(
            AventureroCombate,
            crear(registro, CATALOGO_PLANTILLAS),
        )
        resultado["nombre"] = "Nombre temporal"
        resultado["vida_actual"] = 1

        self.assertEqual(registro["nombre"], "Aldric")
        self.assertEqual(plantilla["estadisticas_raza"]["vida"], 12)

    def test_crea_seis_instancias_independientes_para_la_oleada_dos(
        self,
    ) -> None:
        crear = _operacion("crear_enemigos_oleada")
        oleada: DefinicionOleada = MAZMORRA_LIMOS["oleadas"][1]

        resultado = cast(
            list[EnemigoCombate],
            crear(oleada, CATALOGO_ENEMIGOS),
        )

        self.assertEqual(
            [enemigo["id_instancia"] for enemigo in resultado],
            [
                "LIMOS_LIMO-01",
                "LIMOS_LIMO-02",
                "LIMOS_LIME-01",
                "LIMOS_LIME-02",
                "LIMOS_LIMA-01",
                "LIMOS_LIMA-02",
            ],
        )
        resultado[0]["vida_actual"] = 1
        resultado[0]["efectividades"]["magico"] = "neutral"
        self.assertEqual(resultado[1]["vida_actual"], 20)
        self.assertEqual(
            resultado[1]["efectividades"]["magico"],
            "inefectivo",
        )
        self.assertEqual(
            CATALOGO_ENEMIGOS["LIMOS_LIMO"]["estadisticas"]["vida"],
            20,
        )
        self.assertEqual(
            CATALOGO_ENEMIGOS["LIMOS_LIMO"]["efectividades"]["magico"],
            "inefectivo",
        )

    def test_rechaza_definiciones_de_oleada_invalidas(self) -> None:
        crear = _operacion("crear_enemigos_oleada")
        casos: list[DefinicionOleada] = [
            {"numero": 1, "enemigos": []},
            {
                "numero": 1,
                "enemigos": [
                    {"plantilla_id": "DESCONOCIDO", "cantidad": 1}
                ],
            },
            {
                "numero": 1,
                "enemigos": [
                    {"plantilla_id": "LIMOS_LIMO", "cantidad": 0}
                ],
            },
            {
                "numero": 1,
                "enemigos": [
                    {"plantilla_id": "LIMOS_LIMO", "cantidad": 1},
                    {"plantilla_id": "LIMOS_LIMO", "cantidad": 1},
                ],
            },
        ]

        error = getattr(combate, "DefinicionOleadaInvalidaError", ValueError)
        for oleada in casos:
            with self.subTest(oleada=oleada):
                with self.assertRaises(error):
                    crear(oleada, CATALOGO_ENEMIGOS)

    def test_rechaza_numero_de_oleada_fuera_del_intervalo(self) -> None:
        crear = _operacion("crear_enemigos_oleada")
        error = getattr(combate, "DefinicionOleadaInvalidaError", ValueError)
        oleada: DefinicionOleada = {
            "numero": 11,
            "enemigos": [{"plantilla_id": "LIMOS_LIMO", "cantidad": 1}],
        }

        with self.assertRaises(error):
            crear(oleada, CATALOGO_ENEMIGOS)

    def test_validador_acepta_un_muerto_si_queda_un_aventurero_vivo(
        self,
    ) -> None:
        validar = _operacion("_validar_estados_combate")
        aventureros: list[AventureroCombate] = [
            _estado_aventurero(
                identificador="AV-0001",
                vida_actual=0,
                esta_vivo=False,
            ),
            _estado_aventurero(identificador="AV-0002"),
        ]

        validar(aventureros, [_estado_enemigo()])

    def test_validador_rechaza_grupos_vacios_o_sin_supervivientes(
        self,
    ) -> None:
        validar = _operacion("_validar_estados_combate")
        error = getattr(combate, "EstadoCombateInvalidoError", ValueError)
        muerto: AventureroCombate = _estado_aventurero(
            vida_actual=0,
            esta_vivo=False,
        )

        with self.assertRaises(error):
            validar([], [_estado_enemigo()])
        with self.assertRaises(error):
            validar([muerto], [_estado_enemigo()])
        with self.assertRaises(error):
            validar([_estado_aventurero()], [])

    def test_validador_rechaza_vida_y_estado_incoherentes(self) -> None:
        validar = _operacion("_validar_estados_combate")
        error = getattr(combate, "EstadoCombateInvalidoError", ValueError)

        with self.assertRaises(error):
            validar(
                [_estado_aventurero(vida_actual=0, esta_vivo=True)],
                [_estado_enemigo()],
            )
        with self.assertRaises(error):
            validar(
                [_estado_aventurero()],
                [_estado_enemigo(vida_actual=21)],
            )

    def test_validador_rechaza_ids_de_instancia_duplicados(self) -> None:
        validar = _operacion("_validar_estados_combate")
        error = getattr(
            combate,
            "DefinicionOleadaInvalidaError",
            ValueError,
        )

        with self.assertRaises(error):
            validar(
                [_estado_aventurero()],
                [_estado_enemigo(), _estado_enemigo()],
            )


class PruebasAzarYObjetivos(unittest.TestCase):
    """Comprueba tiradas d100, desempates y objetivos vivos."""

    def test_resuelve_los_limites_de_una_unica_tirada_de_ataque(self) -> None:
        resolver = _operacion("resolver_tirada_ataque")
        casos: list[tuple[int, int, str]] = [
            (5, 5, "critico"),
            (5, 6, "impacto"),
            (0, 90, "impacto"),
            (5, 91, "fallo"),
            (5, 100, "fallo"),
            (90, 90, "critico"),
        ]

        for probabilidad, tirada, esperado in casos:
            with self.subTest(probabilidad=probabilidad, tirada=tirada):
                resultado = resolver(
                    probabilidad,
                    RandomControlado(tiradas=[tirada]),
                )
                self.assertEqual(resultado, esperado)

    def test_tirada_rechaza_probabilidad_critica_sin_normalizar(self) -> None:
        resolver = _operacion("resolver_tirada_ataque")

        for probabilidad in (-1, 91):
            with self.subTest(probabilidad=probabilidad):
                with self.assertRaises(ValueError):
                    resolver(probabilidad, RandomControlado())

    def test_desempate_repite_solo_entre_quienes_siguen_empatados(
        self,
    ) -> None:
        resolver = _operacion("resolver_desempate_d100")
        generador = RandomControlado(tiradas=[80, 80, 20, 40, 90])

        resultado = resolver(["A", "B", "C"], generador)

        self.assertEqual(resultado, ["B", "A", "C"])
        self.assertEqual(generador.tiradas, [])

    def test_seleccion_aleatoria_respeta_la_eleccion_controlada(self) -> None:
        seleccionar = _operacion("seleccionar_objetivo_aventurero")
        atacante: AventureroCombate = _estado_aventurero()
        enemigos: list[EnemigoCombate] = [
            _estado_enemigo(identificador="LIMOS_LIMO-01"),
            _estado_enemigo(identificador="LIMOS_LIMO-02"),
        ]

        resultado = seleccionar(
            atacante,
            enemigos,
            RandomControlado(elecciones=[1]),
        )

        self.assertIs(resultado, enemigos[1])

    def test_selecciona_menor_y_mayor_vida_actual(self) -> None:
        seleccionar = _operacion("seleccionar_objetivo_aventurero")
        enemigos: list[EnemigoCombate] = [
            _estado_enemigo(identificador="LIMOS_LIMO-01", vida_actual=15),
            _estado_enemigo(identificador="LIMOS_LIMO-02", vida_actual=5),
            _estado_enemigo(identificador="LIMOS_LIMO-03", vida_actual=20),
        ]

        menor = seleccionar(
            _estado_aventurero(estrategia="menor_vida_actual"),
            enemigos,
            RandomControlado(),
        )
        mayor = seleccionar(
            _estado_aventurero(estrategia="mayor_vida_actual"),
            enemigos,
            RandomControlado(),
        )

        self.assertIs(menor, enemigos[1])
        self.assertIs(mayor, enemigos[2])

    def test_desempata_objetivos_con_d100(self) -> None:
        seleccionar = _operacion("seleccionar_objetivo_aventurero")
        enemigos: list[EnemigoCombate] = [
            _estado_enemigo(identificador="LIMOS_LIMO-01", vida_actual=5),
            _estado_enemigo(identificador="LIMOS_LIMO-02", vida_actual=5),
            _estado_enemigo(identificador="LIMOS_LIMO-03", vida_actual=20),
        ]

        resultado = seleccionar(
            _estado_aventurero(estrategia="menor_vida_actual"),
            enemigos,
            RandomControlado(tiradas=[10, 90]),
        )

        self.assertIs(resultado, enemigos[1])

    def test_enemigo_excluye_muertos_al_elegir_objetivo(self) -> None:
        seleccionar = _operacion("seleccionar_objetivo_enemigo")
        muerto: AventureroCombate = _estado_aventurero(
            identificador="AV-0001",
            vida_actual=0,
            esta_vivo=False,
        )
        vivo: AventureroCombate = _estado_aventurero(
            identificador="AV-0002"
        )

        resultado = seleccionar(
            [muerto, vivo],
            RandomControlado(elecciones=[0]),
        )

        self.assertIs(resultado, vivo)

    def test_seleccion_rechaza_listas_sin_objetivos_vivos(self) -> None:
        seleccionar_aventurero = _operacion(
            "seleccionar_objetivo_aventurero"
        )
        seleccionar_enemigo = _operacion("seleccionar_objetivo_enemigo")
        muerto: AventureroCombate = _estado_aventurero(
            vida_actual=0,
            esta_vivo=False,
        )
        enemigo_muerto: EnemigoCombate = _estado_enemigo(
            vida_actual=0,
            esta_vivo=False,
        )
        error = getattr(combate, "EstadoCombateInvalidoError", ValueError)

        with self.assertRaises(error):
            seleccionar_aventurero(
                _estado_aventurero(),
                [enemigo_muerto],
                RandomControlado(),
            )
        with self.assertRaises(error):
            seleccionar_enemigo([muerto], RandomControlado())


class PruebasAtaquesBasicos(unittest.TestCase):
    """Comprueba efectividad, defensa y mutación temporal del objetivo."""

    def test_aventurero_consulta_efectividad_segun_su_tipo_de_ataque(
        self,
    ) -> None:
        obtener = _operacion("obtener_efectividad_ataque")
        aventurero: AventureroCombate = _estado_aventurero()
        enemigo: EnemigoCombate = _estado_enemigo()
        esperados: dict[TipoAtaque, EfectividadAtaque] = {
            "cuerpo_a_cuerpo": "efectivo",
            "distancia": "efectivo",
            "magico": "inefectivo",
        }

        for tipo_ataque, esperado in esperados.items():
            with self.subTest(tipo_ataque=tipo_ataque):
                aventurero["tipo_ataque"] = tipo_ataque
                resultado = obtener(
                    {"bando": "aventureros", "combatiente": aventurero},
                    {"bando": "enemigos", "combatiente": enemigo},
                )
                self.assertEqual(resultado, esperado)

    def test_ataque_enemigo_es_siempre_neutral(self) -> None:
        obtener = _operacion("obtener_efectividad_ataque")

        resultado = obtener(
            {"bando": "enemigos", "combatiente": _estado_enemigo()},
            {
                "bando": "aventureros",
                "combatiente": _estado_aventurero(),
            },
        )

        self.assertEqual(resultado, "neutral")

    def test_defensa_resta_dano_y_conserva_minimo_de_uno(self) -> None:
        calcular = _operacion("calcular_dano_recibido")

        self.assertEqual(calcular(30, 10), 20)
        self.assertEqual(calcular(10, 10), 1)
        self.assertEqual(calcular(5, 10), 1)

    def test_defensa_rechaza_valores_negativos(self) -> None:
        calcular = _operacion("calcular_dano_recibido")

        for dano, defensa in ((-1, 0), (0, -1)):
            with self.subTest(dano=dano, defensa=defensa):
                with self.assertRaises(ValueError):
                    calcular(dano, defensa)

    def test_fallo_no_causa_dano_ni_modifica_objetivo(self) -> None:
        ejecutar = _operacion("ejecutar_ataque_basico")
        atacante: AventureroCombate = _estado_aventurero()
        objetivo: EnemigoCombate = _estado_enemigo()

        resultado = ejecutar(
            atacante,
            objetivo,
            "neutral",
            RandomControlado(tiradas=[91]),
        )

        self.assertEqual(
            resultado,
            {
                "resultado": "fallo",
                "dano_aplicado": 0,
                "vida_restante": 20,
                "objetivo_derrotado": False,
            },
        )
        self.assertEqual(objetivo["vida_actual"], 20)
        self.assertTrue(objetivo["esta_vivo"])

    def test_impacto_aplica_efectividad_antes_de_defensa(self) -> None:
        ejecutar = _operacion("ejecutar_ataque_basico")
        casos: list[tuple[EfectividadAtaque, int, int]] = [
            ("neutral", 11, 9),
            ("efectivo", 17, 3),
            ("inefectivo", 5, 15),
        ]

        for efectividad, dano_esperado, vida_esperada in casos:
            with self.subTest(efectividad=efectividad):
                objetivo: EnemigoCombate = _estado_enemigo()
                resultado = cast(
                    dict[str, object],
                    ejecutar(
                        _estado_aventurero(),
                        objetivo,
                        efectividad,
                        RandomControlado(tiradas=[6]),
                    ),
                )
                self.assertEqual(resultado["resultado"], "impacto")
                self.assertEqual(resultado["dano_aplicado"], dano_esperado)
                self.assertEqual(resultado["vida_restante"], vida_esperada)

    def test_critico_duplica_antes_de_defensa_y_actualiza_la_muerte(
        self,
    ) -> None:
        ejecutar = _operacion("ejecutar_ataque_basico")
        objetivo: EnemigoCombate = _estado_enemigo()

        resultado = ejecutar(
            _estado_aventurero(),
            objetivo,
            "neutral",
            RandomControlado(tiradas=[5]),
        )

        self.assertEqual(resultado["resultado"], "critico")
        self.assertEqual(resultado["dano_aplicado"], 23)
        self.assertEqual(resultado["vida_restante"], 0)
        self.assertTrue(resultado["objetivo_derrotado"])
        self.assertEqual(objetivo["vida_actual"], 0)
        self.assertFalse(objetivo["esta_vivo"])

    def test_rechaza_objetivo_muerto_sin_consumir_tirada(self) -> None:
        ejecutar = _operacion("ejecutar_ataque_basico")
        objetivo: EnemigoCombate = _estado_enemigo(
            vida_actual=0,
            esta_vivo=False,
        )
        generador = RandomControlado(tiradas=[5])
        error = getattr(combate, "EstadoCombateInvalidoError", ValueError)

        with self.assertRaises(error):
            ejecutar(
                _estado_aventurero(),
                objetivo,
                "neutral",
                generador,
            )

        self.assertEqual(generador.tiradas, [5])
        self.assertEqual(objetivo["vida_actual"], 0)


class PruebasTurnosYRonda(unittest.TestCase):
    """Comprueba el orden inicial y una vuelta completa de participantes."""

    def test_orden_descendente_desempata_y_excluye_muertos(self) -> None:
        calcular = _operacion("calcular_orden_turnos")
        aventurero_1: AventureroCombate = _estado_aventurero(
            identificador="AV-0001"
        )
        aventurero_1["velocidad"] = 10
        aventurero_2: AventureroCombate = _estado_aventurero(
            identificador="AV-0002"
        )
        aventurero_2["velocidad"] = 10
        muerto: AventureroCombate = _estado_aventurero(
            identificador="AV-0003",
            vida_actual=0,
            esta_vivo=False,
        )
        muerto["velocidad"] = 99
        enemigo_rapido: EnemigoCombate = _estado_enemigo(
            identificador="LIMOS_LIMO-01"
        )
        enemigo_rapido["velocidad"] = 20
        enemigo_empatado: EnemigoCombate = _estado_enemigo(
            identificador="LIMOS_LIMO-02"
        )
        enemigo_empatado["velocidad"] = 10

        orden = cast(
            list[ParticipanteTurno],
            calcular(
                [aventurero_1, aventurero_2, muerto],
                [enemigo_rapido, enemigo_empatado],
                RandomControlado(tiradas=[20, 90, 50]),
            ),
        )

        self.assertEqual(
            [turno["combatiente"]["nombre"] for turno in orden],
            ["Limo", "Aldric", "Limo", "Aldric"],
        )
        self.assertIs(orden[0]["combatiente"], enemigo_rapido)
        self.assertIs(orden[1]["combatiente"], aventurero_2)
        self.assertIs(orden[2]["combatiente"], enemigo_empatado)
        self.assertIs(orden[3]["combatiente"], aventurero_1)
        self.assertNotIn(muerto, [turno["combatiente"] for turno in orden])

    def test_cada_participante_vivo_actua_una_vez(self) -> None:
        resolver = _operacion("resolver_ronda")
        aventurero_1: AventureroCombate = _estado_aventurero(
            identificador="AV-0001"
        )
        aventurero_2: AventureroCombate = _estado_aventurero(
            identificador="AV-0002"
        )
        enemigo: EnemigoCombate = _estado_enemigo()
        aventurero_1["dano"] = 2
        aventurero_1["defensa"] = 0
        aventurero_2["dano"] = 2
        enemigo["vida_maxima"] = 100
        enemigo["vida_actual"] = 100
        enemigo["dano"] = 2
        enemigo["defensa"] = 0
        orden: list[ParticipanteTurno] = [
            _turno_aventurero(aventurero_1),
            _turno_aventurero(aventurero_2),
            _turno_enemigo(enemigo),
        ]

        derrotados = resolver(
            orden,
            [aventurero_1, aventurero_2],
            [enemigo],
            RandomControlado(
                tiradas=[6, 6, 6],
                elecciones=[0, 0, 0],
            ),
        )

        self.assertEqual(derrotados, [])
        self.assertEqual(enemigo["vida_actual"], 94)
        self.assertEqual(aventurero_1["vida_actual"], 18)
        self.assertEqual(aventurero_2["vida_actual"], 20)

    def test_derrotado_antes_de_su_posicion_pierde_el_turno(self) -> None:
        resolver = _operacion("resolver_ronda")
        aventurero: AventureroCombate = _estado_aventurero(
            estrategia="menor_vida_actual"
        )
        enemigo_1: EnemigoCombate = _estado_enemigo(
            identificador="LIMOS_LIMO-01",
            vida_actual=5,
        )
        enemigo_2: EnemigoCombate = _estado_enemigo(
            identificador="LIMOS_LIMO-02"
        )
        orden: list[ParticipanteTurno] = [
            _turno_aventurero(aventurero),
            _turno_enemigo(enemigo_1),
            _turno_enemigo(enemigo_2),
        ]

        derrotados = resolver(
            orden,
            [aventurero],
            [enemigo_1, enemigo_2],
            RandomControlado(tiradas=[6, 6], elecciones=[0]),
        )

        self.assertEqual(derrotados, ["LIMOS_LIMO-01"])
        self.assertEqual(aventurero["vida_actual"], 16)
        self.assertFalse(enemigo_1["esta_vivo"])

    def test_ronda_se_detiene_cuando_un_bando_queda_sin_vivos(self) -> None:
        resolver = _operacion("resolver_ronda")
        aventurero_1: AventureroCombate = _estado_aventurero(
            identificador="AV-0001"
        )
        aventurero_2: AventureroCombate = _estado_aventurero(
            identificador="AV-0002"
        )
        enemigo: EnemigoCombate = _estado_enemigo(vida_actual=5)
        generador = RandomControlado(tiradas=[6], elecciones=[0])
        orden: list[ParticipanteTurno] = [
            _turno_aventurero(aventurero_1),
            _turno_aventurero(aventurero_2),
            _turno_enemigo(enemigo),
        ]

        derrotados = resolver(
            orden,
            [aventurero_1, aventurero_2],
            [enemigo],
            generador,
        )

        self.assertEqual(derrotados, ["LIMOS_LIMO-01"])
        self.assertEqual(generador.tiradas, [])
        self.assertEqual(generador.elecciones, [])

    def test_devuelve_enemigos_en_orden_de_derrota(self) -> None:
        resolver = _operacion("resolver_ronda")
        aventurero_1: AventureroCombate = _estado_aventurero(
            identificador="AV-0001",
            estrategia="menor_vida_actual",
        )
        aventurero_2: AventureroCombate = _estado_aventurero(
            identificador="AV-0002",
            estrategia="menor_vida_actual",
        )
        enemigo_1: EnemigoCombate = _estado_enemigo(
            identificador="LIMOS_LIMO-01",
            vida_actual=4,
        )
        enemigo_2: EnemigoCombate = _estado_enemigo(
            identificador="LIMOS_LIMO-02",
            vida_actual=5,
        )
        orden: list[ParticipanteTurno] = [
            _turno_aventurero(aventurero_1),
            _turno_aventurero(aventurero_2),
            _turno_enemigo(enemigo_1),
            _turno_enemigo(enemigo_2),
        ]

        derrotados = resolver(
            orden,
            [aventurero_1, aventurero_2],
            [enemigo_1, enemigo_2],
            RandomControlado(tiradas=[6, 6]),
        )

        self.assertEqual(
            derrotados,
            ["LIMOS_LIMO-01", "LIMOS_LIMO-02"],
        )

    def test_muerto_previo_no_actua_ni_puede_ser_objetivo(self) -> None:
        resolver = _operacion("resolver_ronda")
        muerto: AventureroCombate = _estado_aventurero(
            identificador="AV-0001",
            vida_actual=0,
            esta_vivo=False,
        )
        vivo: AventureroCombate = _estado_aventurero(
            identificador="AV-0002"
        )
        vivo["dano"] = 0
        enemigo: EnemigoCombate = _estado_enemigo()
        orden: list[ParticipanteTurno] = [
            _turno_aventurero(muerto),
            _turno_aventurero(vivo),
            _turno_enemigo(enemigo),
        ]

        derrotados = resolver(
            orden,
            [muerto, vivo],
            [enemigo],
            RandomControlado(tiradas=[6, 6], elecciones=[0, 0]),
        )

        self.assertEqual(derrotados, [])
        self.assertEqual(muerto["vida_actual"], 0)
        self.assertEqual(vivo["vida_actual"], 16)
        self.assertEqual(enemigo["vida_actual"], 19)


if __name__ == "__main__":
    unittest.main()
