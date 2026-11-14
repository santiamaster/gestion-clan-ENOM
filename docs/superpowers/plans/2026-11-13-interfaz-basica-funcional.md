# Interfaz básica funcional — Plan de implementación

> **For agentic workers:** Execute this plan task by task. Use test-driven development, run the focused verification after every behavioral change, and do not continue when a test or type check introduced by the current task is failing.

**Goal:** Incorporar una interfaz Tkinter simple y funcional que permita crear o continuar una partida, administrar el clan y completar la Mazmorra de los Limos usando los servicios de dominio ya implementados.

**Architecture:** Una única instancia de `tk.Tk` contiene una pantalla `ttk.Frame` intercambiable. `AplicacionClan` coordina navegación, sesión, persistencia y servicios; las pantallas solo capturan acciones y presentan resultados. Las reglas existentes permanecen en `servicios/`, y toda operación administrativa persistente se publica en memoria únicamente después de guardar correctamente copias de los datos.

**Tech Stack:** Python 3.15, Tkinter/ttk, `dataclass`, `TypedDict`, `unittest`, Pyright y JSON mediante la persistencia existente.

**Spec:** `docs/superpowers/specs/2026-11-13-interfaz-basica-funcional-design.md`

## Restricciones globales

- No introducir imágenes, habilidades, sonidos, animaciones ni las mazmorras 2 a 5.
- No duplicar reglas de dominio dentro de `interfaz/`.
- No crear más de una instancia de `tk.Tk`; los avisos y confirmaciones usan `messagebox`.
- No guardar una expedición a mitad de recorrido. Solo se persisten las consecuencias al cerrarla.
- Conservar anotaciones estrictas y documentación interna en funciones, clases y contratos nuevos.
- Mantener los callbacks pequeños y bloquear botones mientras se ejecuta una acción para impedir dobles operaciones.
- Las pruebas automáticas no crean ventanas reales: verifican modelos de presentación y coordinación con dobles o directorios temporales.
- Antes de cerrar cada tramo, ejecutar sus pruebas enfocadas, la suite completa y Pyright sobre los archivos modificados.

## Foco de revisión

1. Una partida incompleta o inválida nunca se elimina sin confirmación explícita; queda fijado por `test_diagnosticar_partida_invalida_no_modifica_archivos` del tramo 2.
2. Si falla el guardado de una operación administrativa, memoria y JSON conservan el estado anterior; queda fijado por `test_aplicar_cambio_y_guardar_no_publica_si_falla_el_guardado` del tramo 1.
3. Una partida ya terminada no vuelve a entrar a la ciudad al cargarse; queda fijado por `test_determinar_destino_carga_finalizada_vuelve_al_inicio` del tramo 2.
4. Cerrar la ventana durante una expedición requiere confirmación; queda fijado por `test_requiere_confirmacion_de_salida_durante_expedicion` del tramo 3.
5. Un fallo al persistir el cierre de una expedición conserva el estado temporal para reintentar sin duplicar recompensas; queda fijado por `test_cierre_fallido_conserva_expedicion_para_reintentar` del tramo 6.

---

## Tramo 1: sesión y transacciones administrativas

**Archivos:**

- Modificar: `interfaz/aplicacion.py`
- Crear: `tests/test_interfaz_aplicacion.py`

### Paso 1: escribir las pruebas fallidas de la sesión

Agregar casos para comprobar:

- `EstadoSesion()` comienza sin partida ni expedición.
- `EstadoSesion.requerir_partida()` devuelve las tres estructuras cuando están cargadas.
- `requerir_partida()` falla con un error claro cuando no existe partida activa.
- `aplicar_cambio_y_guardar()` trabaja sobre copias, persiste y recién entonces publica los cambios.
- Si la operación de dominio falla, no se llama al guardado ni se modifica la sesión.
- Si el guardado falla, no se publican las copias modificadas.

El contrato esperado es:

```python
@dataclass(slots=True)
class EstadoSesion:
    estado_clan: EstadoClan | None = None
    datos_activos: list[AventureroActivo] = field(default_factory=list)
    datos_eliminados: list[AventureroEliminado] = field(default_factory=list)
    expedicion: EstadoExpedicion | None = None

    def requerir_partida(
        self,
    ) -> tuple[
        EstadoClan,
        list[AventureroActivo],
        list[AventureroEliminado],
    ]:
        ...


ResultadoOperacion = TypeVar("ResultadoOperacion")
OperacionPersistente = Callable[
    [EstadoClan, list[AventureroActivo], list[AventureroEliminado]],
    ResultadoOperacion,
]


def aplicar_cambio_y_guardar(
    sesion: EstadoSesion,
    operacion: OperacionPersistente[ResultadoOperacion],
    directorio: Path = DIRECTORIO_PARTIDA,
) -> ResultadoOperacion:
    ...
```

### Paso 2: ejecutar las pruebas y comprobar el fallo esperado

Ejecutar:

```bash
python -m unittest tests.test_interfaz_aplicacion -v
```

Resultado esperado: errores de importación porque los contratos todavía no existen.

### Paso 3: implementar la sesión y la transacción

En `interfaz/aplicacion.py`:

- Definir `PartidaNoCargadaError`.
- Implementar `EstadoSesion`.
- Implementar `aplicar_cambio_y_guardar()` con `deepcopy`.
- Invocar `guardar_partida()` sobre las copias.
- Publicar las copias en la sesión solo después del guardado exitoso.
- No capturar ni transformar excepciones en esta capa; las pantallas decidirán el mensaje visual.

### Paso 4: verificar el tramo

```bash
python -m unittest tests.test_interfaz_aplicacion -v
python -m unittest discover -s tests -v
pyright interfaz/aplicacion.py tests/test_interfaz_aplicacion.py
```

### Paso 5: commit

```bash
git add interfaz/aplicacion.py tests/test_interfaz_aplicacion.py
git commit -m "feat: agregar sesión transaccional de interfaz"
```

---

## Tramo 2: diagnóstico, creación y carga de partidas

**Archivos:**

- Modificar: `interfaz/aplicacion.py`
- Modificar: `interfaz/inicio.py`
- Modificar: `tests/test_interfaz_aplicacion.py`
- Crear: `tests/test_interfaz_inicio.py`

### Paso 1: escribir pruebas para las decisiones de inicio

Definir y probar estos contratos puros:

```python
EstadoDiagnosticoPartida: TypeAlias = Literal[
    "ausente",
    "valida",
    "incompleta",
    "invalida",
]


@dataclass(frozen=True, slots=True)
class DiagnosticoPartida:
    estado: EstadoDiagnosticoPartida
    mensaje: str | None = None


DestinoCarga: TypeAlias = Literal["ciudad", "inicio_finalizada"]


def diagnosticar_partida(
    directorio: Path = DIRECTORIO_PARTIDA,
) -> DiagnosticoPartida:
    ...


def determinar_destino_carga(estado_clan: EstadoClan) -> DestinoCarga:
    ...
```

Cubrir ausencia total, partida válida, presencia parcial, JSON inválido y partida con `estado_partida` igual a `victoria` o `derrota`. Verificar expresamente que diagnosticar nunca elimina archivos.

### Paso 2: ejecutar las pruebas fallidas

```bash
python -m unittest tests.test_interfaz_aplicacion tests.test_interfaz_inicio -v
```

### Paso 3: implementar diagnóstico y operaciones de inicio

En `AplicacionClan`, añadir métodos coordinadores sin lógica visual:

```python
def crear_partida(self, nombre: str, sobrescribir: bool) -> None: ...
def cargar_partida_existente(self) -> DestinoCarga: ...
def eliminar_guardado_conocido(self) -> None: ...
```

Reglas:

- `crear_partida()` usa `crear_nueva_partida()` y reemplaza toda la sesión.
- `cargar_partida_existente()` usa `cargar_partida()` y deja `expedicion` en `None`.
- `eliminar_guardado_conocido()` delega en `eliminar_partida()`; la confirmación pertenece a la pantalla.
- Una partida terminada se carga solo para mostrar su desenlace y luego permanece en inicio.

### Paso 4: crear `PantallaInicio`

La pantalla incluye:

- entrada para el nombre del clan;
- botones `Nueva partida`, `Continuar` y `Salir`;
- `Continuar` deshabilitado si el diagnóstico es `ausente`;
- confirmación antes de sobrescribir una partida válida;
- confirmación específica antes de eliminar los tres JSON conocidos si el guardado está incompleto o inválido;
- mensajes amigables para `ErrorPersistencia` y validaciones de nombre;
- bloqueo temporal del botón ejecutado hasta finalizar el callback.

No abrir la ciudad directamente desde esta clase: llamar siempre al método de navegación de `AplicacionClan`.

### Paso 5: verificar el tramo

```bash
python -m unittest tests.test_interfaz_aplicacion tests.test_interfaz_inicio -v
python -m unittest discover -s tests -v
pyright interfaz/aplicacion.py interfaz/inicio.py tests/test_interfaz_aplicacion.py tests/test_interfaz_inicio.py
```

### Paso 6: commit

```bash
git add interfaz/aplicacion.py interfaz/inicio.py tests/test_interfaz_aplicacion.py tests/test_interfaz_inicio.py
git commit -m "feat: agregar inicio y carga segura de partidas"
```

---

## Tramo 3: contenedor Tkinter y pantalla de ciudad

**Archivos:**

- Modificar: `interfaz/aplicacion.py`
- Modificar: `interfaz/componentes.py`
- Modificar: `interfaz/ciudad.py`
- Modificar: `main.py`
- Crear: `tests/test_interfaz_componentes.py`
- Crear: `tests/test_main.py`

### Paso 1: escribir pruebas de presentación y arranque

Crear una vista inmutable del resumen:

```python
@dataclass(frozen=True, slots=True)
class ResumenClanVista:
    nombre: str
    nivel: int
    dinero: int
    ocupacion: int
    cupo: int
    vivos: int
    muertos: int
    estado: str


def construir_resumen_clan(
    estado_clan: EstadoClan,
    datos_activos: list[AventureroActivo],
) -> ResumenClanVista:
    ...


def requiere_confirmacion_de_salida(sesion: EstadoSesion) -> bool:
    ...
```

Probar el conteo de vivos, muertos, ocupación y cupo. Probar que solo una expedición activa exige confirmación al cerrar.

En `tests/test_main.py`, usar dobles para confirmar que `main()`:

1. crea una raíz;
2. crea `AplicacionClan`;
3. muestra inicio;
4. llama una sola vez a `mainloop()`.

### Paso 2: ejecutar las pruebas fallidas

```bash
python -m unittest tests.test_interfaz_componentes tests.test_main -v
```

### Paso 3: implementar el contenedor de navegación

Completar `AplicacionClan` con:

```python
def __init__(
    self,
    raiz: tk.Tk,
    directorio: Path = DIRECTORIO_PARTIDA,
    generador: Random | None = None,
) -> None: ...

def mostrar_inicio(self) -> None: ...
def mostrar_ciudad(self) -> None: ...
def mostrar_clan(self) -> None: ...
def mostrar_gremio(self) -> None: ...
def mostrar_iglesia(self) -> None: ...
def mostrar_mazmorra(self) -> None: ...
def mostrar_combate(self) -> None: ...
def reemplazar_pantalla(self, pantalla: ttk.Frame) -> None: ...
def cerrar_aplicacion(self) -> None: ...
```

Configurar:

- título de ventana;
- tamaño inicial aproximado `1100x700`;
- mínimo `900x600`;
- pesos de grilla para expansión;
- protocolo `WM_DELETE_WINDOW`;
- destrucción del frame anterior antes de instalar el nuevo.

Las importaciones de pantallas deben evitar ciclos. En las pantallas, importar el tipo de aplicación solo bajo `TYPE_CHECKING`.

### Paso 4: implementar ciudad y `main.py`

`PantallaCiudad` muestra el resumen y botones para Clan, Gremio, Iglesia, Mazmorra y Guardar/salir al inicio. Los botones solo llaman métodos de `AplicacionClan`.

`main.py` queda como punto de entrada real:

```python
def main() -> None:
    raiz: tk.Tk = tk.Tk()
    aplicacion: AplicacionClan = AplicacionClan(raiz)
    aplicacion.mostrar_inicio()
    raiz.mainloop()


if __name__ == "__main__":
    main()
```

### Paso 5: verificar el tramo

```bash
python -m unittest tests.test_interfaz_componentes tests.test_main -v
python -m unittest discover -s tests -v
pyright interfaz main.py tests/test_interfaz_componentes.py tests/test_main.py
```

### Paso 6: prueba manual corta

Ejecutar `python main.py`, comprobar que aparece una sola ventana, redimensionarla y verificar que cerrar desde inicio termina el proceso.

### Paso 7: commit

```bash
git add interfaz main.py tests/test_interfaz_componentes.py tests/test_main.py
git commit -m "feat: agregar navegación base y pantalla de ciudad"
```

---

## Tramo 4: gestión visual de clan, gremio e iglesia

**Archivos:**

- Modificar: `interfaz/aplicacion.py`
- Modificar: `interfaz/componentes.py`
- Modificar: `interfaz/clan.py`
- Modificar: `interfaz/gremio.py`
- Modificar: `interfaz/iglesia.py`
- Crear: `tests/test_interfaz_gestion.py`
- Modificar: `tests/test_interfaz_componentes.py`

### Paso 1: escribir pruebas de filas visuales

En `componentes.py`, definir estructuras inmutables para las tablas:

```python
@dataclass(frozen=True, slots=True)
class FilaAventureroVista:
    identificador: str
    nombre: str
    raza: str
    profesion: str
    nivel: int
    experiencia: int


@dataclass(frozen=True, slots=True)
class FilaOfertaVista:
    identificador: str
    nombre: str
    raza: str
    profesion: str
    nivel: int
    coste: int


@dataclass(frozen=True, slots=True)
class FilaIglesiaVista:
    identificador: str
    nombre: str
    raza: str
    profesion: str
    nivel: int
    coste_resurreccion: int
```

Probar que las funciones de conversión consultan `CATALOGO_PLANTILLAS`, conservan IDs y no modifican los registros recibidos.

### Paso 2: escribir pruebas de coordinación administrativa

Agregar casos con directorio temporal para:

- expulsar un aventurero y persistir el historial;
- impedir expulsar al último vivo sin modificar datos;
- contratar y persistir dinero, oferta, contador e integrante;
- resucitar y persistir dinero/estado;
- enterrar y persistir historial/cupo;
- confirmar que una excepción de guardado deja intacta la sesión.

Los métodos de aplicación serán:

```python
def expulsar_integrante(self, aventurero_id: str) -> AventureroEliminado: ...
def contratar_oferta(self, oferta_id: str) -> AventureroActivo: ...
def resucitar_integrante(self, aventurero_id: str) -> AventureroActivo: ...
def enterrar_integrante(self, aventurero_id: str) -> AventureroEliminado: ...
```

Cada método debe delegar en `aplicar_cambio_y_guardar()` y en el servicio de dominio correspondiente.

### Paso 3: ejecutar las pruebas fallidas

```bash
python -m unittest tests.test_interfaz_componentes tests.test_interfaz_gestion -v
```

### Paso 4: implementar las tres pantallas

- `PantallaClan`: `Treeview` de vivos, botón expulsar, confirmación y regreso.
- `PantallaGremio`: `Treeview` de ofertas, dinero y contrataciones restantes, botón contratar y regreso.
- `PantallaIglesia`: `Treeview` de cuerpos recuperados con coste, botones resucitar/enterrar, confirmaciones, memorial de eliminados y regreso.

Después de una operación exitosa, reconstruir la pantalla correspondiente para refrescar todos los datos. Ante error esperado, mostrar `messagebox.showerror()` y conservar la selección/estado.

### Paso 5: verificar el tramo

```bash
python -m unittest tests.test_interfaz_componentes tests.test_interfaz_gestion -v
python -m unittest discover -s tests -v
pyright interfaz tests/test_interfaz_componentes.py tests/test_interfaz_gestion.py
```

### Paso 6: prueba manual

Crear una partida y recorrer las tres pantallas. Verificar selección obligatoria, confirmaciones, mensajes, actualización de dinero/cupo y protección del último vivo.

### Paso 7: commit

```bash
git add interfaz tests/test_interfaz_componentes.py tests/test_interfaz_gestion.py
git commit -m "feat: integrar gestión visual del clan"
```

---

## Tramo 5: selección de grupo e inicio de expedición

**Archivos:**

- Modificar: `interfaz/aplicacion.py`
- Modificar: `interfaz/componentes.py`
- Modificar: `interfaz/mazmorra.py`
- Crear: `tests/test_interfaz_mazmorra.py`

### Paso 1: escribir pruebas del coordinador de expedición

Agregar:

```python
def iniciar_expedicion_actual(
    self,
    aventureros_ids: list[str],
    mazmorra_id: str = MAZMORRA_LIMOS["id"],
) -> EstadoExpedicion:
    ...
```

Probar que:

- una selección válida crea la expedición sin modificar clan ni activos;
- una selección vacía, repetida, muerta o demasiado grande propaga el error y deja `sesion.expedicion` en `None`;
- no se reemplaza una expedición ya activa;
- el orden de IDs elegido por el jugador se conserva.

### Paso 2: escribir pruebas de la presentación del grupo

Añadir una función pura que construya filas de aventureros vivos con vida máxima, daño, defensa, velocidad y nivel calculados mediante los servicios existentes. Probar que los muertos no aparecen y que el límite mostrado coincide con `calcular_maximo_grupo()`.

### Paso 3: ejecutar las pruebas fallidas

```bash
python -m unittest tests.test_interfaz_mazmorra -v
```

### Paso 4: implementar `PantallaMazmorra`

La pantalla debe mostrar:

- Mazmorra de los Limos como única opción habilitada;
- las demás dificultades como no disponibles, sin botones operativos;
- tabla multiselección de aventureros vivos;
- contador `seleccionados / máximo`;
- botón iniciar, deshabilitado mientras se crea la expedición;
- mensajes de validación y botón volver.

Tras iniciar correctamente, navegar a combate. No guardar JSON en este punto.

### Paso 5: verificar el tramo

```bash
python -m unittest tests.test_interfaz_mazmorra -v
python -m unittest discover -s tests -v
pyright interfaz tests/test_interfaz_mazmorra.py
```

### Paso 6: prueba manual

Comprobar una selección válida, una vacía y una superior al límite. Confirmar que volver a ciudad antes de iniciar no cambia la partida.

### Paso 7: commit

```bash
git add interfaz tests/test_interfaz_mazmorra.py
git commit -m "feat: agregar selección visual de expedición"
```

---

## Tramo 6: resolución visual de las diez oleadas

**Archivos:**

- Modificar: `interfaz/aplicacion.py`
- Modificar: `interfaz/componentes.py`
- Modificar: `interfaz/combate.py`
- Crear: `tests/test_interfaz_combate.py`

### Paso 1: escribir pruebas de los controles por estado

Definir:

```python
@dataclass(frozen=True, slots=True)
class ControlesCombateVista:
    puede_resolver: bool
    puede_continuar: bool
    puede_retirarse: bool
    debe_cerrar: bool


def construir_controles_combate(
    estado_flujo: EstadoFlujoExpedicion,
) -> ControlesCombateVista:
    ...
```

Mapeo esperado:

| Estado | Resolver | Continuar | Retirarse | Cerrar |
|---|---:|---:|---:|---:|
| `lista_para_oleada` | Sí | No | No | No |
| `esperando_decision` | No | Sí | Sí | No |
| `finalizada` | No | No | No | Sí |
| `consecuencias_aplicadas` | No | No | No | No |

### Paso 2: escribir pruebas de coordinación del combate

Añadir y probar:

```python
def resolver_oleada_actual(self) -> ResultadoOleada: ...
def continuar_expedicion_actual(self) -> None: ...
def retirar_expedicion_actual(self) -> None: ...
def cerrar_expedicion_actual(self) -> ResumenCierreExpedicion: ...
```

Casos mínimos:

- resolver modifica solo la expedición temporal;
- continuar y retirarse respetan el estado de flujo;
- cierre exitoso publica consecuencias, guarda, renueva mercado y pone `sesion.expedicion` en `None`;
- cierre fallido deja intacta la expedición y permite reintentar;
- el mismo `Random` de la aplicación se usa durante toda la expedición.

### Paso 3: escribir pruebas de textos de resultado

Probar funciones puras que produzcan:

- resumen de última oleada: resultado, rondas, enemigos derrotados, dinero y experiencia provisional;
- filas de vida actual/máxima de aventureros;
- resumen final: retirada, derrota total, límite de rondas o mazmorra completada, supervivientes, muertos, dinero y experiencia entregados.

### Paso 4: ejecutar las pruebas fallidas

```bash
python -m unittest tests.test_interfaz_combate -v
```

### Paso 5: implementar `PantallaCombate`

Presentar:

- número de próxima oleada y oleadas superadas;
- dinero y experiencia acumulados;
- tabla de integrantes con vida actual/máxima y estado;
- panel de resultado de la última oleada;
- botones `Resolver oleada`, `Continuar` y `Regresar al clan` según el flujo.

Reglas de callback:

- deshabilitar todos los botones mientras se resuelve una acción;
- tras cada acción, reconstruir la pantalla;
- cuando el flujo quede `finalizada`, llamar al cierre transaccional;
- si guardar falla, mostrar error y ofrecer `Reintentar cierre` sin resolver otra vez la oleada;
- tras cerrar, mostrar el resumen final;
- si el estado de partida es `victoria` o `derrota`, limpiar sesión y volver al inicio; en otro caso, volver a ciudad.

### Paso 6: verificar el tramo

```bash
python -m unittest tests.test_interfaz_combate -v
python -m unittest discover -s tests -v
pyright interfaz tests/test_interfaz_combate.py
```

### Paso 7: prueba manual de la mazmorra completa

Con una partida de prueba:

1. seleccionar grupo;
2. resolver oleada;
3. continuar al menos una vez;
4. probar una retirada;
5. iniciar otra expedición;
6. avanzar hasta derrota o completar las diez oleadas;
7. cerrar y volver a cargar para confirmar que consecuencias y mercado quedaron persistidos.

### Paso 8: commit

```bash
git add interfaz tests/test_interfaz_combate.py
git commit -m "feat: integrar expediciones en la interfaz"
```

---

## Tramo 7: integración, documentación y cierre técnico

**Archivos:**

- Crear: `tests/test_interfaz_integracion.py`
- Crear: `documentacion/pruebas_interfaz_basica.md`
- Modificar: `README.md`
- Modificar: `documentacion/estructura_proyecto.md` si existe
- Modificar: archivos de interfaz solo si las verificaciones encuentran defectos

### Paso 1: escribir una integración coordinada sin ventana real

Usar una raíz y pantallas dobles para comprobar:

- solo existe un frame activo;
- navegar destruye el frame anterior;
- nueva partida llega a ciudad;
- carga terminada vuelve a inicio;
- administración exitosa refresca la pantalla;
- una expedición cerrada vuelve a ciudad o inicio según `estado_partida`;
- el protocolo de cierre consulta confirmación solo durante una expedición.

### Paso 2: ejecutar y corregir hasta verde

```bash
python -m unittest tests.test_interfaz_integracion -v
```

No debilitar aserciones para hacer pasar pruebas. Corregir la coordinación real.

### Paso 3: resolver los dos errores previos de Pyright

Corregir sin cambiar comportamiento:

- el reexportado de `AventureroNoEncontradoError` en `servicios/iglesia.py`;
- la firma incompatible del doble de `Random.choice` en `tests/test_reclutamiento.py`.

Agregar o ajustar pruebas solo si la solución cambia contratos observables.

### Paso 4: documentar ejecución y prueba manual

En `README.md`, incluir:

```bash
python main.py
```

Explicar que Tkinter forma parte de la instalación estándar usada por el proyecto y que esta versión ofrece una interfaz provisional sin imágenes ni habilidades.

En `documentacion/pruebas_interfaz_basica.md`, registrar una lista reproducible para:

- 1366x768 y 1920x1080;
- crear, sobrescribir y continuar;
- guardado incompleto/inválido;
- clan, gremio e iglesia;
- selección de grupo;
- retirada, derrota y mazmorra completa;
- cierre de ventana durante expedición;
- reinicio del programa y consistencia del JSON.

### Paso 5: verificación completa

```bash
python -m unittest discover -s tests -v
pyright .
git diff --check
git status --short
```

Resultado esperado:

- toda la suite en verde;
- cero errores de Pyright;
- ningún error de espacios o marcadores de conflicto;
- solo los archivos previstos modificados.

### Paso 6: prueba manual final

Ejecutar `python main.py` en Windows y completar la lista de `documentacion/pruebas_interfaz_basica.md`. Anotar cualquier limitación conocida antes de integrar la rama.

### Paso 7: commit

```bash
git add tests/test_interfaz_integracion.py \
    documentacion/pruebas_interfaz_basica.md \
    README.md \
    interfaz \
    servicios/iglesia.py \
    tests/test_reclutamiento.py
git add documentacion/estructura_proyecto.md  # solo si el archivo existe y cambió
git commit -m "docs: cerrar interfaz básica funcional"
```

---

## Criterios de aceptación finales

- `python main.py` abre la interfaz sin consola interactiva adicional.
- Se puede crear o continuar una partida y nunca se destruye un guardado inválido sin confirmación.
- Clan, gremio e iglesia ejecutan sus operaciones reales y persisten en el momento.
- Se puede elegir un grupo y resolver la Mazmorra de los Limos completa, oleada por oleada.
- El jugador puede continuar o retirarse entre victorias intermedias.
- El cierre de expedición persiste una sola vez y es reintentable ante error.
- Victoria y derrota regresan al inicio con un mensaje final.
- No hay reglas de negocio nuevas dentro de las pantallas.
- La suite completa y `pyright .` terminan sin errores.
