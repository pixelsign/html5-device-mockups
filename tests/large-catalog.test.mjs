import {test} from 'node:test';
import assert from 'node:assert/strict';
import {compile} from '../scripts/catalog.mjs';
const sample={id:'Sample',group:'Demo',brand:'Example',label:'Example',finishes:{silver:'#dddddd'},width:800,height:500,screen:{x:40,y:20,width:720,height:420},provenance:{sources:['https://example.org']}};
test('laptop has only a native landscape frame, with unswapped measured insets',()=>{
  const {picker,sass}=compile([{...sample,type:'laptop'}]);
  assert.equal(picker[0].type,'laptop');assert.deepEqual(picker[0].orientations,['landscape']);assert.equal(picker[0].synthLandscape,false);assert.match(sass,/landscape, 'silver', true, 800, 500, 20, 40, 60, 40/);assert.doesNotMatch(sass,/portrait,/);
});
test('tablets are classified separately and generate a counterclockwise landscape row',()=>{
  const {picker,sass}=compile([{...sample,type:'tablet'}]);assert.equal(picker[0].type,'tablet');assert.deepEqual(picker[0].orientations,['portrait','landscape']);assert.match(sass,/landscape, 'silver', true, 500, 800, 40, 60, 40, 20/);
});
