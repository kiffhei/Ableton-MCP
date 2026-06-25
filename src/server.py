"""
Ableton Live MCP Server
Conecta Claude con Ableton Live via AbletonOSC
"""

import asyncio
import logging
import time
import urllib.parse
from datetime import date

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from music_theory import (
    build_progression, build_chord, note_name_to_midi,
    GENRE_PATTERNS, SCALES,
)
from osc_client import (
    send_osc, start_osc_listener, init_osc_client,
    osc_lock, osc_responses,
)
from project_manager import (
    PROJECTS_DIR, _slug, _project_path,
    _load_project_file, _save_project_file,
    get_active_project, set_active_project,
)
from plugin_registry import (
    add_plugins_bulk, find_plugin_uri, search_plugins,
    list_registry_summary, mark_as_scanned, get_last_scan,
    _load_registry,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ableton-mcp")

# ── Servidor MCP ────────────────────────────────────────────
app = Server("ableton-mcp")

# ── Instrumentos nativos de Ableton ─────────────────────────

INSTRUMENT_PATHS = {
    "analog":     "Instruments/Analog/Default.adg",
    "operator":   "Instruments/Operator/Default.adg",
    "wavetable":  "Instruments/Wavetable/Default.adg",
    "drift":      "Instruments/Drift/Default.adg",
    "meld":       "Instruments/Meld/Default.adg",
    "electric":   "Instruments/Electric/Default.adg",
    "collision":  "Instruments/Collision/Default.adg",
    "tension":    "Instruments/Tension/Default.adg",
    "simpler":    "Instruments/Simpler/Default.adg",
    "sampler":    "Instruments/Sampler/Default.adg",
    "drum_rack":  "Drums/Drum Rack/Default.adg",
    "granulator": "Max for Live/Instruments/Granulator II.amxd",
}

INSTRUMENT_ALIASES = {
    "bass":      "analog",
    "synth":     "wavetable",
    "lead":      "operator",
    "pad":       "wavetable",
    "keys":      "electric",
    "piano":     "electric",
    "drums":     "drum_rack",
    "percusion": "drum_rack",
    "perc":      "drum_rack",
}

# Mapeo de class_name interno de Ableton → etiqueta legible
DEVICE_CLASS_LABELS: dict[str, str] = {
    "Vst3Plugin":               "VST3",
    "VstPlugin":                "VST2",
    "AuPlugin":                 "AU",
    "PluginDevice":             "Plugin",
    "MxDeviceMidiInstrument":   "Max Instrument",
    "MxDeviceAudioEffect":      "Max Effect",
    "MxDeviceMidiEffect":       "Max MIDI Effect",
    "AbletonDeviceGroupDevice": "Device Group",
    "InstrumentGroupDevice":    "Instrument Rack",
    "DrumGroupDevice":          "Drum Rack",
    "AudioEffectGroupDevice":   "Effect Rack",
}

# ── Cache del browser de plugins ─────────────────────────────
_plugin_cache: dict[str, str] = {}    # nombre_normalizado → uri
_plugin_display: dict[str, str] = {}  # nombre_normalizado → nombre para mostrar


def _normalize(s: str) -> str:
    return s.lower().strip().replace(" ", "_").replace("-", "_")


def _parse_browser_items(raw: tuple) -> list[dict]:
    """
    Parsea la respuesta OSC del browser de Ableton.
    AbletonOSC devuelve los items como args planos en grupos de 4:
    (name, uri, is_loadable, is_folder, name, uri, ...)
    Con fallback a pares (name, uri) para versiones antiguas.
    """
    items: list[dict] = []
    if not raw:
        return items
    if len(raw) % 4 == 0:
        for i in range(0, len(raw), 4):
            items.append({
                "name":     str(raw[i]),
                "uri":      str(raw[i + 1]),
                "loadable": bool(raw[i + 2]),
                "folder":   bool(raw[i + 3]),
            })
    elif len(raw) % 2 == 0:
        for i in range(0, len(raw), 2):
            items.append({
                "name":     str(raw[i]),
                "uri":      str(raw[i + 1]),
                "loadable": True,
                "folder":   False,
            })
    return items


# ── Herramientas MCP ─────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
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
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    if name == "set_tempo":
        bpm = arguments["bpm"]
        send_osc("/live/song/set/tempo", float(bpm))
        return [types.TextContent(type="text", text=f"✅ Tempo cambiado a {bpm} BPM")]

    elif name == "play_pause":
        action = arguments["action"]
        if action == "play":
            send_osc("/live/song/start_playing")
        elif action == "pause":
            send_osc("/live/song/stop_playing")
        elif action == "stop":
            send_osc("/live/song/stop_playing")
            send_osc("/live/song/set/current_song_time", 0.0)
        return [types.TextContent(type="text", text=f"✅ {action.capitalize()} ejecutado")]

    elif name == "create_midi_track":
        idx = arguments.get("track_index", -1)
        track_name = arguments.get("name", "MIDI Track")
        send_osc("/live/song/create_midi_track", idx)
        time.sleep(0.3)
        return [types.TextContent(type="text", text=f"✅ Track MIDI '{track_name}' creado en posición {idx}")]

    elif name == "get_session_info":
        send_osc("/live/song/get/tempo")
        send_osc("/live/song/get/num_tracks")
        send_osc("/live/song/get/num_scenes")
        time.sleep(0.5)
        with osc_lock:
            tempo = osc_responses.get("/live/song/get/tempo", ("?",))[0]
            tracks = osc_responses.get("/live/song/get/num_tracks", ("?",))[0]
            scenes = osc_responses.get("/live/song/get/num_scenes", ("?",))[0]
        info = f"🎚️ Proyecto Ableton\n- BPM: {tempo}\n- Tracks: {tracks}\n- Escenas: {scenes}"
        return [types.TextContent(type="text", text=info)]

    elif name == "add_midi_notes":
        track_idx = arguments.get("track_index", 0)
        scene_idx = arguments.get("scene_index", 0)
        notes = arguments["notes"]
        clip_name = arguments.get("clip_name", "MIDI Clip")
        clip_length = arguments.get("clip_length", 16.0)

        send_osc("/live/clip_slot/create_clip", track_idx, scene_idx, clip_length)
        time.sleep(0.4)

        note_args = [track_idx, scene_idx]
        for n in notes:
            note_args += [
                int(n["pitch"]),
                float(n["position"]),
                float(n["duration"]),
                int(n.get("velocity", 80)),
                0,  # muted = False
            ]
        send_osc("/live/clip/add/notes", *note_args)
        time.sleep(0.2)

        send_osc("/live/clip/set/name", track_idx, scene_idx, clip_name)

        return [types.TextContent(
            type="text",
            text=f"✅ {len(notes)} notas agregadas al clip '{clip_name}' (Track {track_idx+1}, Escena {scene_idx+1})"
        )]

    elif name == "add_chord_progression":
        style = arguments["style"]
        key = arguments["key"]
        track_idx = arguments.get("track_index", 0)
        scene_idx = arguments.get("scene_index", 0)
        octave = arguments.get("octave", 3)
        velocity = arguments.get("velocity", 80)
        clip_name = arguments.get("clip_name", f"{key} {style} Chords")
        bars_per_chord = arguments.get("bars_per_chord", 2.0)
        scale_name = arguments.get("scale", "minor")

        notes = build_progression(style, key, scale_name, octave, bars_per_chord, velocity)
        total_length = bars_per_chord * 4 * 4  # 4 acordes × bars × beats

        send_osc("/live/clip_slot/create_clip", track_idx, scene_idx, float(total_length))
        time.sleep(0.4)

        note_args = [track_idx, scene_idx]
        for n in notes:
            note_args += [
                int(n["pitch"]),
                float(n["position"]),
                float(n["duration"]),
                velocity,
                0,
            ]
        send_osc("/live/clip/add/notes", *note_args)
        time.sleep(0.2)

        send_osc("/live/clip/set/name", track_idx, scene_idx, clip_name)

        style_key = style.lower().strip().replace(" ", "_").replace("-", "_")
        pattern = GENRE_PATTERNS.get(style_key, GENRE_PATTERNS["deep_house"])
        chord_summary = " → ".join([f"grado{d} {t}" for d, t in pattern])

        return [types.TextContent(
            type="text",
            text=(
                f"✅ Progresión '{style}' en {key} agregada\n"
                f"📍 Track {track_idx+1}, Escena {scene_idx+1}\n"
                f"🎹 Acordes: {chord_summary}\n"
                f"⏱️ {bars_per_chord} compases por acorde | {len(notes)} notas totales"
            )
        )]

    elif name == "set_clip_color":
        track_idx = arguments["track_index"]
        scene_idx = arguments["scene_index"]
        color = arguments["color"]
        send_osc("/live/clip/set/color", track_idx, scene_idx, color)
        return [types.TextContent(type="text", text=f"✅ Color del clip actualizado")]

    elif name == "load_instrument":
        track_idx = arguments["track_index"]
        instrument = arguments["instrument"].lower().strip().replace(" ", "_")
        instrument = INSTRUMENT_ALIASES.get(instrument, instrument)
        path = INSTRUMENT_PATHS.get(instrument)

        if path is None:
            available = ", ".join(sorted(INSTRUMENT_PATHS.keys()))
            return [types.TextContent(
                type="text",
                text=f"❌ Instrumento '{instrument}' no encontrado.\nDisponibles: {available}",
            )]

        send_osc("/live/view/set/selected_track", track_idx)
        time.sleep(0.3)
        send_osc("/live/track/load_device", track_idx, instrument)
        time.sleep(1.0)

        return [types.TextContent(
            type="text",
            text=f"✅ {instrument.capitalize()} cargado en Track {track_idx + 1}",
        )]

    elif name == "get_device_params":
        track_idx = arguments["track_index"]
        device_idx = arguments.get("device_index", 0)

        send_osc("/live/device/get/parameters/name", track_idx, device_idx)
        time.sleep(0.5)
        send_osc("/live/device/get/parameters/value", track_idx, device_idx)
        time.sleep(0.3)

        with osc_lock:
            names = list(osc_responses.get("/live/device/get/parameters/name", ()))
            values = list(osc_responses.get("/live/device/get/parameters/value", ()))

        if not names:
            return [types.TextContent(
                type="text",
                text=(
                    f"⚠️ Sin parámetros en Track {track_idx + 1}, Device {device_idx}.\n"
                    "¿Hay un instrumento cargado? Usa load_instrument primero."
                ),
            )]

        lines = [f"🎛️ Parámetros — Track {track_idx + 1}, Device {device_idx}:"]
        for i, param_name in enumerate(names):
            val = f"{values[i]:.3f}" if i < len(values) else "?"
            lines.append(f"  [{i:02d}] {param_name}: {val}")

        return [types.TextContent(type="text", text="\n".join(lines))]

    elif name == "set_device_param":
        track_idx = arguments["track_index"]
        device_idx = arguments.get("device_index", 0)
        param_idx = int(arguments["param_index"])
        value = float(arguments["value"])

        send_osc("/live/device/set/parameter/value", track_idx, device_idx, param_idx, value)
        time.sleep(0.1)

        return [types.TextContent(
            type="text",
            text=f"✅ Param [{param_idx}] → {value} (Track {track_idx + 1}, Device {device_idx})",
        )]

    elif name == "set_device_params_bulk":
        track_idx = arguments["track_index"]
        device_idx = arguments.get("device_index", 0)
        params = arguments["params"]

        for param_idx_str, value in params.items():
            send_osc("/live/device/set/parameter/value", track_idx, device_idx, int(param_idx_str), float(value))
            time.sleep(0.05)

        return [types.TextContent(
            type="text",
            text=f"✅ {len(params)} parámetros actualizados (Track {track_idx + 1}, Device {device_idx})",
        )]

    elif name == "get_track_devices":
        track_idx = arguments["track_index"]

        send_osc("/live/track/get/num_devices", track_idx)
        time.sleep(0.3)
        send_osc("/live/track/get/devices/name", track_idx)
        time.sleep(0.3)
        send_osc("/live/track/get/devices/class_name", track_idx)
        time.sleep(0.3)

        with osc_lock:
            num_raw     = osc_responses.get("/live/track/get/num_devices", (0,))
            names_raw   = osc_responses.get("/live/track/get/devices/name", ())
            classes_raw = osc_responses.get("/live/track/get/devices/class_name", ())

        num_devices = int(num_raw[0]) if num_raw else 0

        if num_devices == 0 or not names_raw:
            return [types.TextContent(
                type="text",
                text=(
                    f"⚠️ Track {track_idx + 1} no tiene devices cargados.\n"
                    "Usa load_instrument o load_plugin para agregar uno."
                ),
            )]

        lines = [f"📦 Devices en Track {track_idx + 1}  ({num_devices} total):"]
        for i, dev_name in enumerate(names_raw):
            cls = classes_raw[i] if i < len(classes_raw) else "Unknown"
            label = DEVICE_CLASS_LABELS.get(cls, cls)
            lines.append(f"  [{i:02d}]  {dev_name}   ({label})")

        lines.append(
            "\n💡 Usa get_device_params track_index={} device_index=<índice> "
            "para ver parámetros de cualquier device.".format(track_idx)
        )
        return [types.TextContent(type="text", text="\n".join(lines))]

    elif name == "scan_plugins":
        category_uri = arguments.get("category_uri", "").strip()
        filter_text  = arguments.get("filter", "").strip().lower()

        query = filter_text or ""
        send_osc("/live/browser/scan", query)
        resp_key = "/live/browser/scan"
        time.sleep(1.5)

        with osc_lock:
            raw = osc_responses.get(resp_key, ())

        items = _parse_browser_items(raw)

        if not items:
            return [types.TextContent(
                type="text",
                text=(
                    "⚠️ Sin resultados del browser de Ableton.\n"
                    "Verifica que:\n"
                    "  1. AbletonOSC esté activo (Preferences → Link/MIDI → Control Surface = AbletonOSC)\n"
                    "  2. El browser de Ableton esté abierto (tecla B en Ableton)\n"
                    "  3. La URI de categoría sea correcta (si pasaste una)"
                ),
            )]

        if filter_text:
            items = [it for it in items if filter_text in it["name"].lower()]

        for it in items:
            if it.get("loadable") and it.get("uri"):
                key = _normalize(it["name"])
                _plugin_cache[key]   = it["uri"]
                _plugin_display[key] = it["name"]

        lines = [
            f"🔍 Browser Ableton — {len(items)} items"
            + (f"  [filtro: '{filter_text}']" if filter_text else "")
        ]
        for it in items:
            icon = "📁" if it.get("folder") else ("🎛️" if it.get("loadable") else "  ")
            lines.append(f"\n  {icon}  {it['name']}")
            if it.get("uri"):
                uri_display = it["uri"][:70] + "…" if len(it["uri"]) > 70 else it["uri"]
                lines.append(f"      URI: {uri_display}")

        lines.append("\n" + "─" * 60)
        lines.append("💡 Para entrar en una carpeta: scan_plugins(category_uri='<uri>')")
        lines.append("💡 Para cargar un plugin:  load_plugin(track_index=N, plugin_uri='<uri>')")
        return [types.TextContent(type="text", text="\n".join(lines))]

    elif name == "load_plugin":
        track_idx  = arguments["track_index"]
        plugin_uri = arguments["plugin_uri"].strip()

        send_osc("/live/view/set/selected_track", track_idx)
        time.sleep(0.3)
        send_osc("/live/track/load_device", track_idx, plugin_uri)
        time.sleep(1.5)

        return [types.TextContent(
            type="text",
            text=(
                f"✅ Plugin cargado en Track {track_idx + 1}\n"
                f"📍 URI: {plugin_uri}\n"
                "💡 Usa get_track_devices para confirmar que cargó correctamente.\n"
                "💡 Usa get_device_params para explorar sus parámetros."
            ),
        )]

    elif name == "load_sample":
        track_idx   = arguments["track_index"]
        sample_path = arguments["sample_path"].strip()

        file_uri = "file://" + urllib.parse.quote(sample_path, safe="/:")

        send_osc("/live/view/set/selected_track", track_idx)
        time.sleep(0.3)
        send_osc("/live/track/load_sample", track_idx, file_uri)
        time.sleep(1.2)

        filename = sample_path.split("/")[-1].split("\\")[-1]
        return [types.TextContent(
            type="text",
            text=(
                f"✅ Sample '{filename}' enviado a Track {track_idx + 1}\n"
                f"📍 Path: {sample_path}\n"
                "💡 Si no cargó, verifica que Simpler esté activo en ese track."
            ),
        )]

    elif name == "new_project":
        proj_name  = arguments["name"]
        slug       = _slug(proj_name)
        bpm        = arguments["bpm"]
        root_note  = arguments.get("root_note", "C")
        mode       = arguments.get("mode", "minor")
        genre      = arguments.get("genre", "")
        reference  = arguments.get("reference", "")
        notes      = arguments.get("notes", "")

        existing = _load_project_file(slug)
        if existing:
            set_active_project(existing)
            return [types.TextContent(type="text", text=(
                f"⚠️ Proyecto '{proj_name}' ya existe (slug: {slug}).\n"
                f"Cargado como proyecto activo. Usa load_project para retomarlo "
                f"o elige otro nombre para crear uno nuevo."
            ))]

        data = {
            "name": proj_name,
            "slug": slug,
            "created": str(date.today()),
            "last_updated": str(date.today()),
            "production": {
                "genre": genre,
                "bpm": bpm,
                "root_note": root_note,
                "mode": mode,
                "reference": reference,
            },
            "tracks": [],
            "arrangement": {},
            "mixing": {"status": "pending", "todo": []},
            "notes": notes,
        }
        _save_project_file(data)
        set_active_project(data)

        send_osc("/live/song/set/tempo", float(bpm))

        proj_dir = _project_path(slug)
        (proj_dir / "session.md").write_text(
            f"# {proj_name}\n\n"
            f"**Género:** {genre}  \n"
            f"**BPM:** {bpm}  \n"
            f"**Tonalidad:** {root_note} {mode}  \n"
            f"**Referencia:** {reference}  \n\n"
            f"## Sesión {date.today()}\n\n{notes}\n"
        )

        return [types.TextContent(type="text", text=(
            f"✅ Proyecto '{proj_name}' creado\n"
            f"📁 Carpeta: ableton-mcp/projects/{slug}/\n"
            f"🎵 BPM seteado a {bpm}\n"
            f"🎼 Tonalidad: {root_note} {mode}\n\n"
            f"Archivos creados:\n"
            f"  • project.json — contexto completo\n"
            f"  • session.md   — notas de sesión\n\n"
            f"Próximo paso: crea los tracks con create_midi_track y "
            f"carga los instrumentos con load_instrument."
        ))]

    elif name == "load_project":
        proj_name = arguments["name"]
        slug = _slug(proj_name)
        data = _load_project_file(slug)
        if data is None:
            projects = [p.name for p in PROJECTS_DIR.iterdir() if p.is_dir()]
            return [types.TextContent(type="text", text=(
                f"❌ Proyecto '{proj_name}' no encontrado (slug: {slug}).\n"
                f"Proyectos disponibles: {', '.join(projects) or 'ninguno'}"
            ))]
        set_active_project(data)
        prod = data.get("production", {})
        tracks = data.get("tracks", [])
        track_lines = "\n".join(
            f"  [{t['index']}] {t['name']} — {t.get('instrument','?')} ({t.get('status','?')})"
            for t in tracks
        ) or "  (sin tracks guardados)"
        return [types.TextContent(type="text", text=(
            f"✅ Proyecto '{data['name']}' cargado\n"
            f"🎵 BPM: {prod.get('bpm','?')} | Tonalidad: {prod.get('root_note','?')} {prod.get('mode','?')}\n"
            f"🎸 Género: {prod.get('genre','?')}\n"
            f"📀 Referencia: {prod.get('reference','')}\n\n"
            f"Tracks guardados:\n{track_lines}\n\n"
            f"📅 Última actualización: {data.get('last_updated','?')}"
        ))]

    elif name == "save_project_state":
        active = get_active_project()
        if active is None:
            return [types.TextContent(type="text", text=(
                "❌ No hay proyecto activo. Usa new_project o load_project primero."
            ))]
        session_notes = arguments.get("notes", "")
        active["last_updated"] = str(date.today())

        send_osc("/live/song/get/tempo")
        time.sleep(0.4)
        with osc_lock:
            tempo = osc_responses.get("/live/song/get/tempo", (None,))[0]
        if tempo:
            active["production"]["bpm"] = tempo

        _save_project_file(active)

        slug = active["slug"]
        session_file = _project_path(slug) / "session.md"
        if session_notes and session_file.exists():
            existing = session_file.read_text()
            session_file.write_text(
                existing + f"\n### Update {date.today()}\n{session_notes}\n"
            )

        return [types.TextContent(type="text", text=(
            f"✅ Proyecto '{active['name']}' guardado\n"
            f"📁 ableton-mcp/projects/{slug}/project.json actualizado"
        ))]

    elif name == "list_projects":
        projects = []
        for p in sorted(PROJECTS_DIR.iterdir()):
            if p.is_dir():
                data = _load_project_file(p.name)
                if data:
                    prod = data.get("production", {})
                    projects.append(
                        f"  📁 {data['name']} ({p.name})\n"
                        f"     {prod.get('genre','')} | {prod.get('bpm','')} BPM | "
                        f"{prod.get('root_note','')} {prod.get('mode','')} | "
                        f"Updated: {data.get('last_updated','?')}"
                    )
        if not projects:
            return [types.TextContent(type="text", text="No hay proyectos guardados. Usa new_project para crear uno.")]
        return [types.TextContent(type="text", text="🎵 Proyectos en ableton-mcp:\n\n" + "\n\n".join(projects))]

    # ── Plugin Registry ──────────────────────────────────────────

    elif name == "build_plugin_registry":
        force = arguments.get("force_rescan", False)
        last = get_last_scan()
        if last and not force:
            summary = list_registry_summary()
            return [types.TextContent(
                type="text",
                text=(
                    f"📦 Registry ya existe (último scan: {last})\n\n"
                    f"{summary}\n\n"
                    "Usa force_rescan=true para re-escanear."
                ),
            )]

        categories_arg = arguments.get("categories", [])
        search_terms = categories_arg if categories_arg else ["", "VST", "AU", "Max"]

        total_added = 0
        scan_log: list[str] = []

        for term in search_terms:
            send_osc("/live/browser/scan", term)
            time.sleep(2.0)

            with osc_lock:
                raw = osc_responses.get("/live/browser/scan", ())

            items = _parse_browser_items(raw)
            loadable = [it for it in items if it.get("loadable") and it.get("uri")]

            category = term or "General"
            added = add_plugins_bulk(loadable, category=category)
            total_added += added
            scan_log.append(f"  '{term}' → {len(items)} items, {added} plugins")

        from datetime import datetime
        mark_as_scanned(datetime.now().isoformat())
        summary = list_registry_summary()

        return [types.TextContent(
            type="text",
            text=(
                f"✅ Plugin Registry construido\n\n"
                f"Escaneos realizados:\n" + "\n".join(scan_log) + "\n\n"
                f"{summary}\n\n"
                "💡 Ahora puedes usar load_plugin_by_name con nombres como:\n"
                "   'Maschine 2', 'Arturia Pigments', 'Reaktor 6', 'Orbit'"
            ),
        )]

    elif name == "load_plugin_by_name":
        track_idx   = arguments["track_index"]
        plugin_name = arguments["plugin_name"].strip()

        result = find_plugin_uri(plugin_name)

        if result is None:
            matches = search_plugins(plugin_name)
            if matches:
                options = "\n".join(f"  • {m['display_name']} ({m.get('type','')})" for m in matches[:10])
                return [types.TextContent(
                    type="text",
                    text=(
                        f"⚠️ '{plugin_name}' no encontrado exactamente. ¿Quisiste decir:\n{options}\n\n"
                        "Intenta con el nombre exacto, o usa scan_plugins para ver URIs directas."
                    ),
                )]
            return [types.TextContent(
                type="text",
                text=(
                    f"❌ '{plugin_name}' no encontrado en el registry.\n\n"
                    "Ejecuta build_plugin_registry con Ableton abierto para actualizar la lista.\n"
                    "Luego usa search_plugin_registry para buscar nombres disponibles."
                ),
            )]

        plugin_uri = result["uri"]
        display    = result.get("display_name", plugin_name)

        send_osc("/live/view/set/selected_track", track_idx)
        time.sleep(0.3)
        send_osc("/live/track/load_device", track_idx, plugin_uri)
        time.sleep(1.5)

        return [types.TextContent(
            type="text",
            text=(
                f"✅ {display} cargado en Track {track_idx + 1}\n"
                f"📍 URI: {plugin_uri}\n"
                f"🏷️ Tipo: {result.get('type','')}\n"
                "💡 Usa get_track_devices para confirmar la carga.\n"
                "💡 Usa get_device_params para explorar sus parámetros."
            ),
        )]

    elif name == "search_plugin_registry":
        query = arguments["query"]
        limit = arguments.get("limit", 20)
        results = search_plugins(query, limit)

        if not results:
            summary = list_registry_summary()
            return [types.TextContent(
                type="text",
                text=(
                    f"🔍 Sin resultados para '{query}'\n\n"
                    f"Estado del registry:\n{summary}"
                ),
            )]

        lines = [f"🔍 Plugins que coinciden con '{query}':"]
        for r in results:
            lines.append(f"  • {r['display_name']}  ({r.get('type','')})")
            if r.get("uri"):
                uri_short = r["uri"][:60] + "…" if len(r["uri"]) > 60 else r["uri"]
                lines.append(f"    URI: {uri_short}")
        lines.append(f"\n💡 Usa load_plugin_by_name(track_index=N, plugin_name='<nombre>') para cargar.")
        return [types.TextContent(type="text", text="\n".join(lines))]

    # ── Track Control ─────────────────────────────────────────────

    elif name == "set_track_volume":
        track_idx = arguments["track_index"]
        volume    = float(arguments["volume"])
        send_osc("/live/track/set/volume", track_idx, volume)
        db_approx = "0 dB" if abs(volume - 0.85) < 0.01 else f"{'↑' if volume > 0.85 else '↓'} {volume:.2f}"
        return [types.TextContent(
            type="text",
            text=f"✅ Track {track_idx + 1}: volumen → {volume:.2f} ({db_approx})",
        )]

    elif name == "set_track_pan":
        track_idx = arguments["track_index"]
        pan       = float(arguments["pan"])
        send_osc("/live/track/set/panning", track_idx, pan)
        side = "C" if abs(pan) < 0.05 else ("←L" if pan < 0 else "R→")
        return [types.TextContent(
            type="text",
            text=f"✅ Track {track_idx + 1}: pan → {pan:+.2f} ({side})",
        )]

    elif name == "set_track_mute":
        track_idx = arguments["track_index"]
        muted     = bool(arguments["muted"])
        send_osc("/live/track/set/mute", track_idx, int(muted))
        return [types.TextContent(
            type="text",
            text=f"✅ Track {track_idx + 1}: {'🔇 muteado' if muted else '🔊 activo'}",
        )]

    elif name == "set_track_solo":
        track_idx = arguments["track_index"]
        solo      = bool(arguments["solo"])
        send_osc("/live/track/set/solo", track_idx, int(solo))
        return [types.TextContent(
            type="text",
            text=f"✅ Track {track_idx + 1}: solo {'🟡 ON' if solo else 'OFF'}",
        )]

    elif name == "arm_track":
        track_idx = arguments["track_index"]
        armed     = bool(arguments["armed"])
        send_osc("/live/track/set/arm", track_idx, int(armed))
        return [types.TextContent(
            type="text",
            text=f"✅ Track {track_idx + 1}: {'🔴 armado para grabación' if armed else 'desarmado'}",
        )]

    elif name == "set_track_name":
        track_idx = arguments["track_index"]
        new_name  = arguments["name"]
        send_osc("/live/track/set/name", track_idx, new_name)
        return [types.TextContent(
            type="text",
            text=f"✅ Track {track_idx + 1} renombrado a '{new_name}'",
        )]

    elif name == "set_track_color":
        track_idx = arguments["track_index"]
        color     = int(arguments["color"])
        send_osc("/live/track/set/color", track_idx, color)
        return [types.TextContent(
            type="text",
            text=f"✅ Track {track_idx + 1}: color → #{color:06X}",
        )]

    elif name == "get_track_info":
        track_idx = arguments["track_index"]

        send_osc("/live/track/get/name",   track_idx)
        send_osc("/live/track/get/volume", track_idx)
        send_osc("/live/track/get/panning", track_idx)
        send_osc("/live/track/get/mute",   track_idx)
        send_osc("/live/track/get/solo",   track_idx)
        send_osc("/live/track/get/arm",    track_idx)
        send_osc("/live/track/get/num_devices", track_idx)
        time.sleep(0.6)

        with osc_lock:
            name_val   = osc_responses.get("/live/track/get/name",   ("?",))[0]
            volume_val = osc_responses.get("/live/track/get/volume", ("?",))[0]
            pan_val    = osc_responses.get("/live/track/get/panning", ("?",))[0]
            mute_val   = osc_responses.get("/live/track/get/mute",   (0,))[0]
            solo_val   = osc_responses.get("/live/track/get/solo",   (0,))[0]
            arm_val    = osc_responses.get("/live/track/get/arm",    (0,))[0]
            ndev_val   = osc_responses.get("/live/track/get/num_devices", (0,))[0]

        return [types.TextContent(
            type="text",
            text=(
                f"📊 Track {track_idx + 1}: {name_val}\n"
                f"  Volume : {volume_val}\n"
                f"  Pan    : {pan_val}\n"
                f"  Mute   : {'🔇 sí' if int(mute_val) else 'no'}\n"
                f"  Solo   : {'🟡 sí' if int(solo_val) else 'no'}\n"
                f"  Arm    : {'🔴 sí' if int(arm_val) else 'no'}\n"
                f"  Devices: {ndev_val}"
            ),
        )]

    elif name == "set_track_send":
        track_idx  = arguments["track_index"]
        send_idx   = arguments["send_index"]
        value      = float(arguments["value"])
        send_osc("/live/track/set/send", track_idx, send_idx, value)
        return_letter = chr(ord('A') + send_idx)
        return [types.TextContent(
            type="text",
            text=f"✅ Track {track_idx + 1} → Return {return_letter}: {value:.2f}",
        )]

    elif name == "create_audio_track":
        idx        = arguments.get("track_index", -1)
        track_name = arguments.get("name", "Audio Track")
        send_osc("/live/song/create_audio_track", idx)
        time.sleep(0.3)
        return [types.TextContent(
            type="text",
            text=f"✅ Track de audio '{track_name}' creado en posición {idx}",
        )]

    # ── Clip & Scene Control ────────────────────────────────────

    elif name == "trigger_clip":
        track_idx = arguments["track_index"]
        scene_idx = arguments["scene_index"]
        send_osc("/live/clip_slot/fire", track_idx, scene_idx)
        return [types.TextContent(
            type="text",
            text=f"▶️ Clip disparado — Track {track_idx + 1}, Escena {scene_idx + 1}",
        )]

    elif name == "stop_clip":
        track_idx = arguments["track_index"]
        scene_idx = arguments["scene_index"]
        send_osc("/live/clip_slot/stop", track_idx, scene_idx)
        return [types.TextContent(
            type="text",
            text=f"⏹️ Clip detenido — Track {track_idx + 1}, Escena {scene_idx + 1}",
        )]

    elif name == "trigger_scene":
        scene_idx = arguments["scene_index"]
        send_osc("/live/song/trigger_scene", scene_idx)
        return [types.TextContent(
            type="text",
            text=f"▶️ Escena {scene_idx + 1} disparada",
        )]

    # ── Session ──────────────────────────────────────────────────

    elif name == "set_time_signature":
        numerator   = int(arguments["numerator"])
        denominator = int(arguments["denominator"])
        send_osc("/live/song/set/signature_numerator",   numerator)
        send_osc("/live/song/set/signature_denominator", denominator)
        return [types.TextContent(
            type="text",
            text=f"✅ Compás cambiado a {numerator}/{denominator}",
        )]

    elif name == "get_ableton_version":
        send_osc("/live/application/get/version")
        time.sleep(0.5)
        with osc_lock:
            version_raw = osc_responses.get("/live/application/get/version", ())
        version_str = " ".join(str(v) for v in version_raw) if version_raw else "desconocida"
        registry_summary = list_registry_summary()
        return [types.TextContent(
            type="text",
            text=(
                f"🎛️ Ableton Live\n"
                f"  Versión: {version_str}\n"
                f"  OSC: conectado (puerto 11000/11001)\n\n"
                f"Estado del Plugin Registry:\n{registry_summary}"
            ),
        )]

    else:
        return [types.TextContent(type="text", text=f"❌ Herramienta '{name}' no reconocida")]


# ── Entry point ──────────────────────────────────────────────

async def main():
    init_osc_client()
    start_osc_listener()
    logger.info("🎛️ Ableton MCP Server iniciado — esperando conexiones...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
