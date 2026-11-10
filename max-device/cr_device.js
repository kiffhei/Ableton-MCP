// cr_device.js — glue del objeto `js` dentro del patcher C&R Generator (rebuild).
//
// Este archivo SÍ vive dentro de Max (a diferencia de cr_engine.js, que además se
// valida de forma aislada con Node — ver test_engine.js). Aquí es donde entran los
// mensajes de los objetos live.menu/live.dial/live.slider/live.button del patcher,
// y donde se llama a la Live API para escribir el resultado en un clip.
//
// Regla crítica (documentada en adammurray.link/max-for-live/js-in-live/live-api/,
// confirmada 2026-09-14): "new LiveAPI(...)" NUNCA debe llamarse en código de nivel
// superior — falla en silencio durante la inicialización del device. Por eso aquí
// no hay ningún "new LiveAPI(...)" fuera de una función disparada por un mensaje.
//
// v0 — alcance mínimo para probar el mecanismo más riesgoso (escribir a un clip)
// antes de cablear los 12 controles del plan completo (CALL_RESPONSE_REBUILD_PLAN.md).
// cfg fijo por ahora; los menús/knobs del patcher llenarán este objeto en el
// siguiente paso.

include('cr_engine.js');

// repetitionPreset/contourPreset no están en CR.DATA (son valores libres del
// motor, sin lista indexada propia) — este orden debe coincidir con
// REPETITIONS/CONTOURS en build_device.py.
var REPETITIONS = ['Very repetitive', 'Repetitive', 'Balanced', 'Varied', 'Highly varied'];
var CONTOURS = ['Flat', 'Slight rise', 'Slight fall', 'Arch', 'Inverted arch', 'Wandering', 'Stepwise', 'Leapy'];

var cfg = CR.defaultConfig();
cfg.style = 'Dark Acid';
cfg.key = 'A';
cfg.scaleName = 'Minor Pentatonic';
cfg.scale = CR.SCALE_INTERVALS['Minor Pentatonic'];
cfg.steps = 8;
cfg.responseStrategy = 'Invert contour';

var lastCall = null;
var lastResponse = null;

function seed(v) {
  CR.setSeed(v | 0);
  post('C&R: seed = ' + (v | 0) + '\n');
}

// ---- vista de pasos — actualiza el multislider 'stepview' (solo lectura,
// feedback visual tipo step-sequencer) con el patrón call+response actual.
// No es un parámetro live.*, así que no participa del mecanismo de
// automatización — se empuja directo por nombre con messnamed.
function updateStepView() {
  if (!lastCall || !lastResponse) return;
  var values = [];
  function pushVals(phrase) {
    for (var i = 0; i < phrase.length; i++) {
      var step = phrase[i];
      values.push((!step.active || step.degree === null) ? 0 : (step.accent ? 1 : 0.65));
    }
  }
  pushVals(lastCall);
  pushVals(lastResponse);
  try {
    messnamed('stepview', 'size', values.length);
    messnamed.apply(this, ['stepview', 'set'].concat(values));
  } catch (e) {
    post('C&R stepview error: ' + e + '\n');
  }
}

// ---- New Pair — genera call+response en memoria, no toca Ableton todavía -------
function newpair() {
  lastCall = CR.buildCall(cfg);
  lastResponse = CR.buildResponse(lastCall, cfg);
  post('C&R: nuevo par generado (' + cfg.style + ', ' + cfg.key + ' ' + cfg.scaleName + ', ' + cfg.steps + ' steps, strategy=' + cfg.responseStrategy + ')\n');
  updateStepView();
}

function mutate() {
  if (!lastCall) { post('C&R: nada que mutar todavía — usa New Pair primero\n'); return; }
  lastCall = CR.mutatePhrase(lastCall, cfg, 'Call only');
  lastResponse = CR.buildResponse(lastCall, cfg);
  post('C&R: mutado\n');
  updateStepView();
}

// ---- Write Clip — la parte que toca Ableton, todo dentro de esta función --------
// Escribe call+response concatenados (call primero, response después) en el clip
// slot 0 del track donde vive el device. Sigue el patrón documentado:
//   this_device canonical_parent  -> el track del propio device (no hardcodea índice)
//   clipSlot.get("has_clip") == false  -> NUNCA "!clipSlot.get(...)", es un bug
//     conocido del motor JS de Max/Live API (siempre da false negado)
//   {notes: notes} en vez de {notes} -> shorthand de objeto es ES6, no existe en ES5
function writeclip() {
  if (!lastCall || !lastResponse) { post('C&R: nada que escribir — usa New Pair primero\n'); return; }

  var totalSteps = cfg.steps * 2; // call + response concatenados
  var beatsPerStep = 0.5; // corchea a 120bpm de referencia; ajustable en v1 con Steps/Rate reales
  var clipLength = totalSteps * beatsPerStep;

  var track = new LiveAPI('this_device canonical_parent');
  post('C&R: escribiendo en track "' + track.get('name') + '"\n');

  var clipSlot = new LiveAPI('this_device canonical_parent clip_slots 0');
  if (clipSlot.get('has_clip') == false) {
    clipSlot.call('create_clip', clipLength);
  }
  var clip = new LiveAPI(clipSlot.unquotedpath + ' clip');
  clip.call('remove_notes_extended', 0, 128, 0, clip.get('length'));

  var notes = [];
  var i, step, midi, dur;

  function pushPhrase(phrase, offsetSteps) {
    for (i = 0; i < phrase.length; i++) {
      step = phrase[i];
      if (!step.active || step.degree === null) continue;
      midi = CR.degreeToMidi(step.degree, cfg);
      if (midi < 0 || midi > 127) continue;
      dur = beatsPerStep * (step.gate || 0.8) * (cfg.noteLengthPct / 100);
      notes.push({
        pitch: midi,
        start_time: (offsetSteps + i) * beatsPerStep,
        duration: Math.max(0.05, dur),
        velocity: step.accent ? 110 : 88,
        mute: 0
      });
    }
  }

  pushPhrase(lastCall, 0);
  pushPhrase(lastResponse, cfg.steps);

  clip.call('add_new_notes', { notes: notes });
  post('C&R: ' + notes.length + ' notas escritas en clip (call+response, ' + clipLength + ' beats)\n');
  updateStepView();
}

// ---- setters de configuración — reciben el ÍNDICE del live.menu seleccionado, no
// el texto (más robusto: no depende de configurar el outputmode del live.menu para
// que mande el string en vez del índice, que es su comportamiento por defecto).
function style(i) { cfg.style = CR.DATA.styles[i | 0]; post('C&R: style = ' + cfg.style + '\n'); }
function key(i) { cfg.key = CR.NOTE_NAMES[i | 0]; post('C&R: key = ' + cfg.key + '\n'); }
function scale(i) {
  cfg.scaleName = CR.DATA.scales[i | 0];
  cfg.scale = CR.SCALE_INTERVALS[cfg.scaleName] || CR.SCALE_INTERVALS['Minor Pentatonic'];
  post('C&R: scale = ' + cfg.scaleName + '\n');
}
function responsestrategy(i) { cfg.responseStrategy = CR.DATA.responseStrategies[i | 0]; post('C&R: responseStrategy = ' + cfg.responseStrategy + '\n'); }
function motiftype(i) { cfg.motifType = CR.DATA.motifTypes[i | 0]; post('C&R: motifType = ' + cfg.motifType + '\n'); }
function endingbehaviour(i) { cfg.endingBehaviour = CR.DATA.endingBehaviours[i | 0]; post('C&R: endingBehaviour = ' + cfg.endingBehaviour + '\n'); }
function repetition(i) { cfg.repetitionPreset = REPETITIONS[i | 0]; post('C&R: repetition = ' + cfg.repetitionPreset + '\n'); }
function contour(i) { cfg.contourPreset = CONTOURS[i | 0]; post('C&R: contour = ' + cfg.contourPreset + '\n'); }

// ---- setters de knob/fader/numbox — reciben el valor nativo del control -----------
function octave(v) { cfg.rootOctave = 'C' + (v | 0); }
function steps(v) { cfg.steps = Math.max(2, Math.min(32, v | 0)); }
function density(v) { cfg.densityPreset = v < 0.3 ? 'Sparse' : (v < 0.6 ? 'Medium' : 'Dense'); }
function notelength(v) { cfg.noteLengthPct = v; }
