# Bibliografía de la base de conocimiento

Las fuentes de las que sale la teoría que el MCP aplica. Están aquí para que cada
afirmación tenga un origen rastreable y para que, cuando una recomendación se
discuta, se sepa contra qué contrastarla.

## Regla de uso — importante

**Aquí no se copia texto de ningún libro.** Lo que se codifica en los JSON de
`knowledge/` son *convenciones estructurales* —cuántos compases suele durar un
breakdown, en qué orden entran los elementos, dónde cae el primer estribillo—, que
son hechos del oficio y no texto protegido. Los libros se citan como fuente y
orientación; su redacción, sus ejemplos y sus tablas no se reproducen.

Cuando una convención salga de un libro concreto, se anota el campo `fuente` en el
JSON correspondiente con la clave de abajo. Cuando salga de medir material real
—como `kick_bass_melodic_techno.json`, leído de la rejilla de un anuncio— se anota
el método de medición. **Nunca se mezclan las dos cosas en un mismo campo sin
distinguirlas**, porque "lo midió alguien" y "lo escribió un libro" no se verifican
igual.

---

## Estructura de canción y método de composición

### `seabrook-2015`
**John Seabrook — *The Song Machine: Inside the Hit Factory*** (W. W. Norton, 2015).

El que Brian recordaba. Traza el pop contemporáneo hasta el Estocolmo de principios
de los noventa: Denniz Pop, Cheiron Studios y Max Martin. Describe el modelo
*track-and-hook* —se construye la pista y el gancho primero, la letra después— que
sustituyó al de melodía-y-letra, y la "melodic math" de Denniz Pop perfeccionada por
Max Martin: ajustar sílabas a notas para que la melodía funcione con independencia
de lo que diga la letra.

Convenciones que aporta y que sí podemos codificar: el estribillo entra dentro de
los primeros ~50 segundos; una canción no pasa de 3 o 4 partes distintas; las frases
se construyen en pares simétricos, una como imagen reflejada de la anterior en
número de sílabas.

**Límite:** es pop de radio, no electrónica de club. Sus proporciones no se trasladan
a un techno de 7 minutos. Sirve para la lógica de gancho y economía de partes, no
para los compases.

### `snoman-dance-music-manual`
**Rick Snoman — *Dance Music Manual*** (Focal Press / Routledge; 4.ª edición, ~551 pp.).

La referencia más completa de producción de música de baile: diseño sonoro, mezcla,
masterización y **arreglo**, con tratamiento por subgénero. Es la fuente natural para
las duraciones de sección y el orden de entrada de elementos que le faltan a
`ESTRUCTURA_POR_FAMILIA`.

### `felton-secrets-of-dance-music-production`
**David Felton — *The Secrets of Dance Music Production*** (Attack Press, ~312 pp.).

Centrado en el club. Incluye *beat grids* —representaciones visuales de patrones de
batería por subgénero— y recorridos de diseño sonoro de bajos y sintetizadores. Su
formato de rejilla es el más cercano a cómo guardamos nosotros los patrones.

---

## Armonía y mezcla armónica

### `camelot-wheel`
**Rueda Camelot**, el sistema de notación de tonalidades usado para mezcla armónica
(popularizado por Mixed In Key). No es un libro sino una convención; está
implementada y **verificada contra sus 24 casillas publicadas** en
`tests/test_harmony_tools.py`.

### `krumhansl-kessler-1982`
**Carol Krumhansl y Edward Kessler**, perfiles de tonalidad (*Psychological Review*,
1982). El método estándar para detectar la tonalidad de un fragmento correlacionando
el histograma de clases de altura contra perfiles de referencia. **Todavía no
implementado** — es el camino si se añade detección de tonalidad desde un clip.

---

## Pendiente de evaluar

Candidatos que aún no se han revisado ni incorporado:

- **Mike Senior — *Mixing Secrets for the Small Studio***: mezcla, no composición;
  relevante si el MCP llega a hacer recomendaciones de mezcla.
- **Dennis DeSantis — *Making Music: 74 Creative Strategies for Electronic
  Producers*** (Ableton): estrategias para desbloquear y terminar temas. Publicado por
  Ableton, así que su vocabulario encaja con el nuestro.

La tarea semanal `escaneo-semanal-ecosistema-ableton` revisa repos, no bibliografía.
Si una fuente nueva vale la pena, se añade aquí a mano y se anota en el JSON que la use.
