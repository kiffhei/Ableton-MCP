"""
music_theory.py — Ableton Live MCP Server
Constantes y funciones de teoría musical: escalas, acordes, progresiones por género.
"""

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
