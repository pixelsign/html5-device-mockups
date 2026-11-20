// Run with node scripts/render-large.mjs. Importing never loads or builds the catalog.
import { mkdirSync, readFileSync, readdirSync, realpathSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const defaultRoot = fileURLToPath(new URL('../', import.meta.url));
const n = v => Number(v.toFixed(3));
const native = r => r.type === 'tablet' ? 'portrait' : 'landscape';
const escape = s => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
function svg(width, height, title, content) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">\n<title>${escape(title)}</title>\n${content}\n</svg>\n`;
}
function rect({ x, y, width, height }, radius, fill) {
  return `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="${radius}" fill="${fill}"/>`;
}
const bounds = r => ({ x: 0, y: 0, width: r.width, height: r.height });
// The camera housing may straddle ANY edge of the display. Paint the notch
// last rather than XORing paths (which would expose glass outside the screen).
// The frame's opening is a hair smaller than the screen box. Browsers round the two
// to pixels independently, and an exact fit leaves a hairline seam of page background.
export const bleed = s => n(Math.max(1.5, Math.min(s.width, s.height) * .003));
// screenCorners "top": rounded top, square bottom (Apple: "rounded corners at the top").
function display({ x, y, width: w, height: h }, radius, corners, fill, inset = 0) {
  x += inset; y += inset; w -= 2*inset; h -= 2*inset;
  const r = Math.max(0, radius-inset), turn = `A${n(r)} ${n(r)} 0 0 1`;
  if (corners !== 'top' || !r) return rect({ x: n(x), y: n(y), width: n(w), height: n(h) }, n(r), fill);
  return `<path d="M${n(x)} ${n(y+h)}V${n(y+r)}${turn} ${n(x+r)} ${n(y)}H${n(x+w-r)}${turn} ${n(x+w)} ${n(y+r)}V${n(y+h)}Z" fill="${fill}"/>`;
}
function stencil(r, frame) {
  const box = bounds(r), g = r.geometry, notch = g.notch;
  return `<mask id="aperture" maskUnits="userSpaceOnUse" x="0" y="0" width="${box.width}" height="${box.height}">\n` +
    (frame ? rect(box, 0, 'white') : '') +
    display(r.screen, g.screenRadius, g.screenCorners, frame ? 'black' : 'white', frame ? bleed(r.screen) : 0) +
    (notch ? rect(notch, notch.r, frame ? 'white' : 'black') : '') + '\n</mask>';
}
export function renderMask(r, orientation = native(r)) {
  const s = r.screen, rotated = orientation !== native(r);
  const rotation = rotated ? `translate(0 ${s.width}) rotate(-90) ` : '';
  return svg(rotated ? s.height : s.width, rotated ? s.width : s.height, `${r.label} ${orientation} screen mask`,
    `<defs>${stencil(r, false)}</defs>\n<g transform="${rotation}translate(${-s.x} ${-s.y})"><g mask="url(#aperture)">${rect(s, 0, 'white')}</g></g>`);
}
const materials = `<linearGradient id="brushed" x2="100%" y2="24%">
  <stop stop-color="#151a26" stop-opacity=".38"/><stop offset=".13" stop-color="white" stop-opacity=".45"/>
  <stop offset=".35" stop-color="white" stop-opacity="0"/><stop offset=".82" stop-color="#171d28" stop-opacity=".17"/>
  <stop offset=".96" stop-color="white" stop-opacity=".38"/><stop offset="1" stop-color="#171d28" stop-opacity=".4"/>
</linearGradient>
<radialGradient id="lens" cx="38%" cy="35%" r="65%">
  <stop stop-color="#7190a2"/><stop offset=".27" stop-color="#294050"/>
  <stop offset=".65" stop-color="#101724"/><stop offset="1" stop-color="#040509"/>
</radialGradient>`;
function circle({ x, y, r }, fill) { return `<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}"/>`; }
function front(r, box, color, sheen = 'url(#brushed)', rim = .009) {
  const g = r.geometry, edge = Math.min(box.width, box.height) * rim;
  const inner = { x: box.x+edge, y: box.y+edge, width: box.width-2*edge, height: box.height-2*edge };
  const shell = rect(box, g.bodyRadius, 'white');
  const home = g.home ? circle(g.home, color) + circle({ ...g.home, r: g.home.r*.84 }, '#222429') : '';
  return `<defs><clipPath id="shell">${shell}</clipPath></defs>
<g clip-path="url(#shell)">
${rect(box, 0, color)}${rect(box, 0, sheen)}
${rect(inner, Math.max(0, g.bodyRadius-edge), '#111317')}
${home}${circle(g.webcam, 'url(#lens)')}
</g>`;
}
// Lit from above, so both sides of a laptop match; the diagonal tablet sheen made one edge dark.
const notebookMaterials = `<linearGradient id="lid" x2="0" y2="1">
  <stop stop-color="white" stop-opacity=".4"/><stop offset=".03" stop-color="white" stop-opacity=".08"/>
  <stop offset=".6" stop-color="white" stop-opacity="0"/><stop offset="1" stop-color="#0d1017" stop-opacity=".16"/>
</linearGradient>
<linearGradient id="deck" x2="0" y2="1">
  <stop stop-color="white" stop-opacity=".75"/><stop offset=".12" stop-color="white" stop-opacity=".22"/>
  <stop offset=".4" stop-color="white" stop-opacity="0"/><stop offset=".75" stop-color="#0d1017" stop-opacity=".14"/>
  <stop offset="1" stop-color="#0d1017" stop-opacity=".42"/>
</linearGradient>`;
function notebook(r, color) {
  const s = r.screen, g = r.geometry;
  const chin = r.height-s.y-s.height;
  const seam = g.deck?.y ?? (g.lid ? g.lid.y+g.lid.height : r.height-chin*.45);
  const inset = Math.min(s.x, r.width-s.x-s.width)*.65;
  const lid = g.lid ?? { x: inset, y: 0, width: r.width-2*inset, height: seam };
  const deck = g.deck ?? { x: 0, y: seam, width: r.width, height: r.height-seam };
  // Front elevation: the hinge is only visible in the gap between lid and base, never over the bezel.
  const end = lid.y+lid.height;
  const hinge = deck.y > end
    ? rect({ x: lid.x+g.bodyRadius, y: end, width: lid.width-2*g.bodyRadius, height: deck.y-end }, 0, '#1b1d22') : '';
  const base = deck.profile === 'taper' ? taperedDeck(deck, color) : roundedDeck(deck, color);
  return `<defs>${notebookMaterials}</defs>
${front(r, lid, color, 'url(#lid)', .005)}
${hinge}
${base}`;
}
// Apple's thumb recess is a wide, shallow, flat-bottomed scoop, not a bowl hanging off the hinge.
function scoop(deck, depth, fill, share = .08) {
  if (deck.recess === false) return '';
  const half = deck.width*(deck.recess ?? share), k = depth*1.4, cx = deck.x+deck.width/2, y = deck.y;
  return `<path d="M${n(cx-half)} ${n(y)}Q${n(cx-half+k*.15)} ${n(y+depth)} ${n(cx-half+k)} ${n(y+depth)}` +
    `H${n(cx+half-k)}Q${n(cx+half-k*.15)} ${n(y+depth)} ${n(cx+half)} ${n(y)}Z" ${fill}/>`;
}
// The MacBook Pro base: crisp top corners and a rounded underside.
function roundedDeck(deck, color) {
  const x0 = deck.x, x1 = deck.x+deck.width, y0 = deck.y, y1 = deck.y+deck.height, h = deck.height;
  const top = Math.min(h*.25, 3), under = deck.r ?? h*.42, run = under*2.5;
  const face = `M${n(x0+top)} ${n(y0)}H${n(x1-top)}Q${n(x1)} ${n(y0)} ${n(x1)} ${n(y0+top)}V${n(y1-under)}` +
    `Q${n(x1)} ${n(y1)} ${n(x1-run)} ${n(y1)}H${n(x0+run)}Q${n(x0)} ${n(y1)} ${n(x0)} ${n(y1-under)}V${n(y0+top)}Q${n(x0)} ${n(y0)} ${n(x0+top)} ${n(y0)}Z`;
  return `<path d="${face}" fill="${color}"/><path d="${face}" fill="url(#deck)"/>
${scoop(deck, h*.32, 'fill="#20232a" opacity=".2"')}`;
}
// The wedge MacBook base (deck.profile "taper"): a bright top strip over a darker underside that sweeps up
// into the corners, a polished thumb scoop and two rubber feet.
function taperedDeck(deck, color) {
  const { x, y, width: w, height: h } = deck, x1 = x+w, y1 = y+h, lip = h*.34, run = w*.09;
  const under = `M${n(x)} ${n(y)}H${n(x1)}V${n(y+lip)}Q${n(x1-run*.5)} ${n(y1)} ${n(x1-run)} ${n(y1)}` +
    `H${n(x+run)}Q${n(x+run*.5)} ${n(y1)} ${n(x)} ${n(y+lip)}Z`;
  const feet = [x+w*.094, x1-w*.094].map(cx =>
    `<ellipse cx="${n(cx)}" cy="${n(y+lip+(h-lip)*.55)}" rx="${n(w*.006)}" ry="${n(h*.06)}" fill="#000" opacity=".35"/>`).join('');
  const strip = { x, y, width: w, height: lip };
  return `<defs><linearGradient id="underside" x2="0" y2="1">
  <stop stop-color="#0d1017" stop-opacity=".3"/><stop offset="1" stop-color="#0d1017" stop-opacity=".5"/>
</linearGradient>
<linearGradient id="strip">
  <stop stop-color="#0d1017" stop-opacity=".35"/><stop offset=".07" stop-color="white" stop-opacity=".3"/>
  <stop offset=".93" stop-color="white" stop-opacity=".3"/><stop offset="1" stop-color="#0d1017" stop-opacity=".35"/>
</linearGradient></defs>
<path d="${under}" fill="${color}"/><path d="${under}" fill="url(#underside)"/>${feet}
${rect(strip, 0, color)}${rect(strip, 0, 'url(#strip)')}
${scoop(deck, h*.42, `fill="${color}"`, .095)}${scoop(deck, h*.42, 'fill="url(#strip)"', .095)}`;
}
function television(r, color) {
  const {width:w,height:h,geometry:{panelHeight:p,stand,span}}=r;
  const a=(w-span)/2, b=w-a, rise=h-p;
  const foot = stand==='pedestal'
    ? `<path d="M${w*.46} ${p-1}h${w*.08}l${span*.05} ${rise*.7}H${w*.46-span*.05}Z"/><path d="M${w*.5-span*.35} ${p+rise*.65}h${span*.7}L${b} ${h-4}v4H${a}v-4Z"/>`
    : [a,b].map((u,i)=>{const dir=i?-1:1,k=stand==='feet'?22:8;return `<path d="M${u+dir*k} ${p-2}h${dir*12}L${u+dir*11} ${h-4}h${dir*9}v4H${u}v-5Z"/>`}).join('');
  return `<g fill="${color}">${foot}</g>${rect({x:0,y:0,width:w,height:p},r.geometry.bodyRadius,color)}${rect({x:1,y:1,width:w-2,height:p-2},1,'url(#brushed)')}`;
}
export function renderFrame(r, finish) {
  const color = r.finishes[finish];
  const body = r.type === 'tv' ? television(r,color) : r.type === 'tablet' ? front(r, bounds(r), color) : notebook(r, color);
  const desc = escape(`${r.provenance.artwork ? r.provenance.artwork+' ' : ''}${r.provenance.notes} Sources: ${r.provenance.sources.join('; ')}`);
  return svg(r.width, r.height, `${r.label} — ${finish}`,
    `<desc>${desc}</desc>\n<defs>${materials}\n${stencil(r, true)}</defs>\n<g mask="url(#aperture)">${body}</g>`);
}
export function generate(root = defaultRoot, family = 'large') {
  const catalog = join(root, 'catalog', family), ids = new Set();
  for (const file of readdirSync(catalog).filter(f => f.endsWith('.json')).sort()) {
    const records = JSON.parse(readFileSync(join(catalog, file), 'utf8'));
    if (!Array.isArray(records)) throw new Error(`Expected a record array in ${file}`);
    for (const r of records) {
      if (!/^[a-z0-9][a-z0-9_-]*$/i.test(r.id) || ids.has(r.id.toLowerCase())) throw new Error(`Invalid or duplicate id: ${r.id}`);
      ids.add(r.id.toLowerCase());
      if (!['tablet', 'laptop', 'tv'].includes(r.type)) throw new Error(`Unknown device type: ${r.type}`);
      const dir = join(root, 'device-mockups', r.id), orientation = native(r);
      mkdirSync(dir, { recursive: true });
      for (const c of Object.keys(r.finishes).sort()) {
        if (!/^[a-z0-9][a-z0-9-]*$/.test(c) || c === 'mask' || !/^#[0-9a-f]{6}$/i.test(r.finishes[c])) throw new Error(`Invalid finish: ${r.id}/${c}`);
        writeFileSync(join(dir, `${orientation}_${c}.svg`), renderFrame(r, c));
      }
      writeFileSync(join(dir, `${orientation}_mask.svg`), renderMask(r));
      if (r.type === 'tablet') writeFileSync(join(dir, 'landscape_mask.svg'), renderMask(r, 'landscape'));
    }
  }
}
// On macOS even tmpdir() may contain a symlink. Compare canonical entry paths.
function isEntry() {
  if (import.meta.main !== undefined) return import.meta.main;
  try { return pathToFileURL(realpathSync(process.argv[1])).href === import.meta.url; }
  catch { return false; } // REPL, stdin or node -e
}
if (isEntry()) generate(defaultRoot, process.argv.includes('--tvs') ? 'tvs' : 'large');
