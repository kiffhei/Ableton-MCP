// cr_engine.js — motor generativo de Call & Response, puerto ES5
//
// Fuente original: https://github.com/Nordl3/Call-Response-Generator (MIT License,
// (c) Nordl3). Ese proyecto es una web app de un solo archivo (index.html) en
// JavaScript moderno (ES6+). Este archivo es un puerto a ES5 estricto — sin let/const,
// arrow functions, template literals, destructuring, spread, Array.from, Set,
// nullish coalescing (??) ni optional chaining (?.) — porque el objeto `js` de Max
// (SpiderMonkey embebido) usa el motor ES5, y el objeto `v8ui`/`v8` que sí soporta
// ES6+ no existe en Max 8.6 (ver CALL_RESPONSE_REBUILD_PLAN.md).
//
// Cambio deliberado sobre el original: Math.random() reemplazado por un PRNG con
// seed (mulberry32) para que la generación sea reproducible — el original no lo era.
//
// Este NO es el device de Side Brain ni una copia de sus extensiones (swing, gate
// feel, slide/accent profiles, presets, undo) — esas nunca fueron públicas. Es un
// rebuild del motor de Nordl3 tal cual, para que corra en Max 8.6.
//
// Atribución MIT completa en cr_engine.LICENSE (mismo directorio).

var CR = (function () {
  "use strict";

  // ---- datos ---------------------------------------------------------------

  var NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

  var SCALE_INTERVALS = {
    'Chromatic': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    'Major / Ionian': [0, 2, 4, 5, 7, 9, 11],
    'Natural Minor / Aeolian': [0, 2, 3, 5, 7, 8, 10],
    'Harmonic Minor': [0, 2, 3, 5, 7, 8, 11],
    'Melodic Minor': [0, 2, 3, 5, 7, 9, 11],
    'Dorian': [0, 2, 3, 5, 7, 9, 10],
    'Phrygian': [0, 1, 3, 5, 7, 8, 10],
    'Mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'Locrian': [0, 1, 3, 5, 6, 8, 10],
    'Lydian': [0, 2, 4, 6, 7, 9, 11],
    'Lydian Dominant': [0, 2, 4, 6, 7, 9, 10],
    'Aeolian b5': [0, 2, 3, 5, 6, 8, 10],
    'Dorian b2': [0, 1, 3, 5, 7, 9, 10],
    'Mixolydian b6': [0, 2, 4, 5, 7, 8, 10],
    'Major Pentatonic': [0, 2, 4, 7, 9],
    'Minor Pentatonic': [0, 3, 5, 7, 10],
    'Blues Minor': [0, 3, 5, 6, 7, 10],
    'Blues Major': [0, 2, 3, 4, 7, 9],
    'Phrygian Dominant': [0, 1, 4, 5, 7, 8, 10],
    'Double Harmonic': [0, 1, 4, 5, 7, 8, 11],
    'Hungarian Minor': [0, 2, 3, 6, 7, 8, 11],
    'Romanian Minor': [0, 2, 3, 6, 7, 9, 10],
    'Whole Tone': [0, 2, 4, 6, 8, 10],
    'Diminished Half-Whole': [0, 1, 3, 4, 6, 7, 9, 10],
    'Diminished Whole-Half': [0, 2, 3, 5, 6, 8, 9, 11],
    'Persian': [0, 1, 4, 5, 6, 8, 11],
    'Arabic': [0, 2, 4, 5, 6, 8, 10],
    'Byzantine': [0, 1, 4, 5, 7, 8, 11],
    'Hirajoshi': [0, 2, 3, 7, 8],
    'In Sen': [0, 1, 5, 7, 10],
    'Japanese Pentatonic': [0, 1, 5, 7, 8],
    'Kumoi': [0, 2, 3, 7, 9],
    'Pelog-ish': [0, 1, 3, 7, 8],
    'Egyptian Pentatonic': [0, 2, 5, 7, 10],
    'Minor Triad only': [0, 3, 7],
    'Power Fifths': [0, 7],
    'Root + b7': [0, 10],
    'Root + 5th + b7': [0, 7, 10],
    'Root + 2nd + 5th': [0, 2, 7],
    'Minor 7 arpeggio pool': [0, 3, 7, 10],
    'Dominant 7 arpeggio pool': [0, 4, 7, 10],
    'Diminished 7 arpeggio pool': [0, 3, 6, 9]
  };

  var DATA = {
    styles: ['Classic Acid', 'Raw Acid', 'Squelchy Acid', 'Dark Acid', 'Hypno Acid',
      'Sparse Acid', 'Busy Acid', 'Acid Stabs', 'Acid Runner', 'Acid Question/Answer',
      'Driving Techno', 'Hypnotic Techno', 'Minimal Techno', 'Raw Warehouse',
      'Tool Techno', 'Dub Techno', 'Industrial Techno', 'Percussive Techno',
      'Loop Techno', 'Broken Techno', 'Jackin House', 'Deep House', 'Minimal House',
      'Classic House', 'Tech House', 'Bass House', 'Shuffly House',
      'Organ House-ish', 'House Stabline', 'House Bounce', '90s Rave', 'Dark Rave',
      'Rave Stab', 'Electro Pulse', 'Breaky Electro', 'Detroit-ish', 'Proto-Trance',
      'Hooverish Riff', 'Motif Study', 'Rooted Groove', 'Repetitive Hook',
      'Wide Answer', 'Tight Answer', 'Tension Builder', 'Resolver',
      'Call Lead / Response Support'],
    responseStrategies: ['Same rhythm + resolve', 'Same rhythm + new contour',
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
      'Hook then fill', 'Call dominant / response tonic'],
    motifTypes: ['Pulse', 'Offbeat', 'Syncopated', 'Push', 'Sparse', 'Dense',
      'Rest-heavy', 'Four-on-floor companion', 'Stabbed', 'Rolling', 'Repeated note',
      'Stepwise rise', 'Stepwise fall', 'Rise then drop', 'Drop then rise',
      'Leap then settle', 'Pivot note', 'Two-note hook', 'Three-note hook',
      'Arp fragment', 'Acid nibble', 'Techno cell', 'House bounce',
      'Rave stab figure', 'Drone anchor', 'Pedal point motif', 'Call tag',
      'Answer tag'],
    endingBehaviours: ['Resolve to root', 'Resolve to 5th', 'Leave hanging',
      'Rise into next phrase', 'Fall into next phrase', 'Hard stop', 'Fade energy',
      'Strong cadence', 'Weak cadence', 'Ambiguous ending',
      'Response more resolved than call', 'Response same tension as call',
      'Response more tense than call'],
    // Mismo orden que SCALE_INTERVALS arriba — usado para lookup por índice desde
    // los controles live.menu del patcher (más robusto que rutear texto).
    scales: ['Chromatic', 'Major / Ionian', 'Natural Minor / Aeolian', 'Harmonic Minor',
      'Melodic Minor', 'Dorian', 'Phrygian', 'Mixolydian', 'Locrian', 'Lydian',
      'Lydian Dominant', 'Aeolian b5', 'Dorian b2', 'Mixolydian b6',
      'Major Pentatonic', 'Minor Pentatonic', 'Blues Minor', 'Blues Major',
      'Phrygian Dominant', 'Double Harmonic', 'Hungarian Minor', 'Romanian Minor',
      'Whole Tone', 'Diminished Half-Whole', 'Diminished Whole-Half', 'Persian',
      'Arabic', 'Byzantine', 'Hirajoshi', 'In Sen', 'Japanese Pentatonic', 'Kumoi',
      'Pelog-ish', 'Egyptian Pentatonic', 'Minor Triad only', 'Power Fifths',
      'Root + b7', 'Root + 5th + b7', 'Root + 2nd + 5th', 'Minor 7 arpeggio pool',
      'Dominant 7 arpeggio pool', 'Diminished 7 arpeggio pool']
  };

  // ---- PRNG determinista (mulberry32) — reemplaza Math.random() del original ---

  function imul32(a, b) {
    if (typeof Math.imul === 'function') return Math.imul(a, b);
    var aHi = (a >>> 16) & 0xffff, aLo = a & 0xffff;
    var bHi = (b >>> 16) & 0xffff, bLo = b & 0xffff;
    return ((aLo * bLo) + (((aHi * bLo + aLo * bHi) << 16) >>> 0)) | 0;
  }

  function makeRng(seed) {
    var a = seed | 0;
    return function () {
      a = (a + 0x6D2B79F5) | 0;
      var t = imul32(a ^ (a >>> 15), 1 | a);
      t = (t + imul32(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // rand/chance/pickN se reasignan sobre la instancia de rng activa (setSeed) —
  // mismo patrón que el original (funciones de módulo cerrando sobre una fuente
  // de aleatoriedad compartida), solo que aquí es determinista.
  var _rng = makeRng(1);

  function rand(arr) { return arr[Math.floor(_rng() * arr.length)]; }
  function chance(p) { return _rng() < p; }
  function pickN(arr, n) {
    var a = arr.slice(), out = [];
    while (a.length && out.length < n) {
      out.push(a.splice(Math.floor(_rng() * a.length), 1)[0]);
    }
    return out;
  }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  function setSeed(seed) { _rng = makeRng(seed); }

  // ---- helpers ES5 para lo que en el original era sintaxis ES6+ ---------------

  function nz(x, fallback) { return (x !== null && x !== undefined) ? x : fallback; }

  function range(n) {
    var out = [], i;
    for (i = 0; i < n; i++) out.push(i);
    return out;
  }

  function buildArray(n, fn) {
    var out = [], i;
    for (i = 0; i < n; i++) out.push(fn(i));
    return out;
  }

  function uniq(arr) {
    var out = [], seen = {}, i, key;
    for (i = 0; i < arr.length; i++) {
      key = String(arr[i]);
      if (!seen.hasOwnProperty(key)) { seen[key] = true; out.push(arr[i]); }
    }
    return out;
  }

  function filterLt(arr, bound) {
    var out = [], i;
    for (i = 0; i < arr.length; i++) if (arr[i] < bound) out.push(arr[i]);
    return out;
  }

  // Step = {active, degree, dur, gate, accent, slide, tie}
  function cloneStep(s) {
    return {
      active: s.active, degree: s.degree, dur: nz(s.dur, 1),
      gate: s.gate, accent: s.accent, slide: s.slide, tie: s.tie
    };
  }

  function mergeArt(step, art) {
    var out = cloneStep(step);
    out.gate = art.gate; out.accent = art.accent; out.slide = art.slide; out.tie = art.tie;
    return out;
  }

  // ---- pitch mapping ---------------------------------------------------------

  var OCTAVE_MAP = { 'C1': 24, 'C2': 36, 'C3': 48, 'C4': 60, 'C5': 72 };

  function rootMidi(c) {
    return OCTAVE_MAP[c.rootOctave] + NOTE_NAMES_INDEX(c.key);
  }
  function NOTE_NAMES_INDEX(name) {
    var i;
    for (i = 0; i < NOTE_NAMES.length; i++) if (NOTE_NAMES[i] === name) return i;
    return 0;
  }
  function degreeToMidi(deg, c) {
    var s = c.scale, len = s.length || 1;
    var oct = Math.floor(deg / len);
    var idx = ((deg % len) + len) % len;
    return rootMidi(c) + s[idx] + oct * 12;
  }

  // ---- estilo / densidad / contorno -------------------------------------------

  function densityValue(name) {
    var m = { 'Very sparse': 0.24, 'Sparse': 0.36, 'Medium': 0.52, 'Busy': 0.66, 'Dense': 0.8, 'Very dense': 0.92 };
    return m.hasOwnProperty(name) ? m[name] : 0.5;
  }
  function repetitionValue(name) {
    var m = { 'Very repetitive': 0.88, 'Repetitive': 0.72, 'Balanced': 0.5, 'Varied': 0.32, 'Highly varied': 0.18 };
    return m.hasOwnProperty(name) ? m[name] : 0.5;
  }
  function contourBias(name) {
    var m = { 'Flat': 0, 'Slight rise': 1, 'Slight fall': -1, 'Arch': 2, 'Inverted arch': -2, 'Wandering': 99, 'Stepwise': 100, 'Leapy': 101 };
    return m.hasOwnProperty(name) ? m[name] : 0;
  }

  function stylePresetMap() {
    return {
      'Classic Acid': { cat: 'acid', density: 0.56, repeat: 0.66, slide: 0.38, accent: 0.46, rootBias: 0.30, syncBias: 0.28 },
      'Raw Acid': { cat: 'acid', density: 0.62, repeat: 0.58, slide: 0.32, accent: 0.54, rootBias: 0.24, choppyBias: 0.24 },
      'Squelchy Acid': { cat: 'acid', density: 0.54, repeat: 0.62, slide: 0.46, accent: 0.42, sustainBias: 0.28 },
      'Dark Acid': { cat: 'acid', density: 0.46, repeat: 0.70, slide: 0.26, accent: 0.34, rootBias: 0.38, restBias: 0.20 },
      'Hypno Acid': { cat: 'acid', density: 0.48, repeat: 0.78, slide: 0.24, accent: 0.28, sustainBias: 0.42 },
      'Sparse Acid': { cat: 'acid', density: 0.34, repeat: 0.74, slide: 0.22, accent: 0.30, restBias: 0.30 },
      'Busy Acid': { cat: 'acid', density: 0.72, repeat: 0.54, slide: 0.36, accent: 0.44, motifVar: 0.24 },
      'Acid Stabs': { cat: 'acid', density: 0.42, repeat: 0.66, slide: 0.10, accent: 0.52, choppyBias: 0.46 },
      'Acid Runner': { cat: 'acid', density: 0.70, repeat: 0.60, slide: 0.34, accent: 0.36, leap: 0.26 },
      'Acid Question/Answer': { cat: 'acid', density: 0.52, repeat: 0.68, slide: 0.26, accent: 0.40, responseTightness: 0.78 },
      'Driving Techno': { cat: 'techno', density: 0.44, repeat: 0.78, accent: 0.24, choppyBias: 0.34, rootBias: 0.38 },
      'Hypnotic Techno': { cat: 'techno', density: 0.36, repeat: 0.86, accent: 0.18, sustainBias: 0.28, responseTightness: 0.78 },
      'Minimal Techno': { cat: 'techno', density: 0.28, repeat: 0.84, accent: 0.16, restBias: 0.34, choppyBias: 0.40 },
      'Raw Warehouse': { cat: 'techno', density: 0.48, repeat: 0.66, accent: 0.34, choppyBias: 0.42, leap: 0.18 },
      'Tool Techno': { cat: 'techno', density: 0.40, repeat: 0.82, accent: 0.18, rootBias: 0.44 },
      'Dub Techno': { cat: 'techno', density: 0.26, repeat: 0.88, accent: 0.14, restBias: 0.32, sustainBias: 0.36 },
      'Industrial Techno': { cat: 'techno', density: 0.46, repeat: 0.60, accent: 0.38, choppyBias: 0.48, leap: 0.20 },
      'Percussive Techno': { cat: 'techno', density: 0.42, repeat: 0.74, accent: 0.32, choppyBias: 0.44 },
      'Loop Techno': { cat: 'techno', density: 0.38, repeat: 0.90, accent: 0.16, responseTightness: 0.84 },
      'Broken Techno': { cat: 'techno', density: 0.44, repeat: 0.48, accent: 0.24, motifVar: 0.28, leap: 0.22 },
      'Jackin House': { cat: 'house', density: 0.52, repeat: 0.66, accent: 0.24, offbeatBias: 0.42 },
      'Deep House': { cat: 'house', density: 0.36, repeat: 0.76, accent: 0.18, sustainBias: 0.24, offbeatBias: 0.36 },
      'Minimal House': { cat: 'house', density: 0.30, repeat: 0.82, accent: 0.18, restBias: 0.26, offbeatBias: 0.30 },
      'Classic House': { cat: 'house', density: 0.46, repeat: 0.70, accent: 0.22, offbeatBias: 0.38 },
      'Tech House': { cat: 'house', density: 0.44, repeat: 0.68, accent: 0.22, choppyBias: 0.22, offbeatBias: 0.28 },
      'Bass House': { cat: 'house', density: 0.58, repeat: 0.62, accent: 0.28, rootBias: 0.40, offbeatBias: 0.26 },
      'Shuffly House': { cat: 'house', density: 0.48, repeat: 0.66, accent: 0.22, offbeatBias: 0.48, sustainBias: 0.18 },
      'Organ House-ish': { cat: 'house', density: 0.42, repeat: 0.72, accent: 0.18, sustainBias: 0.30, offbeatBias: 0.34 },
      'House Stabline': { cat: 'house', density: 0.40, repeat: 0.70, accent: 0.34, choppyBias: 0.34, offbeatBias: 0.30 },
      'House Bounce': { cat: 'house', density: 0.50, repeat: 0.68, accent: 0.22, offbeatBias: 0.50, leap: 0.10 },
      '90s Rave': { cat: 'rave', density: 0.56, repeat: 0.46, accent: 0.28, leap: 0.30, octaveBias: 0.22 },
      'Dark Rave': { cat: 'rave', density: 0.44, repeat: 0.56, accent: 0.24, leap: 0.24, rootBias: 0.30 },
      'Rave Stab': { cat: 'rave', density: 0.40, repeat: 0.62, accent: 0.38, choppyBias: 0.36 },
      'Electro Pulse': { cat: 'rave', density: 0.46, repeat: 0.62, accent: 0.24, offbeatBias: 0.24 },
      'Breaky Electro': { cat: 'rave', density: 0.48, repeat: 0.42, accent: 0.22, motifVar: 0.26 },
      'Detroit-ish': { cat: 'other', density: 0.40, repeat: 0.70, accent: 0.18, rootBias: 0.34, sustainBias: 0.20 },
      'Proto-Trance': { cat: 'rave', density: 0.48, repeat: 0.64, accent: 0.18, sustainBias: 0.24, leap: 0.18 },
      'Hooverish Riff': { cat: 'rave', density: 0.52, repeat: 0.50, accent: 0.30, leap: 0.34 },
      'Motif Study': { cat: 'other', density: 0.42, repeat: 0.92, accent: 0.14, motifVar: 0.06, responseTightness: 0.88 },
      'Rooted Groove': { cat: 'other', density: 0.40, repeat: 0.80, accent: 0.16, rootBias: 0.56 },
      'Repetitive Hook': { cat: 'other', density: 0.46, repeat: 0.90, accent: 0.18, motifVar: 0.10 },
      'Wide Answer': { cat: 'other', density: 0.44, repeat: 0.60, accent: 0.18, responseTightness: 0.46, leap: 0.28 },
      'Tight Answer': { cat: 'other', density: 0.44, repeat: 0.72, accent: 0.18, responseTightness: 0.88 },
      'Tension Builder': { cat: 'other', density: 0.48, repeat: 0.66, accent: 0.22, stableEnd: 0.40, leap: 0.22 },
      'Resolver': { cat: 'other', density: 0.40, repeat: 0.74, accent: 0.16, stableEnd: 0.90, responseTightness: 0.78 },
      'Call Lead / Response Support': { cat: 'other', density: 0.42, repeat: 0.72, accent: 0.18, responseTightness: 0.84 }
    };
  }

  function styleCategory(style) {
    var map = stylePresetMap(), s;
    if (map[style] && map[style].cat) return map[style].cat;
    s = style.toLowerCase();
    if (s.indexOf('acid') !== -1) return 'acid';
    if (s.indexOf('house') !== -1) return 'house';
    if (s.indexOf('techno') !== -1) return 'techno';
    if (s.indexOf('rave') !== -1 || s.indexOf('electro') !== -1 || s.indexOf('hoover') !== -1) return 'rave';
    return 'other';
  }

  function preferredStepActivation(cat, idx) {
    if (cat === 'acid') return [0.82, 0.35, 0.72, 0.28][idx % 4];
    if (cat === 'techno') return [0.86, 0.18, 0.58, 0.22][idx % 4];
    if (cat === 'house') return [0.72, 0.48, 0.62, 0.34][idx % 4];
    if (cat === 'rave') return [0.78, 0.42, 0.68, 0.38][idx % 4];
    return [0.7, 0.35, 0.6, 0.3][idx % 4];
  }

  function styleProfile(c) {
    var style = c.style.toLowerCase();
    var density = 0.45, leap = 0.18, repeat = 0.45, stableEnd = 0.7, accent = 0.25, slide = 0.18;
    var restBias = 0.18, motifVar = 0.18, responseTightness = 0.5, rootBias = 0.22, octaveBias = 0.12;
    var syncBias = 0.18, offbeatBias = 0.14, sustainBias = 0.18, choppyBias = 0.14;
    var preset = stylePresetMap()[c.style];

    if (style.indexOf('acid') !== -1) { density = 0.55; leap = 0.22; repeat = 0.62; accent = 0.45; slide = 0.35; rootBias = 0.28; responseTightness = 0.66; syncBias = 0.26; sustainBias = 0.34; }
    if (style.indexOf('raw') !== -1) { density += 0.08; accent += 0.08; motifVar += 0.08; choppyBias += 0.12; }
    if (style.indexOf('hypno') !== -1) { repeat += 0.15; leap -= 0.08; stableEnd = 0.55; restBias = 0.1; responseTightness = 0.72; sustainBias += 0.16; }
    if (style.indexOf('minimal') !== -1) { density -= 0.12; repeat += 0.12; restBias = 0.28; }
    if (style.indexOf('busy') !== -1) { density += 0.18; restBias -= 0.06; }
    if (style.indexOf('sparse') !== -1) { density -= 0.18; restBias += 0.12; }
    if (style.indexOf('house') !== -1) { density = 0.48; leap = 0.12; repeat = 0.58; accent = 0.22; slide = 0.1; rootBias = 0.32; responseTightness = 0.62; offbeatBias = 0.3; syncBias = 0.2; sustainBias = 0.12; }
    if (style.indexOf('techno') !== -1) { density = 0.42; leap = 0.14; repeat = 0.68; accent = 0.2; slide = 0.08; rootBias = 0.35; restBias = 0.24; responseTightness = 0.7; choppyBias = 0.3; syncBias = 0.12; }
    if (style.indexOf('rave') !== -1 || style.indexOf('electro') !== -1 || style.indexOf('hoover') !== -1) { density = 0.5; leap = 0.24; repeat = 0.35; accent = 0.3; slide = 0.06; octaveBias = 0.2; offbeatBias = 0.22; }
    if (style.indexOf('dub') !== -1) { density = 0.34; repeat = 0.7; restBias = 0.3; stableEnd = 0.78; sustainBias = 0.22; }
    if (style.indexOf('industrial') !== -1 || style.indexOf('warehouse') !== -1) { density = 0.46; leap = 0.18; repeat = 0.56; accent = 0.34; rootBias = 0.4; choppyBias = 0.28; }
    if (style.indexOf('motif study') !== -1) { repeat = 0.82; motifVar = 0.08; responseTightness = 0.85; }
    if (style.indexOf('rooted groove') !== -1) { rootBias = 0.5; repeat = 0.7; stableEnd = 0.8; }
    if (style.indexOf('repetitive hook') !== -1) { repeat = 0.85; density = 0.48; motifVar = 0.1; }

    if (preset) {
      density = nz(preset.density, density);
      leap = nz(preset.leap, leap);
      repeat = nz(preset.repeat, repeat);
      stableEnd = nz(preset.stableEnd, stableEnd);
      accent = nz(preset.accent, accent);
      slide = nz(preset.slide, slide);
      restBias = nz(preset.restBias, restBias);
      motifVar = nz(preset.motifVar, motifVar);
      responseTightness = nz(preset.responseTightness, responseTightness);
      rootBias = nz(preset.rootBias, rootBias);
      octaveBias = nz(preset.octaveBias, octaveBias);
      syncBias = nz(preset.syncBias, syncBias);
      offbeatBias = nz(preset.offbeatBias, offbeatBias);
      sustainBias = nz(preset.sustainBias, sustainBias);
      choppyBias = nz(preset.choppyBias, choppyBias);
    }

    return {
      density: density, leap: leap, repeat: repeat, stableEnd: stableEnd, accent: accent,
      slide: slide, restBias: restBias, motifVar: motifVar, responseTightness: responseTightness,
      rootBias: rootBias, octaveBias: octaveBias, syncBias: syncBias, offbeatBias: offbeatBias,
      sustainBias: sustainBias, choppyBias: choppyBias
    };
  }

  // ---- pool de notas / motif ---------------------------------------------------

  function notePool(c) {
    var scaleLen = c.scale.length;
    var pool = range(Math.min(scaleLen, 7));
    if (c.notePoolMode === 'Strict note pool') pool = pickN(pool, Math.min(pool.length, 3));
    else if (c.notePoolMode === 'Pool with spice notes') {
      pool = uniq(pickN(pool, Math.min(pool.length, 4)).concat([Math.min(scaleLen - 1, Math.floor(scaleLen / 2))]));
    }
    else if (c.notePoolMode === 'Pool expands on response') pool = filterLt([0, 1, 2, 4], scaleLen);
    else if (c.notePoolMode === 'Pool contracts on response') pool = range(scaleLen);
    else if (c.notePoolMode === 'Root-heavy') pool = filterLt([0, 0, 0, 1, 2, 4], scaleLen);
    else if (c.notePoolMode === 'Root + 5th heavy') pool = filterLt([0, 0, 4, 4, 1, 2], scaleLen);
    else if (c.notePoolMode === 'Triad pool') pool = filterLt([0, 2, 4], scaleLen);
    else if (c.notePoolMode === 'Seventh pool') pool = filterLt([0, 2, 4, 6], scaleLen);
    else if (c.notePoolMode === 'Scale-wide') pool = range(scaleLen);
    return pool.length ? pool : [0];
  }

  function motifTemplate(c) {
    var t = c.motifType.toLowerCase();
    var len = c.steps <= 4 ? 2 : (c.steps <= 8 ? rand([2, 3, 4]) : rand([3, 4]));
    var rhythm, contour, i;

    if (t.indexOf('pulse') !== -1) rhythm = buildArray(len, function () { return true; });
    else if (t.indexOf('offbeat') !== -1) rhythm = buildArray(len, function (i) { return i % 2 === 1; });
    else if (t.indexOf('sync') !== -1) rhythm = buildArray(len, function (i) { return chance(i === 0 ? 0.78 : 0.55); });
    else if (t.indexOf('sparse') !== -1 || t.indexOf('rest') !== -1) rhythm = buildArray(len, function () { return chance(0.45); });
    else if (t.indexOf('dense') !== -1 || t.indexOf('rolling') !== -1) rhythm = buildArray(len, function () { return chance(0.82); });
    else if (t.indexOf('stab') !== -1) rhythm = buildArray(len, function (i) { return i === 0 || chance(0.25); });
    else rhythm = buildArray(len, function () { return chance(0.65); });

    if (!(function () { for (i = 0; i < rhythm.length; i++) if (rhythm[i]) return true; return false; })()) rhythm[0] = true;

    if (t.indexOf('repeated') !== -1) contour = buildArray(len, function () { return 0; });
    else if (t.indexOf('stepwise rise') !== -1) contour = buildArray(len, function (i) { return i; });
    else if (t.indexOf('stepwise fall') !== -1) contour = buildArray(len, function (i) { return -i; });
    else if (t.indexOf('rise then drop') !== -1) contour = [0, 1, 2, 0, -1].slice(0, len);
    else if (t.indexOf('drop then rise') !== -1) contour = [0, -1, -2, 0, 1].slice(0, len);
    else if (t.indexOf('leap') !== -1) contour = [0, rand([2, 3, 4]), 1, 0].slice(0, len);
    else if (t.indexOf('pivot') !== -1) contour = [0, 1, 0, -1].slice(0, len);
    else if (t.indexOf('two-note') !== -1) contour = [0, 1, 0, 1].slice(0, len);
    else if (t.indexOf('three-note') !== -1) contour = [0, 1, 2, 1].slice(0, len);
    else if (t.indexOf('arp') !== -1) contour = [0, 2, 4, 2].slice(0, len);
    else if (t.indexOf('acid') !== -1 || t.indexOf('techno') !== -1 || t.indexOf('house') !== -1) contour = [0, 0, 1, 0, -1].slice(0, len);
    else contour = buildArray(len, function () { return rand([-1, 0, 1]); });

    return { len: len, rhythm: rhythm, contour: contour };
  }

  // ---- articulación -------------------------------------------------------------

  function articulationForStep(idx, active, c, motifPos) {
    var sp = styleProfile(c);
    var cat = styleCategory(c.style);
    var gate = 0.82, accent = false, slide = false, tie = false;
    var gateFeel = c.gateFeel, conn = c.connectionFeel, slideP = c.slideProfile, accentP = c.accentProfile, art = c.articulationProfile;

    if (gateFeel === 'Tight') gate = 0.45;
    else if (gateFeel === 'Short') gate = 0.6;
    else if (gateFeel === 'Medium') gate = 0.82;
    else if (gateFeel === 'Long') gate = 1.15;
    else if (gateFeel === 'Mixed') gate = [0.55, 0.7, 0.85, 1.0, 1.15][idx % 5];
    else if (gateFeel === 'Random within bounds') gate = 0.45 + _rng() * 0.8;

    if (cat === 'acid') {
      gate = Math.max(gate, 0.72 + (motifPos === 0 ? 0.12 : 0));
      if (idx % 4 === 3 && chance(sp.sustainBias)) gate = Math.max(gate, 1.0);
    } else if (cat === 'techno') {
      gate = Math.min(gate, 0.78);
      if (idx % 4 === 0) gate = Math.min(0.68, gate);
    } else if (cat === 'house') {
      if (idx % 2 === 1 && chance(sp.offbeatBias)) gate = Math.max(gate, 0.9);
      else gate = Math.min(Math.max(gate, 0.62), 0.95);
    }

    if (conn === 'Detached') gate = Math.min(gate, 0.62);
    else if (conn === 'Semi-detached') gate = Math.min(Math.max(gate, 0.6), 0.85);
    else if (conn === 'Legato') gate = Math.max(gate, 1.0);
    else if (conn === 'Tied bias') { gate = Math.max(gate, 1.05); tie = chance(0.25); }
    else if (conn === 'Mixed ties') tie = chance(0.18);
    else if (conn === 'Connected runs') { gate = Math.max(gate, 1.0); tie = chance(0.12); }

    if (art === 'Acidic') { accent = chance(sp.accent); slide = chance(sp.slide); gate = Math.max(gate, 0.86); }
    if (art === 'Punchy') { accent = chance(0.25); gate = Math.min(gate, 0.68); }
    if (art === 'Rolling') { gate = Math.max(gate, 0.95); tie = tie || chance(0.12); }
    if (art === 'Choppy') { gate = Math.min(gate, 0.55); slide = false; }
    if (art === 'Fluid') { gate = Math.max(gate, 1.05); slide = chance(0.18); }
    if (art === 'Stabbed') { gate = Math.min(gate, 0.5); accent = chance(0.35); }
    if (art === 'Tense') { accent = chance(0.32); slide = chance(0.08); }
    if (art === 'Released') { gate = Math.max(gate, 0.95); accent = chance(0.12); }

    if (slideP === 'None') slide = false;
    else if (slideP === 'Rare') slide = chance(0.06);
    else if (slideP === 'Occasional') slide = chance(0.16);
    else if (slideP === 'Acid moderate') slide = chance(0.28);
    else if (slideP === 'Acid heavy') slide = chance(0.42);
    else if (slideP === 'Phrase-end slides') slide = chance(motifPos >= 2 ? 0.32 : 0.04);
    else if (slideP === 'Upward slides bias') slide = chance(0.18);
    else if (slideP === 'Downward slides bias') slide = chance(0.18);

    if (accentP === 'None') accent = false;
    else if (accentP === 'Light') accent = chance(0.14);
    else if (accentP === 'Moderate') accent = chance(0.24);
    else if (accentP === 'Heavy') accent = chance(0.38);
    else if (accentP === 'Offbeat accents') accent = idx % 2 === 1 && chance(0.5);
    else if (accentP === 'Downbeat accents') accent = idx % 4 === 0 || idx === 0;
    else if (accentP === 'Motif accents') accent = motifPos === 0 || chance(0.08);
    else if (accentP === 'Random accents within motif') accent = chance(0.22);

    if (cat === 'acid' && active) {
      if (idx % 4 === 0) accent = accent || chance(0.45);
      if (idx % 4 === 2) slide = slide || chance(0.2);
      tie = tie || chance(0.08);
    } else if (cat === 'techno' && active) {
      accent = accent || (idx % 4 === 0 && chance(0.35));
      gate = Math.min(gate, chance(sp.choppyBias) ? 0.58 : gate);
      slide = slide && chance(0.5);
    } else if (cat === 'house' && active) {
      accent = accent || (idx % 2 === 1 && chance(0.28));
      if (idx % 2 === 1 && chance(sp.offbeatBias)) gate = Math.max(gate, 0.95);
    }

    if (!active) { accent = false; slide = false; tie = false; }
    return { gate: gate, accent: accent, slide: slide, tie: tie };
  }

  function postProcessArticulation(phrase, c) {
    var cat = styleCategory(c.style);
    var i, s, diff, slides, maxSlides;
    if (cat === 'acid') {
      for (i = 0; i < phrase.length; i++) {
        s = phrase[i];
        if (!s.active || s.degree === null) continue;
        if ((i % 4 === 0 || i === 0) && chance(0.55)) s.accent = true;
        if (s.degree === 0 && chance(0.45)) s.accent = true;
        if (i < phrase.length - 1 && phrase[i + 1] && phrase[i + 1].active) {
          diff = Math.abs(nz(phrase[i + 1].degree, s.degree) - s.degree);
          if (diff >= 1 && diff <= 3 && chance(0.28)) s.slide = true;
          if (diff <= 2 && chance(0.16)) { s.tie = true; s.gate = Math.max(nz(s.gate, 0.8), 1.05); }
        }
        if (!s.slide && !s.tie && chance(0.35)) s.gate = Math.min(nz(s.gate, 0.8), 0.82);
      }
      slides = 0;
      for (i = 0; i < phrase.length; i++) if (phrase[i].slide) slides++;
      maxSlides = Math.ceil(phrase.length / 3);
      if (slides > maxSlides) {
        for (i = phrase.length - 1; i >= 0 && slides > maxSlides; i--) {
          if (phrase[i].slide) { phrase[i].slide = false; slides--; }
        }
      }
    } else if (cat === 'techno') {
      for (i = 0; i < phrase.length; i++) {
        s = phrase[i];
        if (s.active) {
          s.slide = false;
          if (i % 4 === 0 && chance(0.42)) s.accent = true;
          if (chance(0.3)) s.gate = Math.min(nz(s.gate, 0.8), 0.62);
        }
      }
    } else if (cat === 'house') {
      for (i = 0; i < phrase.length; i++) {
        s = phrase[i];
        if (s.active) {
          if (i % 2 === 1 && chance(0.36)) s.accent = true;
          if (i % 2 === 1 && chance(0.4)) s.gate = Math.max(nz(s.gate, 0.8), 0.92);
          if (chance(0.1)) s.tie = true;
        }
      }
    }
    return phrase;
  }

  function stableDegreesForScale(c) { return filterLt([0, 2, 4, 6], c.scale.length); }

  function phraseContour(phrase) {
    var degs = [], i;
    for (i = 0; i < phrase.length; i++) if (phrase[i].active && phrase[i].degree !== null) degs.push(phrase[i].degree);
    if (degs.length < 2) return 0;
    return degs[degs.length - 1] - degs[0];
  }

  function motifFromCall(call, steps) {
    var motifLen = Math.max(2, Math.min(4, Math.floor(steps / 2)));
    var out = [], i;
    for (i = 0; i < motifLen; i++) out.push(cloneStep(call[i]));
    return out;
  }

  function applyEnding(phrase, c, phase) {
    phase = phase || 'call';
    var lastIdx = phrase.length - 1;
    if (lastIdx < 0) return;
    if (!phrase[lastIdx].active) { phrase[lastIdx].active = true; phrase[lastIdx].degree = 0; }
    var end = c.endingBehaviour;
    var prevDeg = (lastIdx - 1 >= 0 && phrase[lastIdx - 1]) ? nz(phrase[lastIdx - 1].degree, 0) : 0;

    if (end.indexOf('Resolve to root') !== -1) phrase[lastIdx].degree = 0;
    else if (end.indexOf('Resolve to 5th') !== -1) phrase[lastIdx].degree = Math.min(4, c.scale.length - 1);
    else if (end.indexOf('Rise into') !== -1) phrase[lastIdx].degree = clamp(prevDeg + 1, 0, 10);
    else if (end.indexOf('Fall into') !== -1) phrase[lastIdx].degree = clamp((lastIdx - 1 >= 0 && phrase[lastIdx - 1] ? nz(phrase[lastIdx - 1].degree, 1) : 1) - 1, 0, 10);
    else if (end.indexOf('Hard stop') !== -1) { phrase[lastIdx].gate = 0.35; phrase[lastIdx].tie = false; }
    else if (end.indexOf('Fade energy') !== -1) { phrase[lastIdx].accent = false; phrase[lastIdx].gate = 0.55; }
    else if (end.indexOf('Strong cadence') !== -1) phrase[lastIdx].degree = rand(filterLt([0, 0, 0, 2, 4], c.scale.length));
    else if (end.indexOf('Weak cadence') !== -1) phrase[lastIdx].degree = rand(filterLt([1, 3, 5], c.scale.length));
    else if (end.indexOf('Ambiguous') !== -1) phrase[lastIdx].degree = rand(filterLt([1, 2, 5], c.scale.length));
    if (phase === 'response' && end.indexOf('more resolved') !== -1) phrase[lastIdx].degree = rand(filterLt([0, 0, 2, 4], c.scale.length));
    if (phase === 'response' && end.indexOf('more tense') !== -1) phrase[lastIdx].degree = rand(filterLt([1, 3, 5], c.scale.length));
  }

  // ---- construcción del call ------------------------------------------------------

  function buildCall(c) {
    var sp = styleProfile(c);
    var cat = styleCategory(c.style);
    var motif = motifTemplate(c);
    var pool = notePool(c);
    var steps = c.steps;
    var out = [];
    var densTarget = densityValue(c.densityPreset);
    var repTarget = repetitionValue(c.repetitionPreset);
    var contourMode = contourBias(c.contourPreset);
    var center = 0, i, m, deg, contour, active, prevDeg, art, block, step, spread, styleAct, dens, cloneLen, src;

    if (c.registerProfile === 'Narrow register') center = 0;
    else if (c.registerProfile === 'Medium register') center = rand([0, 1, 2]);
    else center = rand([0, 1, 2, 3]);

    var motifSteps = [];
    prevDeg = center + rand([0, 0, 1, -1]);

    for (m = 0; m < motif.len; m++) {
      active = motif.rhythm[m];
      if (chance(sp.restBias + (1 - densTarget) * 0.25)) active = active && chance(0.68);
      deg = prevDeg;

      if (m === 0 && chance(sp.rootBias)) deg = rand(filterLt([0, 0, 1, 2], c.scale.length));
      else {
        contour = nz(motif.contour[m], 0);
        if (contourMode === 100 && m > 0) deg = prevDeg + rand([-1, 0, 1]);
        else if (contourMode === 101 && m > 0 && chance(0.35)) deg = prevDeg + rand([-3, -2, 2, 3]);
        else if (contourMode === 1) deg = prevDeg + Math.max(0, contour) + rand([-1, 0, 1]);
        else if (contourMode === -1) deg = prevDeg + Math.min(0, contour) + rand([-1, 0, 1]);
        else if (contourMode === 2) deg = prevDeg + (m < Math.ceil(motif.len / 2) ? 1 : -1) + rand([-1, 0, 1]);
        else if (contourMode === -2) deg = prevDeg + (m < Math.ceil(motif.len / 2) ? -1 : 1) + rand([-1, 0, 1]);
        else if (chance(0.65)) deg = prevDeg + contour + rand([-1, 0, 0, 1]);
        else deg = rand(pool) + rand([0, 0, Math.max(0, Math.floor(center / 2))]);
      }

      if (chance(sp.leap * (contourMode === 101 ? 1.45 : 1))) deg += rand([-3, 3]);
      if (cat === 'acid' && chance(sp.syncBias)) deg += rand([-1, 0, 1]);
      if (cat === 'house' && chance(sp.offbeatBias) && m % 2 === 1) deg += rand([0, 1]);
      if (cat === 'techno' && chance(sp.rootBias * 0.4)) deg = rand(filterLt([0, 0, 2, 4], c.scale.length));
      deg = clamp(deg, 0, c.registerProfile === 'Wide register' ? 11 : (c.registerProfile === 'Medium register' ? 8 : 6));
      prevDeg = deg;
      art = articulationForStep(m, active, c, m);
      motifSteps.push({
        active: active, degree: active ? deg : null, dur: 1,
        gate: art.gate, accent: art.accent, slide: art.slide, tie: art.tie
      });
    }

    if (!(function () { for (i = 0; i < motifSteps.length; i++) if (motifSteps[i].active) return true; return false; })()) {
      motifSteps[0].active = true;
      motifSteps[0].degree = 0;
    }

    for (i = 0; i < steps; i++) {
      m = i % motif.len;
      block = Math.floor(i / motif.len);
      step = cloneStep(motifSteps[m]);
      step.gate = motifSteps[m].gate; step.accent = motifSteps[m].accent;
      step.slide = motifSteps[m].slide; step.tie = motifSteps[m].tie;

      if (block > 0) {
        if (chance(repTarget)) {
          step = cloneStep(motifSteps[m]);
          step.gate = motifSteps[m].gate; step.accent = motifSteps[m].accent;
          step.slide = motifSteps[m].slide; step.tie = motifSteps[m].tie;
        } else {
          if (step.active && step.degree !== null) {
            spread = c.repetitionPreset === 'Highly varied' ? [-3, -2, -1, 0, 1, 2, 3] : [-2, -1, 0, 1, 2];
            step.degree = clamp(step.degree + rand(spread), 0, c.registerProfile === 'Wide register' ? 11 : 8);
          }
          if (chance(sp.motifVar + (1 - repTarget) * 0.25)) step.active = !step.active ? chance(0.38) : step.active;
        }
        if (i >= Math.floor(steps * 0.75) && step.active && chance(sp.stableEnd)) {
          step.degree = clamp(step.degree + rand([-1, 0, 1]), 0, 10);
        }
      }

      styleAct = preferredStepActivation(cat, i);
      dens = Math.min(0.98, Math.max(0.05, (densTarget * 0.6) + (styleAct * 0.4)));
      if (chance(1 - dens)) step.active = step.active && chance(dens);

      if (step.active && chance(sp.rootBias * 0.4) && i % Math.max(2, motif.len) === 0) {
        step.degree = rand(filterLt([0, 0, 2, 4], c.scale.length));
      }
      if (cat === 'house' && step.active && i % 2 === 1 && chance(sp.offbeatBias)) step.gate = Math.max(nz(step.gate, 0.8), 0.95);
      if (cat === 'techno' && step.active && i % 4 === 0 && chance(0.4)) step.accent = true;

      if (!step.active) step.degree = null;
      out.push(step);
    }

    if (c.repetitionPreset === 'Very repetitive' || c.repetitionPreset === 'Repetitive') {
      cloneLen = Math.min(motif.len, Math.floor(steps / 2));
      for (i = cloneLen; i < steps; i++) {
        if (chance(c.repetitionPreset === 'Very repetitive' ? 0.9 : 0.72)) {
          src = out[i % cloneLen];
          out[i] = mergeArt(src, articulationForStep(i, src.active, c, i % motif.len));
        }
      }
    }

    applyEnding(out, c, 'call');
    postProcessArticulation(out, c);
    return out;
  }

  // ---- construcción de la response --------------------------------------------------

  function buildResponse(call, c) {
    var steps = c.steps;
    var out = [], i;
    for (i = 0; i < call.length; i++) out.push(cloneStep(call[i]));
    var rt = c.responseStrategy;
    var sp = styleProfile(c);
    var motif = motifFromCall(call, steps);
    var motifLen = motif.length;
    var activeDegrees = [];
    for (i = 0; i < call.length; i++) if (call[i].active && call[i].degree !== null) activeDegrees.push(call[i].degree);
    var avgDeg = 0;
    if (activeDegrees.length) {
      var sum = 0;
      for (i = 0; i < activeDegrees.length; i++) sum += activeDegrees[i];
      avgDeg = sum / activeDegrees.length;
    }
    var respPool = notePool(c);
    if (c.notePoolMode === 'Pool expands on response') respPool = range(Math.min(c.scale.length, 7));
    else if (c.notePoolMode === 'Pool contracts on response') respPool = stableDegreesForScale(c);
    var callContour = phraseContour(call);
    var stable = stableDegreesForScale(c);
    var copyRhythm = [];
    for (i = 0; i < call.length; i++) copyRhythm.push(!!call[i].active);

    function mapMotif(fn) {
      var j, base, d;
      for (j = 0; j < steps; j++) {
        base = motif[j % motifLen];
        out[j] = cloneStep(base);
        if (out[j].active && out[j].degree !== null) {
          d = fn(base.degree, j, base);
          if (chance(sp.responseTightness * 0.28) && respPool.length) {
            d = rand(respPool) + Math.floor(d / Math.max(1, c.scale.length)) * Math.max(1, c.scale.length);
          }
          out[j].degree = clamp(d, 0, 10);
        } else out[j].degree = null;
      }
    }

    var dir, qEnd, dominantish, start;

    if (rt === 'Same rhythm + resolve') {
      for (i = 0; i < steps; i++) {
        out[i].active = copyRhythm[i];
        out[i].degree = out[i].active ? clamp(nz(call[i].degree, 0) + rand([-1, 0, 0, 1]), 0, 10) : null;
      }
    } else if (rt === 'Same rhythm + new contour') {
      dir = callContour >= 0 ? -1 : 1;
      for (i = 0; i < steps; i++) {
        out[i].active = copyRhythm[i];
        out[i].degree = out[i].active ? clamp(nz(call[i].degree, 0) + dir * Math.floor(i / Math.max(2, steps / 4)) + rand([-1, 0, 1]), 0, 10) : null;
      }
    } else if (rt === 'Motif + simplify') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 0, 1]); });
      for (i = 0; i < steps; i++) { out[i].active = out[i].active && chance(i % 2 === 0 ? 1 : 0.35); if (!out[i].active) out[i].degree = null; }
    } else if (rt === 'Motif + extend') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });
      for (i = 1; i < steps; i++) {
        if (!out[i].active && out[i - 1].active && chance(0.42)) { out[i].active = true; out[i].degree = out[i - 1].degree; out[i].tie = true; out[i].gate = Math.max(nz(out[i].gate, 0.8), 1.0); }
      }
    } else if (rt === 'Motif + truncate') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });
      for (i = Math.floor(steps * 0.65); i < steps; i++) { if (chance(0.65)) { out[i].active = false; out[i].degree = null; } }
    } else if (rt === 'Echo' || rt === 'Delayed answer') {
      for (i = 0; i < steps; i++) {
        var src2 = call[(i - 2 + steps) % steps];
        out[i].active = src2.active;
        out[i].degree = out[i].active ? clamp(nz(src2.degree, 0) + rand([-1, 0, 1]), 0, 10) : null;
      }
      if (rt === 'Delayed answer') {
        for (i = steps - 1; i > 0; i--) out[i] = cloneStep(out[i - 1]);
        out[0] = { active: false, degree: null, gate: 0.6, accent: false, slide: false, tie: false, dur: 1 };
      }
    } else if (rt === 'Answer upward' || rt === 'Higher answer') mapMotif(function (deg) { return deg + rand([1, 2, 3]); });
    else if (rt === 'Answer downward' || rt === 'Lower answer') mapMotif(function (deg) { return deg - rand([1, 1, 2]); });
    else if (rt === 'Invert contour' || rt === 'Mirror contour loosely') mapMotif(function (deg) { return Math.round(avgDeg - (deg - avgDeg)) + rand([-1, 0, 1]); });
    else if (rt === 'Copy rhythm / change notes') {
      for (i = 0; i < steps; i++) { out[i].active = copyRhythm[i]; out[i].degree = out[i].active ? clamp(rand(respPool) + rand([0, 0, 2]), 0, 10) : null; }
    } else if (rt === 'Copy notes / change rhythm') {
      for (i = 0; i < steps; i++) { out[i].degree = call[i].degree; out[i].active = chance(call[i].active ? 0.68 : 0.22); if (!out[i].active) out[i].degree = null; }
    } else if (rt === 'Transpose motif up') mapMotif(function (deg) { return deg + rand([2, 3, 4]); });
    else if (rt === 'Transpose motif down') mapMotif(function (deg) { return deg - rand([2, 2, 3]); });
    else if (rt === 'Response resolves to root') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });
      for (i = Math.max(0, steps - 3); i < steps; i++) if (out[i].active) out[i].degree = rand(filterLt([0, 0, 2], c.scale.length));
    } else if (rt === 'Response resolves to 5th') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });
      for (i = Math.max(0, steps - 3); i < steps; i++) if (out[i].active) out[i].degree = rand(filterLt([4, 2, 0], c.scale.length));
    } else if (rt === 'Response resolves lower') {
      mapMotif(function (deg) { return deg - rand([1, 2]); });
      for (i = Math.max(0, steps - 2); i < steps; i++) if (out[i].active) out[i].degree = clamp(nz(out[i].degree, 0) - 1, 0, 10);
    } else if (rt === 'Response resolves harder') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });
      for (i = Math.max(0, steps - 4); i < steps; i++) if (out[i].active) { out[i].degree = rand(stable.length ? stable : [0]); out[i].accent = true; }
    } else if (rt === 'Repeat then break') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });
      for (i = 0; i < steps - 2; i++) if (chance(0.72)) out[i] = cloneStep(call[i]);
      if (out[steps - 2].active) out[steps - 2].degree = clamp(nz(out[steps - 2].degree, 0) + rand([2, 3, -2]), 0, 10);
      if (out[steps - 1].active) out[steps - 1].degree = rand(stable.length ? stable : [0]);
    } else if (rt === 'Tighter answer') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });
      for (i = 0; i < steps; i++) { if (out[i].active) { out[i].gate = 0.48 + (i % 2 === 0 ? 0.04 : 0); out[i].accent = chance(0.3); } }
    } else if (rt === 'Sparser answer') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });
      for (i = 0; i < steps; i++) { out[i].active = out[i].active && chance(i % 2 === 0 ? 0.85 : 0.22); if (!out[i].active) out[i].degree = null; }
    } else if (rt === 'Busier answer') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });
      for (i = 0; i < steps; i++) { if (!out[i].active && chance(0.3)) { out[i].active = true; out[i].degree = nz(out[Math.max(0, i - 1)].degree, rand(respPool)); } }
    } else if (rt === 'Accent the answer') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });
      for (i = 0; i < steps; i++) out[i].accent = out[i].active && (i % 2 === 0 || chance(0.22));
    } else if (rt === 'Slide the answer') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });
      for (i = 0; i < steps; i++) { out[i].slide = out[i].active && chance(0.34); out[i].gate = Math.max(nz(out[i].gate, 0.8), 1.0); }
    } else if (rt === 'Staccato answer') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });
      for (i = 0; i < steps; i++) { out[i].gate = 0.42; out[i].tie = false; }
    } else if (rt === 'Legato answer') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });
      for (i = 0; i < steps; i++) { out[i].gate = 1.08; out[i].tie = out[i].active && chance(0.18); }
    } else if (rt === 'Half-phrase answer') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });
      for (i = 0; i < Math.floor(steps / 2); i++) { out[i].active = false; out[i].degree = null; }
    } else if (rt === 'Fragment reply' || rt === 'Tail answer') {
      start = rt === 'Tail answer' ? Math.floor(steps / 2) : Math.floor(steps / 3);
      for (i = 0; i < steps; i++) {
        var src3 = call[(start + i) % steps];
        out[i].active = src3.active && chance(0.88);
        out[i].degree = out[i].active ? clamp(nz(src3.degree, 0) + rand([-1, 0, 1]), 0, 10) : null;
      }
    } else if (rt === 'Opposite register') mapMotif(function (deg) { return deg + (c.registerProfile === 'Wide register' ? -3 : 3); });
    else if (rt === 'Same motif darker') mapMotif(function (deg) { return deg - 1; });
    else if (rt === 'Same motif brighter') mapMotif(function (deg) { return deg + 1; });
    else if (rt === 'Question then closure') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });
      qEnd = filterLt([1, 3, 5], c.scale.length);
      if (out[steps - 2] && out[steps - 2].active) out[steps - 2].degree = rand(qEnd.length ? qEnd : [1]);
      if (out[steps - 1] && out[steps - 1].active) out[steps - 1].degree = rand(stable.length ? stable : [0]);
    } else if (rt === 'Hook then fill') {
      for (i = 0; i < steps; i++) {
        if (i < Math.floor(steps / 2)) out[i] = cloneStep(call[i]);
        else {
          var srcM = motif[i % motifLen];
          out[i] = cloneStep(srcM);
          if (out[i].active && out[i].degree !== null) out[i].degree = clamp(srcM.degree + rand([-2, -1, 1, 2]), 0, 10);
        }
      }
    } else if (rt === 'Call dominant / response tonic') {
      mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });
      dominantish = filterLt([4, 1, 5], c.scale.length);
      for (i = 0; i < steps; i++) {
        if (i < Math.floor(steps / 2) && out[i].active) out[i].degree = rand(dominantish.length ? dominantish : [1]);
        if (i >= Math.floor(steps / 2) && out[i].active && chance(0.55)) out[i].degree = rand(stable.length ? stable : [0]);
      }
    } else mapMotif(function (deg) { return deg + rand([-1, 0, 1]); });

    for (i = 0; i < steps; i++) {
      if (out[i].active && call[i] && call[i].active && chance(sp.responseTightness)) {
        out[i].degree = clamp(Math.round((out[i].degree + call[i].degree) / 2), 0, 10);
      }
      var a2 = articulationForStep(i, out[i].active, c, i % motifLen);
      out[i].gate = nz(out[i].gate, a2.gate);
      out[i].accent = a2.accent; out[i].slide = a2.slide; out[i].tie = a2.tie;
      if (!out[i].active) out[i].degree = null;
    }
    applyEnding(out, c, 'response');
    postProcessArticulation(out, c);
    return out;
  }

  // ---- mutación --------------------------------------------------------------------

  function mutatePhrase(phrase, c, target) {
    target = target || 'Whole phrase';
    if (target === 'Call + response linked') target = 'Whole phrase';
    var out = [], i;
    for (i = 0; i < phrase.length; i++) out.push(cloneStep(phrase[i]));
    var amtMap = { 'Tiny': 1, 'Small': 2, 'Medium': 3, 'Strong': 5, 'Brutal': Math.max(4, Math.floor(out.length * 0.7)) };
    var amt = amtMap.hasOwnProperty(c.mutationAmount) ? amtMap[c.mutationAmount] : 3;
    var idxs = pickN(range(out.length), amt);
    var j, idx, a, src;
    for (j = 0; j < idxs.length; j++) {
      idx = idxs[j];
      if (target === 'Rhythm only' || target === 'Whole phrase' || target === 'Call only' || target === 'Response only') {
        if (chance(0.7)) out[idx].active = !out[idx].active;
      }
      if ((target === 'Pitch only' || target === 'Whole phrase' || target === 'Call only' || target === 'Response only') && out[idx].active) {
        out[idx].degree = clamp(nz(out[idx].degree, 0) + rand([-2, -1, 1, 2]), 0, 10);
      }
      if (target === 'Articulation only' || target === 'Whole phrase') {
        a = articulationForStep(idx, out[idx].active, c, idx % 4);
        out[idx].gate = a.gate; out[idx].accent = a.accent; out[idx].slide = a.slide; out[idx].tie = a.tie;
      }
      if (target === 'Ending only' && idx === out.length - 1) applyEnding(out, c, 'call');
      if (target === 'Motif only') {
        src = idx % Math.max(2, Math.floor(out.length / 4));
        out[idx] = cloneStep(out[src]);
      }
      if (!out[idx].active) out[idx].degree = null;
    }
    return out;
  }

  // ---- config por defecto (equivalente a DEFAULTS del original, recortado a v1) ----

  function defaultConfig() {
    return {
      style: 'Classic Acid', responseStrategy: 'Same rhythm + resolve', motifType: 'Acid nibble',
      endingBehaviour: 'Response more resolved than call', key: 'A', scaleName: 'Minor Pentatonic',
      scale: SCALE_INTERVALS['Minor Pentatonic'], rootOctave: 'C3', steps: 8,
      registerProfile: 'Medium register', densityPreset: 'Medium', contourPreset: 'Stepwise',
      repetitionPreset: 'Repetitive', mutationAmount: 'Medium', mutationTarget: 'Call + response linked',
      notePoolMode: 'Pool with spice notes', articulationProfile: 'Acidic', gateFeel: 'Mixed',
      connectionFeel: 'Legato', slideProfile: 'Occasional', accentProfile: 'Motif accents',
      noteLengthPct: 100
    };
  }

  return {
    NOTE_NAMES: NOTE_NAMES,
    SCALE_INTERVALS: SCALE_INTERVALS,
    DATA: DATA,
    setSeed: setSeed,
    clamp: clamp,
    degreeToMidi: degreeToMidi,
    rootMidi: rootMidi,
    styleCategory: styleCategory,
    styleProfile: styleProfile,
    notePool: notePool,
    motifTemplate: motifTemplate,
    buildCall: buildCall,
    buildResponse: buildResponse,
    mutatePhrase: mutatePhrase,
    defaultConfig: defaultConfig
  };
})();

if (typeof module !== 'undefined' && module.exports) module.exports = CR;
