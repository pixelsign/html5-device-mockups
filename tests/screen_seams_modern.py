# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright==1.56.0", "pillow==11.3.0"]
# ///
"""uv run --no-project tests/screen_seams_modern.py [--device iPhone17] [--width 319.375]

Tests built CSS and external SVGs as shipped, without regenerating them. DPR 1.
Two pixel-aligned copies have identical bright green content; ONLY the host's green
channel changes (magenta -> white). Its per-pixel delta is the host contribution,
not a heuristic based on bezel color. Fail at >= 32/255 coverage, or on an opaque
near-white pixel inside the aperture. Save paired PNGs (one failure/model by
 default); PNG coordinates in JSON are relative to the left/magenta tile.
"""
import argparse
from collections import Counter
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import math
from pathlib import Path
import tempfile
import threading

from PIL import Image, ImageChops, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
GREEN = (0, 255, 64)
HTML = '''<!doctype html><link rel="stylesheet" href="/dist/device-mockups.min.css">
<style>*{box-sizing:border-box}body{margin:0;display:flex}section{flex:none;background:#f0f;padding:4px}
section+section{background:white}.device-wrapper{max-width:none}.probe{position:absolute;inset:0;background:#00ff40}</style>'''
TILE = '<section><div class="device-wrapper"><div class="device"><div class="screen"><div class="probe"></div></div></div></div></section>'
SETUP = '''async ([device,orientation,color,width,stride])=>{
 const images=new Set();for(const el of document.querySelectorAll('.device')){
   const wrapper=el.parentNode;wrapper.style.width=width+'px';wrapper.parentNode.style.width=stride+'px';
   Object.assign(el.dataset,{device,orientation,color});
   for(const url of [getComputedStyle(el,'::after').backgroundImage,getComputedStyle(el.firstChild).maskImage]){
     if(!url.startsWith('url(')) throw Error('missing CSS for '+[device,orientation,color]);
     images.add(JSON.parse(url.slice(4,-1)));
   }
 } await Promise.all([...images].map(src=>{const i=new Image();i.src=src;return i.decode()}));
 return document.querySelector('.device').getBoundingClientRect().toJSON();}'''


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass


def inventory():
    paths = [ROOT/'catalog/modern.json', *sorted((ROOT/'catalog/large').glob('*.json')),
             *sorted((ROOT/'catalog/tvs').glob('*.json'))]
    rows = [r for path in paths for r in json.loads(path.read_text())]
    assert len({r['id'] for r in rows}) == len(rows)
    assert {r.get('type','phone') for r in rows} == {'phone','tablet','laptop','tv'}
    return rows


def aperture(d, rotated, width, size):
    """Nominal display including cutouts (which should be opaque), excluding exterior chassis corners."""
    s = d['screen']; w,h = d['width'],d['height']; k = width/(h if rotated else w)
    x,y,a,b = (s[t] for t in ('x','y','width','height'))
    if rotated: x,y,a,b = y,w-x-a,b,a
    x,y = 4+x*k,4+y*k
    box = (math.ceil(x-.5),math.ceil(y-.5),math.floor(x+a*k-.5),math.floor(y+b*k-.5))
    roi = Image.new('L',size); draw = ImageDraw.Draw(roi)
    draw.rounded_rectangle(box, radius=round(d['geometry']['screenRadius']*k),fill=255)
    if d['geometry'].get('screenCorners')=='top':
        draw.rectangle((box[0],(box[1]+box[3])//2,box[2],box[3]),fill=255)
    return roi,k


def probe(left, right, roi):
    # Differencing cancels green-to-black antialiasing and opaque silver highlights.
    delta = ImageChops.multiply(roi,ImageChops.subtract(right.getchannel('G'),left.getchannel('G')))
    # Near-white on BOTH hosts is painted light, rather than exposed page background.
    r,g,b = left.split()
    bright = ImageChops.multiply(roi,ImageChops.darker(ImageChops.darker(r,g),b)).point(lambda n:255 if n>=244 else 0)
    peak = delta.getextrema()[1]; hist = delta.histogram()
    score = delta if peak>=32 else bright
    if peak<32 and not bright.getbbox(): return {'peak':peak}
    maximum = score.getextrema()[1]
    box = score.point(lambda n:255 if n==maximum else 0).getbbox()
    yy=box[1]; xx=next(x for x in range(box[0],box[2]) if score.getpixel((x,yy))==maximum)
    return dict(peak=peak, host_pixels_ge32=sum(hist[32:]), white_pixels=bright.histogram()[255],
                pixel=[xx,yy], magenta=left.getpixel((xx,yy)), white=right.getpixel((xx,yy)))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--device',action='append'); ap.add_argument('--width',type=float,action='append')
    ap.add_argument('--out',type=Path); ap.add_argument('--all-png',action='store_true')
    args=ap.parse_args(); out=args.out or Path(tempfile.mkdtemp(prefix='modern-seams-')); out.mkdir(exist_ok=True,parents=True)
    rows=inventory(); widths=args.width or [240,319.375,400.625]
    if args.device:
        rows=[r for r in rows if r['id'] in args.device]; assert {r['id'] for r in rows}==set(args.device)
    assert all(0<w<2000 for w in widths)
    server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=ROOT))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    results=[]; saved=set(); failures=Counter()
    with sync_playwright() as pw:
        browser=pw.chromium.launch(channel='chrome'); version=browser.version
        page=browser.new_page(viewport={'width':2*(math.ceil(max(widths))+8),'height':math.ceil(max(widths)*3)+16},device_scale_factor=1)
        page.route('**/__seams',lambda route:route.fulfill(content_type='text/html',body=HTML+TILE*2))
        page.goto(f'http://127.0.0.1:{server.server_port}/__seams')
        for d in rows:
            model=d['id']; kind=d.get('type','phone'); mobile=kind in ('phone','tablet')
            for orientation in (('portrait','landscape') if mobile else ('landscape',)):
                rotated=mobile and orientation=='landscape'
                for width in widths:
                    stride=math.ceil(width)+8
                    for color in d.get('colors',d.get('finishes')):
                        rect=page.evaluate(SETUP,[model,orientation,color,width,stride]); assert rect['x']==rect['y']==4 and abs(rect['width']-width)<.016 and rect['height']>0
                        height=math.ceil(rect['height'])+8
                        shot=page.screenshot(clip=dict(x=0,y=0,width=2*stride,height=height))
                        im=Image.open(io.BytesIO(shot)).convert('RGB'); assert im.size==(2*stride,height)
                        left=im.crop((0,0,stride,height)); right=im.crop((stride,0,2*stride,height))
                        roi,k=aperture(d,rotated,width,left.size); l,t,r,b=roi.getbbox(); center=((l+r)//2,(t+b)//2)
                        assert (left.getpixel((0,0)),right.getpixel((0,0)))==((255,0,255),(255,255,255))
                        assert left.getpixel(center)==right.getpixel(center)==GREEN,(model,color,orientation,center)
                        result=probe(left,right,roi)
                        if 'pixel' in result:
                            px,py=result['pixel']; a,b=(px+.5-4)/k,(py+.5-4)/k
                            result['svg_xy']=[round(p,2) for p in ((d['width']-b,a) if rotated else (a,b))]
                            native='portrait' if mobile else 'landscape'; result['art']=f'device-mockups/{model}/{native}_{color}.svg'
                            failures[kind]+=1
                            if args.all_png or model not in saved:
                                name=f'{model}-{orientation}-{color}-{width:g}.png'; (out/name).write_bytes(shot); result['png']=name; saved.add(model)
                        results.append(dict(model=model,kind=kind,color=color,orientation=orientation,width=width,**result))
        browser.close()
    server.shutdown(); server.server_close()
    report=out/'results.json'; report.write_text(json.dumps(dict(chrome=version,cases=results),indent=2))
    print(f'Chrome {version}: {len(rows)} models, {len(results)} cases; failures by type {dict(failures)}; {report}')
    return int(bool(failures))

if __name__=='__main__': raise SystemExit(main())
