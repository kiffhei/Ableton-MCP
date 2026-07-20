"""
transport_tools.py — Ableton Live MCP Server
Handlers de transporte y estado general de la sesión: tempo, play/pause,
info de sesión, compás y versión de Ableton.
"""

import time

from mcp import types

from osc_client import send_osc, osc_lock, osc_responses
from plugin_registry import list_registry_summary


def set_tempo(arguments: dict) -> list[types.TextContent]:
    bpm = arguments["bpm"]
    send_osc("/live/song/set/tempo", float(bpm))
    return [types.TextContent(type="text", text=f"✅ Tempo cambiado a {bpm} BPM")]


def play_pause(arguments: dict) -> list[types.TextContent]:
    action = arguments["action"]
    if action == "play":
        send_osc("/live/song/start_playing")
    elif action == "pause":
        send_osc("/live/song/stop_playing")
    elif action == "stop":
        send_osc("/live/song/stop_playing")
        send_osc("/live/song/set/current_song_time", 0.0)
    return [types.TextContent(type="text", text=f"✅ {action.capitalize()} ejecutado")]


def get_session_info(arguments: dict) -> list[types.TextContent]:
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


def set_time_signature(arguments: dict) -> list[types.TextContent]:
    numerator   = int(arguments["numerator"])
    denominator = int(arguments["denominator"])
    send_osc("/live/song/set/signature_numerator",   numerator)
    send_osc("/live/song/set/signature_denominator", denominator)
    return [types.TextContent(
        type="text",
        text=f"✅ Compás cambiado a {numerator}/{denominator}",
    )]


def get_ableton_version(arguments: dict) -> list[types.TextContent]:
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


HANDLERS = {
    "set_tempo": set_tempo,
    "play_pause": play_pause,
    "get_session_info": get_session_info,
    "set_time_signature": set_time_signature,
    "get_ableton_version": get_ableton_version,
}
