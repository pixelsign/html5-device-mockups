import test from 'node:test';
import assert from 'node:assert/strict';
import {readFamilies} from '../scripts/catalog.mjs';
import {fileURLToPath} from 'node:url';

test('each new illustration has its own artwork licence, separate from its sources', () => {
  for (const family of ['families','large','tvs']) {
    for (const d of readFamilies(fileURLToPath(new URL(`../catalog/${family}/`,import.meta.url)))) {
      const note=d.provenance?.artwork ?? '';
      for (const text of [/original.*illustration/i,/\bMIT\b/,/LICENSE\.txt/]) assert.match(note,text,d.id);
      assert.ok(d.provenance.sources.length,d.id);
    }
  }
});
