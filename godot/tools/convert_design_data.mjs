// Converts the TypeScript design data (beryl-design/species.ts) into JSON the Godot game reads.
//
//   node godot/tools/convert_design_data.mjs <path to beryl-design>
//
// Writes godot/data/species.json. Moves live in godot/data/moves.json and are edited by hand.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const designDir = process.argv[2] ?? '/mnt/project-files/beryl-design';
const outDir = path.join(path.dirname(new URL(import.meta.url).pathname), '..', 'data');

/** Pulls `const name ... = <literal>;` out of a TS file and evaluates the literal as plain JS. */
function literal(src, name, open, close) {
  const start = src.indexOf(open, src.indexOf("=", src.indexOf(`const ${name}`)));
  let depth = 0;
  for (let i = start; i < src.length; i++) {
    if (src[i] === open) depth++;
    else if (src[i] === close && --depth === 0) {
      return vm.runInNewContext(`(${src.slice(start, i + 1)})`);
    }
  }
  throw new Error(`could not find ${name}`);
}

const src = fs.readFileSync(path.join(designDir, 'species.ts'), 'utf8');
const list = literal(src, 'list', '[', ']');
const dex = literal(src, 'DEX_ENTRIES', '{', '}');

const out = {};
for (const s of list) {
  out[s.id] = {
    dex: s.dex,
    name: s.name,
    types: s.types,
    base: s.base,
    exp_yield: s.expYield,
    catch_rate: s.catchRate ?? 190,
    learnset: s.learnset,
    sprite: s.sprite ? s.sprite : null,
    evolves_to: s.evolvesTo ?? null,
    category: dex[s.id]?.kind ?? '',
    dex_text: dex[s.id]?.text ?? '',
  };
}
fs.writeFileSync(path.join(outDir, 'species.json'), JSON.stringify(out, null, 1));
console.log(`species.json: ${Object.keys(out).length} species`);
