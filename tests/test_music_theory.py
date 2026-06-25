import sys
sys.path.insert(0, "src")

import pytest
from music_theory import (
    note_name_to_midi, scale_degree_to_root, build_chord, build_progression,
    SCALES, NOTE_TO_MIDI, CHORD_TYPES, GENRE_PATTERNS,
)


def test_note_to_midi_c4():
    assert note_name_to_midi("C", 4) == 60


def test_note_to_midi_a4():
    assert note_name_to_midi("A", 4) == 69


def test_note_to_midi_fsharp3():
    assert note_name_to_midi("F#", 3) == 54


def test_note_to_midi_bb3():
    assert note_name_to_midi("Bb", 3) == 58


def test_note_to_midi_c0():
    assert note_name_to_midi("C", 0) == 12


def test_scale_c_major():
    root = note_name_to_midi("C", 4)
    scale = [root + i for i in SCALES["major"]]
    assert scale == [60, 62, 64, 65, 67, 69, 71]


def test_scale_a_minor():
    root = note_name_to_midi("A", 3)
    scale = [root + i for i in SCALES["minor"]]
    assert scale == [57, 59, 60, 62, 64, 65, 67]


def test_scale_dorian_intervals():
    assert SCALES["dorian"] == [0, 2, 3, 5, 7, 9, 10]


def test_scale_blues_intervals():
    assert SCALES["blues"] == [0, 3, 5, 6, 7, 10]


def test_scale_degree_to_root_tonic():
    root_midi = note_name_to_midi("C", 4)
    scale = SCALES["major"]
    assert scale_degree_to_root(root_midi, scale, 0) == root_midi


def test_scale_degree_to_root_fifth():
    root_midi = note_name_to_midi("C", 4)
    scale = SCALES["major"]
    # degree 4 (V) in C major → G (7 semitones up)
    assert scale_degree_to_root(root_midi, scale, 4) == root_midi + 7


def test_scale_degree_wraps():
    root_midi = note_name_to_midi("C", 4)
    scale = SCALES["major"]
    # degree 7 wraps to degree 0 (7 % 7 == 0)
    assert scale_degree_to_root(root_midi, scale, 7) == scale_degree_to_root(root_midi, scale, 0)


def test_build_chord_major():
    notes = build_chord(60, "maj")  # C major
    pitches = [n["pitch"] for n in notes]
    assert pitches == [60, 64, 67]  # C E G


def test_build_chord_minor():
    notes = build_chord(60, "min")  # C minor
    pitches = [n["pitch"] for n in notes]
    assert pitches == [60, 63, 67]  # C Eb G


def test_build_chord_maj7():
    notes = build_chord(60, "maj7")
    pitches = [n["pitch"] for n in notes]
    assert pitches == [60, 64, 67, 71]


def test_build_chord_has_velocity():
    notes = build_chord(60, "maj")
    for n in notes:
        assert "velocity" in n
        assert n["velocity"] == 80  # default


def test_build_chord_has_duration():
    notes = build_chord(60, "maj")
    for n in notes:
        assert "duration" in n
        assert n["duration"] == 2.0  # default


def test_build_chord_custom_velocity():
    notes = build_chord(60, "min", velocity=100)
    for n in notes:
        assert n["velocity"] == 100


def test_build_chord_fallback_unknown_type():
    # unknown chord type falls back to min7
    notes = build_chord(60, "unknown_chord")
    assert len(notes) == len(CHORD_TYPES["min7"])


def test_build_progression_returns_list():
    result = build_progression("deep_house", "C", "minor", octave=3, bars_per_chord=2.0)
    assert isinstance(result, list)
    assert len(result) > 0


def test_build_progression_notes_have_pitch():
    result = build_progression("deep_house", "C", "minor", octave=3, bars_per_chord=2.0)
    for note in result:
        assert "pitch" in note
        assert isinstance(note["pitch"], int)


def test_build_progression_notes_have_position():
    result = build_progression("deep_house", "C", "minor", octave=3, bars_per_chord=2.0)
    for note in result:
        assert "position" in note


def test_build_progression_four_chords():
    # deep_house has 4 chords, each a chord with notes
    result = build_progression("deep_house", "C", "minor", octave=3, bars_per_chord=2.0)
    pattern = GENRE_PATTERNS["deep_house"]
    # positions should be 4 distinct groups
    positions = sorted(set(n["position"] for n in result))
    assert len(positions) == len(pattern)


def test_build_progression_unknown_style_falls_back():
    # unknown style should not raise, falls back to deep_house
    result = build_progression("nonexistent_genre_xyz", "C", "minor")
    assert isinstance(result, list)
    assert len(result) > 0


def test_build_progression_key_transposition():
    # C and D progressions should differ in pitch
    c_notes = build_progression("house", "C", "minor", octave=3)
    d_notes = build_progression("house", "D", "minor", octave=3)
    c_pitches = [n["pitch"] for n in c_notes]
    d_pitches = [n["pitch"] for n in d_notes]
    assert c_pitches != d_pitches
    # D is 2 semitones up from C
    assert d_pitches[0] == c_pitches[0] + 2


def test_genre_patterns_all_have_four_chords():
    for genre, pattern in GENRE_PATTERNS.items():
        assert len(pattern) == 4, f"{genre} pattern length != 4"


def test_genre_patterns_chord_types_exist():
    for genre, pattern in GENRE_PATTERNS.items():
        for degree, chord_type in pattern:
            assert chord_type in CHORD_TYPES, f"{genre}: chord type '{chord_type}' not in CHORD_TYPES"
