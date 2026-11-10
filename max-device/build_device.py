#!/usr/bin/env python3
"""
build_device.py — arma el device .amxd de Call & Response Generator (rebuild) con
py2max (github.com/shakfu/py2max, MIT). Genera el binario .amxd directo, verificado
por esa librería contra devices reales exportados por Max — no arma el contenedor
binario a mano (a diferencia de lo documentado en AUDIT.md Addendum 4 para ediciones
de un device ya existente).

Las listas STYLES/RESPONSE_STRATEGIES/MOTIF_TYPES/ENDING_BEHAVIOURS/SCALES/NOTE_NAMES
de abajo deben coincidir EXACTAMENTE en orden con las mismas listas en cr_engine.js —
los controles live.menu mandan el ÍNDICE seleccionado, no el texto, y cr_device.js
usa ese índice para indexar el arreglo correspondiente dentro de CR.DATA. Si estas
listas se desincronizan, el menú va a seleccionar el estilo/escala/etc. equivocado
sin ningún error visible.

REPETITIONS/CONTOURS no están en CR.DATA (son valores libres del motor, no listas
indexadas) — su orden aquí debe coincidir con el arreglo homónimo hardcodeado en
cr_device.js, no con nada dentro de cr_engine.js.

Layout: horizontal, no vertical — feedback real del usuario tras ver un primer
intento apilado en secciones ("no distribuyas hacia abajo, hazlo hacia la
derecha mejor"). 3 filas anchas (menús / menús / dials+botones) + la vista de
pasos al final, en vez de 5 secciones apiladas con encabezados.
"""

from py2max import Patcher

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

STYLES = ['Classic Acid', 'Raw Acid', 'Squelchy Acid', 'Dark Acid', 'Hypno Acid',
    'Sparse Acid', 'Busy Acid', 'Acid Stabs', 'Acid Runner', 'Acid Question/Answer',
    'Driving Techno', 'Hypnotic Techno', 'Minimal Techno', 'Raw Warehouse',
    'Tool Techno', 'Dub Techno', 'Industrial Techno', 'Percussive Techno',
    'Loop Techno', 'Broken Techno', 'Jackin House', 'Deep House', 'Minimal House',
    'Classic House', 'Tech House', 'Bass House', 'Shuffly House',
    'Organ House-ish', 'House Stabline', 'House Bounce', '90s Rave', 'Dark Rave',
    'Rave Stab', 'Electro Pulse', 'Breaky Electro', 'Detroit-ish', 'Proto-Trance',
    'Hooverish Riff', 'Motif Study', 'Rooted Groove', 'Repetitive Hook',
    'Wide Answer', 'Tight Answer', 'Tension Builder', 'Resolver',
    'Call Lead / Response Support']

RESPONSE_STRATEGIES = ['Same rhythm + resolve', 'Same rhythm + new contour',
    'Motif + simplify', 'Motif + extend', 'Motif + truncate', 'Echo',
    'Answer upward', 'Answer downward', 'Higher answer', 'Lower answer',
    'Invert contour', 'Mirror contour loosely', 'Copy rhythm / change notes',
    'Copy notes / change rhythm', 'Transpose motif up', 'Transpose motif down',
    'Response resolves to root', 'Response resolves to 5th',
    'Response resolves lower', 'Response resolves harder', 'Repeat then break',
    'Tighter answer', 'Sparser answer', 'Busier answer', 'Accent the answer',
    'Slide the answer', 'Staccato answer', 'Legato answer', 'Delayed answer',
    'Half-phrase answer', 'Fragment reply', 'Tail answer', 'Opposite register',
    'Same motif darker', 'Same motif brighter', 'Question then closure',
    'Hook then fill', 'Call dominant / response tonic']

MOTIF_TYPES = ['Pulse', 'Offbeat', 'Syncopated', 'Push', 'Sparse', 'Dense',
    'Rest-heavy', 'Four-on-floor companion', 'Stabbed', 'Rolling', 'Repeated note',
    'Stepwise rise', 'Stepwise fall', 'Rise then drop', 'Drop then rise',
    'Leap then settle', 'Pivot note', 'Two-note hook', 'Three-note hook',
    'Arp fragment', 'Acid nibble', 'Techno cell', 'House bounce',
    'Rave stab figure', 'Drone anchor', 'Pedal point motif', 'Call tag',
    'Answer tag']

ENDING_BEHAVIOURS = ['Resolve to root', 'Resolve to 5th', 'Leave hanging',
    'Rise into next phrase', 'Fall into next phrase', 'Hard stop', 'Fade energy',
    'Strong cadence', 'Weak cadence', 'Ambiguous ending',
    'Response more resolved than call', 'Response same tension as call',
    'Response more tense than call']

SCALES = ['Chromatic', 'Major / Ionian', 'Natural Minor / Aeolian', 'Harmonic Minor',
    'Melodic Minor', 'Dorian', 'Phrygian', 'Mixolydian', 'Locrian', 'Lydian',
    'Lydian Dominant', 'Aeolian b5', 'Dorian b2', 'Mixolydian b6',
    'Major Pentatonic', 'Minor Pentatonic', 'Blues Minor', 'Blues Major',
    'Phrygian Dominant', 'Double Harmonic', 'Hungarian Minor', 'Romanian Minor',
    'Whole Tone', 'Diminished Half-Whole', 'Diminished Whole-Half', 'Persian',
    'Arabic', 'Byzantine', 'Hirajoshi', 'In Sen', 'Japanese Pentatonic', 'Kumoi',
    'Pelog-ish', 'Egyptian Pentatonic', 'Minor Triad only', 'Power Fifths',
    'Root + b7', 'Root + 5th + b7', 'Root + 2nd + 5th', 'Minor 7 arpeggio pool',
    'Dominant 7 arpeggio pool', 'Diminished 7 arpeggio pool']

REPETITIONS = ['Very repetitive', 'Repetitive', 'Balanced', 'Varied', 'Highly varied']

CONTOURS = ['Flat', 'Slight rise', 'Slight fall', 'Arch', 'Inverted arch',
    'Wandering', 'Stepwise', 'Leapy']

DEVICE_WIDTH = 960
MARGIN = 8
COLS = 8
COL_GAP = 8
COL_W = (DEVICE_WIDTH - 2 * MARGIN - (COLS - 1) * COL_GAP) // COLS  # 111


def col_x(i):
    return MARGIN + i * (COL_W + COL_GAP)


def add_control(p, js, maxclass, varname, label, y, col=0, span=1,
                 ctl_h=20, param_type=None, param_min=None, param_max=None,
                 param_initial=None, param_enum=None, **attrs):
    """Crea un control live.* con su etiqueta arriba (estilo macro de Ableton:
    nombre chico + knob/menú debajo), su [prepend <varname>] y el cableado al js.

    El rango real que Live expone al LOM/automatización NO sale de los atributos
    de nivel superior (min/max/items) — esos solo gobiernan el widget dentro del
    editor de Max. Live lee el rango del parámetro automatizable desde
    saved_attribute_attributes.valueof (parameter_mmin/parameter_mmax para
    dial/slider/numbox, parameter_enum para el conteo de un live.menu). Sin este
    bloque, todo dial/numbox/slider cae al default 0-127 y todo live.menu cae a
    un enum de rango 2, sin importar los items reales — bug encontrado via
    /live/device/get/parameters/min|max, que no coincidía con lo declarado aquí.

    Retorna la coordenada Y del borde inferior de este control (para encadenar
    filas sin pisar el layout anterior).
    """
    x = col_x(col)
    w = span * COL_W + (span - 1) * COL_GAP

    # live.dial/live.slider/live.numbox ya muestran su propio nombre + valor
    # debajo del widget en el panel de Ableton — un comment propio arriba
    # duplicaba la etiqueta (reportado por el usuario: "se enciman etiquetas").
    # Solo live.menu y live.button necesitan una etiqueta propia (no traen una).
    needs_own_label = maxclass not in ('live.dial', 'live.slider', 'live.numbox')
    if needs_own_label:
        label_box = p.add_comment(label, patching_rect=[x, y, w, 20], fontsize=9)
        label_box.add_to_presentation([x, y, w, 13])

    valueof = {'parameter_longname': label, 'parameter_shortname': label[:8]}
    if param_type is not None:
        valueof['parameter_type'] = param_type
    if param_min is not None:
        valueof['parameter_mmin'] = param_min
    if param_max is not None:
        valueof['parameter_mmax'] = param_max
    if param_enum is not None:
        valueof['parameter_enum'] = param_enum
    if param_initial is not None:
        valueof['parameter_initial'] = [param_initial]
        valueof['parameter_initial_enable'] = 1

    ctl_y = y + 15
    ctl = p.add_textbox(maxclass, maxclass=maxclass,
                         patching_rect=[x, ctl_y + 200, w, ctl_h],
                         varname=varname, parameter_longname=label,
                         parameter_shortname=label[:8],
                         saved_attribute_attributes=dict(valueof=valueof),
                         **attrs)
    ctl.add_to_presentation([x, ctl_y, w, ctl_h])

    prep = p.add_textbox('prepend ' + varname,
                          patching_rect=[x, ctl_y + 230, 100, 20])
    p.add_line(ctl, prep, inlet=0, outlet=0)
    p.add_line(prep, js, inlet=0, outlet=0)

    return ctl_y + ctl_h


def main():
    p = Patcher('CR_Generator_rebuild.amxd', device_type='midi_effect')
    p.enable_presentation(devicewidth=DEVICE_WIDTH)

    # Passthrough MIDI mínimo — el device no filtra MIDI entrante, genera y escribe
    # directo a un clip vía LiveAPI, pero se deja un paso directo por seguridad.
    midi_in = p.add_textbox('midiin', patching_rect=[20, 700, 60, 20])
    midi_out = p.add_textbox('midiout', patching_rect=[20, 730, 60, 20])
    p.add_line(midi_in, midi_out, inlet=0, outlet=0)

    # Motor — el archivo real se carga por nombre, debe copiarse junto al .amxd.
    js = p.add_textbox('js cr_device.js', patching_rect=[20, 660, 150, 20])

    y = MARGIN

    # Fila 1 (8 columnas): armonía + estilo
    add_control(p, js, 'live.menu', 'key', 'Key', y, col=0,
                param_type=2, param_min=0, param_max=len(NOTE_NAMES) - 1, param_enum=NOTE_NAMES)
    add_control(p, js, 'live.menu', 'scale', 'Scale', y, col=1, span=2,
                items=SCALES, param_type=2, param_min=0, param_max=len(SCALES) - 1, param_enum=SCALES)
    add_control(p, js, 'live.menu', 'style', 'Style', y, col=3, span=2,
                items=STYLES, param_type=2, param_min=0, param_max=len(STYLES) - 1, param_enum=STYLES)
    add_control(p, js, 'live.menu', 'motiftype', 'Motif Type', y, col=5, span=2,
                items=MOTIF_TYPES, param_type=2, param_min=0, param_max=len(MOTIF_TYPES) - 1, param_enum=MOTIF_TYPES)
    y += 35

    # Fila 2 (8 columnas): respuesta
    add_control(p, js, 'live.menu', 'responsestrategy', 'Resp. Strategy', y, col=0, span=2,
                items=RESPONSE_STRATEGIES, param_type=2, param_min=0,
                param_max=len(RESPONSE_STRATEGIES) - 1, param_enum=RESPONSE_STRATEGIES)
    add_control(p, js, 'live.menu', 'endingbehaviour', 'Ending', y, col=2, span=2,
                items=ENDING_BEHAVIOURS, param_type=2, param_min=0,
                param_max=len(ENDING_BEHAVIOURS) - 1, param_enum=ENDING_BEHAVIOURS)
    add_control(p, js, 'live.menu', 'repetition', 'Repetition', y, col=4,
                items=REPETITIONS, param_type=2, param_min=0, param_max=len(REPETITIONS) - 1, param_enum=REPETITIONS)
    add_control(p, js, 'live.menu', 'contour', 'Contour', y, col=5, span=2,
                items=CONTOURS, param_type=2, param_min=0, param_max=len(CONTOURS) - 1, param_enum=CONTOURS)
    y += 35

    # Fila 3 (8 columnas): dials/slider/numbox + los 3 botones de generación,
    # todo en la misma fila para que quede visible sin scroll.
    add_control(p, js, 'live.dial', 'octave', 'Octave', y, col=0, ctl_h=44,
                size=4, min=1, max=5, param_type=1, param_min=1, param_max=5, param_initial=3)
    # Steps hasta 32 (64 pasos totales call+response) para progresiones más largas.
    add_control(p, js, 'live.dial', 'steps', 'Steps', y, col=1, ctl_h=44,
                size=30, min=2, max=32, param_type=1, param_min=2, param_max=32, param_initial=8)
    add_control(p, js, 'live.dial', 'density', 'Density', y, col=2, ctl_h=44,
                size=1, min=0.0, max=1.0, param_type=0, param_min=0.0, param_max=1.0, param_initial=0.5)
    add_control(p, js, 'live.slider', 'notelength', 'Note Length', y, col=3, ctl_h=44,
                min=40, max=200, param_type=1, param_min=40, param_max=200, param_initial=100)
    add_control(p, js, 'live.numbox', 'seed', 'Seed', y, col=4, ctl_h=20)

    # live.button es un LED pequeño sin texto propio — sin una etiqueta aparte es
    # casi invisible en el panel del device (reportado por el usuario). Se agrega
    # un comment con el nombre justo encima de cada uno, estilo macro de Ableton.
    buttons = [('newpair', 'New Pair'), ('mutate', 'Mutate'), ('writeclip', 'Write Clip')]
    for i, (varname, label) in enumerate(buttons):
        add_control(p, js, 'live.button', varname, label, y, col=5 + i, ctl_h=30)
    # live.dial en Ableton dibuja su propio nombre + valor DEBAJO del knob —
    # esa franja no está contada en ctl_h, por eso el label "Pattern" de abajo
    # se encimaba con el "3" del dial de Octave (reportado por el usuario).
    y += 15 + 44 + 20


    # ---- vista de pasos (multislider) — feedback visual del patrón generado,
    # tipo step-sequencer. Es de solo lectura: cr_device.js la actualiza vía
    # messnamed('stepview', 'set', ...) después de New Pair / Mutate / Write
    # Clip; no es un parámetro live.* automatizable, es puramente visual.
    label_box = p.add_comment('Pattern (call + response)', patching_rect=[MARGIN, y, 300, 16], fontsize=9)
    label_box.add_to_presentation([MARGIN, y, 300, 13])
    y += 15
    stepview = p.add_textbox('multislider', maxclass='multislider',
                              patching_rect=[MARGIN, y + 400, DEVICE_WIDTH - 2 * MARGIN, 50],
                              varname='stepview', size=64, setminmax=[0.0, 1.0],
                              setstyle=1)
    stepview.add_to_presentation([MARGIN, y, DEVICE_WIDTH - 2 * MARGIN, 50])

    p.save()
    print('escrito:', p.file.resolve() if hasattr(p, 'file') else 'CR_Generator_rebuild.amxd')


if __name__ == '__main__':
    main()
