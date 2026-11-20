# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright==1.56.0", "pillow==11.3.0"]
# ///
"""uv run --no-project tests/browser_large.py; run npm run build && npm run bundle:large first."""
import functools, io, json, sys, tempfile, threading
from pathlib import Path
from http.server import ThreadingHTTPServer
from zipfile import ZipFile
from playwright.sync_api import sync_playwright, expect
from PIL import Image
from browser_frames import Handler, FIXTURE, ROOT, GREEN, near, demo


def check(page, d, base):
    id_=d['id']; tablet=d['type']=='tablet'; w,h=d['width'],d['height']; s=d['screen']; x,y,sw,sh=(s[k] for k in ('x','y','width','height'))
    colors=list(d['finishes']); g=d['geometry']
    for orient in (('portrait','landscape') if tablet else ('landscape',)):
        rotate=tablet and orient=='landscape'; vw,vh=(h,w) if rotate else (w,h)
        for width in (300,640):
            page.goto(base+'/fixture'); frame=page.locator('.device'); color=colors[0 if width==300 else -1]
            frame.evaluate('(e,[d,o,c,w])=>{Object.assign(e.dataset,{device:d,orientation:o,color:c});e.parentNode.style.width=w+"px"}', [id_,orient,color,width])
            frame.evaluate('''async e=>{for(const url of [getComputedStyle(e,'::after').backgroundImage,getComputedStyle(e.querySelector('.screen')).maskImage]) {const i=new Image(); i.src=url.slice(4,-1).replaceAll('"',''); await i.decode()}}''')
            box=frame.bounding_box(); screen=page.locator('.screen').bounding_box(); k=width/vw
            near([box['width'],box['height']],[width,vh*k],1,'body')
            expected=(y,w-x-sw,sh,sw) if rotate else (x,y,sw,sh)
            near([screen['x']-box['x'],screen['y']-box['y'],screen['width'],screen['height']],[a*k for a in expected],1,'screen')
            im=Image.open(io.BytesIO(frame.screenshot())).convert('RGB')
            def pixel(a,b):
                ax,ay=(b,w-a) if rotate else (a,b)
                return im.getpixel((int(ax*k),int(ay*k)))
            assert pixel(x+sw*.5,y+sh*.5)==GREEN,'screen content obscured'
            n=g.get('notch'); deck=g.get('deck')
            if n: assert pixel(n['x']+n['width']/2,n['y']+n['height']/2)!=GREEN,'missing camera cutout'
            if d['type']=='tv':
                p=g['panelHeight']; samplex=w/2 if g['stand']=='pedestal' else (w-g['span'])/2+(23 if g['stand']=='feet' else 14)
                assert pixel(samplex,p+(h-p)*.28) not in (GREEN,(255,0,255)), 'stand absent'
            if deck: assert pixel(deck['x']+deck['width']*.35,deck['y']+deck['height']*.5) not in (GREEN,(255,0,255)), 'missing laptop base'
            page.mouse.click(screen['x']+screen['width']/2,screen['y']+screen['height']/2)
            expect(page.frame_locator('iframe').locator('button')).to_have_attribute('data-hit','1')


def main():
    tv='--tvs' in sys.argv
    records=[d for p in sorted((ROOT/('catalog/tvs' if tv else 'catalog/large')).glob('*.json')) for d in json.loads(p.read_text())]; assert records
    def serve(dir):
        srv=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(dir)));threading.Thread(target=srv.serve_forever,daemon=True).start();return srv
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as pw:
        with ZipFile(ROOT/('dist/tvs.zip' if tv else 'dist/tablets-laptops.zip')) as archive: archive.extractall(tmp)
        app=serve(ROOT); bundle=serve(tmp); base=f'http://127.0.0.1:{bundle.server_port}'; appurl=f'http://127.0.0.1:{app.server_port}'
        browser=pw.chromium.launch(channel='chrome'); page=browser.new_page(viewport={'width':1400,'height':1400},reduced_motion='reduce');page.set_default_timeout(4000)
        page.route(base+'/fixture',lambda r:r.fulfill(content_type='text/html',body=FIXTURE.replace('device-mockups.min.css','tvs-only.min.css' if tv else 'large-only.min.css')))
        page.goto(base+'/example.html'); assert page.locator('.device').count()==len(records)
        for d in records:
            try:
                check(page,d,base);demo(page,appurl,d['id'],list(d['finishes']))
                if d['type'] in ('tv','laptop'): assert page.locator('input[name=orientation][value=portrait]').is_disabled()
            except Exception as e: raise AssertionError(d['id']) from e
        print(f'Passed packed iframe/geometry checks and demo selection for {len(records)} devices, two widths and all supported orientations.')
        browser.close();app.shutdown();bundle.shutdown();app.server_close();bundle.server_close()
if __name__=='__main__': main()
