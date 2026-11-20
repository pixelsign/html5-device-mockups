import test from 'node:test';
import assert from 'node:assert/strict';
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { execFileSync, spawnSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const raster = { skip: !['magick', 'rsvg-convert'].every(bin => spawnSync(bin, ['--version']).status === 0)
  && 'raster checks require rsvg-convert and ImageMagick' };
function pixels(text, w, h) {
  const png = execFileSync('rsvg-convert', [], { input: text });
  const bytes = execFileSync('magick', ['png:-', '-depth', '8', 'rgba:-'], { input: png });
  assert.equal(bytes.length, w * h * 4);
  return { alpha: (x, y) => bytes[(y*w+x)*4+3], rgb: (x, y) => bytes.readUIntBE((y*w+x)*4, 3) };
}

const script = new URL('../scripts/render-large.mjs', import.meta.url);
const tablet = {
  id: 'Slate', label: 'Slate <A&B>', type: 'tablet', group: 'Test', brand: 'Test',
  width: 160, height: 240, screen: { x: 12, y: 17, width: 134, height: 202 },
  finishes: { silver: '#dcdeda', navy: '#384864' },
  geometry: { bodyRadius: 16, screenRadius: 11, webcam: { x: 144, y: 87, r: 2 },
    notch: { x: 137, y: 76, width: 14, height: 22, r: 4 }, home: { x: 80, y: 229, r: 6 } },
  provenance: { sources: ['https://example.org/?a=1&b=2'], notes: 'Fixture dimensions.' },
};
const laptop = {
  ...tablet, id: 'Notebook', label: 'Notebook', type: 'laptop', width: 320, height: 200,
  screen: { x: 37, y: 13, width: 242, height: 153 }, finishes: { silver: '#dcdeda' },
  geometry: { bodyRadius: 10, screenRadius: 0, webcam: { x: 150, y: 8, r: 2 },
    lid: { x: 26, y: 2, width: 268, height: 176 }, deck: { x: 3, y: 178, width: 314, height: 20 } },
};
function fixture(t) {
  const root = mkdtempSync(join(tmpdir(), 'large art #'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(join(root, 'scripts')); mkdirSync(join(root, 'catalog/large'), { recursive: true });
  copyFileSync(script, join(root, 'scripts/render-large.mjs'));
  for (const r of [tablet, laptop]) writeFileSync(join(root, 'catalog/large', r.type + '.json'), JSON.stringify([r]));
  return root;
}
test('side notch uses artwork coordinates and rotates CCW with the rounded screen', raster, async t => {
  const { renderMask } = await import(pathToFileURL(join(fixture(t), 'scripts/render-large.mjs')));
  const { width: w, height: h } = tablet.screen;
  const p = pixels(renderMask(tablet), w, h), l = pixels(renderMask(tablet, 'landscape'), h, w);
  for (const [x, y, alpha] of [[0, 0, 0], [130, 70, 0], [133, 70, 0], [124, 70, 255], [130, 85, 255], [55, 100, 255]]) {
    assert.equal(p.alpha(x, y), alpha, `screen-local ${x},${y}`);
    assert.equal(l.alpha(y, w-1-x), alpha);
  }
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++)
    assert.ok(Math.abs(p.alpha(x,y) - l.alpha(y,w-1-x)) < 12, `rotated pixel ${x},${y}`);
});
for (const r of [tablet, laptop]) test(`${r.type} exposes exactly the usable screen and retains enclosure details`, raster, async t => {
  const { renderMask, renderFrame } = await import(pathToFileURL(join(fixture(t), 'scripts/render-large.mjs')));
  const frame = pixels(renderFrame(r, 'silver'), r.width, r.height);
  const s = r.screen, mask = pixels(renderMask(r), s.width, s.height);
  for (let y = 0; y < s.height; y++) for (let x = 0; x < s.width; x++)
    assert.ok(Math.abs(frame.alpha(x+s.x,y+s.y) + mask.alpha(x,y) - 255) <= 2, `frame vs mask at ${x},${y}`);
  const cam = r.geometry.webcam;
  assert.equal(frame.alpha(cam.x, cam.y), 255);
  assert.notEqual(frame.rgb(cam.x, cam.y), frame.rgb(cam.x, cam.y-4));
  assert.equal(frame.alpha(0, 0), 0);
  if (r.type === 'tablet') {
    const navy = pixels(renderFrame(r, 'navy'), r.width, r.height);
    assert.notEqual(frame.rgb(0, 120), navy.rgb(0, 120), 'finish on thin rim');
    assert.equal(frame.rgb(8, 120), navy.rgb(8, 120), 'glass bezel independent of finish');
    assert.notEqual(frame.rgb(80, 229), frame.rgb(92, 229), 'home button');
  } else {
    for (const [x,y] of [[0, 100], [26, 2], [319, 180], [3, 197]]) assert.equal(frame.alpha(x,y), 0, `outside shell ${x},${y}`);
    for (const [x,y] of [[30, 90], [20, 182], [150, 194]]) assert.equal(frame.alpha(x,y), 255);
    assert.notEqual(frame.rgb(150, 177), frame.rgb(45, 177), 'hinge under lid');
    assert.notEqual(frame.rgb(150, 181), frame.rgb(45, 181), 'centered opening lip');
    for (const x of [0, s.width-1]) for (const y of [0, s.height-1]) assert.equal(mask.alpha(x, y), 255);
  }
});
test('laptop without explicit lid or deck still surrounds its aperture', raster, async t => {
  const { renderFrame } = await import(pathToFileURL(join(fixture(t), 'scripts/render-large.mjs')));
  const { lid, deck, ...geometry } = laptop.geometry;
  for (const boxes of [{}, { lid }, { deck }]) {
    const r = { ...laptop, geometry: { ...geometry, ...boxes } };
    const frame = pixels(renderFrame(r, 'silver'), r.width, r.height);
    assert.equal(frame.alpha(40, 20), 0);
    assert.equal(frame.alpha(150, 8), 255);
    assert.equal(frame.alpha(150, 192), 255);
    assert.equal(frame.alpha(0, 50), 0);
  }
});
test('standalone CLI resolves its catalog relative to the module; import is inert', async t => {
  const root = fixture(t), entry = join(root, 'scripts/render-large.mjs'), output = join(root, 'device-mockups');
  const { renderFrame, renderMask } = await import(pathToFileURL(entry));
  assert.ok(!existsSync(output));
  execFileSync(process.execPath, [entry], { cwd: tmpdir() });
  assert.deepEqual(readdirSync(output).sort(), ['Notebook', 'Slate']);
  for (const [r, native] of [[tablet, 'portrait'], [laptop, 'landscape']]) {
    const files = new Map(Object.keys(r.finishes).map(c => [`${native}_${c}.svg`, renderFrame(r, c)]));
    files.set(`${native}_mask.svg`, renderMask(r, native));
    if (r.type === 'tablet') files.set('landscape_mask.svg', renderMask(r, 'landscape'));
    const dir = join(output, r.id);
    assert.deepEqual(readdirSync(dir).sort(), [...files.keys()].sort());
    for (const [name, expected] of files) assert.equal(readFileSync(join(dir, name), 'utf8'), expected);
    assert.match(files.get(`${native}_silver.svg`), new RegExp(`viewBox="0 0 ${r.width} ${r.height}"`));
  }
});
