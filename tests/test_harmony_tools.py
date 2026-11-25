"""Pruebas del círculo de quintas, Camelot y conducción de voces."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from harmony_tools import (  # noqa: E402
    HarmonyError, camelot, circle_distance, group_by_compatibility,
    key_compatibility, parse_key, voice_lead,
)
from harmony_handlers import HANDLERS  # noqa: E402
from music_theory import build_chord  # noqa: E402

# La rueda Camelot tal como está publicada. Si algo de esto falla, el mapeo
# está mal y cualquier recomendación de mezcla que demos sería falsa.
RUEDA = {
    "C": "8B", "G": "9B", "D": "10B", "A": "11B", "E": "12B", "B": "1B",
    "F#": "2B", "Db": "3B", "Ab": "4B", "Eb": "5B", "Bb": "6B", "F": "7B",
    "Am": "8A", "Em": "9A", "Bm": "10A", "F#m": "11A", "C#m": "12A", "G#m": "1A",
    "D#m": "2A", "Bbm": "3A", "Fm": "4A", "Cm": "5A", "Gm": "6A", "Dm": "7A",
}


@pytest.mark.parametrize("tonalidad,codigo", sorted(RUEDA.items()))
def test_camelot_coincide_con_la_rueda_publicada(tonalidad, codigo):
    assert camelot(*parse_key(tonalidad)) == codigo


def test_las_24_tonalidades_dan_24_codigos_distintos():
    codigos = {camelot(*parse_key(k)) for k in RUEDA}
    assert len(codigos) == 24


@pytest.mark.parametrize("entrada", ["Am", "A minor", "A min", "a m", "A_minor"])
def test_parse_key_acepta_variantes_de_menor(entrada):
    assert parse_key(entrada) == (9, "minor")


@pytest.mark.parametrize("entrada", ["C", "C major", "c maj"])
def test_parse_key_acepta_variantes_de_mayor(entrada):
    assert parse_key(entrada) == (0, "major")


def test_parse_key_rechaza_basura():
    with pytest.raises(HarmonyError):
        parse_key("H#")
    with pytest.raises(HarmonyError):
        parse_key("")


def test_las_compatibles_estan_a_un_paso_en_camelot():
    """Las tres mezclables deben caer en la casilla Camelot contigua o en la misma."""
    for tonalidad in RUEDA:
        datos = key_compatibility(tonalidad)
        propio = int(datos["camelot"][:-1])
        for vecina in datos["compatibles"]:
            numero = int(vecina["camelot"][:-1])
            salto = min(abs(numero - propio), 12 - abs(numero - propio))
            assert salto <= 1, f"{tonalidad} -> {vecina['tonalidad']} salta {salto}"


def test_la_homonima_no_se_vende_como_mezcla_transparente():
    """Siempre está a 3 casillas Camelot: va en su propio campo, no entre las
    compatibles. Confundirlas haría recomendar una mezcla que choca."""
    for tonalidad in RUEDA:
        datos = key_compatibility(tonalidad)
        assert all(v["relacion"] != "homónima" for v in datos["compatibles"])
        propio = int(datos["camelot"][:-1])
        otro = int(datos["cambio_de_modo"]["camelot"][:-1])
        assert min(abs(otro - propio), 12 - abs(otro - propio)) == 3


def test_la_relativa_comparte_las_siete_notas():
    for tonalidad in ("C", "Am", "F#m", "Eb"):
        datos = key_compatibility(tonalidad)
        relativa = next(v for v in datos["compatibles"] if v["relacion"] == "relativa")
        assert set(key_compatibility(relativa["tonalidad"])["escala"]) == set(datos["escala"])


def test_circle_distance_es_simetrica_y_corta():
    assert circle_distance("C", "G") == 1
    assert circle_distance("G", "C") == 1
    assert circle_distance("C", "F#") == 6          # el máximo posible
    assert circle_distance("C", "C") == 0
    assert all(0 <= circle_distance(a, b) <= 6 for a in RUEDA for b in RUEDA)


def test_group_by_compatibility_reproduce_las_familias_de_arytmo():
    """Las 13 raíces medidas del pack deben dar las mismas 3 familias que se
    usaron para colorear las escenas. Es la comprobación de que el agrupamiento
    sigue siendo el mismo criterio."""
    raices = ["A#m", "F#m", "Dm", "Em", "Bm", "Bm", "Fm",
              "G#m", "G#m", "D#m", "D#m", "A#m", "Dm"]
    familias = [sorted(set(f)) for f in group_by_compatibility(raices)]
    assert familias == [["Dm"], ["Bm", "Em", "F#m"], ["A#m", "D#m", "Fm", "G#m"]]


def test_group_by_compatibility_cierra_el_anillo():
    """F y C son contiguas aunque estén en extremos opuestos de la lista."""
    assert len(group_by_compatibility(["F", "C", "G"])) == 1


def test_group_by_compatibility_con_lista_vacia():
    assert group_by_compatibility([]) == []


def _centro(acorde):
    return sum(acorde) / len(acorde)


def test_voice_lead_reduce_el_movimiento():
    prog = [[n["pitch"] for n in build_chord(r, t)]
            for r, t in ((60, "maj"), (65, "maj"), (67, "maj"), (60, "maj"))]
    antes = sum(abs(_centro(a) - _centro(b)) for a, b in zip(prog, prog[1:]))
    despues = sum(abs(_centro(a) - _centro(b)) for a, b in zip(voice_lead(prog), prog[1:]))
    assert despues < antes


def test_voice_lead_conserva_las_clases_de_altura():
    """Puede cambiar la octava de una nota, nunca la nota."""
    prog = [[n["pitch"] for n in build_chord(r, t)]
            for r, t in ((62, "min7"), (69, "min7"), (65, "maj7"))]
    for original, conducido in zip(prog, voice_lead(prog)):
        assert {p % 12 for p in original} == {p % 12 for p in conducido}


def test_voice_lead_conserva_el_numero_de_voces():
    prog = [[n["pitch"] for n in build_chord(r, t)]
            for r, t in ((60, "maj"), (62, "min9"), (67, "dom7"))]
    for original, conducido in zip(prog, voice_lead(prog)):
        assert len(conducido) == len({p % 12 for p in original})


def test_voice_lead_se_queda_cerca_del_centro():
    prog = [[n["pitch"] for n in build_chord(r, "maj")] for r in (60, 65, 67, 60)]
    for acorde in voice_lead(prog, center=60, span=12):
        assert all(36 <= nota <= 84 for nota in acorde)


def test_voice_lead_con_lista_vacia():
    assert voice_lead([]) == []


def test_handler_de_tonalidad_rechaza_basura():
    assert "❌" in HANDLERS["get_key_compatibility"]({"key": "H#"})[0].text


def test_handler_de_agrupacion_exige_lista():
    assert "❌" in HANDLERS["group_keys_by_compatibility"]({"keys": []})[0].text


def test_handler_de_agrupacion_lista_las_familias():
    texto = HANDLERS["group_keys_by_compatibility"]({"keys": ["Am", "Em", "Bbm"]})[0].text
    assert "familia 1" in texto and "familia 2" in texto
