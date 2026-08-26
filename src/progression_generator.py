"""
progression_generator.py — Ableton Live MCP Server
Generador Würfelspiel de progresiones de acordes: mulberry32 + algoritmo de
selección determinista descrito en

  /Users/brianear/proyectos/ba-automation-forge/data/harmonic-skeletons/README.md

(secciones 2 y 3). El orden de llamadas a rng() es parte del contrato — no
reordenar ni "optimizar" sin releer esa sección primero.
"""

import math
from typing import Callable

from harmonic_skeletons import ESQUELETOS_POR_GENERO
from music_theory import build_chord, scale_degree_to_root, note_name_to_midi, SCALES


def mulberry32(seed: int) -> Callable[[], float]:
    """
    PRNG determinista mulberry32. Debe producir, bit a bit, los mismos floats
    que la implementación JavaScript de referencia (README §3) para el mismo
    seed — esto es lo único que garantiza reproducibilidad cruzada con la
    implementación JS de harmony-lab.

    NOTA (2026-08-25): al implementar esto se detectó que el bloque "Python"
    que aparecía entonces en el README §3 tenía un error de transcripción real
    (le faltaba el `^ r` final del tercer paso, y en su lugar aplicaba una
    operación distinta que colapsaba el resultado casi a cero — verificado
    empíricamente: con seed=42 los primeros 20 floats caían todos en
    [5e-6, 6e-5], nunca cerca de 1). Se reportó al orquestador y el README
    canónico ya fue corregido (ver "Corrección 2026-08-25" en esa sección).
    La implementación de abajo es un puerto bit a bit del bloque JavaScript
    de la sección 3 y coincide, verificado, con el bloque Python ya corregido
    del README — no es una reescritura "a mi manera".
    """
    state = {"t": seed & 0xFFFFFFFF}

    def imul(a: int, b: int) -> int:
        return (a * b) & 0xFFFFFFFF

    def rng() -> float:
        state["t"] = (state["t"] + 0x6D2B79F5) & 0xFFFFFFFF
        t = state["t"]
        r = imul(t ^ (t >> 15), 1 | t)
        r = (r + imul(r ^ (r >> 7), 61 | r)) ^ r
        r &= 0xFFFFFFFF
        return ((r ^ (r >> 14)) & 0xFFFFFFFF) / 4294967296

    return rng


class GeneroNoEncontradoError(ValueError):
    """El género pedido no existe en ESQUELETOS_POR_GENERO. No hay fallback."""


def _elegir_esqueleto_y_acordes(
    genero: str,
    creativity_level: float = 0.0,
    seed: int = 0,
    semicadencia: bool = False,
) -> tuple[str, list[tuple[int, str]]]:
    """
    Implementa el algoritmo Würfelspiel de la sección 2 del README, paso a
    paso, en el orden exacto de llamadas a rng() ahí descrito. Devuelve
    (skeleton_id, resultado) donde resultado es la lista de (grado, tipo_acorde)
    elegida — sin convertir a MIDI todavía.
    """
    genero_data = ESQUELETOS_POR_GENERO.get(genero)
    if genero_data is None:
        raise GeneroNoEncontradoError(
            f"Género '{genero}' no está en ESQUELETOS_POR_GENERO. "
            "No hay fallback a otro género — agrégalo primero al contrato canónico "
            "(ba-automation-forge/data/harmonic-skeletons/skeletons.json)."
        )

    creativity_level = max(0.0, min(1.0, creativity_level))

    rng = mulberry32(seed)

    skeletons = genero_data["esqueletos"]
    skel_idx = math.floor(rng() * len(skeletons))  # paso 3: SIEMPRE 1 llamada
    skeleton = skeletons[skel_idx]
    slots = list(skeleton["slots"])  # copia — nunca mutar el dato canónico

    if semicadencia:
        slots[-1] = "D"  # paso 5: sustitución fija, no consume rng()

    opciones_por_funcion = genero_data["opciones_por_funcion"]
    resultado: list[tuple[int, str]] = []

    for funcion in slots:
        opciones = opciones_por_funcion[funcion]
        if len(opciones) == 1:
            elegido = opciones[0]  # 0 llamadas a rng()
        else:
            r = rng()  # 1 llamada
            if r < (1 - creativity_level):
                elegido = opciones[0]
            else:
                idx = 1 + math.floor(rng() * (len(opciones) - 1))  # 1 llamada más
                elegido = opciones[idx]
        resultado.append(elegido)

    return skeleton["id"], resultado


def generate_progression(
    genero: str,
    key: str,
    scale: str | None = None,
    creativity_level: float = 0.0,
    seed: int = 0,
    semicadencia: bool = False,
    octave: int = 3,
    velocity: int = 80,
    bars_per_chord: float = 2.0,
) -> dict:
    """
    Genera una progresión de acordes Würfelspiel para `genero`, transpuesta a
    `key`/`scale`, y devuelve tanto la selección abstracta (grado, tipo_acorde)
    como las notas MIDI resultantes (mismo shape que build_progression, pero
    con len(resultado) acordes en vez de 4 fijos).

    Lanza GeneroNoEncontradoError si `genero` no está en el contrato canónico
    — nunca cae a otro género en silencio (a diferencia de build_progression).
    """
    genero_data = ESQUELETOS_POR_GENERO.get(genero)
    if genero_data is None:
        raise GeneroNoEncontradoError(
            f"Género '{genero}' no está en ESQUELETOS_POR_GENERO. "
            "No hay fallback a otro género — agrégalo primero al contrato canónico "
            "(ba-automation-forge/data/harmonic-skeletons/skeletons.json)."
        )

    scale_name = scale if scale is not None else genero_data["escala_default"]
    scale_intervals = SCALES.get(scale_name)
    if scale_intervals is None:
        raise ValueError(f"Escala '{scale_name}' no existe en SCALES (music_theory.py).")

    skeleton_id, grados_acordes = _elegir_esqueleto_y_acordes(
        genero, creativity_level=creativity_level, seed=seed, semicadencia=semicadencia
    )

    root_midi = note_name_to_midi(key.rstrip("m"), octave)
    beat_duration = bars_per_chord * 4  # beats por acorde en 4/4, igual que build_progression

    notas: list[dict] = []
    position = 0.0
    for grado, tipo_acorde in grados_acordes:
        chord_root = scale_degree_to_root(root_midi, scale_intervals, grado)
        for nota in build_chord(chord_root, tipo_acorde, velocity, beat_duration):
            notas.append({
                "pitch": nota["pitch"],
                "velocity": nota["velocity"],
                "duration": nota["duration"],
                "position": position,
            })
        position += beat_duration

    return {
        "skeleton_id": skeleton_id,
        "grados_acordes": grados_acordes,
        "notas": notas,
    }
