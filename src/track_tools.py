"""
track_tools.py — Ableton Live MCP Server
Handlers de control de tracks: volumen, pan, mute, solo, arm, nombre, color, sends.
"""

import time

from mcp import types

from osc_client import send_osc, osc_lock, osc_responses


def create_midi_track(arguments: dict) -> list[types.TextContent]:
    idx = arguments.get("track_index", -1)
    track_name = arguments.get("name", "MIDI Track")
    send_osc("/live/song/create_midi_track", idx)
    time.sleep(0.3)
    return [types.TextContent(type="text", text=f"✅ Track MIDI '{track_name}' creado en posición {idx}")]


def create_audio_track(arguments: dict) -> list[types.TextContent]:
    idx        = arguments.get("track_index", -1)
    track_name = arguments.get("name", "Audio Track")
    send_osc("/live/song/create_audio_track", idx)
    time.sleep(0.3)
    return [types.TextContent(
        type="text",
        text=f"✅ Track de audio '{track_name}' creado en posición {idx}",
    )]


def set_track_volume(arguments: dict) -> list[types.TextContent]:
    track_idx = arguments["track_index"]
    volume    = float(arguments["volume"])
    send_osc("/live/track/set/volume", track_idx, volume)
    db_approx = "0 dB" if abs(volume - 0.85) < 0.01 else f"{'↑' if volume > 0.85 else '↓'} {volume:.2f}"
    return [types.TextContent(
        type="text",
        text=f"✅ Track {track_idx + 1}: volumen → {volume:.2f} ({db_approx})",
    )]


def set_track_pan(arguments: dict) -> list[types.TextContent]:
    track_idx = arguments["track_index"]
    pan       = float(arguments["pan"])
    send_osc("/live/track/set/panning", track_idx, pan)
    side = "C" if abs(pan) < 0.05 else ("←L" if pan < 0 else "R→")
    return [types.TextContent(
        type="text",
        text=f"✅ Track {track_idx + 1}: pan → {pan:+.2f} ({side})",
    )]


def set_track_mute(arguments: dict) -> list[types.TextContent]:
    track_idx = arguments["track_index"]
    muted     = bool(arguments["muted"])
    send_osc("/live/track/set/mute", track_idx, int(muted))
    return [types.TextContent(
        type="text",
        text=f"✅ Track {track_idx + 1}: {'🔇 muteado' if muted else '🔊 activo'}",
    )]


def set_track_solo(arguments: dict) -> list[types.TextContent]:
    track_idx = arguments["track_index"]
    solo      = bool(arguments["solo"])
    send_osc("/live/track/set/solo", track_idx, int(solo))
    return [types.TextContent(
        type="text",
        text=f"✅ Track {track_idx + 1}: solo {'🟡 ON' if solo else 'OFF'}",
    )]


def arm_track(arguments: dict) -> list[types.TextContent]:
    track_idx = arguments["track_index"]
    armed     = bool(arguments["armed"])
    send_osc("/live/track/set/arm", track_idx, int(armed))
    return [types.TextContent(
        type="text",
        text=f"✅ Track {track_idx + 1}: {'🔴 armado para grabación' if armed else 'desarmado'}",
    )]


def set_track_name(arguments: dict) -> list[types.TextContent]:
    track_idx = arguments["track_index"]
    new_name  = arguments["name"]
    send_osc("/live/track/set/name", track_idx, new_name)
    return [types.TextContent(
        type="text",
        text=f"✅ Track {track_idx + 1} renombrado a '{new_name}'",
    )]


def set_track_color(arguments: dict) -> list[types.TextContent]:
    track_idx = arguments["track_index"]
    color     = int(arguments["color"])
    send_osc("/live/track/set/color", track_idx, color)
    return [types.TextContent(
        type="text",
        text=f"✅ Track {track_idx + 1}: color → #{color:06X}",
    )]


def get_track_info(arguments: dict) -> list[types.TextContent]:
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


def set_track_send(arguments: dict) -> list[types.TextContent]:
    track_idx  = arguments["track_index"]
    send_idx   = arguments["send_index"]
    value      = float(arguments["value"])
    send_osc("/live/track/set/send", track_idx, send_idx, value)
    return_letter = chr(ord('A') + send_idx)
    return [types.TextContent(
        type="text",
        text=f"✅ Track {track_idx + 1} → Return {return_letter}: {value:.2f}",
    )]


HANDLERS = {
    "create_midi_track": create_midi_track,
    "create_audio_track": create_audio_track,
    "set_track_volume": set_track_volume,
    "set_track_pan": set_track_pan,
    "set_track_mute": set_track_mute,
    "set_track_solo": set_track_solo,
    "arm_track": arm_track,
    "set_track_name": set_track_name,
    "set_track_color": set_track_color,
    "get_track_info": get_track_info,
    "set_track_send": set_track_send,
}
