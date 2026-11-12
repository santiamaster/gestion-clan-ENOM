# Presentación preliminar del proyecto ENOM — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear una presentación editable de 15 diapositivas que permita explicar en veinte minutos el juego Gestión de Clan ENOM, sus mecánicas, su arquitectura técnica y su estado actual.

**Architecture:** La presentación se construirá como un archivo PPTX 16:9 mediante JavaScript y `@oai/artifact-tool`. El contenido se obtendrá únicamente del repositorio; las ilustraciones atmosféricas serán conceptuales y no representarán pantallas terminadas. Cada bloque se renderizará y revisará visualmente antes de continuar.

**Tech Stack:** JavaScript ES Modules, `@oai/artifact-tool`, generación de imágenes, PowerPoint/PPTX, renderizado de diapositivas y validación visual.

**Spec:** `docs/superpowers/specs/2026-11-11-presentacion-proyecto-enom-design.md`

## Global Constraints

- La presentación tendrá exactamente 15 diapositivas en relación 16:9.
- La exposición está dirigida al profesor de Programación II y dura alrededor de veinte minutos.
- El contenido del juego ocupará aproximadamente quince minutos y la parte técnica cinco minutos.
- Se utilizará un mínimo orientativo de 42 puntos para la portada, 32 para títulos y 17 para cuerpo.
- Las notas del presentador ampliarán el contenido sin convertirse en un discurso rígido.
- Los diagramas y tablas que expresen relaciones exactas permanecerán editables.
- Las ilustraciones atmosféricas no se presentarán como capturas de una interfaz terminada.
- Toda función futura deberá aparecer identificada como planificada o pendiente.
- No se inventarán enemigos, recompensas, estadísticas o reglas ausentes del repositorio.
- La presentación final se guardará de forma persistente y se entregará como archivo PPTX.

## Review Focus

- Las quince combinaciones de raza y profesión deben aparecer exactamente una vez y conservar su ortografía canónica: Task 3 verificará la lista contra `catalogos/plantillas.py`.
- Las diapositivas deben diferenciar lo implementado de lo planificado para no inducir al profesor a creer que existe una versión jugable: Tasks 2, 4 y 5 revisarán títulos, cuerpo y notas.
- Los textos largos, especialmente arquetipos y estado actual, no deben desbordar ni reducirse por debajo de 17 puntos: Tasks 3–5 inspeccionarán los renders.
- Los diagramas del ciclo y la arquitectura deben seguir siendo legibles al proyectarse y conservar objetos editables: Tasks 2 y 4 validarán ambos artefactos.
- Las notas deben sostener una exposición aproximada de veinte minutos sin repetir literalmente las diapositivas: Task 5 comprobará cobertura, transición y tiempo orientativo.

---

## Estructura de trabajo

- Crear temporalmente: `/workspace/scratch/bffce8f7b423/presentacion_enom/crear_presentacion.mjs` — construcción completa del PPTX.
- Crear temporalmente: `/workspace/scratch/bffce8f7b423/presentacion_enom/assets/` — ilustraciones conceptuales y recursos visuales.
- Crear temporalmente: `/workspace/scratch/bffce8f7b423/presentacion_enom/render/` — imágenes de revisión de las diapositivas.
- Crear: `/workspace/scratch/bffce8f7b423/presentacion_enom/Gestion_Clan_ENOM_presentacion.pptx` — archivo final verificable.
- Modificar: `docs/superpowers/specs/2026-11-11-presentacion-proyecto-enom-design.md` solo si durante la ejecución aparece una contradicción factual.

### Task 1: Preparar contenido y dirección visual

**Files:**
- Read: `README.md`
- Read: `documentacion/reglas_definidas.md`
- Read: `documentacion/estructura.md`
- Read: `catalogos/plantillas.py`
- Read: `catalogos/habilidades.py`
- Create: `/workspace/scratch/bffce8f7b423/presentacion_enom/assets/`

**Interfaces:**
- Consumes: contenido canónico y guion definido por la especificación.
- Produces: inventario factual, textos finales y recursos visuales para Tasks 2–4.

- [ ] **Step 1: Crear el inventario factual de la presentación**

Registrar en el script los nombres canónicos de las quince razas, profesiones y cinco habilidades representativas. Conservar tildes, apóstrofos tipográficos y mayúsculas.

- [ ] **Step 2: Redactar el texto final de las 15 diapositivas y sus notas**

Limitar el cuerpo visible a las ideas necesarias. Las notas deben indicar objetivo, explicación sugerida, transición y estado implementado o planificado cuando corresponda.

- [ ] **Step 3: Generar las ilustraciones conceptuales**

Crear imágenes panorámicas sin texto para portada, ciudad y mazmorra. Mantener una estética de fantasía oscura con luz dorada y acentos turquesa. La ciudad debe admitir etiquetas superpuestas sin parecer una captura de Tkinter.

- [ ] **Step 4: Verificar los recursos**

Comprobar relación de aspecto, resolución suficiente, ausencia de texto generado y coherencia visual entre las imágenes.

Expected: tres ilustraciones utilizables y contenido factual trazable al repositorio.

### Task 2: Construir la base visual y las diapositivas 1–5

**Files:**
- Create: `/workspace/scratch/bffce8f7b423/presentacion_enom/crear_presentacion.mjs`
- Create: `/workspace/scratch/bffce8f7b423/presentacion_enom/Gestion_Clan_ENOM_presentacion.pptx`
- Create: `/workspace/scratch/bffce8f7b423/presentacion_enom/render/`

**Interfaces:**
- Consumes: textos e ilustraciones de Task 1.
- Produces: tema reutilizable, portada, propuesta, objetivo, ciudad y ciclo de juego para Tasks 3–4.

- [ ] **Step 1: Leer la documentación instalada de Artifact Tool**

Leer `API_QUICK_START.md`, `api/API_DOCS.md`, referencias de texto, imágenes, tablas, diagramas y notas del presentador desde la instalación activa de `@oai/artifact-tool`.

- [ ] **Step 2: Crear el tema 16:9**

Definir fondos oscuros, acentos dorados y turquesa, tipografías legibles, márgenes consistentes y funciones auxiliares reutilizables. No simular paneles de interfaz.

- [ ] **Step 3: Construir las diapositivas 1–4**

Crear portada, propuesta, objetivo y ciudad. La diapositiva de ciudad debe identificar edificio del clan, gremio, iglesia y acceso a mazmorras mediante objetos editables sobre la ilustración.

- [ ] **Step 4: Construir la diapositiva 5**

Crear el ciclo principal mediante un diagrama circular editable con seis etapas y una lectura clara en el sentido de avance.

- [ ] **Step 5: Renderizar y revisar las diapositivas 1–5**

Expected: sin desbordes, contraste suficiente, ciclo legible y ninguna ilustración presentada como interfaz funcional.

### Task 3: Construir progresión, arquetipos, habilidades y reclutamiento

**Files:**
- Modify: `/workspace/scratch/bffce8f7b423/presentacion_enom/crear_presentacion.mjs`
- Modify: `/workspace/scratch/bffce8f7b423/presentacion_enom/Gestion_Clan_ENOM_presentacion.pptx`
- Modify: `/workspace/scratch/bffce8f7b423/presentacion_enom/render/`

**Interfaces:**
- Consumes: tema y auxiliares de Task 2; inventario factual de Task 1.
- Produces: diapositivas 6–10 para el relato completo.

- [ ] **Step 1: Construir la diapositiva 6**

Crear una tabla editable con los cinco niveles, cupos `5, 10, 15, 20, 25` y máximos de grupo `3, 4, 5, 6, 7`.

- [ ] **Step 2: Construir la diapositiva 7**

Explicar niveles 1–10, cuatro estadísticas, fórmula de crecimiento, experiencia y bono de nivel 10 sin mostrar estadísticas individuales.

- [ ] **Step 3: Construir la diapositiva 8**

Distribuir las quince combinaciones en tres columnas por función expositiva. Verificar mediante una lista literal que cada raza y profesión canónica aparezca exactamente una vez.

- [ ] **Step 4: Construir las diapositivas 9 y 10**

Mostrar cinco habilidades representativas y explicar el reclutamiento mediante una relación editable entre ofertas, dinero, cupo y decisión de contratación.

- [ ] **Step 5: Renderizar y revisar las diapositivas 6–10**

Expected: texto mínimo de 17 puntos, las quince combinaciones completas, tabla legible y ningún dato numérico inventado.

### Task 4: Construir expediciones, combate, consecuencias y arquitectura

**Files:**
- Modify: `/workspace/scratch/bffce8f7b423/presentacion_enom/crear_presentacion.mjs`
- Modify: `/workspace/scratch/bffce8f7b423/presentacion_enom/Gestion_Clan_ENOM_presentacion.pptx`
- Modify: `/workspace/scratch/bffce8f7b423/presentacion_enom/render/`

**Interfaces:**
- Consumes: tema de Task 2 y contenido verificado de Task 1.
- Produces: diapositivas 11–15 y presentación completa para Task 5.

- [ ] **Step 1: Construir las diapositivas 11 y 12**

Crear la explicación de mazmorras y un diagrama secuencial editable del combate. Identificar explícitamente que enemigos y oleadas definitivos están en balanceo.

- [ ] **Step 2: Construir la diapositiva 13**

Contrastar retirada con derrota total y explicar botín, experiencia, cuerpos recuperados, resurrección y entierro.

- [ ] **Step 3: Construir la diapositiva 14**

Crear un diagrama editable de interfaz, servicios, modelos tipados y JSON. Añadir Python 3.11+, Tkinter y `unittest` sin mostrar código extenso.

- [ ] **Step 4: Construir la diapositiva 15**

Separar visualmente lo implementado de los próximos bloques. Incluir la cifra verificada de 127 pruebas con fecha 11 de noviembre de 2026.

- [ ] **Step 5: Renderizar y revisar las diapositivas 11–15**

Expected: arquitectura legible, funciones futuras diferenciadas y cierre que no afirme que el juego ya es ejecutable.

### Task 5: Validar, corregir y entregar la presentación

**Files:**
- Modify: `/workspace/scratch/bffce8f7b423/presentacion_enom/crear_presentacion.mjs`
- Modify: `/workspace/scratch/bffce8f7b423/presentacion_enom/Gestion_Clan_ENOM_presentacion.pptx`
- Read: `/workspace/scratch/bffce8f7b423/presentacion_enom/render/`

**Interfaces:**
- Consumes: presentación completa de Tasks 2–4.
- Produces: PPTX final persistente y listo para la exposición preliminar.

- [ ] **Step 1: Renderizar las 15 diapositivas**

Generar vistas previas de todas las diapositivas y una lámina de contacto para revisar ritmo, consistencia y variedad visual.

- [ ] **Step 2: Ejecutar las validaciones automáticas**

Comprobar cantidad exacta de diapositivas, integridad del PPTX, fuentes, objetos fuera del lienzo, solapamientos y texto desbordado.

Expected: 15 diapositivas válidas y sin advertencias que afecten legibilidad.

- [ ] **Step 3: Realizar la revisión visual manual**

Inspeccionar cada render en tamaño de proyección. Corregir contraste, jerarquía, alineación, densidad y recortes de imágenes.

- [ ] **Step 4: Revisar contenido y notas**

Confirmar las quince combinaciones, reglas numéricas, estado implementado o planificado y cobertura oral aproximada de veinte minutos.

- [ ] **Step 5: Guardar la presentación final de forma persistente**

Subir `Gestion_Clan_ENOM_presentacion.pptx` y conservar una versión descargable para futuras modificaciones.

- [ ] **Step 6: Entregar**

Presentar el enlace al archivo final y aclarar únicamente cualquier limitación visual pendiente por falta de las imágenes definitivas del usuario.

## Verificación final

Run: renderizado completo y validación de Artifact Tool según `references/finalization.md`.

Expected:

- 15 diapositivas en 16:9.
- Sin desbordes, solapamientos o imágenes deformadas.
- Texto visible mínimo de 17 puntos.
- Notas del presentador presentes en las 15 diapositivas.
- Quince razas y profesiones exactamente una vez.
- Diapositivas 11 y 15 identifican claramente los elementos pendientes.
- PPTX disponible de forma persistente.
