// Validación aislada del motor portado — sin Max, sin Ableton.
// Corre con: node test_engine.js

var CR = require('./cr_engine.js');
var assert = require('assert');

function summarizePhrase(phrase) {
  return phrase.map(function (s) {
    if (!s.active || s.degree === null) return '.';
    return s.degree + (s.accent ? '!' : '') + (s.slide ? '~' : '') + (s.tie ? '_' : '');
  }).join(' ');
}

// 1. Determinismo: mismo seed -> misma salida, bit a bit
CR.setSeed(42);
var cfg1 = CR.defaultConfig();
cfg1.style = 'Dark Acid'; cfg1.key = 'A'; cfg1.steps = 16;
var call1 = CR.buildCall(cfg1);
var resp1 = CR.buildResponse(call1, cfg1);

CR.setSeed(42);
var cfg2 = CR.defaultConfig();
cfg2.style = 'Dark Acid'; cfg2.key = 'A'; cfg2.steps = 16;
var call2 = CR.buildCall(cfg2);
var resp2 = CR.buildResponse(call2, cfg2);

assert.deepStrictEqual(call1, call2, 'FALLO: mismo seed no produjo el mismo call');
assert.deepStrictEqual(resp1, resp2, 'FALLO: mismo seed no produjo la misma response');
console.log('[OK] determinismo: seed=42 reproduce exactamente el mismo call+response');

// 2. Seeds distintos -> salidas distintas (no está devolviendo una constante)
CR.setSeed(7);
var cfg3 = CR.defaultConfig();
var call3 = CR.buildCall(cfg3);
assert.notDeepStrictEqual(call1, call3, 'FALLO: seeds distintos dieron el mismo resultado');
console.log('[OK] seeds distintos producen resultados distintos');

// 3. Al menos una nota activa en cada frase (nunca un clip completamente vacío)
function hasActive(phrase) {
  return phrase.some(function (s) { return s.active; });
}
assert.ok(hasActive(call1), 'FALLO: call sin ninguna nota activa');
assert.ok(hasActive(resp1), 'FALLO: response sin ninguna nota activa');
console.log('[OK] call y response tienen al menos una nota activa');

// 4. degreeToMidi da valores MIDI válidos (0-127) para todas las notas activas
CR.setSeed(42);
var cfgMidi = CR.defaultConfig(); cfgMidi.key = 'A'; cfgMidi.rootOctave = 'C3';
var callMidi = CR.buildCall(cfgMidi);
callMidi.forEach(function (s) {
  if (s.active && s.degree !== null) {
    var midi = CR.degreeToMidi(s.degree, cfgMidi);
    assert.ok(midi >= 0 && midi <= 127, 'FALLO: MIDI fuera de rango: ' + midi);
  }
});
console.log('[OK] degreeToMidi produce valores MIDI válidos (0-127)');

// 5. Recorrer los 46 estilos y las 38 estrategias de respuesta sin excepciones
var i, j, errors = 0;
for (i = 0; i < CR.DATA.styles.length; i++) {
  for (j = 0; j < CR.DATA.responseStrategies.length; j++) {
    try {
      CR.setSeed(i * 100 + j);
      var cfg = CR.defaultConfig();
      cfg.style = CR.DATA.styles[i];
      cfg.responseStrategy = CR.DATA.responseStrategies[j];
      var call = CR.buildCall(cfg);
      var resp = CR.buildResponse(call, cfg);
      assert.strictEqual(call.length, cfg.steps);
      assert.strictEqual(resp.length, cfg.steps);
    } catch (e) {
      errors++;
      console.log('[FALLO] style=' + CR.DATA.styles[i] + ' strategy=' + CR.DATA.responseStrategies[j] + ': ' + e.message);
    }
  }
}
assert.strictEqual(errors, 0, errors + ' combinaciones estilo/estrategia fallaron');
console.log('[OK] las ' + CR.DATA.styles.length + ' x ' + CR.DATA.responseStrategies.length + ' = ' +
  (CR.DATA.styles.length * CR.DATA.responseStrategies.length) + ' combinaciones estilo/estrategia corrieron sin excepciones');

// 6. mutatePhrase no explota y respeta la longitud
CR.setSeed(1);
var cfgMut = CR.defaultConfig();
var callMut = CR.buildCall(cfgMut);
var mutated = CR.mutatePhrase(callMut, cfgMut, 'Whole phrase');
assert.strictEqual(mutated.length, callMut.length);
console.log('[OK] mutatePhrase corre y preserva la longitud de la frase');

// 7. Muestra legible de un par call/response real
CR.setSeed(42);
var cfgDemo = CR.defaultConfig();
cfgDemo.style = 'Dark Acid'; cfgDemo.key = 'A'; cfgDemo.scaleName = 'Minor Pentatonic';
cfgDemo.scale = CR.SCALE_INTERVALS['Minor Pentatonic']; cfgDemo.steps = 16;
cfgDemo.responseStrategy = 'Invert contour';
var callDemo = CR.buildCall(cfgDemo);
var respDemo = CR.buildResponse(callDemo, cfgDemo);
console.log('');
console.log('Demo — Dark Acid, A Minor Pentatonic, 16 steps, seed=42, Invert contour:');
console.log('  call:     ' + summarizePhrase(callDemo));
console.log('  response: ' + summarizePhrase(respDemo));

console.log('');
console.log('TODAS LAS VALIDACIONES PASARON');
