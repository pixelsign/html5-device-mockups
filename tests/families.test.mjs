import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import * as mod from '../scripts/catalog.mjs';
test('family records merge in stable order without hiding missing or duplicate models', t => {
  const dir=mkdtempSync(join(tmpdir(),'phone-families-'));
  t.after(()=>rmSync(dir,{recursive:true,force:true}));
  writeFileSync(join(dir,'z.json'),'[{"id":"z"}]');
  writeFileSync(join(dir,'a.json'),'[{"id":"a"}]');
  assert.equal(typeof mod.readFamilies,'function');
  assert.deepEqual(mod.readFamilies(dir).map(x=>x.id),['a','z']);
  writeFileSync(join(dir,'repeat.json'),'[{"id":"a"}]');
  assert.throws(()=>mod.readFamilies(dir),/duplicate/i);
});
