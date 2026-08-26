import sys
sys.path.insert(0, "src")

import pytest

from harmonic_skeletons import FUNCION_POR_GRADO, ESQUELETOS_POR_GENERO
from progression_generator import (
    mulberry32,
    generate_progression,
    _elegir_esqueleto_y_acordes,
    GeneroNoEncontradoError,
)


# ── mulberry32 ────────────────────────────────────────────────

def test_mulberry32_returns_floats_in_unit_interval():
    rng = mulberry32(42)
    values = [rng() for _ in range(50)]
    assert all(isinstance(v, float) for v in values)
    assert all(0.0 <= v < 1.0 for v in values)
    # sanity: no debe estar colapsado cerca de 0 (regresión del bug de
    # transcripción encontrado y corregido en el README canónico 2026-08-25)
    assert max(values) > 0.5


def test_mulberry32_deterministic_same_seed():
    rng_a = mulberry32(7)
    rng_b = mulberry32(7)
    assert [rng_a() for _ in range(10)] == [rng_b() for _ in range(10)]


def test_mulberry32_different_seeds_diverge():
    rng_a = mulberry32(1)
    rng_b = mulberry32(2)
    assert [rng_a() for _ in range(5)] != [rng_b() for _ in range(5)]


# ── Reproducibilidad ─────────────────────────────────────────

def test_generate_progression_reproducible_same_params():
    params = dict(
        genero="techno", key="C", scale="minor",
        creativity_level=0.5, seed=123, semicadencia=False,
    )
    r1 = generate_progression(**params)
    r2 = generate_progression(**params)
    assert r1["skeleton_id"] == r2["skeleton_id"]
    assert r1["grados_acordes"] == r2["grados_acordes"]
    assert r1["notas"] == r2["notas"]


def test_generate_progression_reproducible_three_calls():
    params = dict(genero="pop", key="G", creativity_level=0.9, seed=999, semicadencia=True)
    results = [generate_progression(**params) for _ in range(3)]
    assert all(r["grados_acordes"] == results[0]["grados_acordes"] for r in results)


# ── Cadencia (criterio de aceptación, README §2 "Regla de cadencia") ──

def test_all_skeletons_start_and_end_in_tonic():
    for genero, data in ESQUELETOS_POR_GENERO.items():
        for esqueleto in data["esqueletos"]:
            slots = esqueleto["slots"]
            assert slots[0] == "T", f"{genero}/{esqueleto['id']}: no empieza en T"
            assert slots[-1] == "T", f"{genero}/{esqueleto['id']}: no termina en T"


def test_at_least_three_skeletons_per_genre():
    for genero, data in ESQUELETOS_POR_GENERO.items():
        assert len(data["esqueletos"]) >= 3, f"{genero} tiene menos de 3 esqueletos"


# ── creativity_level = 0 ⇒ siempre opción canónica ────────────

def test_creativity_zero_always_picks_canonical_option():
    for genero, data in ESQUELETOS_POR_GENERO.items():
        for seed in range(5):
            _, resultado = _elegir_esqueleto_y_acordes(
                genero, creativity_level=0.0, seed=seed, semicadencia=False
            )
            skeleton_slots = None
            # recuperar los slots efectivamente usados no es directo aquí,
            # así que en vez de eso validamos por función: cada elegido debe
            # ser opciones_por_funcion[funcion][0] para la función a la que
            # pertenece su grado según FUNCION_POR_GRADO.
            for grado, tipo in resultado:
                funcion = FUNCION_POR_GRADO[grado]
                opciones = data["opciones_por_funcion"][funcion]
                assert (grado, tipo) == tuple(opciones[0]), (
                    f"{genero} seed={seed}: {(grado, tipo)} no es la opción canónica "
                    f"de la función '{funcion}' ({opciones[0]})"
                )


# ── Ningún grado fuera de las opciones declaradas para su función ─

def test_generated_chords_match_declared_function_options():
    for genero, data in ESQUELETOS_POR_GENERO.items():
        for creativity in (0.0, 0.3, 0.7, 1.0):
            for seed in range(5):
                _, resultado = _elegir_esqueleto_y_acordes(
                    genero, creativity_level=creativity, seed=seed, semicadencia=False
                )
                for grado, tipo in resultado:
                    funcion = FUNCION_POR_GRADO[grado]
                    opciones = data["opciones_por_funcion"][funcion]
                    assert (grado, tipo) in [tuple(o) for o in opciones], (
                        f"{genero} seed={seed} creativity={creativity}: "
                        f"({grado}, {tipo}) no está en opciones_por_funcion['{funcion}']"
                    )


# ── Género inexistente ⇒ excepción explícita, sin fallback ────

def test_unknown_genre_raises_explicit_error():
    with pytest.raises(GeneroNoEncontradoError):
        generate_progression("genero_que_no_existe_xyz", "C")


def test_unknown_genre_raises_in_internal_selector_too():
    with pytest.raises(GeneroNoEncontradoError):
        _elegir_esqueleto_y_acordes("genero_que_no_existe_xyz")


# ── Estructura de las notas MIDI generadas ────────────────────

def test_generate_progression_notes_shape():
    result = generate_progression("house", "C", "minor", seed=1)
    assert isinstance(result["notas"], list)
    assert len(result["notas"]) > 0
    for note in result["notas"]:
        assert set(note.keys()) == {"pitch", "velocity", "duration", "position"}


def test_generate_progression_length_matches_skeleton_not_hardcoded_four():
    # minimal_techno_1 slots = ["T","T","D","T"] (4), pero verificamos que el
    # cálculo de posiciones use len(resultado) real, no una constante.
    result = generate_progression("minimal_techno", "C", "minor", seed=1)
    n_chords = len(result["grados_acordes"])
    positions = sorted(set(n["position"] for n in result["notas"]))
    assert len(positions) == n_chords


def test_semicadencia_overrides_last_slot_to_dominant():
    _, resultado_normal = _elegir_esqueleto_y_acordes(
        "trance", creativity_level=0.0, seed=5, semicadencia=False
    )
    _, resultado_semicadencia = _elegir_esqueleto_y_acordes(
        "trance", creativity_level=0.0, seed=5, semicadencia=True
    )
    ultimo_grado, ultimo_tipo = resultado_semicadencia[-1]
    assert FUNCION_POR_GRADO[ultimo_grado] == "D"
    # mismo esqueleto elegido (semicadencia no consume rng() en el paso 5)
    assert len(resultado_normal) == len(resultado_semicadencia)


# ── Vector de verificación cruzada obligatorio (README §5) ────
#
# genero="deep_house", key="A", scale="minor", seed=42, creativity_level=0.7,
# semicadencia=False
#
# Resultado exacto obtenido con esta implementación (ableton-mcp / Python),
# recalculado el 2026-08-25 después de ampliar el dataset canónico de 20 a
# 76 géneros y corregir la repetición estructural de esqueletos (ver README
# §1 y §2) — el vector anterior a esa ampliación ya no aplica, el dataset
# cambió. harmony-lab (JS) debe reproducir byte a byte esta misma secuencia:
#
#   skeleton_id: "deep_house_2"
#   grados_acordes: [(2, "maj7"), (2, "maj7"), (6, "dom7"), (2, "maj7")]
#
def test_cross_verification_vector_deep_house_seed_42():
    skeleton_id, resultado = _elegir_esqueleto_y_acordes(
        "deep_house", creativity_level=0.7, seed=42, semicadencia=False
    )
    assert skeleton_id == "deep_house_2"
    assert resultado == [(2, "maj7"), (2, "maj7"), (6, "dom7"), (2, "maj7")]

    # y a través de la función pública completa (incluye key/scale, no debería
    # afectar la selección abstracta de grados/acordes)
    full = generate_progression(
        genero="deep_house", key="A", scale="minor",
        seed=42, creativity_level=0.7, semicadencia=False,
    )
    assert full["skeleton_id"] == "deep_house_2"
    assert full["grados_acordes"] == [(2, "maj7"), (2, "maj7"), (6, "dom7"), (2, "maj7")]
