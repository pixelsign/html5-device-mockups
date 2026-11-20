"""Bundle the large-screen catalog with a self-contained HTML example and license."""
from release_order import release_order, release_label, family as release_family
import json
import sys
import posixpath
import re
from html import escape
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

root = Path(__file__).resolve().parents[1]
tv = '--tvs' in sys.argv
title = 'TVs' if tv else 'Tablets and laptops'
family = 'catalog/tvs' if tv else 'catalog/large'
css = 'dist/tvs-only.min.css' if tv else 'dist/large-only.min.css'
zipname = 'dist/tvs.zip' if tv else 'dist/tablets-laptops.zip'
doc = 'catalog/TVS.md' if tv else 'catalog/TABLETS-LAPTOPS.md'
records = [d for f in sorted((root/family).glob('*.json')) for d in json.loads(f.read_text())]
files = {css, 'LICENSE.txt'}
sections = []
coverage = ['# '+title, '', 'Landscape tabletop TV frames. The display opening is 16:9; stand details and colours are illustrative.' if tv else 'Original front views. Display ratios and references are in `catalog/large/*.json`; bezel details, finishes and laptop deck projections are illustrative. Tablets rotate. Laptops are open, front-facing landscape views.', '', '| Device | ID | Finishes | Manufacturer references |', '|---|---|---|---|']
for d in sorted(records, key=release_order):
    if not sections or group != release_family(d):
        group=release_family(d)
        sections.append(f'<h2 style="grid-column:1/-1">{escape(group)}</h2>')
    tablet = d['type']=='tablet' 
    native = 'portrait' if tablet else 'landscape'
    folder = f'device-mockups/{d["id"]}/'
    colors = list(d['finishes'])
    files.update(folder+native+'_'+c+'.svg' for c in colors)
    files.update(folder+o+'_mask.svg' for o in (('portrait','landscape') if tablet else ('landscape',)))
    content = "<button onclick=\"this.textContent='It works!'\">Try the screen</button>"
    if 'previewOS' in d:
        os = d['previewOS']
        stem = 'screens/'+os.replace(' ','-')
        files.update(stem+'-'+mode+'.svg' for mode in ('app','lock'))
        content = (f'<button class="os-preview" aria-label="Toggle {escape(os)} preview" '
                   f'onclick="const i=this.firstElementChild;i.src=i.src.endsWith(\'-app.svg\')?\'{stem}-lock.svg\':\'{stem}-app.svg\'">'
                   f'<img src="{stem}-app.svg" alt="{escape(os)} preview"></button>')
    sections.append(f'<section><h2>{escape(d["label"].split(" · ")[0])} · {release_label(d)}</h2><div class="device-wrapper"><div class="device" data-device="{d["id"]}" data-orientation="{native}" data-color="{colors[0]}"><div class="screen">{content}</div></div></div></section>')
    sources = ' · '.join(f'[source {i}]({s})' for i,s in enumerate(d['provenance']['sources'],1))
    coverage.append(f'| {d["label"]} | `{d["id"]}` | {", ".join(colors)} | {sources} |')
(root/doc).write_text('\n'.join(coverage)+'\n')
files.add(doc)
files.update(f.relative_to(root).as_posix() for f in (root/family).glob('*.json'))
entries = {f:(root/f).read_bytes() for f in files}
for ref in re.findall(r'url\(([^)]+)\)',entries[css].decode()):
    if posixpath.normpath(posixpath.join('dist',ref.strip('\"\''))) not in entries: raise ValueError('Missing CSS asset: '+ref)
entries['example.html'] = ('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Tablets and laptops</title><link rel="stylesheet" href="dist/large-only.min.css"><style>body{margin:2rem;font:16px system-ui}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:2rem}.device-wrapper{max-width:450px}.screen{display:grid;place-items:center;background:#daf4fb}.os-preview{position:absolute;inset:0;padding:0;border:0;cursor:pointer}.os-preview img{display:block;width:100%;height:100%}h2{font-size:1rem}</style><h1>Tablets and laptops</h1><main>'''+''.join(sections)+'</main></html>').replace('Tablets and laptops',title).replace('dist/large-only.min.css',css).encode()
with ZipFile(root/zipname,'w') as archive:
    for path,data in sorted(entries.items()): archive.writestr(ZipInfo(path),data,compress_type=ZIP_DEFLATED)
print(f'{zipname}: {len(records)} entries, {len(entries)} files')
