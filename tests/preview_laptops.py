# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright==1.56.0"]
# ///
"""Render every laptop from the downloadable ZIP at equal widths for silhouette review."""
from pathlib import Path
from zipfile import ZipFile
from tempfile import TemporaryDirectory
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from functools import partial
from html import escape
from playwright.sync_api import sync_playwright
import argparse, json

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('output',type=Path)
parser.add_argument('--zip',type=Path,default=root/'dist/tablets-laptops.zip')
args=parser.parse_args()
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
with TemporaryDirectory() as tmp, ZipFile(args.zip) as archive, sync_playwright() as pw:
    archive.extractall(tmp)
    devices=json.loads(archive.read('catalog/large/laptops.json'))
    gallery='''<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="dist/large-only.min.css"><style>*{box-sizing:border-box}body{background:#fafafa;margin:20px;color:#232426;font:15px system-ui}main{display:grid;grid-template-columns:repeat(3,1fr);gap:24px 20px}article{display:grid;align-content:end;text-align:center}h2{font:500 14px system-ui}.device-wrapper{width:100%;max-width:none}.screen{background:linear-gradient(140deg,#89bfc4,#427c98 45%,#24374d)}</style><main>'''
    for d in devices:
        c=next((c for c in ['silver','platinum','sky'] if c in d['finishes']),next(iter(d['finishes'])))
        gallery+=f'<article><div class="device-wrapper"><div class="device" data-device="{d["id"]}" data-orientation="landscape" data-color="{c}"><div class="screen"></div></div></div><h2>{escape(d["label"])}</h2></article>'
    Path(tmp,'preview.html').write_text(gallery+'</main>')
    with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=tmp)) as server:
        Thread(target=server.serve_forever,daemon=True).start()
        browser=pw.chromium.launch(channel='chrome'); page=browser.new_page(viewport={'width':1200,'height':840},device_scale_factor=1)
        page.goto(f'http://127.0.0.1:{server.server_port}/preview.html',wait_until='networkidle');page.screenshot(path=str(args.output),full_page=True);browser.close();server.shutdown()
print(args.output)
