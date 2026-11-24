"""Pruebas de la base de conocimiento rítmica y de get_rhythm_pattern.

Las tres primeras son las que pedía el encargo original del análisis; el resto
cubre la integridad de los datos medidos y el manejo de errores del handler.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rhythm_tools import (  # noqa: E402
    GENRE_FILES, get_rhythm_pattern, load_knowledge, normalize_genre,
)

DOWNBEATS = {0, 4, 8, 12}
STEPS_PER_BAR = 16
PATTERN_BARS = 2


@pytest.fixture(scope="module")
def data():
    return load_knowledge("melodic techno")


@pytest.fixture(scope="module")
def all_rows(data):
    return [(loop["nombre"], voz) for loop in data["loops"] for voz in loop["voces"]]


# --- las tres del encargo original -----------------------------------------

def test_todos_los_pasos_estan_en_rango(all_rows):
    limite = STEPS_PER_BAR * PATTERN_BARS
    for nombre, voz in all_rows:
        for paso in voz["pasos"]:
            assert 0 <= paso < limite, f"{nombre}: paso {paso} fuera de 0..{limite - 1}"


def test_el_bajo_no_cae_siempre_en_el_paso_cero(data):
    con_cero = [l["nombre"] for l in data["loops"]
                if any(0 in v["pasos"] for v in l["voces"])]
    assert not con_cero, f"estos loops tocan en el paso 0: {con_cero}"


def test_el_kick_incluye_los_cuatro_tiempos(data):
    assert set(data["kick"]["cierto"]) == DOWNBEATS


# --- integridad de lo medido -----------------------------------------------

def test_el_bajo_nunca_pisa_un_tiempo_fuerte(all_rows):
    """Lo que hace que el 4 en el piso engrane con los 13 sin tocar nada."""
    fuertes = {b * STEPS_PER_BAR + d for b in range(PATTERN_BARS) for d in DOWNBEATS}
    for nombre, voz in all_rows:
        choques = fuertes & set(voz["pasos"])
        assert not choques, f"{nombre} ({voz['nota']}) pisa los tiempos {sorted(choques)}"


def test_no_hay_pasos_repetidos_en_una_voz(all_rows):
    for nombre, voz in all_rows:
        pasos = voz["pasos"]
        assert len(pasos) == len(set(pasos)), f"{nombre} ({voz['nota']}) repite pasos"


def test_las_raices_estan_en_registro_de_bajo(data):
    """Entre C1 (24) y C3 (48): si algo cae fuera, la lectura del teclado falló."""
    for loop in data["loops"]:
        for voz in loop["voces"]:
            assert 24 <= voz["midi"] <= 48, f"{loop['nombre']}: {voz['nota']} fuera de registro"


def test_la_raiz_declarada_es_la_voz_mas_grave(data):
    for loop in data["loops"]:
        assert loop["raiz_medida"] == min(loop["voces"], key=lambda v: v["midi"])["nota"]


def test_el_campo_coincide_concuerda_con_la_etiqueta(data):
    """Si este campo miente, se pierde el rastro de qué rotuló mal el anuncio."""
    for loop in data["loops"]:
        esperado = loop["raiz_medida"][:-1] == loop["etiqueta_del_anuncio"]
        assert loop["coincide"] is esperado, f"{loop['nombre']}: campo 'coincide' incorrecto"


def test_los_nombres_de_loop_son_unicos(data):
    nombres = [l["nombre"] for l in data["loops"]]
    assert len(nombres) == len(set(nombres))


def test_cada_genero_registrado_tiene_su_archivo():
    for genero in GENRE_FILES:
        assert load_knowledge(genero)["loops"], f"{genero} sin loops"


# --- handler ----------------------------------------------------------------

@pytest.mark.parametrize("entrada", ["melodic techno", "Melodic_Techno", "MELODIC-TECHNO"])
def test_normalize_genre_acepta_variantes(entrada):
    assert normalize_genre(entrada) == "melodic techno"


def test_handler_devuelve_los_trece_loops():
    texto = get_rhythm_pattern({"genre": "melodic techno"})[0].text
    data = load_knowledge("melodic techno")
    for loop in data["loops"]:
        assert loop["nombre"] in texto


def test_handler_rechaza_genero_desconocido():
    texto = get_rhythm_pattern({"genre": "reggaeton"})[0].text
    assert "❌" in texto and "melodic techno" in texto


def test_handler_avisa_si_el_bpm_no_coincide():
    assert "⚠️" in get_rhythm_pattern({"genre": "melodic techno", "bpm": 140})[0].text
    assert "⚠️" not in get_rhythm_pattern({"genre": "melodic techno", "bpm": 125})[0].text


def test_el_json_del_repo_es_el_mismo_que_se_sirve():
    ruta = Path(__file__).resolve().parent.parent / "knowledge" / GENRE_FILES["melodic techno"]
    assert json.loads(ruta.read_text(encoding="utf-8")) == load_knowledge("melodic techno")
