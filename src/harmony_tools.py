"""
harmony_tools.py — Ableton Live MCP Server
Círculo de quintas, compatibilidad de tonalidades y conducción de voces.

Cubre dos huecos que `music_theory.py` no tenía:

1. **Relaciones entre tonalidades.** Qué se mezcla con qué, por qué, y en qué
   dirección mueve la energía. Útil para encadenar loops, ordenar escenas o
   decidir a dónde modular.

2. **Conducción de voces.** `build_chord` apila desde la raíz, así que cada acorde
   salta de registro y la progresión suena a bloques. Aquí se eligen inversiones
   que minimicen el movimiento entre acordes, que es lo que hace un teclista.
"""

from itertools import product

NOTE_TO_PC = {
    "C": 0, "B#": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "Fb": 4, "F": 5, "E#": 5, "F#": 6, "Gb": 6, "G": 7,
    "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11, "Cb": 11,
}
PC_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Posición en el círculo de quintas, contando desde Do: C G D A E B F# Db Ab Eb Bb F
CIRCLE_POSITION = {(7 * step) % 12: step for step in range(12)}

MAJOR_SCALE = (0, 2, 4, 5, 7, 9, 11)
MINOR_SCALE = (0, 2, 3, 5, 7, 8, 10)


class HarmonyError(ValueError):
    """Entrada que no se puede interpretar como tonalidad o acorde."""


def parse_key(key: str) -> tuple[int, str]:
    """'F#m', 'Bb major', 'Am' -> (clase de altura, 'major'|'minor')."""
    raw = str(key).strip()
    if not raw:
        raise HarmonyError("Tonalidad vacía.")
    texto = raw.replace("_", " ").strip()
    bajo = texto.lower()
    modo = "minor" if any(
        bajo.endswith(s) for s in (" m", " min", " minor", "m", "min", "minor")
    ) and not bajo.endswith("dim") else "major"
    # recortar el sufijo de modo para quedarse con la nota
    for sufijo in (" minor", " major", " min", " maj", "minor", "major", "min", "maj", "m"):
        if bajo.endswith(sufijo):
            texto = texto[: len(texto) - len(sufijo)]
            break
    nota = texto.strip().capitalize().replace("B#", "B#")
    nota = nota[0].upper() + nota[1:].replace("B", "b") if len(nota) > 1 else nota.upper()
    if nota not in NOTE_TO_PC:
        raise HarmonyError(
            f"No reconozco la nota '{raw}'. Usa C, C#, Db, D... con 'm' o 'minor' para menor."
        )
    return NOTE_TO_PC[nota], modo


def camelot(pc: int, mode: str) -> str:
    """Código Camelot, el que usan los DJ para mezclar en armonía.

    La rueda es el círculo de quintas renumerado: La menor es 8A y Do mayor 8B,
    y cada paso de quinta suma uno.
    """
    pos = CIRCLE_POSITION[pc % 12]
    numero = ((pos + 7) % 12 + 1) if mode == "major" else ((pos + 4) % 12 + 1)
    return f"{numero}{'B' if mode == 'major' else 'A'}"


def key_name(pc: int, mode: str) -> str:
    return f"{PC_NAMES[pc % 12]}{'' if mode == 'major' else 'm'}"


def relative_key(pc: int, mode: str) -> tuple[int, str]:
    """La relativa: comparte las mismas notas, cambia el centro."""
    return ((pc + 9) % 12, "minor") if mode == "major" else ((pc + 3) % 12, "major")


def key_compatibility(key: str) -> dict:
    """Con qué se mezcla una tonalidad, y qué hace cada movimiento.

    Las tres mezclables son la dominante (un paso a favor del círculo, sube la
    energía), la subdominante (un paso en contra, la baja) y la relativa (mismas
    siete notas, otro centro). Las tres caen en una casilla Camelot contigua.

    La homónima va aparte y no es una vecina: misma raíz pero otro modo, lo que
    en Camelot son SIEMPRE tres casillas de salto y solo cuatro notas compartidas
    de siete. Es intercambio modal — un recurso deliberado para un breakdown o un
    giro de color, no una mezcla que pase desapercibida. Mezclarlas como si fueran
    equivalentes es el error que esta separación evita.
    """
    pc, mode = parse_key(key)
    pos = CIRCLE_POSITION[pc]
    dominante = (pc + 7) % 12
    subdominante = (pc + 5) % 12
    rel_pc, rel_mode = relative_key(pc, mode)
    homonimo = "minor" if mode == "major" else "major"

    return {
        "tonalidad": key_name(pc, mode),
        "camelot": camelot(pc, mode),
        "posicion_en_el_circulo": pos,
        "escala": [PC_NAMES[(pc + i) % 12]
                   for i in (MAJOR_SCALE if mode == "major" else MINOR_SCALE)],
        "compatibles": [
            {"tonalidad": key_name(dominante, mode), "camelot": camelot(dominante, mode),
             "relacion": "dominante", "efecto": "sube la energía medio punto"},
            {"tonalidad": key_name(subdominante, mode), "camelot": camelot(subdominante, mode),
             "relacion": "subdominante", "efecto": "la baja, deja respirar"},
            {"tonalidad": key_name(rel_pc, rel_mode), "camelot": camelot(rel_pc, rel_mode),
             "relacion": "relativa", "efecto": "mismas notas, cambia el color"},
        ],
        "cambio_de_modo": {
            "tonalidad": key_name(pc, homonimo), "camelot": camelot(pc, homonimo),
            "relacion": "homónima",
            "efecto": "misma raíz, otro modo — 3 casillas Camelot, 4 de 7 notas en común",
            "uso": "intercambio modal: para un breakdown o un giro de color, no para mezclar sin que se note",
        },
    }


def circle_distance(key_a: str, key_b: str) -> int:
    """Pasos de quinta entre dos tonalidades, por el camino corto (0 a 6)."""
    pc_a, _ = parse_key(key_a)
    pc_b, _ = parse_key(key_b)
    bruta = abs(CIRCLE_POSITION[pc_a] - CIRCLE_POSITION[pc_b])
    return min(bruta, 12 - bruta)


def group_by_compatibility(keys: list[str]) -> list[list[str]]:
    """Agrupa tonalidades en familias que se mezclan entre sí.

    Dos tonalidades a un paso de quinta —o a la misma— conviven. Se agrupa por
    cadenas de adyacencia sobre el círculo, cerrando el anillo. Es la regla con la
    que se colorearon las escenas de la sesión de melodic techno.
    """
    if not keys:
        return []
    posiciones = sorted({CIRCLE_POSITION[parse_key(k)[0]] for k in keys})
    familias, actual = [], [posiciones[0]]
    for pos in posiciones[1:]:
        if pos - actual[-1] == 1:
            actual.append(pos)
        else:
            familias.append(actual)
            actual = [pos]
    familias.append(actual)
    if len(familias) > 1 and (posiciones[0] + 12 - posiciones[-1]) == 1:
        familias[0] = familias.pop() + familias[0]
    salida = []
    for familia in sorted(familias, key=lambda f: f[0]):
        salida.append(sorted(
            (k for k in keys if CIRCLE_POSITION[parse_key(k)[0]] in familia),
            key=lambda k: CIRCLE_POSITION[parse_key(k)[0]],
        ))
    return salida


def voice_lead(chords: list[list[int]], center: int = 60, span: int = 12) -> list[list[int]]:
    """Reescribe una progresión eligiendo la inversión que menos mueva las voces.

    `build_chord` apila desde la raíz: Do-Fa-Sol salta una cuarta arriba y una
    quinta abajo, y suena a bloques. Un teclista mueve cada voz lo mínimo. Aquí
    se prueban las octavas posibles de cada nota del acorde alrededor del registro
    anterior y se queda la combinación de menor movimiento total.

    `chords` son listas de notas MIDI (lo que devuelve build_chord). Se conserva
    el número de voces de cada acorde.
    """
    if not chords:
        return []
    salida = []
    anterior = None
    for acorde in chords:
        if not acorde:
            salida.append([])
            continue
        clases = sorted({n % 12 for n in acorde})
        octavas = range(center - span, center + span + 1, 12)
        candidatos = [sorted(set(c)) for c in product(
            *[[o + pc for o in octavas] for pc in clases]
        )]
        candidatos = [c for c in candidatos if len(c) == len(clases)]
        if anterior is None:
            objetivo = sorted(acorde)
            mejor = min(candidatos, key=lambda c: (
                sum(abs(a - b) for a, b in zip(c, objetivo[:len(c)])), c[0]))
        else:
            mejor = min(candidatos, key=lambda c: (_movimiento(anterior, c), c[0]))
        salida.append(mejor)
        anterior = mejor
    return salida


def _movimiento(previo: list[int], siguiente: list[int]) -> int:
    """Suma del salto de cada voz, emparejando de grave a agudo."""
    pares = zip(sorted(previo), sorted(siguiente))
    total = sum(abs(a - b) for a, b in pares)
    return total + abs(len(previo) - len(siguiente)) * 12
