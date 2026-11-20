import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';

const compiler = new URL('../scripts/catalog.mjs', import.meta.url);
const sample = {id:'TestPhone',brand:'Example',group:'Demo',label:'Test phone',colors:['black'],provenance:{license:'MIT'},width:80,height:160,screen:{x:4,y:10,width:70,height:140}};

test('one source record supplies the picker and properly rotated responsive Sass insets', async () => {
  assert.ok(existsSync(compiler), 'missing catalog compiler');
  const {compile} = await import(compiler);
  const {picker, sass} = compile([sample]);
  assert.equal(picker[0].id,'TestPhone');
  assert.equal(picker[0].ext,'svg');
  assert.deepEqual(picker[0].orientations,['portrait','landscape']);
  assert.match(sass,/80, 160, 10, 6, 10, 4,/);
  assert.match(sass,/160, 80, 6, 10, 4, 10,/);
  assert.throws(() => compile([sample,sample]), /duplicate/i);
  assert.throws(() => compile([{...sample,screen:{...sample.screen,x:79}}]), /screen/i);
});
