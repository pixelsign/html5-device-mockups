"""Build a relocatable, deterministic ZIP of the modern catalog plus the existing X-era frames."""
from release_order import release_order, release_label, family as release_family
import json
import posixpath
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

root = Path(__file__).resolve().parents[1]
records = json.loads((root / 'catalog/modern.json').read_text())
legacy = [('iPhoneX', 'iPhone X', 'black'), ('iPhoneXS', 'iPhone XS', 'spacegrey'), ('iPhoneXSMax', 'iPhone XS Max', 'spacegrey')]
files = ['catalog/COVERAGE.md', 'CREDITS.txt', 'LICENSE.txt', 'catalog/modern.json', 'dist/modern-only.min.css']
files += [str(p.relative_to(root)) for p in (root / 'catalog').glob('*NOTICE*')]
for d in records:
    base = 'device-mockups/' + d['id'] + '/'
    files += [base + 'portrait_' + c + '.svg' for c in d['colors']]
    files += [base + o + '_mask.svg' for o in ('portrait', 'landscape')]
for id_, label, finish in legacy:
    files += [str(p.relative_to(root)) for p in (root / 'device-mockups' / id_).glob('*.png')]
    records.append({'id':id_, 'label':label, 'brand':'Apple', 'colors':[finish]})
records.sort(key=release_order)
example = '''<!doctype html><html lang="en"><meta charset="utf-8"><title>Modern phone frames</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="dist/modern-only.min.css">
<style>body{font:16px system-ui;margin:2em;display:flex;gap:2em;flex-wrap:wrap}section{width:min(240px,100%)}.screen{background:#c6e9ff;display:grid;place-items:center}</style>
''' + '\n'.join((f'<h2 style="flex-basis:100%">{release_family(d)}</h2>' if i==0 or release_family(records[i-1])!=release_family(d) else '') + f'<section><h2>{d["label"]} · {release_label(d)}</h2><div class="device-wrapper"><div class="device" data-device="{d["id"]}" data-color="{d["colors"][0]}" data-orientation="portrait"><div class="screen"><button onclick="this.textContent=\'It works!\'">Try the screen</button></div></div></div></section>' for i,d in enumerate(records)) + '</html>'
entries = {p: (root / p).read_bytes() for p in files}
entries['example.html'] = example.encode()
# Fail the build instead of shipping a ZIP with a missing mask or frame.
css = entries['dist/modern-only.min.css'].decode()
for ref in re.findall(r'url\(([^)]+)\)', css):
    asset = posixpath.normpath(posixpath.join('dist', ref.strip(chr(34)+chr(39))))
    if asset not in entries:
        raise ValueError(f'Download is missing CSS resource: {asset}')
for d in records:
    if d['id'] not in css:
        raise ValueError(f'Download is missing CSS for {d["id"]}')
with ZipFile(root / 'dist/modern-phones.zip', 'w') as archive:
    for path, data in sorted(entries.items()):
        archive.writestr(ZipInfo(path), data, compress_type=ZIP_DEFLATED)
print(f'dist/modern-phones.zip: {len(records)} models, {len(entries)} files')
