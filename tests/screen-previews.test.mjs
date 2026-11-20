import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {compile} from '../scripts/catalog.mjs';
const dirs=['catalog/large','catalog/tvs'];
test('picker and optional artwork agree on every laptop and TV platform',()=>{
  const expected={Apple:'macOS',Microsoft:'Windows',Dell:'Windows',Samsung:'Tizen',LG:'webOS',Sony:'Google TV',TCL:'Google TV'};
  for(const dir of dirs) for(const file of readdirSync(dir).filter(f=>f.endsWith('.json'))) {
    const records=JSON.parse(readFileSync(`${dir}/${file}`));
    for(const d of compile(records).picker.filter(d=>['laptop','tv'].includes(d.type))) {
      assert.equal(d.previewOS,expected[d.brand],d.id);
      for(const mode of ['app','lock']) assert.match(readFileSync(`screens/${d.previewOS.replaceAll(' ','-')}-${mode}.svg`,'utf8'),/Original illustration, MIT/);
    }
  }
});
