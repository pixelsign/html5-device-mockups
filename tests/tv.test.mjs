import {test} from 'node:test';
import assert from 'node:assert/strict';
import {compile} from '../scripts/catalog.mjs';
test('TVs expose only a native landscape layout without a laptop or portrait alias',()=>{
 const r={id:'DemoTV',group:'TVs',brand:'Demo',label:'Demo TV',type:'tv',width:1200,height:740,screen:{x:8,y:8,width:1184,height:666},finishes:{black:'#242424'},provenance:{sources:[]}};
 const {picker:[d],sass}=compile([r]);assert.equal(d.type,'tv');assert.deepEqual(d.orientations,['landscape']);assert.equal(d.synthLandscape,false);assert.match(sass,/1200, 740, 8, 8, 66, 8/);
});
