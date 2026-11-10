"""
tool_definitions.py — Ableton Live MCP Server
Esquemas de las 39 tools MCP expuestas por el servidor (solo datos, sin lógica).
"""

from mcp import types

TOOL_DEFINITIONS: list[types.Tool] = [
    types.Tool(
        name="add_chord_progression",
        description=(
            "Agrega una progresión de acordes MIDI a un clip en Ableton Live. "
            "Genera automáticamente los acordes según el estilo musical y la tonalidad. "
            "Ejemplo: estilo='deep_house', key='Am', track=0, scene=0"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "style": {
                    "type": "string",
                    "description": "Género musical. Ejemplos: deep_house, techno, trap, jazz, reggae, afrobeats, cinematic, metal, amapiano. Acepta texto libre con espacios o guiones.",
                },
                "key": {
                    "type": "string",
                    "description": "Nota raíz en cualquier tonalidad: C, C#, Db, D, D#, Eb, E, F, F#, Gb, G, G#, Ab, A, A#, Bb, B",
                },
                "scale": {
                    "type": "string",
                    "description": "Escala a usar. Opciones: major, minor, harmonic_minor, melodic_minor, dorian, phrygian, lydian, mixolydian, locrian, pentatonic_minor, pentatonic_major, blues, whole_tone, diminished, phrygian_dominant, hungarian_minor, double_harmonic. Default: minor",
                    "default": "minor",
                },
                "track_index": {"type": "integer", "default": 0},
                "scene_index": {"type": "integer", "default": 0},
                "octave": {
                    "type": "integer",
                    "default": 3,
                    "description": "Octava base 0-6",
                },
                "velocity": {
                    "type": "integer",
                    "default": 80,
                    "description": "Velocidad MIDI 0-127",
                },
                "clip_name": {"type": "string", "default": "Chord Progression"},
                "bars_per_chord": {
                    "type": "number",
                    "default": 2.0,
                    "description": "Compases por acorde",
                },
            },
            "required": ["style", "key"],
        },
    ),
    types.Tool(
        name="generate_chord_progression",
        description=(
            "Genera una progresión de acordes usando el algoritmo Würfelspiel "
            "(juego de dados musical determinista) del contrato canónico "
            "compartido con harmony-lab: elige un esqueleto armónico (secuencia "
            "de funciones T/S/D) y, por slot, un acorde concreto — reproducible "
            "bit a bit dado el mismo seed. A diferencia de add_chord_progression "
            "(patrón fijo por género), aquí el resultado varía según seed y "
            "creativity_level, con al menos 3 esqueletos distintos por género "
            "en los mismos 76 géneros que add_chord_progression. "
            "Ejemplo: genero='deep_house', key='A', seed=42, creativity_level=0.7"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "genero": {
                    "type": "string",
                    "description": (
                        "Género del catálogo Würfelspiel — los mismos 76 géneros que "
                        "add_chord_progression (ver ESQUELETOS_POR_GENERO en "
                        "harmonic_skeletons.py o el README del contrato canónico para la "
                        "lista completa). Género fuera de esta lista lanza error explícito, "
                        "sin fallback a otro género."
                    ),
                },
                "key": {
                    "type": "string",
                    "description": "Nota raíz: C, C#, Db, D, D#, Eb, E, F, F#, Gb, G, G#, Ab, A, A#, Bb, B",
                },
                "scale": {
                    "type": "string",
                    "description": "Escala a usar. Si se omite, usa la escala_default del género (minor o major según el género).",
                },
                "creativity_level": {
                    "type": "number",
                    "default": 0.0,
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": (
                        "0.0 = siempre la progresión canónica del género (opción[0] en cada slot). "
                        "1.0 = máxima variedad dentro de las opciones declaradas por función "
                        "(nunca sale de la tonalidad/escala)."
                    ),
                },
                "seed": {
                    "type": "integer",
                    "description": "Semilla entera del PRNG determinista (mulberry32). Mismo seed + mismos parámetros = mismo resultado, siempre.",
                },
                "semicadencia": {
                    "type": "boolean",
                    "default": False,
                    "description": "Si es true, sustituye el último slot del esqueleto elegido por una función Dominante (termina en tensión en vez de resolver en tónica).",
                },
                "track_index": {"type": "integer", "default": 0},
                "scene_index": {"type": "integer", "default": 0},
                "octave": {
                    "type": "integer",
                    "default": 3,
                    "description": "Octava base 0-6",
                },
                "velocity": {
                    "type": "integer",
                    "default": 80,
                    "description": "Velocidad MIDI 0-127",
                },
                "bars_per_chord": {
                    "type": "number",
                    "default": 2.0,
                    "description": "Compases por acorde",
                },
            },
            "required": ["genero", "key", "seed"],
        },
    ),
    types.Tool(
        name="generate_song_structure",
        description=(
            "Genera un SET de al menos 4 secciones con rol de canción (intro/verso/coro/"
            "puente, o el vocabulario que corresponda según la familia del género — "
            "electrónica usa intro/build_up/drop/breakdown, cinemática usa intro/desarrollo/"
            "climax/resolucion) y crea un clip por sección en escenas consecutivas del "
            "Session View. Cada sección usa su propio nivel de creatividad y puede terminar "
            "en semicadencia (puente/build_up) según la familia. Requiere que esas escenas "
            "ya existan — no crea escenas nuevas, igual que add_chord_progression. "
            "Ejemplo: genero='deep_house', key='A', seed=100, start_scene_index=0"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "genero": {
                    "type": "string",
                    "description": (
                        "Género del catálogo Würfelspiel — los mismos 76 géneros que "
                        "add_chord_progression y generate_chord_progression."
                    ),
                },
                "key": {
                    "type": "string",
                    "description": "Nota raíz: C, C#, Db, D, D#, Eb, E, F, F#, Gb, G, G#, Ab, A, A#, Bb, B",
                },
                "scale": {
                    "type": "string",
                    "description": "Escala a usar. Si se omite, usa la escala_default del género.",
                },
                "seed": {
                    "type": "integer",
                    "description": "Semilla base entera. Cada sección usa seed+índice — mismo seed = misma estructura completa, siempre.",
                },
                "track_index": {"type": "integer", "default": 0},
                "start_scene_index": {
                    "type": "integer",
                    "default": 0,
                    "description": "Primera escena a usar; las siguientes secciones ocupan las escenas consecutivas.",
                },
                "octave": {"type": "integer", "default": 3, "description": "Octava base 0-6"},
                "velocity": {"type": "integer", "default": 80, "description": "Velocidad MIDI 0-127"},
                "bars_per_chord": {
                    "type": "number",
                    "default": 2.0,
                    "description": "Compases por acorde",
                },
            },
            "required": ["genero", "key", "seed"],
        },
    ),
    types.Tool(
        name="add_midi_notes",
        description=(
            "Agrega notas MIDI individuales a un clip en Ableton. "
            "Úsalo para basslines, melodías o cualquier secuencia personalizada."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer", "default": 0},
                "scene_index": {"type": "integer", "default": 0},
                "notes": {
                    "type": "array",
                    "description": "Lista de notas MIDI",
                    "items": {
                        "type": "object",
                        "properties": {
                            "pitch":    {"type": "integer", "description": "Nota MIDI (60 = C4)"},
                            "position": {"type": "number",  "description": "Posición en beats"},
                            "duration": {"type": "number",  "description": "Duración en beats"},
                            "velocity": {"type": "integer", "description": "Velocidad 0-127"},
                        },
                        "required": ["pitch", "position", "duration"],
                    },
                },
                "clip_name": {"type": "string", "default": "MIDI Clip"},
                "clip_length": {"type": "number", "description": "Longitud total del clip en beats", "default": 16.0},
            },
            "required": ["notes"],
        },
    ),
    types.Tool(
        name="create_midi_track",
        description="Crea un nuevo track MIDI en Ableton Live.",
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {
                    "type": "integer",
                    "description": "Posición donde insertar el track (-1 = al final)",
                    "default": -1,
                },
                "name": {
                    "type": "string",
                    "description": "Nombre del track",
                    "default": "MIDI Track",
                },
            },
        },
    ),
    types.Tool(
        name="set_tempo",
        description="Cambia el tempo (BPM) del proyecto en Ableton.",
        inputSchema={
            "type": "object",
            "properties": {
                "bpm": {
                    "type": "number",
                    "description": "Tempo en BPM (ej: 128 para house, 140 para techno)",
                }
            },
            "required": ["bpm"],
        },
    ),
    types.Tool(
        name="play_pause",
        description="Inicia o pausa la reproducción en Ableton.",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["play", "pause", "stop"],
                    "description": "Acción a ejecutar",
                }
            },
            "required": ["action"],
        },
    ),
    types.Tool(
        name="get_session_info",
        description="Obtiene información del proyecto actual: BPM, tracks, escenas.",
        inputSchema={"type": "object", "properties": {}},
    ),
    types.Tool(
        name="new_project",
        description=(
            "Crea un nuevo proyecto en ableton-mcp con su carpeta de contexto. "
            "Guarda BPM, tonalidad, escala, género, referencia y tracks iniciales. "
            "Llama esto al inicio de cada nueva sesión de producción."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name":       {"type": "string", "description": "Nombre artístico del proyecto, ej: 'Digital Simbiosis'"},
                "genre":      {"type": "string", "description": "Género musical, ej: 'tech_house'"},
                "bpm":        {"type": "number", "description": "Tempo inicial"},
                "root_note":  {"type": "string", "description": "Nota raíz, ej: 'D'"},
                "mode":       {"type": "string", "description": "Escala/modo, ej: 'dorian'"},
                "reference":  {"type": "string", "description": "Canción o artista de referencia"},
                "notes":      {"type": "string", "description": "Notas creativas libres"},
            },
            "required": ["name", "genre", "bpm", "root_note"],
        },
    ),
    types.Tool(
        name="load_project",
        description="Carga el contexto de un proyecto existente desde su carpeta en ableton-mcp/projects/. Usa esto al retomar una sesión.",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nombre del proyecto (ej: 'Digital Simbiosis') o su slug (ej: 'digital-simbiosis')"},
            },
            "required": ["name"],
        },
    ),
    types.Tool(
        name="save_project_state",
        description="Guarda el estado actual del proyecto (tracks, dispositivos, notas) en su carpeta. Llama esto periódicamente durante la sesión.",
        inputSchema={
            "type": "object",
            "properties": {
                "notes": {"type": "string", "description": "Notas opcionales sobre lo que se hizo en esta sesión"},
            },
        },
    ),
    types.Tool(
        name="list_projects",
        description="Lista todos los proyectos guardados en ableton-mcp/projects/.",
        inputSchema={"type": "object", "properties": {}},
    ),
    types.Tool(
        name="set_clip_color",
        description="Cambia el color de un clip en la Session View.",
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer"},
                "scene_index": {"type": "integer"},
                "color": {
                    "type": "integer",
                    "description": "Color en formato entero RGB (ej: 16711680 = rojo)",
                },
            },
            "required": ["track_index", "scene_index", "color"],
        },
    ),
    types.Tool(
        name="load_instrument",
        description=(
            "Carga un instrumento nativo de Ableton en un track MIDI. "
            "Instrumentos disponibles: analog, operator, wavetable, drift, meld, "
            "electric, collision, tension, simpler, sampler, drum_rack, granulator. "
            "Aliases: bass→analog, synth/pad→wavetable, lead→operator, "
            "keys/piano→electric, drums/perc→drum_rack."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {
                    "type": "integer",
                    "description": "Índice del track (0-based)",
                },
                "instrument": {
                    "type": "string",
                    "description": "Nombre del instrumento o alias: analog, operator, wavetable, drum_rack, electric, meld, drift, simpler, sampler, bass, synth, lead, pad, keys, drums",
                },
                "device_index": {
                    "type": "integer",
                    "default": 0,
                    "description": "Posición en la cadena de devices del track (generalmente 0)",
                },
            },
            "required": ["track_index", "instrument"],
        },
    ),
    types.Tool(
        name="get_device_params",
        description="Obtiene todos los parámetros de un instrumento o efecto cargado en un track. Úsalo antes de set_device_param para saber los índices.",
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer"},
                "device_index": {
                    "type": "integer",
                    "default": 0,
                    "description": "Índice del device en la cadena (0 = primero)",
                },
            },
            "required": ["track_index"],
        },
    ),
    types.Tool(
        name="set_device_param",
        description="Cambia un parámetro de un instrumento o efecto. Usa get_device_params primero para ver los índices disponibles.",
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer"},
                "device_index": {"type": "integer", "default": 0},
                "param_index": {
                    "type": "integer",
                    "description": "Índice del parámetro (ver get_device_params)",
                },
                "value": {
                    "type": "number",
                    "description": "Valor a asignar (0.0–1.0 normalizado para la mayoría de parámetros)",
                },
            },
            "required": ["track_index", "param_index", "value"],
        },
    ),
    types.Tool(
        name="set_device_params_bulk",
        description="Cambia múltiples parámetros de un device de una sola vez. Ideal para configurar un preset completo.",
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer"},
                "device_index": {"type": "integer", "default": 0},
                "params": {
                    "type": "object",
                    "description": "Mapa de índice_parámetro (string) → valor. Ej: {\"1\": 0.7, \"5\": 0.3}",
                    "additionalProperties": {"type": "number"},
                },
            },
            "required": ["track_index", "params"],
        },
    ),
    types.Tool(
        name="get_track_devices",
        description=(
            "Lista todos los devices y plugins cargados en un track, "
            "con su índice, nombre y tipo (VST3, AU, Max, Rack, etc.). "
            "Úsalo para saber qué device_index pasar a get_device_params o set_device_param."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {
                    "type": "integer",
                    "description": "Índice del track (0-based)",
                },
            },
            "required": ["track_index"],
        },
    ),
    types.Tool(
        name="scan_plugins",
        description=(
            "Escanea el browser de Ableton y devuelve la lista de plugins/devices "
            "disponibles con su nombre y URI. "
            "Sin argumentos devuelve el nivel raíz del browser. "
            "Pasa category_uri (URI de una carpeta devuelta por una llamada anterior) "
            "para entrar en subcarpetas como 'VST3 Plug-Ins', 'Audio Units', 'Max for Live'. "
            "La URI obtenida aquí es la que usa load_plugin. "
            "Tip: filtra por nombre con el parámetro 'filter' (ej: 'serum', 'fabfilter', 'reverb')."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "category_uri": {
                    "type": "string",
                    "description": "URI de una carpeta del browser para listar su contenido. Omitir para ver el nivel raíz.",
                    "default": "",
                },
                "filter": {
                    "type": "string",
                    "description": "Texto para filtrar resultados por nombre (case-insensitive). Ej: 'serum', 'pro-q', 'fabfilter'.",
                    "default": "",
                },
            },
        },
    ),
    types.Tool(
        name="load_plugin",
        description=(
            "Carga cualquier plugin (VST3, VST2, AU, Max for Live) en un track de Ableton "
            "usando su URI del browser (obtenida con scan_plugins). "
            "Una vez cargado, usa get_device_params para ver sus parámetros "
            "y set_device_param / set_device_params_bulk para modificarlos."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {
                    "type": "integer",
                    "description": "Índice del track donde cargar el plugin (0-based)",
                },
                "plugin_uri": {
                    "type": "string",
                    "description": "URI del plugin tal como la devolvió scan_plugins.",
                },
            },
            "required": ["track_index", "plugin_uri"],
        },
    ),
    types.Tool(
        name="load_sample",
        description=(
            "Carga un archivo de audio (WAV, AIFF) en el Simpler del track especificado. "
            "El track debe tener Simpler cargado previamente con load_instrument. "
            "Usa la ruta absoluta del archivo en el sistema de archivos."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {
                    "type": "integer",
                    "description": "Índice del track (0-based)",
                },
                "sample_path": {
                    "type": "string",
                    "description": "Ruta absoluta al archivo de audio. Ej: /Volumes/HD/samples/kick.wav",
                },
            },
            "required": ["track_index", "sample_path"],
        },
    ),

    # ── Plugin Registry ──────────────────────────────────────
    types.Tool(
        name="build_plugin_registry",
        description=(
            "Escanea el browser de Ableton y construye un registro persistente de todos los "
            "plugins instalados (VST3, VST2, AU, Max for Live). "
            "Guarda los resultados en registry/plugins.json para uso futuro. "
            "IMPORTANTE: ejecuta esto la primera vez que uses el MCP, con Ableton abierto "
            "y el browser visible (tecla B). El escaneo puede tardar 10-30 segundos. "
            "Después de hacer build_plugin_registry puedes usar load_plugin_by_name con "
            "nombres amigables como 'Maschine 2', 'Pigments', 'Reaktor 6', etc."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "categories": {
                    "type": "array",
                    "description": "Categorías específicas a escanear. Vacío = escanear todo.",
                    "items": {"type": "string"},
                    "default": [],
                },
                "force_rescan": {
                    "type": "boolean",
                    "description": "Forzar re-escaneo aunque ya exista un registry guardado.",
                    "default": False,
                },
            },
        },
    ),
    types.Tool(
        name="load_plugin_by_name",
        description=(
            "Carga un plugin en un track usando su nombre en lenguaje natural. "
            "Requiere que build_plugin_registry se haya ejecutado antes. "
            "Ejemplos: 'Maschine 2', 'Pigments', 'Reaktor 6', 'Orbit', 'Pro-Q 3', 'Serum'. "
            "Si el nombre es ambiguo, devuelve una lista de coincidencias para elegir."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {
                    "type": "integer",
                    "description": "Índice del track donde cargar el plugin (0-based)",
                },
                "plugin_name": {
                    "type": "string",
                    "description": "Nombre del plugin. Ej: 'Maschine 2', 'Arturia Pigments', 'Reaktor 6', 'Orbit'",
                },
            },
            "required": ["track_index", "plugin_name"],
        },
    ),
    types.Tool(
        name="search_plugin_registry",
        description=(
            "Busca plugins en el registry local por nombre parcial. "
            "Útil para verificar si un plugin está en el registry antes de cargarlo, "
            "o para descubrir qué plugins están instalados. "
            "Si el registry está vacío, ejecuta build_plugin_registry primero."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Texto a buscar. Ej: 'arturia', 'native instruments', 'fabfilter', 'output'",
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "description": "Máximo de resultados a devolver",
                },
            },
            "required": ["query"],
        },
    ),

    # ── Track Control ─────────────────────────────────────────
    types.Tool(
        name="set_track_volume",
        description=(
            "Ajusta el volumen de un track. "
            "El valor 0.85 corresponde a 0 dB (volumen de unidad). "
            "Rango: 0.0 (silencio) a 1.0 (máximo, +6 dB aprox)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer", "description": "Índice del track (0-based)"},
                "volume": {
                    "type": "number",
                    "description": "Volumen 0.0–1.0. 0.85 = 0 dB. 0.0 = silencio.",
                    "minimum": 0.0,
                    "maximum": 1.0,
                },
            },
            "required": ["track_index", "volume"],
        },
    ),
    types.Tool(
        name="set_track_pan",
        description="Ajusta el paneo de un track. -1.0 = izquierda completa, 0.0 = centro, 1.0 = derecha completa.",
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer"},
                "pan": {
                    "type": "number",
                    "description": "Paneo: -1.0 (L) a 1.0 (R), 0.0 = centro",
                    "minimum": -1.0,
                    "maximum": 1.0,
                },
            },
            "required": ["track_index", "pan"],
        },
    ),
    types.Tool(
        name="set_track_mute",
        description="Silencia o activa un track.",
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer"},
                "muted": {
                    "type": "boolean",
                    "description": "true = silenciar, false = activar",
                },
            },
            "required": ["track_index", "muted"],
        },
    ),
    types.Tool(
        name="set_track_solo",
        description="Activa o desactiva el solo de un track.",
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer"},
                "solo": {
                    "type": "boolean",
                    "description": "true = activar solo, false = desactivar solo",
                },
            },
            "required": ["track_index", "solo"],
        },
    ),
    types.Tool(
        name="arm_track",
        description="Arma o desarma un track para grabación. El track debe ser MIDI o audio.",
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer"},
                "armed": {
                    "type": "boolean",
                    "description": "true = armar para grabación, false = desarmar",
                },
            },
            "required": ["track_index", "armed"],
        },
    ),
    types.Tool(
        name="set_track_name",
        description="Renombra un track en Ableton.",
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer"},
                "name": {"type": "string", "description": "Nuevo nombre del track"},
            },
            "required": ["track_index", "name"],
        },
    ),
    types.Tool(
        name="set_track_color",
        description="Cambia el color de un track. Usa el entero RGB (ej: 16711680 = rojo, 65280 = verde, 255 = azul).",
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer"},
                "color": {
                    "type": "integer",
                    "description": "Color RGB como entero. Ej: 16711680=rojo, 16776960=amarillo, 65280=verde, 255=azul, 16711935=magenta",
                },
            },
            "required": ["track_index", "color"],
        },
    ),
    types.Tool(
        name="get_track_info",
        description=(
            "Obtiene información completa de un track: nombre, volumen, pan, mute, solo, arm, "
            "número de clips, y lista de devices. "
            "Útil para ver el estado actual antes de hacer cambios."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer", "description": "Índice del track (0-based)"},
            },
            "required": ["track_index"],
        },
    ),
    types.Tool(
        name="set_track_send",
        description=(
            "Ajusta el nivel de envío de un track a un return track. "
            "Ejemplo: set_track_send(track_index=0, send_index=0, value=0.7) envía el track 1 "
            "al return A con 70% de nivel."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer", "description": "Track de origen"},
                "send_index": {
                    "type": "integer",
                    "description": "Índice del return (0=A, 1=B, 2=C, etc.)",
                },
                "value": {
                    "type": "number",
                    "description": "Nivel de envío 0.0–1.0",
                    "minimum": 0.0,
                    "maximum": 1.0,
                },
            },
            "required": ["track_index", "send_index", "value"],
        },
    ),
    types.Tool(
        name="create_audio_track",
        description="Crea un nuevo track de audio en Ableton Live.",
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {
                    "type": "integer",
                    "description": "Posición donde insertar el track (-1 = al final)",
                    "default": -1,
                },
                "name": {
                    "type": "string",
                    "description": "Nombre del track",
                    "default": "Audio Track",
                },
            },
        },
    ),

    # ── Clip & Scene Control ──────────────────────────────────
    types.Tool(
        name="trigger_clip",
        description=(
            "Dispara (lanza) un clip en un slot específico de la Session View. "
            "El clip empieza a reproducirse en el próximo tiempo cuantizado. "
            "Si el slot está vacío, no hace nada."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer", "description": "Índice del track (0-based)"},
                "scene_index": {"type": "integer", "description": "Índice de la escena/fila (0-based)"},
            },
            "required": ["track_index", "scene_index"],
        },
    ),
    types.Tool(
        name="stop_clip",
        description="Detiene un clip que está reproduciendo en un slot de la Session View.",
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer"},
                "scene_index": {"type": "integer"},
            },
            "required": ["track_index", "scene_index"],
        },
    ),
    types.Tool(
        name="get_clip_notes",
        description=(
            "Lee las notas MIDI de un clip existente en un slot de la Session View: "
            "pitch, posición, duración, velocidad y mute de cada nota. "
            "Útil para verificar qué generó realmente un device (nativo o Max for Live) "
            "en vez de asumir por el mensaje de confirmación de la tool que lo disparó. "
            "Si el slot no tiene clip, no es un clip MIDI, o está vacío, lo reporta explícitamente."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "track_index": {"type": "integer", "description": "Índice del track (0-based)"},
                "scene_index": {"type": "integer", "description": "Índice de la escena/fila (0-based)"},
            },
            "required": ["track_index", "scene_index"],
        },
    ),
    types.Tool(
        name="trigger_scene",
        description=(
            "Dispara una escena completa (fila) en la Session View. "
            "Lanza todos los clips de esa fila simultáneamente. "
            "Equivale a hacer clic en el botón ► de una escena."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "scene_index": {"type": "integer", "description": "Índice de la escena/fila (0-based)"},
            },
            "required": ["scene_index"],
        },
    ),

    # ── Ableton Session ───────────────────────────────────────
    types.Tool(
        name="set_time_signature",
        description="Cambia el compás del proyecto. Ejemplo: 4/4, 3/4, 6/8.",
        inputSchema={
            "type": "object",
            "properties": {
                "numerator": {
                    "type": "integer",
                    "description": "Numerador del compás (ej: 4 para 4/4, 3 para 3/4)",
                    "minimum": 1,
                    "maximum": 16,
                },
                "denominator": {
                    "type": "integer",
                    "description": "Denominador del compás (ej: 4 para /4, 8 para /8)",
                    "enum": [1, 2, 4, 8, 16],
                },
            },
            "required": ["numerator", "denominator"],
        },
    ),
    types.Tool(
        name="get_ableton_version",
        description=(
            "Obtiene la versión de Ableton Live instalada y el estado general de la conexión OSC. "
            "Útil para verificar que AbletonOSC está activo y para saber qué funciones están disponibles."
        ),
        inputSchema={"type": "object", "properties": {}},
    ),

    # ── Herramientas gratuitas de terceros ────────────────────
    types.Tool(
        name="suggest_free_tool",
        description=(
            "Busca en la base de conocimiento (tools_knowledge_base.json) herramientas "
            "gratuitas de terceros (Max for Live devices, Live Extensions, plugins) que "
            "ya resuelvan la tarea pedida, antes de construirla desde cero vía OSC. "
            "Úsala primero cuando el usuario pida un recurso musical como un patrón "
            "rítmico complejo, separar un loop de batería en stems, variación melódica "
            "automática, live-looping por slices, o efectos de granular/glitch. "
            "Devuelve la(s) herramienta(s) recomendada(s), si ya está(n) descargada(s) "
            "localmente, y cómo instalarla(s) si no."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "task_description": {
                    "type": "string",
                    "description": "Descripción en lenguaje natural de lo que el usuario quiere lograr. Ej: 'separar un loop de batería en stems', 'generar un patrón rítmico complejo'",
                },
            },
            "required": ["task_description"],
        },
    ),
]
