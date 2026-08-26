"""
harmonic_skeletons.py — Ableton Live MCP Server
Datos canónicos del contrato "Würfelspiel" (juego de dados musical) compartido
con harmony-lab (JS). Fuente de verdad: NO este archivo.

Fuente única de verdad (solo lectura, no editar aquí):
  /Users/brianear/proyectos/ba-automation-forge/data/harmonic-skeletons/README.md
  /Users/brianear/proyectos/ba-automation-forge/data/harmonic-skeletons/skeletons.json

Cualquier cambio de género/esqueleto/opción se hace editando esos archivos y
resincronizando esta copia a mano (ver §6 del README) — nunca al revés.
"""

# Idéntico a $funcion_por_grado en skeletons.json, que a su vez replica
# HARMONIC_FUNCTION en harmony-lab/src/core/HarmonyGraph.js:26-34.
# Aplica solo a escalas de 7 grados (major, minor, harmonic_minor,
# melodic_minor y modos) — ver §1 del README.
FUNCION_POR_GRADO = {
    0: "T",
    1: "S",
    2: "T",
    3: "S",
    4: "D",
    5: "T",
    6: "D",
}

# Copia fiel de "generos" en skeletons.json. grado es 0-based; tipo_acorde es
# una clave de CHORD_TYPES en music_theory.py.
ESQUELETOS_POR_GENERO = {
  "house": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj"), (2, "maj")],
      "S": [(1, "min"), (3, "min")],
      "D": [(4, "maj"), (6, "maj")],
    },
    "esqueletos": [
      {
        "id": "house_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "house_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "house_3",
        "slots": ["T", "S", "S", "T"],
      },
    ],
  },
  "deep_house": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (2, "maj7")],
      "S": [(3, "min7"), (1, "min7")],
      "D": [(4, "dom7"), (6, "dom7")],
    },
    "esqueletos": [
      {
        "id": "deep_house_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "deep_house_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "deep_house_3",
        "slots": ["T", "S", "D", "T"],
      },
    ],
  },
  "afro_house": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(4, "min7"), (6, "dom7")],
    },
    "esqueletos": [
      {
        "id": "afro_house_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "afro_house_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "afro_house_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "tech_house": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (2, "min7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "maj"), (4, "dom7")],
    },
    "esqueletos": [
      {
        "id": "tech_house_1",
        "slots": ["T", "T", "T", "T"],
      },
      {
        "id": "tech_house_2",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "tech_house_3",
        "slots": ["T", "T", "D", "T"],
      },
    ],
  },
  "garage_house": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "dom7"), (4, "min7"), (4, "sus4")],
    },
    "esqueletos": [
      {
        "id": "garage_house_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "garage_house_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "garage_house_3",
        "slots": ["T", "D", "S", "T"],
      },
    ],
  },
  "techno": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (2, "min")],
      "S": [(3, "min"), (1, "min")],
      "D": [(4, "min"), (6, "maj")],
    },
    "esqueletos": [
      {
        "id": "techno_1",
        "slots": ["T", "T", "T", "T"],
      },
      {
        "id": "techno_2",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "techno_3",
        "slots": ["T", "S", "T", "T"],
      },
    ],
  },
  "detroit_techno": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (2, "min7")],
      "S": [(3, "min7"), (1, "min7")],
      "D": [(6, "maj7"), (4, "dom7")],
    },
    "esqueletos": [
      {
        "id": "detroit_techno_1",
        "slots": ["T", "T", "T", "T"],
      },
      {
        "id": "detroit_techno_2",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "detroit_techno_3",
        "slots": ["T", "S", "D", "T"],
      },
    ],
  },
  "industrial_techno": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "min")],
      "S": [(1, "min"), (3, "min")],
      "D": [(6, "dim"), (4, "maj"), (4, "sus2")],
    },
    "esqueletos": [
      {
        "id": "industrial_techno_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "industrial_techno_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "industrial_techno_3",
        "slots": ["T", "S", "D", "T"],
      },
    ],
  },
  "minimal_techno": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (2, "min")],
      "S": [(1, "min"), (3, "min")],
      "D": [(6, "maj"), (4, "maj"), (4, "sus2")],
    },
    "esqueletos": [
      {
        "id": "minimal_techno_1",
        "slots": ["T", "T", "T", "T"],
      },
      {
        "id": "minimal_techno_2",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "minimal_techno_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "melodic_techno": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "maj7"), (2, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "dom7"), (4, "dom7")],
    },
    "esqueletos": [
      {
        "id": "melodic_techno_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "melodic_techno_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "melodic_techno_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "trance": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj"), (2, "maj")],
      "S": [(1, "min"), (3, "min")],
      "D": [(6, "maj"), (4, "maj"), (4, "dim7")],
    },
    "esqueletos": [
      {
        "id": "trance_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "trance_2",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "trance_3",
        "slots": ["T", "S", "D", "T"],
      },
    ],
  },
  "progressive_trance": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "maj7"), (2, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(4, "min7"), (6, "dom7"), (4, "sus4")],
    },
    "esqueletos": [
      {
        "id": "progressive_trance_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "progressive_trance_2",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "progressive_trance_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "psytrance": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj")],
      "S": [(1, "min"), (3, "min")],
      "D": [(6, "maj"), (4, "maj"), (4, "sus4")],
    },
    "esqueletos": [
      {
        "id": "psytrance_1",
        "slots": ["T", "T", "T", "T"],
      },
      {
        "id": "psytrance_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "psytrance_3",
        "slots": ["T", "S", "T", "T"],
      },
    ],
  },
  "uplifting_trance": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj")],
      "S": [(3, "min"), (1, "min")],
      "D": [(6, "maj"), (4, "maj"), (4, "sus4")],
    },
    "esqueletos": [
      {
        "id": "uplifting_trance_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "uplifting_trance_2",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "uplifting_trance_3",
        "slots": ["T", "D", "S", "T"],
      },
    ],
  },
  "drum_and_bass": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "maj7"), (4, "dom7"), (4, "sus2")],
    },
    "esqueletos": [
      {
        "id": "drum_and_bass_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "drum_and_bass_2",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "drum_and_bass_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "liquid_dnb": {
    "escala_default": "major",
    "opciones_por_funcion": {
      "T": [(0, "maj7"), (5, "maj7")],
      "S": [(3, "min7"), (1, "min7")],
      "D": [(6, "dom7"), (4, "dom7")],
    },
    "esqueletos": [
      {
        "id": "liquid_dnb_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "liquid_dnb_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "liquid_dnb_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "neurofunk": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "min7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "dim7"), (4, "dom7")],
    },
    "esqueletos": [
      {
        "id": "neurofunk_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "neurofunk_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "neurofunk_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "jungle": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "maj"), (4, "dom7"), (4, "dim7")],
    },
    "esqueletos": [
      {
        "id": "jungle_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "jungle_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "jungle_3",
        "slots": ["T", "D", "S", "T"],
      },
    ],
  },
  "halftime": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "maj7")],
      "S": [(3, "min7"), (1, "min7")],
      "D": [(4, "dom7"), (6, "dom7"), (4, "sus4")],
    },
    "esqueletos": [
      {
        "id": "halftime_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "halftime_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "halftime_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "hip_hop": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "maj7"), (4, "dom7"), (4, "sus4")],
    },
    "esqueletos": [
      {
        "id": "hip_hop_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "hip_hop_2",
        "slots": ["T", "D", "T", "T"],
      },
      {
        "id": "hip_hop_3",
        "slots": ["T", "D", "S", "T"],
      },
    ],
  },
  "lo_fi": {
    "escala_default": "major",
    "opciones_por_funcion": {
      "T": [(0, "maj7"), (5, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(4, "dom7"), (6, "dom7")],
    },
    "esqueletos": [
      {
        "id": "lo_fi_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "lo_fi_2",
        "slots": ["T", "D", "T", "T"],
      },
      {
        "id": "lo_fi_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "boom_bap": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (2, "min7")],
      "S": [(3, "min7"), (1, "min7")],
      "D": [(4, "dom7"), (6, "dom7"), (4, "sus2")],
    },
    "esqueletos": [
      {
        "id": "boom_bap_1",
        "slots": ["T", "T", "T", "T"],
      },
      {
        "id": "boom_bap_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "boom_bap_3",
        "slots": ["T", "S", "D", "T"],
      },
    ],
  },
  "trap": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj")],
      "S": [(1, "min"), (3, "min")],
      "D": [(6, "maj"), (4, "maj"), (4, "add9")],
    },
    "esqueletos": [
      {
        "id": "trap_1",
        "slots": ["T", "T", "T", "T"],
      },
      {
        "id": "trap_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "trap_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "drill": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (2, "min")],
      "S": [(1, "min"), (3, "min")],
      "D": [(6, "dim"), (6, "maj")],
    },
    "esqueletos": [
      {
        "id": "drill_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "drill_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "drill_3",
        "slots": ["T", "D", "S", "T"],
      },
    ],
  },
  "phonk": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(4, "dom7"), (6, "dom7")],
    },
    "esqueletos": [
      {
        "id": "phonk_1",
        "slots": ["T", "T", "T", "T"],
      },
      {
        "id": "phonk_2",
        "slots": ["T", "S", "T", "T"],
      },
      {
        "id": "phonk_3",
        "slots": ["T", "S", "D", "T"],
      },
    ],
  },
  "cloud_rap": {
    "escala_default": "major",
    "opciones_por_funcion": {
      "T": [(0, "maj7"), (5, "maj7"), (2, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(4, "min7"), (6, "dom7"), (4, "sus2")],
    },
    "esqueletos": [
      {
        "id": "cloud_rap_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "cloud_rap_2",
        "slots": ["T", "D", "S", "T"],
      },
      {
        "id": "cloud_rap_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "rnb": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (2, "maj7")],
      "S": [(3, "min7"), (1, "min7")],
      "D": [(6, "dom7"), (4, "dom7"), (4, "sus4")],
    },
    "esqueletos": [
      {
        "id": "rnb_1",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "rnb_2",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "rnb_3",
        "slots": ["T", "S", "D", "T"],
      },
    ],
  },
  "neo_soul": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min9"), (2, "maj9")],
      "S": [(3, "min9"), (1, "min9")],
      "D": [(6, "dom7"), (4, "dom9")],
    },
    "esqueletos": [
      {
        "id": "neo_soul_1",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "neo_soul_2",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "neo_soul_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "funk": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (2, "min7")],
      "S": [(3, "dom7"), (1, "min7")],
      "D": [(4, "dom7"), (6, "dom7")],
    },
    "esqueletos": [
      {
        "id": "funk_1",
        "slots": ["T", "T", "T", "T"],
      },
      {
        "id": "funk_2",
        "slots": ["T", "S", "T", "T"],
      },
      {
        "id": "funk_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "soul": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "maj7")],
      "S": [(3, "min7"), (1, "min7")],
      "D": [(4, "dom7"), (6, "dom7"), (4, "dim7")],
    },
    "esqueletos": [
      {
        "id": "soul_1",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "soul_2",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "soul_3",
        "slots": ["T", "D", "S", "T"],
      },
    ],
  },
  "gospel": {
    "escala_default": "major",
    "opciones_por_funcion": {
      "T": [(0, "maj7"), (2, "maj7")],
      "S": [(3, "maj7"), (1, "min7")],
      "D": [(4, "dom7"), (6, "dom7")],
    },
    "esqueletos": [
      {
        "id": "gospel_1",
        "slots": ["T", "T", "T", "T"],
      },
      {
        "id": "gospel_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "gospel_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "reggae": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (2, "min7")],
      "S": [(3, "min7"), (1, "min7")],
      "D": [(4, "dom7"), (6, "dom7"), (4, "sus4")],
    },
    "esqueletos": [
      {
        "id": "reggae_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "reggae_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "reggae_3",
        "slots": ["T", "S", "T", "T"],
      },
    ],
  },
  "dancehall": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "maj"), (4, "dom7"), (4, "sus2")],
    },
    "esqueletos": [
      {
        "id": "dancehall_1",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "dancehall_2",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "dancehall_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "dub": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (2, "min7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "maj7"), (4, "dom7")],
    },
    "esqueletos": [
      {
        "id": "dub_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "dub_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "dub_3",
        "slots": ["T", "S", "D", "T"],
      },
    ],
  },
  "roots_reggae": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "maj7")],
      "S": [(3, "min7"), (1, "min7")],
      "D": [(4, "dom7"), (6, "dom7"), (4, "add9")],
    },
    "esqueletos": [
      {
        "id": "roots_reggae_1",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "roots_reggae_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "roots_reggae_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "jazz": {
    "escala_default": "major",
    "opciones_por_funcion": {
      "T": [(0, "maj7"), (2, "maj7")],
      "S": [(1, "min7"), (3, "maj7")],
      "D": [(4, "dom7"), (6, "dom7")],
    },
    "esqueletos": [
      {
        "id": "jazz_1",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "jazz_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "jazz_3",
        "slots": ["T", "D", "S", "T"],
      },
    ],
  },
  "jazz_fusion": {
    "escala_default": "major",
    "opciones_por_funcion": {
      "T": [(0, "maj9"), (2, "maj9")],
      "S": [(1, "min9"), (3, "maj7")],
      "D": [(4, "dom7"), (6, "dom9")],
    },
    "esqueletos": [
      {
        "id": "jazz_fusion_1",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "jazz_fusion_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "jazz_fusion_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "bossa_nova": {
    "escala_default": "major",
    "opciones_por_funcion": {
      "T": [(0, "maj7"), (2, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(4, "dom7"), (6, "dom7")],
    },
    "esqueletos": [
      {
        "id": "bossa_nova_1",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "bossa_nova_2",
        "slots": ["T", "D", "T", "T"],
      },
      {
        "id": "bossa_nova_3",
        "slots": ["T", "D", "S", "T"],
      },
    ],
  },
  "bebop": {
    "escala_default": "major",
    "opciones_por_funcion": {
      "T": [(0, "maj7"), (5, "dom7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(4, "dom7"), (6, "dom7")],
    },
    "esqueletos": [
      {
        "id": "bebop_1",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "bebop_2",
        "slots": ["T", "D", "T", "T"],
      },
      {
        "id": "bebop_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "modal_jazz": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (2, "min7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(4, "dom7"), (6, "dom7")],
    },
    "esqueletos": [
      {
        "id": "modal_jazz_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "modal_jazz_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "modal_jazz_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "ambient": {
    "escala_default": "major",
    "opciones_por_funcion": {
      "T": [(0, "maj7"), (5, "maj7"), (2, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "maj7"), (4, "dom7")],
    },
    "esqueletos": [
      {
        "id": "ambient_1",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "ambient_2",
        "slots": ["T", "D", "S", "T"],
      },
      {
        "id": "ambient_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "dark_ambient": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (2, "min")],
      "S": [(1, "min"), (3, "min")],
      "D": [(6, "dim"), (4, "maj")],
    },
    "esqueletos": [
      {
        "id": "dark_ambient_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "dark_ambient_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "dark_ambient_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "idm": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "min7"), (6, "dom7")],
    },
    "esqueletos": [
      {
        "id": "idm_1",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "idm_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "idm_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "chillout": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "maj7"), (2, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(4, "min7"), (6, "dom7"), (4, "sus2")],
    },
    "esqueletos": [
      {
        "id": "chillout_1",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "chillout_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "chillout_3",
        "slots": ["T", "D", "S", "T"],
      },
    ],
  },
  "downtempo": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "maj7")],
      "S": [(3, "min7"), (1, "min7")],
      "D": [(6, "dom7"), (4, "dom7")],
    },
    "esqueletos": [
      {
        "id": "downtempo_1",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "downtempo_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "downtempo_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "synthwave": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj"), (2, "maj")],
      "S": [(1, "min"), (3, "min")],
      "D": [(6, "maj"), (4, "maj"), (4, "add9")],
    },
    "esqueletos": [
      {
        "id": "synthwave_1",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "synthwave_2",
        "slots": ["T", "D", "T", "T"],
      },
      {
        "id": "synthwave_3",
        "slots": ["T", "D", "S", "T"],
      },
    ],
  },
  "darksynth": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "min")],
      "S": [(1, "min"), (3, "min")],
      "D": [(6, "maj"), (4, "maj")],
    },
    "esqueletos": [
      {
        "id": "darksynth_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "darksynth_2",
        "slots": ["T", "S", "T", "T"],
      },
      {
        "id": "darksynth_3",
        "slots": ["T", "S", "D", "T"],
      },
    ],
  },
  "electro": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "maj")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "maj"), (4, "dom7")],
    },
    "esqueletos": [
      {
        "id": "electro_1",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "electro_2",
        "slots": ["T", "D", "T", "T"],
      },
      {
        "id": "electro_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "future_bass": {
    "escala_default": "major",
    "opciones_por_funcion": {
      "T": [(0, "maj7"), (5, "maj7"), (2, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "dom7"), (4, "dom7")],
    },
    "esqueletos": [
      {
        "id": "future_bass_1",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "future_bass_2",
        "slots": ["T", "D", "S", "T"],
      },
      {
        "id": "future_bass_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "dubstep": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "maj"), (4, "dom7"), (4, "add9")],
    },
    "esqueletos": [
      {
        "id": "dubstep_1",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "dubstep_2",
        "slots": ["T", "D", "T", "T"],
      },
      {
        "id": "dubstep_3",
        "slots": ["T", "D", "S", "T"],
      },
    ],
  },
  "riddim": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (2, "min")],
      "S": [(1, "min"), (3, "min")],
      "D": [(6, "maj"), (4, "maj"), (4, "sus4")],
    },
    "esqueletos": [
      {
        "id": "riddim_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "riddim_2",
        "slots": ["T", "S", "T", "T"],
      },
      {
        "id": "riddim_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "future_garage": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "maj7")],
      "S": [(3, "min7"), (1, "min7")],
      "D": [(4, "dom7"), (6, "dom7"), (4, "sus2")],
    },
    "esqueletos": [
      {
        "id": "future_garage_1",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "future_garage_2",
        "slots": ["T", "D", "T", "T"],
      },
      {
        "id": "future_garage_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "pop": {
    "escala_default": "major",
    "opciones_por_funcion": {
      "T": [(0, "maj"), (5, "min")],
      "S": [(3, "maj"), (1, "min")],
      "D": [(4, "maj"), (6, "maj")],
    },
    "esqueletos": [
      {
        "id": "pop_1",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "pop_2",
        "slots": ["T", "D", "S", "T"],
      },
      {
        "id": "pop_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "indie_pop": {
    "escala_default": "major",
    "opciones_por_funcion": {
      "T": [(5, "min7"), (0, "maj")],
      "S": [(3, "maj7"), (1, "min7")],
      "D": [(4, "maj"), (6, "dom7")],
    },
    "esqueletos": [
      {
        "id": "indie_pop_1",
        "slots": ["T", "D", "T", "T"],
      },
      {
        "id": "indie_pop_2",
        "slots": ["T", "D", "S", "T"],
      },
      {
        "id": "indie_pop_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "dream_pop": {
    "escala_default": "major",
    "opciones_por_funcion": {
      "T": [(0, "maj7"), (5, "maj7"), (2, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(4, "min7"), (6, "dom7"), (4, "sus4")],
    },
    "esqueletos": [
      {
        "id": "dream_pop_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "dream_pop_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "dream_pop_3",
        "slots": ["T", "S", "S", "T"],
      },
    ],
  },
  "shoegaze": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj"), (2, "maj")],
      "S": [(1, "min"), (3, "min")],
      "D": [(6, "maj"), (4, "maj"), (4, "sus4")],
    },
    "esqueletos": [
      {
        "id": "shoegaze_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "shoegaze_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "shoegaze_3",
        "slots": ["T", "S", "D", "T"],
      },
    ],
  },
  "hyperpop": {
    "escala_default": "major",
    "opciones_por_funcion": {
      "T": [(0, "maj7"), (5, "min7")],
      "S": [(3, "maj7"), (1, "min7")],
      "D": [(4, "dom7"), (6, "dom7")],
    },
    "esqueletos": [
      {
        "id": "hyperpop_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "hyperpop_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "hyperpop_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "afrobeats": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "dom7"), (4, "min7"), (4, "sus2")],
    },
    "esqueletos": [
      {
        "id": "afrobeats_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "afrobeats_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "afrobeats_3",
        "slots": ["T", "D", "S", "T"],
      },
    ],
  },
  "afrobeat": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (2, "min7")],
      "S": [(3, "dom7"), (1, "min7")],
      "D": [(6, "dom7"), (4, "dom7")],
    },
    "esqueletos": [
      {
        "id": "afrobeat_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "afrobeat_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "afrobeat_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "amapiano": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (2, "maj7")],
      "S": [(3, "min7"), (1, "min7")],
      "D": [(6, "dom7"), (4, "dom7"), (4, "sus2")],
    },
    "esqueletos": [
      {
        "id": "amapiano_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "amapiano_2",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "amapiano_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "baile_funk": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj")],
      "S": [(1, "min"), (3, "min")],
      "D": [(6, "maj"), (4, "maj"), (4, "sus2")],
    },
    "esqueletos": [
      {
        "id": "baile_funk_1",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "baile_funk_2",
        "slots": ["T", "S", "T", "T"],
      },
      {
        "id": "baile_funk_3",
        "slots": ["T", "S", "D", "T"],
      },
    ],
  },
  "cumbia": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (2, "min7")],
      "S": [(3, "min"), (1, "min7")],
      "D": [(4, "dom7"), (6, "dom7"), (4, "sus2")],
    },
    "esqueletos": [
      {
        "id": "cumbia_1",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "cumbia_2",
        "slots": ["T", "S", "T", "T"],
      },
      {
        "id": "cumbia_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "salsa": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (2, "min7")],
      "S": [(3, "min7"), (1, "min7")],
      "D": [(4, "dom7"), (6, "dom7"), (4, "add9")],
    },
    "esqueletos": [
      {
        "id": "salsa_1",
        "slots": ["T", "T", "D", "T"],
      },
      {
        "id": "salsa_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "salsa_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "dembow": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "maj"), (4, "dom7"), (4, "sus4")],
    },
    "esqueletos": [
      {
        "id": "dembow_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "dembow_2",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "dembow_3",
        "slots": ["T", "S", "D", "T"],
      },
    ],
  },
  "reggaeton": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "maj"), (4, "dom7"), (4, "aug")],
    },
    "esqueletos": [
      {
        "id": "reggaeton_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "reggaeton_2",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "reggaeton_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "rock": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "maj"), (4, "dom7"), (4, "min11")],
    },
    "esqueletos": [
      {
        "id": "rock_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "rock_2",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "rock_3",
        "slots": ["T", "D", "S", "T"],
      },
    ],
  },
  "indie_rock": {
    "escala_default": "major",
    "opciones_por_funcion": {
      "T": [(5, "min"), (0, "maj")],
      "S": [(3, "maj"), (1, "min")],
      "D": [(4, "maj"), (6, "maj")],
    },
    "esqueletos": [
      {
        "id": "indie_rock_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "indie_rock_2",
        "slots": ["T", "S", "S", "T"],
      },
      {
        "id": "indie_rock_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "metal": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "min")],
      "S": [(1, "min"), (3, "min")],
      "D": [(6, "dim"), (4, "maj"), (4, "sus4")],
    },
    "esqueletos": [
      {
        "id": "metal_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "metal_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "metal_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "doom_metal": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "min")],
      "S": [(1, "min"), (3, "min")],
      "D": [(6, "min"), (4, "maj")],
    },
    "esqueletos": [
      {
        "id": "doom_metal_1",
        "slots": ["T", "S", "T", "T"],
      },
      {
        "id": "doom_metal_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "doom_metal_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "post_rock": {
    "escala_default": "major",
    "opciones_por_funcion": {
      "T": [(0, "maj7"), (5, "maj7"), (2, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(4, "min7"), (6, "dom7"), (4, "add9")],
    },
    "esqueletos": [
      {
        "id": "post_rock_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "post_rock_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "post_rock_3",
        "slots": ["T", "D", "T", "T"],
      },
    ],
  },
  "grunge": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj")],
      "S": [(3, "maj"), (1, "min")],
      "D": [(6, "maj"), (4, "maj")],
    },
    "esqueletos": [
      {
        "id": "grunge_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "grunge_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "grunge_3",
        "slots": ["T", "D", "S", "T"],
      },
    ],
  },
  "cinematic": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj"), (2, "maj")],
      "S": [(1, "min"), (3, "min")],
      "D": [(6, "maj"), (4, "maj"), (4, "sus2")],
    },
    "esqueletos": [
      {
        "id": "cinematic_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "cinematic_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "cinematic_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "orchestral": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (2, "min7")],
      "S": [(3, "min"), (1, "min7")],
      "D": [(4, "dom7"), (6, "dom7"), (4, "sus4")],
    },
    "esqueletos": [
      {
        "id": "orchestral_1",
        "slots": ["T", "T", "T", "T"],
      },
      {
        "id": "orchestral_2",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "orchestral_3",
        "slots": ["T", "T", "D", "T"],
      },
    ],
  },
  "neoclassical": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min7"), (5, "maj7"), (2, "maj7")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(4, "dom7"), (6, "dom7")],
    },
    "esqueletos": [
      {
        "id": "neoclassical_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "neoclassical_2",
        "slots": ["T", "D", "T", "T"],
      },
      {
        "id": "neoclassical_3",
        "slots": ["T", "D", "S", "T"],
      },
    ],
  },
  "epic": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "maj")],
      "S": [(3, "min"), (1, "min")],
      "D": [(6, "maj"), (4, "maj"), (4, "sus2")],
    },
    "esqueletos": [
      {
        "id": "epic_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "epic_2",
        "slots": ["T", "D", "T", "T"],
      },
      {
        "id": "epic_3",
        "slots": ["T", "D", "D", "T"],
      },
    ],
  },
  "horror": {
    "escala_default": "minor",
    "opciones_por_funcion": {
      "T": [(0, "min"), (5, "min")],
      "S": [(1, "min7"), (3, "min7")],
      "D": [(6, "dim7"), (4, "dom7")],
    },
    "esqueletos": [
      {
        "id": "horror_1",
        "slots": ["T", "T", "S", "T"],
      },
      {
        "id": "horror_2",
        "slots": ["T", "S", "D", "T"],
      },
      {
        "id": "horror_3",
        "slots": ["T", "D", "S", "T"],
      },
    ],
  },
}

FAMILIA_POR_GENERO = {
  "house": "electronica",
  "deep_house": "electronica",
  "afro_house": "electronica",
  "tech_house": "electronica",
  "garage_house": "electronica",
  "techno": "electronica",
  "detroit_techno": "electronica",
  "industrial_techno": "electronica",
  "minimal_techno": "electronica",
  "melodic_techno": "electronica",
  "trance": "electronica",
  "progressive_trance": "electronica",
  "psytrance": "electronica",
  "uplifting_trance": "electronica",
  "drum_and_bass": "electronica",
  "liquid_dnb": "electronica",
  "neurofunk": "electronica",
  "jungle": "electronica",
  "halftime": "electronica",
  "synthwave": "electronica",
  "darksynth": "electronica",
  "electro": "electronica",
  "future_bass": "electronica",
  "dubstep": "electronica",
  "riddim": "electronica",
  "future_garage": "electronica",
  "hip_hop": "cancion",
  "lo_fi": "cancion",
  "boom_bap": "cancion",
  "trap": "cancion",
  "drill": "cancion",
  "phonk": "cancion",
  "cloud_rap": "cancion",
  "rnb": "cancion",
  "neo_soul": "cancion",
  "funk": "cancion",
  "soul": "cancion",
  "gospel": "cancion",
  "reggae": "cancion",
  "dancehall": "cancion",
  "dub": "cancion",
  "roots_reggae": "cancion",
  "jazz": "cancion",
  "jazz_fusion": "cancion",
  "bossa_nova": "cancion",
  "bebop": "cancion",
  "modal_jazz": "cancion",
  "pop": "cancion",
  "indie_pop": "cancion",
  "dream_pop": "cancion",
  "shoegaze": "cancion",
  "hyperpop": "cancion",
  "afrobeats": "cancion",
  "afrobeat": "cancion",
  "amapiano": "cancion",
  "baile_funk": "cancion",
  "cumbia": "cancion",
  "salsa": "cancion",
  "dembow": "cancion",
  "reggaeton": "cancion",
  "rock": "cancion",
  "indie_rock": "cancion",
  "metal": "cancion",
  "doom_metal": "cancion",
  "post_rock": "cancion",
  "grunge": "cancion",
  "ambient": "cinematica",
  "dark_ambient": "cinematica",
  "idm": "cinematica",
  "chillout": "cinematica",
  "downtempo": "cinematica",
  "cinematic": "cinematica",
  "orchestral": "cinematica",
  "neoclassical": "cinematica",
  "epic": "cinematica",
  "horror": "cinematica",
}

ESTRUCTURA_POR_FAMILIA = {
  "electronica": {
    "secciones": [
      {
        "nombre": "intro",
        "creativity_level": 0.0,
        "semicadencia": False,
      },
      {
        "nombre": "build_up",
        "creativity_level": 0.8,
        "semicadencia": True,
      },
      {
        "nombre": "drop",
        "creativity_level": 0.1,
        "semicadencia": False,
      },
      {
        "nombre": "breakdown",
        "creativity_level": 0.5,
        "semicadencia": False,
      },
    ],
  },
  "cancion": {
    "secciones": [
      {
        "nombre": "intro",
        "creativity_level": 0.1,
        "semicadencia": False,
      },
      {
        "nombre": "verso",
        "creativity_level": 0.6,
        "semicadencia": False,
      },
      {
        "nombre": "coro",
        "creativity_level": 0.2,
        "semicadencia": False,
      },
      {
        "nombre": "puente",
        "creativity_level": 0.9,
        "semicadencia": True,
      },
    ],
  },
  "cinematica": {
    "secciones": [
      {
        "nombre": "intro",
        "creativity_level": 0.0,
        "semicadencia": False,
      },
      {
        "nombre": "desarrollo",
        "creativity_level": 0.7,
        "semicadencia": True,
      },
      {
        "nombre": "climax",
        "creativity_level": 0.3,
        "semicadencia": False,
      },
      {
        "nombre": "resolucion",
        "creativity_level": 0.0,
        "semicadencia": False,
      },
    ],
  },
}
