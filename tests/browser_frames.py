# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright==1.56.0", "pillow==11.3.0"]
# ///
"""Run: uv run --no-project tests/browser_frames.py (installed Google Chrome).
Optional: QA_ROOT points at another built checkout; QA_BROWSER=chromium uses
`uv run --with playwright==1.56.0 playwright install chromium` instead of Chrome.
"""
import functools
import io
import json
import os
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import tempfile
import threading

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright, expect

PILOTS = ('iPhone17', 'galaxyS25', 'Pixel10', 'NothingPhone3')
ROOT = Path(os.getenv('QA_ROOT', Path(__file__).resolve().parents[1]))
WIDTHS = (240, 400)
GREEN = (0, 255, 64)
BACK = (255, 0, 255)
FIXTURE = '''<!doctype html><link rel="stylesheet" href="/dist/device-mockups.min.css">
<style>body { margin: 12px; background: #f0f } .device-wrapper {max-width:none}
iframe {display:block; width:100%; height:100%; border:0}</style>
<div class="device-wrapper"><div class="device"><div class="screen"><iframe title="test"
srcdoc="<style>*{margin:0}button{display:block;width:100vw;height:100vh;border:0;background:#00ff40}</style><button aria-label='target' onclick='if(event.isTrusted)this.dataset.hit=1'></button>"></iframe></div><div class="button"></div></div></div>'''


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass


def catalog():
    out = {item['id']:item for item in json.loads((ROOT/'catalog/modern.json').read_text())}
    assert all(out.get(id_, {}).get('colors') for id_ in PILOTS), 'missing pilot or finishes'
    return out


def demo(page, base, model, colors):
    page.goto(base + '/index.html')
    row = page.locator(f'label:has(input[name=device][value="{model}"])')
    assert row.count() == 1, f'demo picker missing {model}'
    row.click()
    device = page.locator('#device')
    expect(device).to_have_attribute('data-device', model)
    for selector, attr, value in [('orientation', 'data-orientation', 'landscape'),
                                  ('finish', 'data-color', colors[-1])]:
        page.locator(f'label:has(input[name={selector}][value="{value}"])').click()
        expect(device).to_have_attribute(attr, value)
    assert page.url.endswith(f'#{model}/landscape/{colors[-1]}'), page.url
    page.locator('#code-toggle').click()
    code = page.locator('#code-out').inner_text()
    for value in (f'data-device="{model}"', 'data-orientation="landscape"', f'data-color="{colors[-1]}"'):
        assert value in code, f'generated markup missing {value}'


def hole(image, model):
    """Find a dark, enclosed camera/island against green (not bezel/corners).
    Input is the screen crop, rotated to put the camera end at the top.
    Return normalized centroid and span for cross-orientation comparisons.
    """
    w, h = image.size
    band = image.crop((0, 0, w, max(1, round(h*.16))))
    mask = Image.new('L', band.size)
    mask.putdata([255 if max(rgb) < 145 else 0 for rgb in band.getdata()])
    # Strip anything connected to a crop edge (rim, corner clipping, etc.).
    bw, bh = mask.size
    for p in ([(x,y) for x in range(bw) for y in (0,bh-1)] +
              [(x,y) for y in range(bh) for x in (0,bw-1)]):
        if mask.getpixel(p): ImageDraw.floodfill(mask, p, 0)
    candidates = []
    while box := mask.getbbox():
        x = next(x for x in range(box[0],box[2]) if mask.getpixel((x,box[1])))
        ImageDraw.floodfill(mask, (x,box[1]), 128)
        component = mask.point(lambda v: 255 if v==128 else 0)
        l,t,r,b = component.getbbox()
        mask.paste(0, mask=component)
        width, height = (r-l)/w, (b-t)/w
        if .010 <= height <= .13 and (.07 if model=='iPhone17' else .010) <= width <= .43:
            aspect = (r-l)/(b-t)
            if (aspect >= 1.65 if model=='iPhone17' else .5 <= aspect <= 1.8):
                candidates.append((component.histogram()[255], ((r+l)/2/w,(t+b)/2/h,width,height)))
    return max(candidates)[1] if candidates else None


def near(a,b,tolerance,description):
    assert len(a)==len(b) and all(abs(x-y)<=tolerance for x,y in zip(a,b)), f'{description}: {a} vs {b} (tol {tolerance})'


def render(page, base, model, color, orientation, width, control, shots):
    page.goto(base+'/__qa__')
    page.locator('.device').evaluate('''(el,[device,color,orientation,width])=>{
      Object.assign(el.dataset,{device,color,orientation}); el.parentNode.style.width=width+'px';
    }''', [model,color,orientation,width])
    frame = page.locator('.device')
    d = frame.bounding_box(); s = page.locator('.screen').bounding_box()
    assert d and s and d['height']>0 and s['height']>0, 'zero frame/screen height; built selector missing?'
    w,h = d['width'],d['height']; near([w],[width],1,'wrapper width')
    ratio = h/w
    assert 1.75 < (ratio if orientation=='portrait' else 1/ratio) < 2.45, f'unexpected frame aspect: {ratio}'
    x,y = s['x']-d['x'],s['y']-d['y']; sw,sh=s['width'],s['height']
    insets = (x/w,y/h,(w-x-sw)/w,(h-y-sh)/h)  # left, top, right, bottom
    assert all(0<i<.13 for i in insets), f'screen outside phone or implausible margins: {insets}'
    shot = frame.screenshot(animations='disabled'); shots.append(shot)
    image = Image.open(io.BytesIO(shot)).convert('RGB')
    screen = image.crop((round(x),round(y),round(x+sw),round(y+sh)))
    assert screen.getpixel((screen.width//2,screen.height//2)) == GREEN, 'bright iframe center not visible'
    assert sum(n for n,c in screen.getcolors(screen.width*screen.height) if c==GREEN) > .86*sw*sh, 'screen mostly obscured'
    for u,v in ((0,0),(1,0),(0,1),(1,1)):
        assert screen.getpixel((u*(screen.width-1),v*(screen.height-1))) != GREEN, 'unclipped display corner'
    for bx,by in ((x/2,y+sh*.55),(x+sw+(w-x-sw)/2,y+sh*.55),(x+sw*.45,y/2),(x+sw*.45,y+sh+(h-y-sh)/2)):
        pixel = image.getpixel((int(bx),int(by)))
        assert pixel not in (GREEN,BACK), f'missing frame art or content bleed at bezel: {pixel}'
    page.mouse.click(s['x']+sw/2,s['y']+sh/2)
    expect(page.frame_locator('iframe').locator('button')).to_have_attribute('data-hit','1',timeout=1500)
    camera = None
    if not control:
        if orientation=='portrait': camera = hole(screen, model)
        else:
            # A landscape asset may rotate either way. Preserve which transform
            # recovered the camera so screen insets must match that direction too.
            for turn in (Image.Transpose.ROTATE_90, Image.Transpose.ROTATE_270):
                camera = hole(screen.transpose(turn),model)
                if camera:
                    l,t,r,b = insets
                    insets = (t,r,b,l) if turn==Image.Transpose.ROTATE_90 else (b,l,t,r)
                    break
        assert camera, 'no distinct dark island/punch hole at camera end over bright content'
    return (ratio if orientation=='portrait' else 1/ratio),insets,camera


def matrix(page, base, model, color, spec, shots):
    control = spec is None
    first = None
    for width in WIDTHS:
        for orient in ('portrait','landscape'):
            try:
                aspect,insets,camera = render(page,base,model,color,orient,width,control,shots)
                if spec:
                    w,h,s = spec['width'],spec['height'],spec['screen']
                    x,y,sw,sh = (s[k] for k in ('x','y','width','height'))
                    near([aspect],[h/w],.01,'catalog aspect')
                    near(insets,(x/w,y/h,(w-x-sw)/w,(h-y-sh)/h),.005,'catalog screen insets')
                    c = spec['geometry']['camera']
                    near(camera[:2],(.5,(c['top']+c['height']/2)/sh),.015,'catalog camera position')
                    # hole() returns integer bounding-box spans; each antialiased
                    # end can round by a pixel at DPR 1 (e.g. a 5px punch hole).
                    span_px=width*sw/(w if orient=='portrait' else h)
                    near(camera[2:],(c['width']/sw,c['height']/sw),max(.015,2/span_px),'catalog camera span')
                if first is None: first = aspect,insets,camera
                near([aspect],[first[0]],.02,'frame aspect changed')
                if not control or orient=='portrait': near(insets,first[1],.009,'screen insets changed')
                if camera:
                    near(camera[:2],first[2][:2],.012,'camera position changed')
                    near(camera[2:],first[2][2:],max(.012,2/span_px) if spec else .012,'camera span changed')
            except Exception as exc:
                raise AssertionError(f'{orient} {width}px: {exc}') from exc


def check_family(page, base, spec, shots):
    """Check rectangular SEs, attached notches, offset cameras and foldables."""
    model = spec['id']; s = spec['screen']; g = spec['geometry']
    w, h = spec['width'], spec['height']
    sw, sh, x, y = (s[k] for k in ('width','height','x','y'))
    for orientation in ('portrait','landscape'):
        for width in WIDTHS:
            page.goto(base+'/__qa__')
            frame = page.locator('.device')
            frame.evaluate('(e,[m,o,c,w])=>{Object.assign(e.dataset,{device:m,orientation:o,color:c});e.parentNode.style.width=w+"px"}', [model,orientation,spec['colors'][0],width])
            # Decode both external SVGs before sampling their rendered pixels.
            page.evaluate('''async () => {const d=document.querySelector('.device');
              const urls=[getComputedStyle(d,'::after').backgroundImage,getComputedStyle(d.querySelector('.screen')).maskImage];
              await Promise.all(urls.map(u=>{const i=new Image();i.src=u.slice(4,-1).replaceAll('"','');return i.decode()}))}''')
            d = frame.bounding_box(); sc = page.locator('.screen').bounding_box()
            assert d and sc
            landscape = orientation=='landscape'
            vw,vh = (h,w) if landscape else (w,h)
            scale=width/vw
            near([d['width'],d['height']], [width,vh*scale],1, 'device bounds')
            box = (y,w-x-sw,sh,sw) if landscape else (x,y,sw,sh)
            near([sc['x']-d['x'],sc['y']-d['y'],sc['width'],sc['height']],[v*scale for v in box],1,'screen bounds')
            shot=frame.screenshot(animations='disabled'); shots.append(shot)
            im=Image.open(io.BytesIO(shot)).convert('RGB')
            def paint(px,py):
                a,b=(py,w-px) if landscape else (px,py)
                return im.getpixel((int(a*scale),int(b*scale)))
            assert paint(x+sw*.5,y+sh*.5)==GREEN, 'center hidden'
            camera=g['camera']; kind=camera.get('kind','punch')
            if kind!='none':
                color=paint(x+camera.get('centerX',sw/2), y+camera['top']+camera['height']/2)
                assert color!=BACK and max(color)<210, f'{orientation} camera not visible: {color}'
            if g['screenRadius']>8: assert paint(x+1,y+1)!=GREEN, 'corner not clipped'
            page.mouse.click(sc['x']+sc['width']/2,sc['y']+sc['height']/2)
            expect(page.frame_locator('iframe').locator('button')).to_have_attribute('data-hit','1')


def main():
    failures = []
    artifacts = Path(tempfile.mkdtemp(prefix='frame-qa-'))
    def run(label, fn, *args):
        try:
            fn(*args)
            print('PASS', label)
        except Exception as exc:
            failures.append(label); print('FAIL', label, '-', exc)
            if shots: (artifacts / f'{label}.png').write_bytes(shots[-1])
        finally: shots.clear()

    server = ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base = 'http://127.0.0.1:'+str(server.server_port)
    shots = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel=os.getenv('QA_BROWSER','chrome'))
            page = browser.new_page(viewport={'width':1280,'height':1100},device_scale_factor=1,reduced_motion='reduce')
            page.set_default_timeout(3000)
            page.route(base+'/__qa__',lambda r:r.fulfill(content_type='text/html',body=FIXTURE))
            run('control-iPhoneXS',matrix,page,base,'iPhoneXS','gold',None,shots)
            run('demo-control-iPhoneXS',demo,page,base,'iPhoneXS',['gold'])
            try: records = catalog()
            except (OSError,ValueError,KeyError,TypeError,AssertionError) as exc:
                failures.append('catalog'); print('FAIL catalog -',exc); records = {}
            for model in PILOTS:
                # Even before the catalog exists, exercise the live demo picker.
                if model not in records:
                    page.goto(base+'/index.html')
                    if not page.locator(f'input[name=device][value="{model}"]').count():
                        failures.append(model); print('FAIL demo picker missing',model)
                    continue
                spec = records[model]
                for color in spec['colors']: run(f'{model}-{color}',matrix,page,base,model,color,spec,shots)
                run('demo-'+model,demo,page,base,model,spec['colors'])
            for model,spec in records.items():
                if model in PILOTS: continue
                run('frame-'+model,check_family,page,base,spec,shots)
                run('demo-'+model,demo,page,base,model,spec['colors'])
            browser.close()
    finally:
        server.shutdown(); server.server_close()
    print(f'{len(failures)} failing groups; failure screenshots (if rendered): {artifacts}')
    return bool(failures)

if __name__=='__main__':
    raise SystemExit(main())
