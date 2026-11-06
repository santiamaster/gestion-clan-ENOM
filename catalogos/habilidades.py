"""Catálogo permanente de las quince habilidades profesionales."""

from modelos.tipos import (
    Habilidad,
    HabilidadCuracionGrupal,
    HabilidadCuracionIndividual,
    HabilidadDanoArea,
    HabilidadDanoUnico,
    HabilidadDanoVidaFaltante,
    HabilidadEscudo,
    HabilidadMuerteInstantanea,
    HabilidadMultigolpe,
    HabilidadProteccion,
    HabilidadProvocacion,
)


EXPLOSION_ARCANA: HabilidadDanoArea = {
    "id": "HAB_EXPLOSION_ARCANA",
    "nombre": "Explosión Arcana",
    "profesion": "Mago Arcano",
    "tipo": "dano_area",
    "enfriamiento": 6,
    "descripcion": "Daña a todos los enemigos vivos con una explosión mágica.",
    "estrategia_objetivo": "todos_los_enemigos",
    "multiplicador_dano": 2.50,
    "maximo_objetivos": None,
    "tiradas_individuales": False,
}

RAYO: HabilidadDanoUnico = {
    "id": "HAB_RAYO",
    "nombre": "Rayo",
    "profesion": "Hechicero",
    "tipo": "dano_unico",
    "enfriamiento": 3,
    "descripcion": "Ataca con un rayo al enemigo que tenga mayor vida actual.",
    "estrategia_objetivo": "mayor_vida_actual",
    "multiplicador_dano": 1.50,
}

MULTIDISPAROS: HabilidadMultigolpe = {
    "id": "HAB_MULTIDISPAROS",
    "nombre": "Multidisparos",
    "profesion": "Arquero",
    "tipo": "multigolpe",
    "enfriamiento": 2,
    "descripcion": "Realiza dos disparos consecutivos contra el mismo enemigo.",
    "estrategia_objetivo": "aleatorio",
    "cantidad_golpes": 2,
    "multiplicador_por_golpe": 1.00,
    "tiradas_individuales": True,
}

CAOS_LIBERADO: HabilidadMultigolpe = {
    "id": "HAB_CAOS_LIBERADO",
    "nombre": "Caos liberado",
    "profesion": "Ninja",
    "tipo": "multigolpe",
    "enfriamiento": 3,
    "descripcion": "Realiza tres ataques potenciados contra un mismo enemigo.",
    "estrategia_objetivo": "mayor_vida_actual",
    "cantidad_golpes": 3,
    "multiplicador_por_golpe": 1.20,
    "tiradas_individuales": True,
}

COMPARTIR_DOLOR: HabilidadDanoVidaFaltante = {
    "id": "HAB_COMPARTIR_DOLOR",
    "nombre": "Compartir el dolor",
    "profesion": "Bárbaro",
    "tipo": "dano_vida_faltante",
    "enfriamiento": 3,
    "descripcion": "Agrega al daño la vida faltante del Bárbaro.",
    "estrategia_objetivo": "aleatorio",
    "porcentaje_curacion_al_matar": 0.50,
}

PROVOCAR: HabilidadProvocacion = {
    "id": "HAB_PROVOCAR",
    "nombre": "Provocar",
    "profesion": "Defensor",
    "tipo": "provocacion",
    "enfriamiento": 3,
    "descripcion": "Obliga a cada enemigo a dirigir su siguiente ataque al Defensor.",
    "estrategia_objetivo": "todos_los_enemigos",
    "duracion": "un_ataque_por_enemigo",
    "requiere_tirada": True,
}

GOLPE_TEMBLOR: HabilidadDanoArea = {
    "id": "HAB_GOLPE_TEMBLOR",
    "nombre": "Golpe temblor",
    "profesion": "Alabardero",
    "tipo": "dano_area",
    "enfriamiento": 4,
    "descripcion": "Golpea con la alabarda a todos los enemigos vivos.",
    "estrategia_objetivo": "todos_los_enemigos",
    "multiplicador_dano": 1.50,
    "maximo_objetivos": None,
    "tiradas_individuales": False,
}

FLECHA_PESADA: HabilidadDanoArea = {
    "id": "HAB_FLECHA_PESADA",
    "nombre": "Flecha pesada",
    "profesion": "Cazador",
    "tipo": "dano_area",
    "enfriamiento": 3,
    "descripcion": "Dispara una flecha que puede alcanzar hasta tres enemigos.",
    "estrategia_objetivo": "hasta_tres_enemigos",
    "multiplicador_dano": 1.30,
    "maximo_objetivos": 3,
    "tiradas_individuales": True,
}

GRAN_CURA: HabilidadCuracionIndividual = {
    "id": "HAB_GRAN_CURA",
    "nombre": "Gran Cura",
    "profesion": "Curador",
    "tipo": "curacion_individual",
    "enfriamiento": 4,
    "descripcion": "Cura un 30% de la vida máxima del aliado más herido.",
    "estrategia_objetivo": "menor_porcentaje_vida",
    "porcentaje_vida_maxima": 0.30,
    "puede_elegirse_a_si_mismo": True,
}

MUERTE: HabilidadMuerteInstantanea = {
    "id": "HAB_MUERTE",
    "nombre": "Muerte",
    "profesion": "Asesino",
    "tipo": "muerte_instantanea",
    "enfriamiento": 6,
    "descripcion": "Intenta causar muerte instantánea; si falla, no causa daño.",
    "estrategia_objetivo": "mayor_vida_actual",
    "probabilidad_normal": 30,
    "probabilidad_jefe": 5,
}

GOLPE_POTENCIADO: HabilidadDanoUnico = {
    "id": "HAB_GOLPE_POTENCIADO",
    "nombre": "Golpe potenciado",
    "profesion": "Soldado",
    "tipo": "dano_unico",
    "enfriamiento": 2,
    "descripcion": "Ataca al enemigo con menor vida actual.",
    "estrategia_objetivo": "menor_vida_actual",
    "multiplicador_dano": 1.20,
}

ESCUDO_MENTAL: HabilidadEscudo = {
    "id": "HAB_ESCUDO_MENTAL",
    "nombre": "Escudo mental",
    "profesion": "Psíquico",
    "tipo": "escudo",
    "enfriamiento": 4,
    "descripcion": "Reduce el daño recibido por un aliado hasta el siguiente turno.",
    "estrategia_objetivo": "menor_porcentaje_vida",
    "reduccion_dano": 0.30,
    "puede_elegirse_a_si_mismo": True,
    "duracion": "hasta_siguiente_turno_usuario",
}

BOLA_OSCURA: HabilidadDanoUnico = {
    "id": "HAB_BOLA_OSCURA",
    "nombre": "Bola oscura",
    "profesion": "Infernal",
    "tipo": "dano_unico",
    "enfriamiento": 4,
    "descripcion": "Dispara una esfera de magia oscura contra un enemigo.",
    "estrategia_objetivo": "aleatorio",
    "multiplicador_dano": 2.00,
}

FUENTE_DE_VIDA: HabilidadCuracionGrupal = {
    "id": "HAB_FUENTE_DE_VIDA",
    "nombre": "Fuente de vida",
    "profesion": "Conjurador de Mareas",
    "tipo": "curacion_grupal",
    "enfriamiento": 5,
    "descripcion": "Cura un 20% de la vida máxima de todo el grupo.",
    "estrategia_objetivo": "todos_los_aliados",
    "porcentaje_vida_maxima": 0.20,
    "incluye_usuario": True,
}

PROTEGER: HabilidadProteccion = {
    "id": "HAB_PROTEGER",
    "nombre": "Proteger",
    "profesion": "Paladín",
    "tipo": "proteccion",
    "enfriamiento": 5,
    "descripcion": "Redirige al Paladín los ataques destinados a un aliado.",
    "estrategia_objetivo": "menor_porcentaje_vida",
    "duracion": "hasta_siguiente_turno_usuario",
}


CATALOGO_HABILIDADES: dict[str, Habilidad] = {
    habilidad["id"]: habilidad
    for habilidad in (
        EXPLOSION_ARCANA,
        RAYO,
        MULTIDISPAROS,
        CAOS_LIBERADO,
        COMPARTIR_DOLOR,
        PROVOCAR,
        GOLPE_TEMBLOR,
        FLECHA_PESADA,
        GRAN_CURA,
        MUERTE,
        GOLPE_POTENCIADO,
        ESCUDO_MENTAL,
        BOLA_OSCURA,
        FUENTE_DE_VIDA,
        PROTEGER,
    )
}

