"""
device_tools.py — Ableton Live MCP Server
Handlers de instrumentos, plugins y parámetros de devices.
"""

import time
import urllib.parse

from mcp import types

from osc_client import send_osc, osc_lock, osc_responses
from plugin_registry import normalize_name, _parse_browser_items

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

# Cache del browser de plugins (poblado por scan_plugins)
_plugin_cache: dict[str, str] = {}    # nombre_normalizado → uri
_plugin_display: dict[str, str] = {}  # nombre_normalizado → nombre para mostrar


def load_instrument(arguments: dict) -> list[types.TextContent]:
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


def get_device_params(arguments: dict) -> list[types.TextContent]:
    track_idx = arguments["track_index"]
    device_idx = arguments.get("device_index", 0)

    send_osc("/live/device/get/parameters/name", track_idx, device_idx)
    time.sleep(0.5)
    send_osc("/live/device/get/parameters/value", track_idx, device_idx)
    time.sleep(0.3)

    with osc_lock:
        names = list(osc_responses.get("/live/device/get/parameters/name", ()))[2:]
        values = list(osc_responses.get("/live/device/get/parameters/value", ()))[2:]

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


def set_device_param(arguments: dict) -> list[types.TextContent]:
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


def set_device_params_bulk(arguments: dict) -> list[types.TextContent]:
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


def get_track_devices(arguments: dict) -> list[types.TextContent]:
    track_idx = arguments["track_index"]

    send_osc("/live/track/get/num_devices", track_idx)
    time.sleep(0.3)
    send_osc("/live/track/get/devices/name", track_idx)
    time.sleep(0.3)
    send_osc("/live/track/get/devices/class_name", track_idx)
    time.sleep(0.3)

    with osc_lock:
        num_raw     = osc_responses.get("/live/track/get/num_devices", (0, 0))
        names_raw   = osc_responses.get("/live/track/get/devices/name", ())[1:]
        classes_raw = osc_responses.get("/live/track/get/devices/class_name", ())[1:]

    num_devices = int(num_raw[1]) if len(num_raw) > 1 else 0

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


def scan_plugins(arguments: dict) -> list[types.TextContent]:
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
            key = normalize_name(it["name"])
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


def load_plugin(arguments: dict) -> list[types.TextContent]:
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


def load_sample(arguments: dict) -> list[types.TextContent]:
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


HANDLERS = {
    "load_instrument": load_instrument,
    "get_device_params": get_device_params,
    "set_device_param": set_device_param,
    "set_device_params_bulk": set_device_params_bulk,
    "get_track_devices": get_track_devices,
    "scan_plugins": scan_plugins,
    "load_plugin": load_plugin,
    "load_sample": load_sample,
}
