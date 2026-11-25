"""
harmony_handlers.py — Ableton Live MCP Server
Handlers MCP para las herramientas de armonía (círculo de quintas y voces).
"""

from mcp import types

from harmony_tools import (
    HarmonyError, circle_distance, group_by_compatibility, key_compatibility,
)


def get_key_compatibility(arguments: dict) -> list[types.TextContent]:
    key = arguments.get("key", "")
    try:
        datos = key_compatibility(key)
    except HarmonyError as error:
        return [types.TextContent(type="text", text=f"❌ {error}")]

    lineas = [
        f"🎹 {datos['tonalidad']}  ·  Camelot {datos['camelot']}  ·  "
        f"posición {datos['posicion_en_el_circulo']} del círculo de quintas",
        f"   escala: {' '.join(datos['escala'])}",
        "",
        "Se mezcla con:",
    ]
    for vecina in datos["compatibles"]:
        lineas.append(
            f"   {vecina['tonalidad']:<5} {vecina['camelot']:<4} "
            f"{vecina['relacion']:<14} — {vecina['efecto']}"
        )
    modo = datos["cambio_de_modo"]
    lineas += [
        "",
        "Cambio de modo (aparte — no es una mezcla transparente):",
        f"   {modo['tonalidad']:<5} {modo['camelot']:<4} {modo['relacion']:<14} — {modo['efecto']}",
        f"   {modo['uso']}",
        "",
        "Cualquier otra queda a dos pasos o más del círculo: comparte menos notas "
        "y el cambio se oye como un choque, no como una modulación.",
    ]
    return [types.TextContent(type="text", text="\n".join(lineas))]


def group_keys_by_compatibility(arguments: dict) -> list[types.TextContent]:
    keys = arguments.get("keys") or []
    if not isinstance(keys, list) or not keys:
        return [types.TextContent(
            type="text",
            text="❌ Pasa una lista de tonalidades, por ejemplo [\"Am\", \"Dm\", \"F\"].",
        )]
    try:
        familias = group_by_compatibility([str(k) for k in keys])
    except HarmonyError as error:
        return [types.TextContent(type="text", text=f"❌ {error}")]

    lineas = [f"🎼 {len(keys)} tonalidades en {len(familias)} familia(s):", ""]
    for indice, familia in enumerate(familias, 1):
        unicas = sorted(set(familia), key=familia.index)
        lineas.append(f"   familia {indice}: {', '.join(unicas)}")
    lineas.append(
        "\nDentro de una familia se encadenan sin choque de tonalidad. Entre familias "
        "el salto se oye: resérvalo para un breakdown o un cambio de sección."
    )
    if len(familias) > 1:
        a, b = familias[0][0], familias[1][0]
        lineas.append(
            f"   (de {a} a {b} hay {circle_distance(a, b)} pasos de quinta)"
        )
    return [types.TextContent(type="text", text="\n".join(lineas))]


HANDLERS = {
    "get_key_compatibility": get_key_compatibility,
    "group_keys_by_compatibility": group_keys_by_compatibility,
}
