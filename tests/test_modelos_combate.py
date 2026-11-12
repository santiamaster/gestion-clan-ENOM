"""Pruebas de los tipos compartidos por el motor de combate."""

import unittest
from typing import get_args, get_type_hints

import modelos.combate as combate


def _tipo(nombre: str) -> object:
    """Obtiene un tipo público y falla claramente si todavía no existe."""

    tipo: object | None = getattr(combate, nombre, None)
    if tipo is None:
        raise AssertionError(f"Falta definir el tipo público {nombre}.")
    return tipo


class PruebasAliasCombate(unittest.TestCase):
    """Fija los valores admitidos por los resultados del combate."""

    def test_resultado_tirada_solo_admite_tres_resultados(self) -> None:
        resultado_tirada: object = _tipo("ResultadoTirada")

        self.assertEqual(
            get_args(resultado_tirada),
            ("fallo", "impacto", "critico"),
        )

    def test_resultado_combate_admite_las_tres_finalizaciones(self) -> None:
        resultado_combate: object = _tipo("ResultadoCombate")

        self.assertEqual(
            get_args(resultado_combate),
            ("victoria", "derrota", "limite_de_rondas"),
        )


class PruebasDefinicionesPermanentes(unittest.TestCase):
    """Comprueba los contratos de enemigos, oleadas y mazmorras."""

    def test_plantilla_enemigo_contiene_todos_los_datos_del_catalogo(
        self,
    ) -> None:
        plantilla_enemigo: object = _tipo("PlantillaEnemigo")

        self.assertEqual(
            set(get_type_hints(plantilla_enemigo)),
            {
                "id",
                "nombre",
                "estadisticas",
                "tipo_ataque",
                "efectividades",
                "experiencia",
                "dinero",
                "es_jefe",
                "imagen",
                "descripcion",
            },
        )

    def test_definiciones_de_oleada_y_mazmorra_tienen_claves_estables(
        self,
    ) -> None:
        grupo: object = _tipo("GrupoEnemigosOleada")
        oleada: object = _tipo("DefinicionOleada")
        mazmorra: object = _tipo("DefinicionMazmorra")

        self.assertEqual(
            set(get_type_hints(grupo)),
            {"plantilla_id", "cantidad"},
        )
        self.assertEqual(
            set(get_type_hints(oleada)),
            {"numero", "enemigos"},
        )
        self.assertEqual(
            set(get_type_hints(mazmorra)),
            {"id", "nombre", "dificultad", "oleadas"},
        )


class PruebasEstadosTemporales(unittest.TestCase):
    """Fija la información mutable que existe durante una oleada."""

    def test_combatiente_base_reune_los_campos_compartidos(self) -> None:
        combatiente_base: object = _tipo("CombatienteBase")

        self.assertEqual(
            set(get_type_hints(combatiente_base)),
            {
                "nombre",
                "vida_maxima",
                "vida_actual",
                "dano",
                "defensa",
                "velocidad",
                "probabilidad_critica",
                "esta_vivo",
            },
        )

    def test_estados_especializados_conservan_campos_compartidos_y_propios(
        self,
    ) -> None:
        aventurero: object = _tipo("AventureroCombate")
        enemigo: object = _tipo("EnemigoCombate")

        self.assertEqual(
            set(get_type_hints(aventurero)),
            {
                "nombre",
                "vida_maxima",
                "vida_actual",
                "dano",
                "defensa",
                "velocidad",
                "probabilidad_critica",
                "esta_vivo",
                "id",
                "plantilla_id",
                "tipo_ataque",
                "estrategia_objetivo",
            },
        )
        self.assertEqual(
            set(get_type_hints(enemigo)),
            {
                "nombre",
                "vida_maxima",
                "vida_actual",
                "dano",
                "defensa",
                "velocidad",
                "probabilidad_critica",
                "esta_vivo",
                "id_instancia",
                "plantilla_id",
                "tipo_ataque",
                "efectividades",
                "experiencia",
                "dinero",
                "es_jefe",
            },
        )

    def test_participante_turno_es_una_union_discriminada(self) -> None:
        participante: object = _tipo("ParticipanteTurno")
        turno_aventurero: object = _tipo("TurnoAventurero")
        turno_enemigo: object = _tipo("TurnoEnemigo")

        self.assertEqual(
            set(get_args(participante)),
            {turno_aventurero, turno_enemigo},
        )
        self.assertEqual(
            set(get_type_hints(turno_aventurero)),
            {"bando", "combatiente"},
        )
        self.assertEqual(
            set(get_type_hints(turno_enemigo)),
            {"bando", "combatiente"},
        )


class PruebasResultadosTemporales(unittest.TestCase):
    """Comprueba los datos devueltos sin crear un historial de ataques."""

    def test_resultado_ataque_contiene_solo_el_efecto_inmediato(self) -> None:
        resultado_ataque: object = _tipo("ResultadoAtaque")

        self.assertEqual(
            set(get_type_hints(resultado_ataque)),
            {
                "resultado",
                "dano_aplicado",
                "vida_restante",
                "objetivo_derrotado",
            },
        )

    def test_resultado_oleada_contiene_resumen_y_recompensas(self) -> None:
        resultado_oleada: object = _tipo("ResultadoOleada")

        self.assertEqual(
            set(get_type_hints(resultado_oleada)),
            {
                "resultado",
                "rondas",
                "aventureros",
                "enemigos",
                "enemigos_derrotados",
                "experiencia_obtenida",
                "dinero_obtenido",
            },
        )


if __name__ == "__main__":
    unittest.main()
