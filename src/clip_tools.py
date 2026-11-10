"""
clip_tools.py — Ableton Live MCP Server
Handlers de clips MIDI, progresiones de acordes y control de Session View.
"""

import time

from mcp import types

from music_theory import build_progression, GENRE_PATTERNS
from osc_client import send_osc, osc_lock, osc_responses
from progression_generator import generate_progression, generate_song_structure, GeneroNoEncontradoError


def add_midi_notes(arguments: dict) -> list[types.TextContent]:
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


def add_chord_progression(arguments: dict) -> list[types.TextContent]:
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


def generate_chord_progression(arguments: dict) -> list[types.TextContent]:
    genero = arguments["genero"]
    key = arguments["key"]
    scale = arguments.get("scale")
    creativity_level = arguments.get("creativity_level", 0.0)
    seed = arguments["seed"]
    semicadencia = arguments.get("semicadencia", False)
    track_idx = arguments.get("track_index", 0)
    scene_idx = arguments.get("scene_index", 0)
    octave = arguments.get("octave", 3)
    velocity = arguments.get("velocity", 80)
    bars_per_chord = arguments.get("bars_per_chord", 2.0)
    clip_name = arguments.get("clip_name", f"{key} {genero} (seed {seed})")

    try:
        resultado = generate_progression(
            genero=genero,
            key=key,
            scale=scale,
            creativity_level=creativity_level,
            seed=seed,
            semicadencia=semicadencia,
            octave=octave,
            velocity=velocity,
            bars_per_chord=bars_per_chord,
        )
    except GeneroNoEncontradoError as error:
        return [types.TextContent(type="text", text=f"❌ {error}")]

    notes = resultado["notas"]
    n_chords = len(resultado["grados_acordes"])
    total_length = bars_per_chord * 4 * n_chords

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

    chord_summary = " → ".join(f"grado{d} {t}" for d, t in resultado["grados_acordes"])

    return [types.TextContent(
        type="text",
        text=(
            f"✅ Progresión Würfelspiel '{genero}' en {key} agregada\n"
            f"📍 Track {track_idx+1}, Escena {scene_idx+1}\n"
            f"🎲 Esqueleto: {resultado['skeleton_id']} | seed={seed} | creativity_level={creativity_level}\n"
            f"🎹 Acordes: {chord_summary}\n"
            f"⏱️ {bars_per_chord} compases por acorde | {len(notes)} notas totales"
        )
    )]


def generate_song_structure_tool(arguments: dict) -> list[types.TextContent]:
    genero = arguments["genero"]
    key = arguments["key"]
    scale = arguments.get("scale")
    seed = arguments["seed"]
    track_idx = arguments.get("track_index", 0)
    start_scene_index = arguments.get("start_scene_index", 0)
    octave = arguments.get("octave", 3)
    velocity = arguments.get("velocity", 80)
    bars_per_chord = arguments.get("bars_per_chord", 2.0)

    try:
        estructura = generate_song_structure(
            genero=genero, key=key, scale=scale, seed=seed,
            octave=octave, velocity=velocity, bars_per_chord=bars_per_chord,
        )
    except GeneroNoEncontradoError as error:
        return [types.TextContent(type="text", text=f"❌ {error}")]

    resumen_lineas = [
        f"✅ Estructura de canción Würfelspiel '{genero}' en {key} "
        f"(familia: {estructura['familia']})",
        f"📍 Track {track_idx+1}, escenas {start_scene_index+1}–"
        f"{start_scene_index+len(estructura['secciones'])}",
        f"🎲 seed base={seed} (cada sección usa seed+índice)",
        (
            "⚠️ Requiere que esas escenas ya existan en el Session View — "
            "esta tool no crea escenas nuevas, igual que add_chord_progression."
        ),
    ]

    for i, seccion in enumerate(estructura["secciones"]):
        scene_idx = start_scene_index + i
        notes = seccion["notas"]
        n_chords = len(seccion["grados_acordes"])
        total_length = bars_per_chord * 4 * n_chords
        clip_name = f"{key} {genero} — {seccion['nombre']}"

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

        chord_summary = " → ".join(f"grado{d} {t}" for d, t in seccion["grados_acordes"])
        resumen_lineas.append(
            f"  {i+1}. {seccion['nombre']} (escena {scene_idx+1}, esqueleto "
            f"{seccion['skeleton_id']}): {chord_summary}"
        )

    return [types.TextContent(type="text", text="\n".join(resumen_lineas))]


def set_clip_color(arguments: dict) -> list[types.TextContent]:
    track_idx = arguments["track_index"]
    scene_idx = arguments["scene_index"]
    color = arguments["color"]
    send_osc("/live/clip/set/color", track_idx, scene_idx, color)
    return [types.TextContent(type="text", text="✅ Color del clip actualizado")]


def trigger_clip(arguments: dict) -> list[types.TextContent]:
    track_idx = arguments["track_index"]
    scene_idx = arguments["scene_index"]
    send_osc("/live/clip_slot/fire", track_idx, scene_idx)
    return [types.TextContent(
        type="text",
        text=f"▶️ Clip disparado — Track {track_idx + 1}, Escena {scene_idx + 1}",
    )]


def stop_clip(arguments: dict) -> list[types.TextContent]:
    track_idx = arguments["track_index"]
    scene_idx = arguments["scene_index"]
    send_osc("/live/clip_slot/stop", track_idx, scene_idx)
    return [types.TextContent(
        type="text",
        text=f"⏹️ Clip detenido — Track {track_idx + 1}, Escena {scene_idx + 1}",
    )]


def get_clip_notes(arguments: dict) -> list[types.TextContent]:
    track_idx = arguments["track_index"]
    scene_idx = arguments["scene_index"]

    send_osc("/live/clip/get/notes", track_idx, scene_idx)
    time.sleep(0.4)

    with osc_lock:
        raw = list(osc_responses.get("/live/clip/get/notes", ()))[2:]

    if not raw:
        return [types.TextContent(
            type="text",
            text=(
                f"⚠️ Sin notas en Track {track_idx + 1}, Escena {scene_idx + 1}.\n"
                "El clip no existe, está vacío, o no es un clip MIDI."
            ),
        )]

    notes = []
    for i in range(0, len(raw), 5):
        pitch, start_time, duration, velocity, mute = raw[i:i + 5]
        notes.append({
            "pitch": int(pitch),
            "position": float(start_time),
            "duration": float(duration),
            "velocity": int(velocity),
            "muted": bool(mute),
        })

    lines = [f"🎵 {len(notes)} notas — Track {track_idx + 1}, Escena {scene_idx + 1}:"]
    for n in notes:
        mute_flag = " (muted)" if n["muted"] else ""
        lines.append(
            f"  pitch={n['pitch']:>3} pos={n['position']:.2f} dur={n['duration']:.2f} "
            f"vel={n['velocity']}{mute_flag}"
        )

    return [types.TextContent(type="text", text="\n".join(lines))]


def trigger_scene(arguments: dict) -> list[types.TextContent]:
    scene_idx = arguments["scene_index"]
    send_osc("/live/song/trigger_scene", scene_idx)
    return [types.TextContent(
        type="text",
        text=f"▶️ Escena {scene_idx + 1} disparada",
    )]


HANDLERS = {
    "add_midi_notes": add_midi_notes,
    "add_chord_progression": add_chord_progression,
    "generate_chord_progression": generate_chord_progression,
    "generate_song_structure": generate_song_structure_tool,
    "set_clip_color": set_clip_color,
    "get_clip_notes": get_clip_notes,
    "trigger_clip": trigger_clip,
    "stop_clip": stop_clip,
    "trigger_scene": trigger_scene,
}
