# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow==11.3.0", "playwright==1.56.0"]
# ///
"""uv run --no-project tests/browser_legacy_apertures.py [model]; needs Chrome and npm deps.
Compile legacy-only CSS in memory; serve just the fixture, stylesheet and PNGs.
"""
import io
import re
import subprocess
import sys
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'device-mockups'
NOTCHED = {'iPhoneX', 'iPhoneXS', 'iPhoneXSMax'}
ROTATED = NOTCHED - {'iPhoneX'}
GREEN = (0, 255, 64)
HOST = 'http://legacy.test'
HTML = '''<!doctype html><link rel="stylesheet" href="/qa.css"><style>
body{margin:0;background:white;text-align:center} .device-wrapper{max-width:none}
iframe{display:block;width:100%;height:100%;border:0}</style>
<div class="device-wrapper"><div class="device"><div class="screen"><iframe
srcdoc="<style>*{margin:0}button{border:0;background:#00ff40;width:100vw;height:100vh;display:block}</style><button onclick='if(event.isTrusted)this.dataset.hit=1'></button>"></iframe></div><div class="button"></div></div></div>'''


def inventory():
    rows = re.findall(r"\((\w+),\s*(portrait|landscape),\s*'(\w+)',\s*(?:true|false),([^)]*)\)",
                      (ROOT / 'src/scss/devices.scss').read_text())
    assert len({r[:3] for r in rows}) == len(rows) == 99 and len({r[0] for r in rows}) == 27
    return sorted(rows, key=lambda r: r[0] != 'iPhoneSE')


def picture(model, orientation, color):
    rotate = model in ROTATED and orientation == 'landscape'
    im = Image.open(ART / model / f'{"portrait" if rotate else orientation}_{color}.png').convert('RGBA')
    return im.transpose(Image.Transpose.ROTATE_90) if rotate else im


def measure(im, model):
    """Straight parts of the opening; 22% avoids the notch and curved corners."""
    w, h = im.size
    p = im.load()
    fill = p[w//2, h//2]
    def inside(x, y):
        return p[x,y][3] < 128 if model == 'iPhoneX' else p[x,y] == fill
    box = []
    for x,y,dx,dy in [(int(w*.22),h//2,0,-1),(w//2,int(h*.22),1,0),
                      (int(w*.22),h//2,0,1),(w//2,int(h*.22),-1,0)]:
        while 0 <= x < w and 0 <= y < h and inside(x,y):
            x += dx
            y += dy
        box.append((x+1 if dx<0 else w-x) if dx else (y+1 if dy<0 else h-y))
    return box


def main():
    css = subprocess.check_output([ROOT/'node_modules/.bin/sass', '--stdin', '--load-path=src/scss'],
        cwd=ROOT, input=b'@use "device-mockups" with ($include-phones:false,$include-large:false,$include-tvs:false);')
    def serve(route):
        path = route.request.url.removeprefix(HOST)
        if path == '/': route.fulfill(content_type='text/html',body=HTML)
        elif path == '/qa.css': route.fulfill(content_type='text/css', body=css)
        elif path.startswith('/device-mockups/') and path.endswith('.png'):
            route.fulfill(path=ROOT/path[1:])
        else: route.abort()
    errors, cases, renders = [], 0, 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome')
        page = browser.new_page(viewport={'width':800,'height':1100})
        page.route(HOST+'/**', serve)
        page.goto(HOST+'/')
        for model,o,c,values in inventory():
            if sys.argv[1:] and model not in sys.argv[1:]: continue
            cases += 1
            key = f'{model}/{o}/{c}'
            w,h,t,r,b,l,*_ = map(int,values.split(','))
            im = picture(model,o,c)
            assert im.size == (w,h), key
            # The black Lumia glass and inactive surround have identical RGBA.
            # Its white twin exposes the boundary; do not enlarge into that surround.
            measured = measure(im,model)
            if (model,c)==('Lumia930','black'):
                twin = measure(picture(model,o,'white'),model)
                assert all(a<=b for a,b in zip(measured,twin)), key
                measured = twin
            mt,mr,mb,ml = measured
            gaps = [a-z for a,z in zip((t,r,b,l),(mt,mr,mb,ml))]
            if max(gaps)>0: errors.append(f'{key} uncovered fill (T,R,B,L): {gaps}')
            for width in (240, 400):
                renders += 1
                page.locator('.device').evaluate('''async (el,[device,orientation,color,width])=>{
                    Object.assign(el.dataset,{device,orientation,color});el.parentNode.style.width=width+'px';
                    for(const url of [getComputedStyle(el,'::after').backgroundImage,getComputedStyle(el).backgroundImage,getComputedStyle(el.firstElementChild).maskImage]){
                        if(url.startsWith('url(')){const im=new Image();im.src=url.slice(5,-2);await im.decode()}
                    }}''',[model,o,c,width])
                shot = Image.open(io.BytesIO(page.locator('.device').screenshot())).convert('RGB')
                scale = width/w
                L,T,R,B = [round(v*scale) for v in (ml,mt,w-mr,h-mb)]
                pts = [(L+1,(T+B)//2),(R-2,(T+B)//2),((L+R)//2,T+1),((L+R)//2,B-2)]
                if model not in NOTCHED:
                    pts += [(x,y) for x in (L+1,R-2) for y in (T+1,B-2)]
                else: # sample beside the notch, not inside it
                    # Use the same native scanlines used to measure the aperture.
                    x,y = int(w*.22*scale),int(h*.22*scale)
                    pts = [(L+2,y),(R-3,y),(x,T+2),(x,B-3)]
                    notch = ((L+R)//2,T+1) if o=='portrait' else (L+1,(T+B)//2)
                    if shot.getpixel(notch)==GREEN: errors.append(f'{key}@{width} missing notch')
                # Independent outside probes catch content painting across the rim.
                for x,y in [(L-4,(T+B)//2),(R+3,(T+B)//2),((L+R)//2,T-4),((L+R)//2,B+3)]:
                    if 0<=x<shot.width and 0<=y<shot.height and shot.getpixel((x,y))==GREEN:
                        errors.append(f'{key}@{width} content over bezel at {(x,y)}')
                misses = [pt for pt in pts if shot.getpixel(pt)!=GREEN]
                if misses: errors.append(f'{key}@{width} exposed screen at {misses}')
                if model == 'iPhoneSE':
                    # Seven native pixels of dark rim, then real white (or black)
                    # bezel. Sample the flat surface, not a resampled boundary.
                    for x,y in [(ml-23,h//2),(w-mr+22,h//2),(w//2,mt-23),(w//2,h-mb+22)]:
                        actual = shot.getpixel((int(x*scale),int(y*scale)))
                        expected = im.getpixel((x,y))[:3]
                        if max(abs(a-b) for a,b in zip(actual,expected))>3:
                            errors.append(f'{key}@{width} bezel {actual} != {expected}')
                # Check a chassis landmark independent of the live box: a misregistered
                # pseudo-element can leave clickable content floating on a white page.
                for x,y in [(ml//2,h//2), (w-mr//2,h//2),(w//2,mt*3//4)]:
                    px=im.getpixel((x,y)); pt=(int(x*scale),int(y*scale))
                    if px[3]==255 and max(px[:3])<200 and shot.getpixel(pt)==(255,255,255):
                        errors.append(f'{key}@{width} missing frame at {pt}'); break
                button = page.frame_locator('iframe').locator('button')
                button.evaluate('el=>delete el.dataset.hit')
                rect = button.bounding_box()
                page.mouse.click(rect['x']+rect['width']/2, rect['y']+rect['height']/2)
                if button.get_attribute('data-hit')!='1': errors.append(f'{key}@{width} click blocked')
        browser.close()
    assert cases
    print(f'{cases} variants; {renders} browser renders and trusted iframe clicks; {len(errors)} failures')
    if errors: raise SystemExit('\n'.join(errors))


if __name__ == '__main__': main()
