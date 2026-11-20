# /// script
# dependencies = ["playwright==1.56.0"]
# ///
"""Regression: neither end of the sample status bar may intersect a foldable's camera."""
import functools,json,threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from playwright.sync_api import sync_playwright,expect
root=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,format,*args): pass
srv=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root)))
threading.Thread(target=srv.serve_forever,daemon=True).start()
records=[d for d in json.loads((root/'catalog/modern.json').read_text()) if any(k in d['id'].lower() for k in ('fold','duo','flip','razr'))];assert records
with sync_playwright() as pw:
    browser=pw.chromium.launch(channel='chrome'); page=browser.new_page(reduced_motion='reduce'); failures=[]
    for width in [430,1280]:
        page.set_viewport_size({'width':width,'height':860})
        for d in records:
            for orientation in ('portrait','landscape'):
                page.goto(f'http://127.0.0.1:{srv.server_port}/#{d["id"]}/{orientation}/{next(iter(d["finishes"]))}');frame=page.locator('.device:has(#screen)');expect(frame).to_have_attribute('data-device',d['id']);expect(frame).to_have_attribute('data-orientation',orientation)
                s=page.locator('#screen').bounding_box(); sw,sh=d['screen']['width'],d['screen']['height'];c=d['geometry']['camera'];w,h=c['width'],c['height'];cx=c.get('centerX',sw/2);y=c['top'];x=cx-w/2
                if not w:continue
                if orientation=='landscape': x,y,w,h,sw,sh=y,sw-x-w,h,w,sh,sw
                X,Y=s['x']+x/sw*s['width'],s['y']+y/sh*s['height']; W,H=w/sw*s['width'],h/sh*s['height']
                for el in page.locator('#screen .app-bar > *').all():
                    q=el.bounding_box();qx,qy=q['x'],q['y']; overlapping=min(qx+q['width'],X+W)>max(qx,X) and min(qy+q['height'],Y+H)>max(qy,Y)
                    if overlapping: failures.append((d['id'],orientation,width,el.evaluate('e=>e.tagName')))
    browser.close();assert not failures,failures
srv.shutdown();srv.server_close();print(f'Checked foldable status layout for {len(records)} views in both orientations at two viewport sizes.')
