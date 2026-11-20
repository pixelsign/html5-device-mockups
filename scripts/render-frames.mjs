// Original front elevations. Regenerate from any directory with Node; no npm dependencies.
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';

const root = new URL('../', import.meta.url);
const records = JSON.parse(readFileSync(new URL('catalog/modern.json', root), 'utf8'));
const n = value => Number(value.toFixed(3));

// A closed subpath works both as a solid and as a hole under the even-odd rule.
function roundRect(x, y, w, h, r) {
  if (r === 0) return `M${n(x)} ${n(y)}h${w}v${h}h${-w}Z`;
  const turn = `a${r} ${r} 0 0 1`;
  return `M${n(x+r)} ${n(y)}H${n(x+w-r)}${turn} ${r} ${r}V${n(y+h-r)}${turn} ${-r} ${r}H${n(x+r)}${turn} ${-r} ${-r}V${n(y+r)}${turn} ${r} ${-r}Z`;
}

function apertures({ screen: s, geometry: g }, x, y) {
  const display = roundRect(x, y, s.width, s.height, g.screenRadius);
  const c = g.camera;
  if (c.kind === 'none') return { display, sensor: '' };
  const center = x + (c.centerX ?? s.width/2);
  const left = center-c.width/2, top = y+c.top, r = c.height/2;
  // Flat top attaches to the bezel; only the two lower corners turn.
  const sensor = c.kind === 'notch'
    ? `M${n(left)} ${n(top)}h${c.width}v${r}q0 ${r} ${-r} ${r}h${n(2*r-c.width)}q${-r} 0 ${-r} ${-r}Z`
    : roundRect(left, top, c.width, c.height, r);
  return { display, sensor, center };
}

function svg(w, h, title, description, content) {
  const escape = s => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;');
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
  <title>${escape(title)}</title>
  <desc>${escape(description)}</desc>
${content}
</svg>\n`;
}

function screenMask(record, landscape) {
  const { width, height } = record.screen;
  const { display, sensor } = apertures(record, 0, 0);
  const transform = landscape ? ` transform="translate(0 ${width}) rotate(-90)"` : '';
  return svg(landscape ? height : width, landscape ? width : height,
    `${record.label} ${landscape ? 'landscape' : 'portrait'} screen mask`,
    'White is visible content; corners and camera are transparent.',
    `  <path${transform} fill="white" fill-rule="evenodd" d="${display} ${sensor}"/>`);
}

function portrait(record, color) {
  const { label, width: w, height: h, geometry: g, screen: s } = record;
  const { display, sensor, center } = apertures(record, s.x, s.y);
  const contour = inset => roundRect(inset, inset-3, w-2*inset, h-2*(inset-3), g.bodyRadius-inset);
  const shell = `${contour(4)} ${contour(13)}`;
  const details = [];
  if (g.hingeX != null) {
    // Intersect the seam with the body minus the display, even for side hinges.
    details.push(`  <clipPath id="bezel"><path clip-rule="evenodd" d="${contour(4)} ${display}"/></clipPath>`,
      `  <path clip-path="url(#bezel)" d="M${g.hingeX} 0V${h}" stroke="#393b40" stroke-width="2"/>`);
  }
  if (sensor) {
    const lensX = n(center + (g.camera.width-g.camera.height)/2);
    const lensY = n(s.y + g.camera.top + g.camera.height/2);
    // Overlap the glass at the shared notch edge: adjacent antialiased fills
    // alone can leave a translucent hairline after fractional downscaling.
    if (g.camera.kind === 'notch') details.push(`  <rect x="${n(center-g.camera.width/2)}" y="${n(s.y-4)}" width="${g.camera.width}" height="8" fill="#050608"/>`);
    details.push(`  <path fill="#050608" d="${sensor}"/>`,
      `  <circle cx="${lensX}" cy="${lensY}" r="${n(g.camera.height*.32)}" fill="url(#optic)"/>`,
      `  <circle cx="${n(lensX-2)}" cy="${n(lensY-2)}" r="1.5" fill="#9ab5d1" opacity=".5"/>`);
  }
  if (g.home) {
    const { x, y, r } = g.home;
    details.push(`  <circle cx="${x}" cy="${y}" r="${r}" fill="#08090b" stroke="${record.finishes[color]}" stroke-width="2"/>`);
  }
  const keys = g.buttons.map(({ side, y, height }) =>
    `    <rect x="${side === 'left' ? 0 : n(w-8)}" y="${y}" width="8" height="${height}" rx="3"/>`).join('\n');
  // The keys occupy the outermost edge. A thin polished rim overlaps the black glass.
  return svg(w, h, `${label} — ${color}`, `${record.provenance.artwork} Measurements: ${record.provenance.sources.join('; ')}`, `  <defs>
    <linearGradient id="polish" x2="1" y2="0.25" gradientUnits="objectBoundingBox">
      <stop stop-color="#121519" stop-opacity=".55"/><stop offset=".12" stop-color="white" stop-opacity=".43"/>
      <stop offset=".34" stop-color="white" stop-opacity="0"/><stop offset=".7" stop-color="#202027" stop-opacity=".19"/>
      <stop offset=".92" stop-color="white" stop-opacity=".45"/><stop offset="1" stop-color="#17191b" stop-opacity=".5"/>
    </linearGradient>
    <radialGradient id="optic"><stop stop-color="#263b50"/><stop offset=".5" stop-color="#121824"/><stop offset="1" stop-color="#07080a"/></radialGradient>
  </defs>
  <g fill="${record.finishes[color]}" stroke="#303237" stroke-width="1">
${keys}
  </g>
  <g fill-rule="evenodd">
    <path fill="#101114" d="${contour(9)} ${display}"/>
    <path fill="${record.finishes[color]}" d="${shell}"/>
    <path fill="url(#polish)" d="${shell}"/>
  </g>
${details.join('\n')}`);
}

for (const r of records) {
  if (!/^[a-zA-Z0-9]+$/.test(r.id) || !r.colors.every(c => /^[a-z][a-z0-9-]*$/.test(c) && c !== 'mask')) {
    throw new Error('Invalid output name in modern catalog');
  }
  const dir = new URL(`device-mockups/${r.id}/`, root);
  mkdirSync(dir, { recursive: true });
  const write = (name, content) => writeFileSync(new URL(name, dir), content);
  for (const c of r.colors) write(`portrait_${c}.svg`, portrait(r, c));
  write('portrait_mask.svg', screenMask(r, false));
  write('landscape_mask.svg', screenMask(r, true));
}
