// Run with node scripts/render-large.mjs. Importing never loads or builds the catalog.
import { mkdirSync, readFileSync, readdirSync, realpathSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const defaultRoot = fileURLToPath(new URL('../', import.meta.url));
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
function stencil(r, frame) {
  const box = bounds(r), notch = r.geometry.notch;
  return `<mask id="aperture" maskUnits="userSpaceOnUse" x="0" y="0" width="${box.width}" height="${box.height}">\n` +
    (frame ? rect(box, 0, 'white') : '') + rect(r.screen, r.geometry.screenRadius, frame ? 'black' : 'white') +
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
function front(r, box, color) {
  const g = r.geometry, edge = Math.min(box.width, box.height) * .009;
  const inner = { x: box.x+edge, y: box.y+edge, width: box.width-2*edge, height: box.height-2*edge };
  const shell = rect(box, g.bodyRadius, 'white');
  const home = g.home ? circle(g.home, color) + circle({ ...g.home, r: g.home.r*.84 }, '#222429') : '';
  return `<defs><clipPath id="shell">${shell}</clipPath></defs>
<g clip-path="url(#shell)">
${rect(box, 0, color)}${rect(box, 0, 'url(#brushed)')}
${rect(inner, Math.max(0, g.bodyRadius-edge), '#111317')}
${home}${circle(g.webcam, 'url(#lens)')}
</g>`;
}
function notebook(r, color) {
  const s = r.screen, g = r.geometry;
  const chin = r.height-s.y-s.height;
  const seam = g.deck?.y ?? (g.lid ? g.lid.y+g.lid.height : r.height-chin*.45);
  const inset = Math.min(s.x, r.width-s.x-s.width)*.65;
  const lid = g.lid ?? { x: inset, y: 0, width: r.width-2*inset, height: seam };
  const deck = g.deck ?? { x: 0, y: seam, width: r.width, height: r.height-seam };
  // The barrel bridges the two parts, including a gap between their boxes.
  const end = lid.y+lid.height, barrel = lid.height*.019;
  const hinge = { x: lid.x+lid.width*.19, width: lid.width*.62, y: end-barrel,
    height: Math.max(barrel, deck.y-end+barrel*1.5) };
  // Local unit square: sloping shoulders, a rolled lower edge and a thumb recess.
  return `${front(r, lid, color)}\n${rect(hinge, barrel*.35, '#34383e')}
<g transform="translate(${deck.x} ${deck.y}) scale(${deck.width} ${deck.height})">
  <defs><clipPath id="base"><path d="M.007 0H.993Q1 0 1 .12V.45Q.98 .92 .90 1H.10Q.02 .92 0 .45V.12Q0 0 .007 0Z"/></clipPath></defs>
  <g clip-path="url(#base)">
    <rect width="1" height="1" fill="${color}"/><rect width="1" height="1" fill="url(#brushed)"/>
    <path d="M0 .52Q.5 .64 1 .52V1H0Z" fill="#212633" opacity=".36"/>
    <path d="M.405 0H.595Q.59 .25 .575 .26H.425Q.41 .25 .405 0Z" fill="#161a22" opacity=".57"/>
  </g>
</g>`;
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
