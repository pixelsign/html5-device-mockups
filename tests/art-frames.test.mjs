import test from 'node:test';
import assert from 'node:assert/strict';
import { copyFileSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { execFileSync, spawnSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const records = JSON.parse(readFileSync(join(root, 'catalog/modern.json')));
const specs = {
  iPhone17: ['iPhone', 71.5, 149.6, 1206, 2622],
  galaxyS25: ['Samsung', 70.5, 146.9, 1080, 2340],
  Pixel10: ['Google', 72, 152.8, 1080, 2424],
  NothingPhone3: ['Nothing', 75.59, 160.6, 1260, 2800],
};

test('pilot proportions are preserved and all catalog entries define usable swatches', () => {
  for (const [id, [group, w, h, pw, ph]] of Object.entries(specs)) {
    const r = records.find(r => r.id === id);
    assert.ok(r, id);
    assert.equal(r.group, group);
    assert.ok(Math.abs(r.width / r.height - w / h) < 0.00001);
    assert.ok(Math.abs(r.screen.width / r.screen.height - pw / ph) < 0.00001);
  }
  for (const r of records) {
    const s = r.screen;
    assert.ok(r.label && r.brand && r.provenance.sources.every(s => s.startsWith('https://')));
    assert.ok(s.x > 0 && s.y > 0 && s.x + s.width < r.width && s.y + s.height < r.height);
    assert.ok(r.colors.length > 0);
    assert.deepEqual(Object.keys(r.finishes).sort(), [...r.colors].sort());
    for (const id of r.colors) {
      assert.match(id, /^[a-z][a-z0-9-]*$/);
      assert.match(r.finishes[id], /^#[0-9a-f]{6}$/i);
    }
  }
});

function generate(t, catalog) {
  const tmp = mkdtempSync(join(tmpdir(), 'art-frames-'));
  t.after(() => rmSync(tmp, { recursive: true, force: true }));
  for (const dir of ['catalog', 'scripts']) mkdirSync(join(tmp, dir));
  copyFileSync(join(root, 'scripts/render-frames.mjs'), join(tmp, 'scripts/render-frames.mjs'));
  writeFileSync(join(tmp, 'catalog/modern.json'), JSON.stringify(catalog));
  execFileSync(process.execPath, [join(tmp, 'scripts/render-frames.mjs')], { cwd: tmp });
  return join(tmp, 'device-mockups');
}

test('an empty output tree regenerates exactly the distributed SVGs', t => {
  const output = generate(t, records);
  assert.deepEqual(readdirSync(output).sort(), records.map(r => r.id).sort());
  for (const r of records) {
    const expected = ['landscape_mask.svg', 'portrait_mask.svg', ...r.colors.map(c => `portrait_${c}.svg`)].sort();
    assert.deepEqual(readdirSync(join(output, r.id)).sort(), expected);
    for (const name of expected) {
      const svg = readFileSync(join(output, r.id, name), 'utf8');
      assert.equal(svg, readFileSync(join(root, 'device-mockups', r.id, name), 'utf8'));
      const [w, h] = name === 'portrait_mask.svg' ? [r.screen.width, r.screen.height] :
        name === 'landscape_mask.svg' ? [r.screen.height, r.screen.width] : [r.width, r.height];
      assert.ok(svg.includes(`viewBox="0 0 ${w} ${h}"`));
    }
  }
});

const canRasterize = ['rsvg-convert', 'magick'].every(cmd => spawnSync(cmd, ['--version']).status === 0);
const raster = { skip: !canRasterize && 'requires rsvg-convert and magick' };
function pixels(path, w, h) {
  const png = execFileSync('rsvg-convert', ['-w', `${w}`, '-h', `${h}`, path]);
  const data = execFileSync('magick', ['png:-', '-depth', '8', 'rgba:-'], { input: png, maxBuffer: w*h*4+1024 });
  return {
    alpha: (x, y) => data[4*(Math.floor(y)*w + Math.floor(x))+3],
    rgb: (x, y) => data.readUIntBE(4*(Math.floor(y)*w + Math.floor(x)), 3),
  };
}

function checkRaster(dir, r) {
  const { screen: s, geometry: g } = r;
  const w = 300, h = Math.round(w*s.height/s.width), fh = Math.round(w*r.height/r.width);
  const p = pixels(join(dir, 'portrait_mask.svg'), w, h);
  const l = pixels(join(dir, 'landscape_mask.svg'), h, w);
  const f = pixels(join(dir, `portrait_${r.colors[0]}.svg`), w, fh);
  let different = 0;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    if (Math.abs(p.alpha(x,y) - l.alpha(y,w-1-x)) > 8) different++;
  }
  assert.ok(different < w*h*0.001, `${r.id} CCW alpha mismatch`);
  function screen(x, y, visible) {
    const msg = `${r.id} screen-local (${x}, ${y})`;
    assert.equal(p.alpha(x*w/s.width, y*h/s.height), visible ? 255 : 0, `mask: ${msg}`);
    assert.equal(f.alpha((s.x+x)*w/r.width, (s.y+y)*fh/r.height), visible ? 0 : 255, `frame: ${msg}`);
  }
  assert.equal(p.alpha(0,0), g.screenRadius === 0 ? 255 : 0);
  assert.equal(f.alpha(w*s.x/r.width/2, fh/2), 255);
  screen(s.width/2, s.height/2, true);
  const c = g.camera;
  if (c.kind === 'none') {
    // Probe two raster pixels inside the display, not an antialiased bezel
    // boundary (on an open foldable 3 artwork units can be < 1 pixel).
    screen(s.width/2, Math.max(3, 2*r.height/fh), true);
  } else {
    const x = c.centerX ?? s.width/2, y = c.top + c.height/2;
    screen(x, y, false);
    if (c.width > c.height) screen(x+(c.width-c.height)/2, y, false);
    screen(x, c.top+c.height+4, true);
    if (c.kind === 'notch') screen(x-c.width/2+3, 2, false);
    else screen(x, c.top/2, true);
    if (Math.abs(x-s.width/2) > c.width/2+4) screen(s.width/2, y, true);
  }
}

test('catalog masks rotate left and frames expose only usable content', raster, () => {
  for (const r of records) checkRaster(join(root, 'device-mockups', r.id), r);
});

function fixture(camera, extra = {}) {
  return {
    id: 'Fixture', label: 'Fixture', width: 300, height: 480,
    screen: { x: 40, y: 48, width: 216, height: 368 },
    colors: ['silver'], finishes: { silver: '#dddddd' }, provenance: { artwork: 'Fixture', sources: [] },
    geometry: { bodyRadius: 32, screenRadius: 18, buttons: [], camera, ...extra },
  };
}

test('expanded aggregate generates reproducible fixture frames and both masks', t => {
  const extras = [
    fixture({ kind: 'notch', top: 0, width: 80, height: 24 }),
    fixture({ kind: 'none' }, { screenRadius: 0, home: { x: 144, y: 445, r: 15 } }),
    fixture({ width: 20, height: 20, top: 12, centerX: 162 }, { hingeX: 110 }),
  ].map((r, i) => ({ ...r, id: `Fixture${i}` }));
  const aggregate = [...records, ...extras];
  const first = generate(t, aggregate), second = generate(t, aggregate);
  for (const r of extras) {
    for (const file of ['portrait_silver.svg', 'portrait_mask.svg', 'landscape_mask.svg']) {
      const svg = readFileSync(join(first, r.id, file), 'utf8');
      assert.doesNotMatch(svg, /NaN|undefined/);
      assert.equal(svg, readFileSync(join(second, r.id, file), 'utf8'));
    }
  }
});

test('rectangular SE screen is unobstructed and the chin carries a visible home button', raster, t => {
  const home = { x: 144, y: 445, r: 15 };
  const r = fixture({ kind: 'none' }, { screenRadius: 0, home });
  const dir = join(generate(t, [r]), r.id);
  checkRaster(dir, r);
  const f = pixels(join(dir, 'portrait_silver.svg'), r.width, r.height);
  for (const x of [r.screen.x, r.screen.x+r.screen.width-1]) {
    for (const y of [r.screen.y, r.screen.y+r.screen.height-1]) assert.equal(f.alpha(x,y), 0);
  }
  const chin = f.rgb(home.x-home.r-4, home.y);
  assert.equal(f.alpha(home.x, home.y), 255);
  assert.notEqual(f.rgb(home.x, home.y), chin);
  assert.notEqual(f.rgb(home.x+home.r-1, home.y), chin);
  assert.equal(f.rgb(home.x+home.r+4, home.y), chin);
});

test('hinge detail is visible on the bezel, not across the usable display', raster, t => {
  const r = fixture({ kind: 'none' }, { hingeX: 110 });
  const dir = join(generate(t, [r]), r.id);
  const f = pixels(join(dir, 'portrait_silver.svg'), r.width, r.height);
  for (const y of [30, 430]) assert.notEqual(f.rgb(110,y), f.rgb(104,y));
  for (let y = r.screen.y; y < r.screen.y+r.screen.height; y++) assert.equal(f.alpha(110,y), 0);
  const mask = pixels(join(dir, 'portrait_mask.svg'), r.screen.width, r.screen.height);
  assert.equal(mask.alpha(110-r.screen.x, r.screen.height/2), 255);
});

test('offset punch hole and lens use the screen-local camera center', raster, t => {
  const r = fixture({ kind: 'punch', width: 20, height: 20, top: 12, centerX: 162 });
  checkRaster(join(generate(t, [r]), r.id), r);
});

test('attached notch meets the bezel across its top edge', raster, t => {
  const r = fixture({ kind: 'notch', width: 80, height: 24, top: 0 });
  checkRaster(join(generate(t, [r]), r.id), r);
});
