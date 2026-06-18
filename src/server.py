"""
Ableton Live MCP Server
Conecta Claude con Ableton Live via AbletonOSC
"""

import asyncio
import json
import logging
import os
import re
from datetime import date
from pathlib import Path
from typing import Any
from pythonosc import udp_client, dispatcher, osc_server
import threading
import time

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ableton-mcp")

# ── Proyectos ────────────────────────────────────────────────
PROJECTS_DIR = Path(__file__).parent.parent / "projects"
PROJECTS_DIR.mkdir(exist_ok=True)
_active_project: dict | None = None

def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def _project_path(slug: str) -> Path:
    return PROJECTS_DIR / slug

def _load_project_file(slug: str) -> dict | None:
    p = _project_path(slug) / "project.json"
    if p.exists():
        return json.loads(p.read_text())
    return None

def _save_project_file(data: dict) -> None:
    slug = data["slug"]
    path = _project_path(slug)
    path.mkdir(exist_ok=True)
    (path / "project.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))
    logger.info(f"Proyecto guardado: {slug}")

# ── OSC Config ──────────────────────────────────────────────
ABLETON_HOST = "127.0.0.1"
ABLETON_SEND_PORT = 11000   # Puerto donde Ableton escucha
ABLETON_RECV_PORT = 11001   # Puerto donde recibimos respuestas

# ── Servidor MCP ────────────────────────────────────────────
app = Server("ableton-mcp")

# ── Cliente OSC global ──────────────────────────────────────
osc_client: udp_client.SimpleUDPClient | None = None
osc_responses: dict[str, Any] = {}
osc_lock = threading.Lock()


def init_osc_client():
    global osc_client
    osc_client = udp_client.SimpleUDPClient(ABLETON_HOST, ABLETON_SEND_PORT)
    logger.info(f"OSC client → {ABLETON_HOST}:{ABLETON_SEND_PORT}")


def send_osc(address: str, *args):
    """Envía un mensaje OSC a Ableton."""
    if osc_client is None:
        init_osc_client()
    logger.info(f"OSC → {address} {args}")
    osc_client.send_message(address, list(args))


def osc_response_handler(address, *args):
    with osc_lock:
        osc_responses[address] = args
    logger.info(f"OSC ← {address}: {args}")


def start_osc_listener():
    """Inicia listener para respuestas de Ableton."""
    disp = dispatcher.Dispatcher()
    disp.set_default_handler(osc_response_handler)
    server = osc_server.ThreadingOSCUDPServer(
        (ABLETON_HOST, ABLETON_RECV_PORT), disp
    )
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    logger.info(f"OSC listener en puerto {ABLETON_RECV_PORT}")


# ── Helpers musicales ────────────────────────────────────────

# Notas cromáticas
CHROMATIC = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

NOTE_TO_MIDI = {note: i for i, note in enumerate(CHROMATIC)}
NOTE_TO_MIDI.update({"Db": 1, "Eb": 3, "Gb": 6, "Ab": 8, "Bb": 10})

# Escalas definidas por intervalos en semitonos desde la raíz
SCALES = {
    "major":            [0, 2, 4, 5, 7, 9, 11],
    "minor":            [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor":   [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor":    [0, 2, 3, 5, 7, 9, 11],
    "dorian":           [0, 2, 3, 5, 7, 9, 10],
    "phrygian":         [0, 1, 3, 5, 7, 8, 10],
    "lydian":           [0, 2, 4, 6, 7, 9, 11],
    "mixolydian":       [0, 2, 4, 5, 7, 9, 10],
    "locrian":          [0, 1, 3, 5, 6, 8, 10],
    "pentatonic_minor": [0, 3, 5, 7, 10],
    "pentatonic_major": [0, 2, 4, 7, 9],
    "blues":            [0, 3, 5, 6, 7, 10],
    "whole_tone":       [0, 2, 4, 6, 8, 10],
    "diminished":       [0, 2, 3, 5, 6, 8, 9, 11],
    "phrygian_dominant": [0, 1, 4, 5, 7, 8, 10],
    "hungarian_minor":  [0, 2, 3, 6, 7, 8, 11],
    "double_harmonic":  [0, 1, 4, 5, 7, 8, 11],
}

# Tipos de acorde por intervalos en semitonos
CHORD_TYPES = {
    "maj":      [0, 4, 7],
    "min":      [0, 3, 7],
    "maj7":     [0, 4, 7, 11],
    "min7":     [0, 3, 7, 10],
    "dom7":     [0, 4, 7, 10],
    "maj9":     [0, 4, 7, 11, 14],
    "min9":     [0, 3, 7, 10, 14],
    "add9":     [0, 4, 7, 14],
    "dim":      [0, 3, 6],
    "dim7":     [0, 3, 6, 9],
    "aug":      [0, 4, 8],
    "sus2":     [0, 2, 7],
    "sus4":     [0, 5, 7],
    "min11":    [0, 3, 7, 10, 14, 17],
    "maj7s11":  [0, 4, 7, 11, 18],
    "dom9":     [0, 4, 7, 10, 14],
    "half_dim": [0, 3, 6, 10],
}

# Progresiones por género definidas como grados de escala (0-based) y tipo de acorde.
# Formato: [ (grado, tipo_acorde), ... ]
GENRE_PATTERNS = {
    # ── HOUSE ──────────────────────────────────────────────
    "house":            [(0, "min"), (5, "maj"), (2, "maj"), (4, "maj")],
    "deep_house":       [(0, "min7"), (3, "min7"), (4, "dom7"), (2, "maj7")],
    "afro_house":       [(0, "min7"), (4, "min7"), (5, "maj7"), (6, "dom7")],
    "tech_house":       [(0, "min7"), (6, "maj"), (0, "min7"), (4, "dom7")],
    "garage_house":     [(0, "min7"), (5, "maj7"), (6, "dom7"), (4, "min7")],

    # ── TECHNO ─────────────────────────────────────────────
    "techno":           [(0, "min"), (4, "min"), (3, "min"), (0, "min")],
    "detroit_techno":   [(0, "min7"), (3, "min7"), (6, "maj7"), (0, "min7")],
    "industrial_techno": [(0, "min"), (6, "dim"), (0, "min"), (5, "min")],
    "minimal_techno":   [(0, "min"), (0, "min"), (6, "maj"), (0, "min")],
    "melodic_techno":   [(0, "min7"), (5, "maj7"), (2, "maj7"), (6, "dom7")],

    # ── TRANCE ─────────────────────────────────────────────
    "trance":           [(0, "min"), (5, "maj"), (2, "maj"), (6, "maj")],
    "progressive_trance": [(0, "min7"), (5, "maj7"), (2, "maj7"), (4, "min7")],
    "psytrance":        [(0, "min"), (0, "min"), (6, "maj"), (5, "maj")],
    "uplifting_trance": [(0, "min"), (5, "maj"), (3, "min"), (6, "maj")],

    # ── DRUM AND BASS ───────────────────────────────────────
    "drum_and_bass":    [(0, "min7"), (6, "maj7"), (5, "maj7"), (4, "dom7")],
    "liquid_dnb":       [(0, "maj7"), (5, "maj7"), (3, "min7"), (6, "dom7")],
    "neurofunk":        [(0, "min7"), (6, "dim7"), (5, "min7"), (0, "min7")],
    "jungle":           [(0, "min"), (6, "maj"), (5, "maj"), (4, "dom7")],
    "halftime":         [(0, "min7"), (5, "maj7"), (3, "min7"), (4, "dom7")],

    # ── HIP HOP ────────────────────────────────────────────
    "hip_hop":          [(0, "min7"), (6, "maj7"), (5, "maj7"), (4, "dom7")],
    "lo_fi":            [(0, "maj7"), (5, "maj7"), (1, "min7"), (4, "dom7")],
    "boom_bap":         [(0, "min7"), (3, "min7"), (4, "dom7"), (0, "min7")],
    "trap":             [(0, "min"), (5, "maj"), (6, "maj"), (0, "min")],
    "drill":            [(0, "min"), (6, "dim"), (6, "maj"), (0, "min")],
    "phonk":            [(0, "min"), (5, "maj"), (0, "min"), (4, "dom7")],
    "cloud_rap":        [(0, "maj7"), (5, "maj7"), (2, "maj7"), (4, "min7")],

    # ── R&B / SOUL / FUNK ───────────────────────────────────
    "rnb":              [(0, "min7"), (3, "min7"), (6, "dom7"), (2, "maj7")],
    "neo_soul":         [(0, "min9"), (3, "min9"), (6, "dom7"), (2, "maj9")],
    "funk":             [(0, "min7"), (3, "dom7"), (0, "min7"), (4, "dom7")],
    "soul":             [(0, "min7"), (5, "maj7"), (3, "min7"), (4, "dom7")],
    "gospel":           [(0, "maj7"), (3, "maj7"), (4, "dom7"), (0, "maj7")],

    # ── REGGAE / DUB ───────────────────────────────────────
    "reggae":           [(0, "min7"), (3, "min7"), (4, "dom7"), (0, "min7")],
    "dancehall":        [(0, "min"), (5, "maj"), (6, "maj"), (4, "dom7")],
    "dub":              [(0, "min7"), (6, "maj7"), (0, "min7"), (4, "dom7")],
    "roots_reggae":     [(0, "min7"), (3, "min7"), (4, "dom7"), (5, "maj7")],

    # ── JAZZ ───────────────────────────────────────────────
    "jazz":             [(1, "min7"), (4, "dom7"), (0, "maj7"), (3, "maj7")],
    "jazz_fusion":      [(1, "min9"), (4, "dom7"), (0, "maj9"), (3, "maj7")],
    "bossa_nova":       [(1, "min7"), (4, "dom7"), (0, "maj7"), (4, "dom7")],
    "bebop":            [(1, "min7"), (4, "dom7"), (0, "maj7"), (5, "dom7")],
    "modal_jazz":       [(0, "min7"), (0, "min7"), (1, "min7"), (0, "min7")],

    # ── AMBIENT / ELECTRÓNICA ──────────────────────────────
    "ambient":          [(0, "maj7"), (5, "maj7"), (2, "maj7"), (6, "maj7")],
    "dark_ambient":     [(0, "min"), (6, "dim"), (0, "min"), (6, "dim")],
    "idm":              [(0, "min7"), (5, "maj7"), (6, "min7"), (6, "dom7")],
    "chillout":         [(0, "min7"), (5, "maj7"), (2, "maj7"), (4, "min7")],
    "downtempo":        [(0, "min7"), (3, "min7"), (6, "dom7"), (5, "maj7")],

    # ── SYNTHWAVE / ELECTRO ─────────────────────────────────
    "synthwave":        [(0, "min"), (5, "maj"), (2, "maj"), (6, "maj")],
    "darksynth":        [(0, "min"), (5, "min"), (6, "maj"), (0, "min")],
    "electro":          [(0, "min7"), (6, "maj"), (5, "maj"), (4, "dom7")],
    "future_bass":      [(0, "maj7"), (5, "maj7"), (2, "maj7"), (6, "dom7")],
    "dubstep":          [(0, "min"), (5, "maj"), (6, "maj"), (4, "dom7")],
    "riddim":           [(0, "min"), (0, "min"), (6, "maj"), (0, "min")],
    "future_garage":    [(0, "min7"), (5, "maj7"), (3, "min7"), (4, "dom7")],

    # ── POP ────────────────────────────────────────────────
    "pop":              [(0, "maj"), (4, "maj"), (5, "min"), (3, "maj")],
    "indie_pop":        [(5, "min7"), (3, "maj7"), (0, "maj"), (4, "maj")],
    "dream_pop":        [(0, "maj7"), (5, "maj7"), (2, "maj7"), (4, "min7")],
    "shoegaze":         [(0, "min"), (5, "maj"), (2, "maj"), (6, "maj")],
    "hyperpop":         [(0, "maj7"), (3, "maj7"), (5, "min7"), (4, "dom7")],

    # ── AFROBEATS / GLOBAL ──────────────────────────────────
    "afrobeats":        [(0, "min7"), (5, "maj7"), (6, "dom7"), (4, "min7")],
    "afrobeat":         [(0, "min7"), (3, "dom7"), (0, "min7"), (6, "dom7")],
    "amapiano":         [(0, "min7"), (3, "min7"), (6, "dom7"), (2, "maj7")],
    "baile_funk":       [(0, "min"), (6, "maj"), (5, "maj"), (0, "min")],
    "cumbia":           [(0, "min"), (3, "min"), (4, "dom7"), (0, "min")],
    "salsa":            [(0, "min7"), (3, "min7"), (4, "dom7"), (0, "min7")],
    "dembow":           [(0, "min"), (5, "maj"), (6, "maj"), (4, "dom7")],
    "reggaeton":        [(0, "min"), (5, "maj"), (6, "maj"), (4, "dom7")],

    # ── ROCK / METAL ───────────────────────────────────────
    "rock":             [(0, "min"), (6, "maj"), (5, "maj"), (4, "dom7")],
    "indie_rock":       [(5, "min"), (3, "maj"), (0, "maj"), (4, "maj")],
    "metal":            [(0, "min"), (6, "dim"), (5, "min"), (0, "min")],
    "doom_metal":       [(0, "min"), (5, "min"), (6, "min"), (0, "min")],
    "post_rock":        [(0, "maj7"), (5, "maj7"), (2, "maj7"), (4, "min7")],
    "grunge":           [(0, "min"), (6, "maj"), (5, "maj"), (3, "maj")],

    # ── CINEMATIC ──────────────────────────────────────────
    "cinematic":        [(0, "min"), (5, "maj"), (2, "maj"), (6, "maj")],
    "orchestral":       [(0, "min"), (3, "min"), (4, "dom7"), (0, "min")],
    "neoclassical":     [(0, "min7"), (5, "maj7"), (2, "maj7"), (4, "dom7")],
    "epic":             [(0, "min"), (5, "maj"), (3, "min"), (6, "maj")],
    "horror":           [(0, "min"), (6, "dim7"), (5, "min"), (4, "dom7")],
}

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


def note_name_to_midi(note: str, octave: int) -> int:
    """Convierte nombre de nota + octava a número MIDI absoluto."""
    note = note.strip()
    base = NOTE_TO_MIDI.get(note)
    if base is None:
        base = 9  # fallback A
    return base + (octave + 1) * 12


def scale_degree_to_root(root_midi: int, scale: list[int], degree: int) -> int:
    """Obtiene la nota raíz de un grado de la escala. degree es 0-based."""
    degree = degree % len(scale)
    return root_midi + scale[degree]


def build_chord(root_midi: int, chord_type: str, velocity: int = 80, duration: float = 2.0) -> list[dict]:
    """Construye las notas de un acorde desde su raíz MIDI."""
    intervals = CHORD_TYPES.get(chord_type, CHORD_TYPES["min7"])
    return [
        {"pitch": root_midi + i, "velocity": velocity, "duration": duration}
        for i in intervals
    ]


def build_progression(
    style: str,
    key: str,
    scale_name: str = "minor",
    octave: int = 3,
    bars_per_chord: float = 2.0,
    velocity: int = 80,
) -> list[dict]:
    """
    Construye progresión MIDI desde cualquier tonalidad, escala y género.
    Transpone matemáticamente los grados del género a la clave real.
    """
    style_key = style.lower().strip().replace(" ", "_").replace("-", "_")
    pattern = GENRE_PATTERNS.get(style_key)
    if pattern is None:
        for k in GENRE_PATTERNS:
            if style_key in k or k in style_key:
                pattern = GENRE_PATTERNS[k]
                break
    if pattern is None:
        pattern = GENRE_PATTERNS["deep_house"]

    scale_key = scale_name.lower().strip().replace(" ", "_").replace("-", "_")
    scale = SCALES.get(scale_key, SCALES["minor"])

    root_midi = note_name_to_midi(key.rstrip("m"), octave)

    all_notes = []
    position = 0.0
    beat_duration = bars_per_chord * 4  # beats por acorde en 4/4

    for degree, chord_type in pattern:
        chord_root = scale_degree_to_root(root_midi, scale, degree)
        notes = build_chord(chord_root, chord_type, velocity, beat_duration)
        for note in notes:
            all_notes.append({
                "pitch":    note["pitch"],
                "velocity": note["velocity"],
                "duration": note["duration"],
                "position": position,
            })
        position += beat_duration

    return all_notes


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
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    global _active_project

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
        # Renombrar track (AbletonOSC usa track_index para esto)
        # Si es -1, asumimos que se creó al final — necesitamos el count real
        # Por ahora lo asignamos al último track conocido
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

        # Crear clip vacío
        send_osc("/live/clip_slot/create_clip", track_idx, scene_idx, clip_length)
        time.sleep(0.4)

        # Agregar notas: /live/clip/add/notes track scene [pitch pos dur vel muted ...]
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

        # Nombrar clip
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

        # Construir notas
        scale_name = arguments.get("scale", "minor")
        notes = build_progression(style, key, scale_name, octave, bars_per_chord, velocity)
        total_length = bars_per_chord * 4 * 4  # 4 acordes × bars × beats

        # Crear clip
        send_osc("/live/clip_slot/create_clip", track_idx, scene_idx, float(total_length))
        time.sleep(0.4)

        # Enviar notas
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

        # Nombre
        send_osc("/live/clip/set/name", track_idx, scene_idx, clip_name)

        # Resumen de los acordes generados
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
            num_raw    = osc_responses.get("/live/track/get/num_devices", (0,))
            names_raw  = osc_responses.get("/live/track/get/devices/name", ())
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

        # Actualizar cache con los items cargables
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
        import urllib.parse
        track_idx   = arguments["track_index"]
        sample_path = arguments["sample_path"].strip()

        # Construir URI file:// compatible con el browser de Ableton
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
            _active_project = existing
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
        _active_project = data

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
        _active_project = data
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
        if _active_project is None:
            return [types.TextContent(type="text", text=(
                "❌ No hay proyecto activo. Usa new_project o load_project primero."
            ))]
        session_notes = arguments.get("notes", "")
        _active_project["last_updated"] = str(date.today())

        # Actualizar BPM desde Ableton
        send_osc("/live/song/get/tempo")
        time.sleep(0.4)
        with osc_lock:
            tempo = osc_responses.get("/live/song/get/tempo", (None,))[0]
        if tempo:
            _active_project["production"]["bpm"] = tempo

        _save_project_file(_active_project)

        # Append to session.md
        slug = _active_project["slug"]
        session_file = _project_path(slug) / "session.md"
        if session_notes and session_file.exists():
            existing = session_file.read_text()
            session_file.write_text(
                existing + f"\n### Update {date.today()}\n{session_notes}\n"
            )

        return [types.TextContent(type="text", text=(
            f"✅ Proyecto '{_active_project['name']}' guardado\n"
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
