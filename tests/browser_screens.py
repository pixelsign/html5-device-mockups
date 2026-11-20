# /// script
# dependencies = ["playwright==1.56.0"]
# ///
"""Exercise platform changes in the gallery and offline ZIP examples."""
import functools, tempfile, threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zipfile import ZipFile
from playwright.sync_api import sync_playwright, expect

root = Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
srv = ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root)))
threading.Thread(target=srv.serve_forever,daemon=True).start()
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome'); page=browser.new_page(reduced_motion='reduce'); errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(f'http://127.0.0.1:{srv.server_port}/#MacBookAir13M5/landscape/silver')
    img=page.locator('#screen img'); expect(img).to_have_attribute('src','screens/macOS-app.svg')
    def device(id): page.evaluate('id=>location.hash=id',id)
    for id,os in [('SurfaceLaptop138Gen8','Windows'),('Chromebook','ChromeOS'),('samsungFrame55LS03F','Tizen'),('lgOLED55C5','webOS'),('sonyBravia8II55','Google-TV'),('SamsungTV','Smart-TV')]:
        device(id); expect(img).to_have_attribute('src',f'screens/{os}-app.svg'); img.evaluate('i=>i.decode()')
    page.locator('#seg-screen label').nth(1).click();expect(img).to_have_attribute('src','screens/Smart-TV-lock.svg')
    device('MacbookPro'); expect(img).to_have_attribute('src','screens/macOS-lock.svg')
    page.locator('#seg-screen label').nth(2).click();page.locator('#file-input').set_input_files(str(root/'screens/ChromeOS-app.svg'));expect(img).to_have_count(1); uploaded=img.get_attribute('src'); assert uploaded.startswith('blob:')
    device('tcl55C7K');expect(page.locator('#app-mode-text')).to_have_text('Home');expect(img).to_have_attribute('src',uploaded)
    device('iPhoneX');expect(page.locator('#app-mode-text')).to_have_text('App');page.locator('#seg-screen label').first.click();expect(img).to_have_count(0)
    for pack in ('tablets-laptops','tvs'):
        with tempfile.TemporaryDirectory() as tmp:
            with ZipFile(root/f'dist/{pack}.zip') as z:z.extractall(tmp)
            page.goto((Path(tmp)/'example.html').as_uri()); buttons=page.locator('.os-preview');assert buttons.count()>0
            for btn in buttons.all():
                asset=btn.locator('img');asset.evaluate('i=>i.decode()');btn.click();expect(asset).to_have_attribute('src',asset.get_attribute('src').replace('-app.svg','-lock.svg'));asset.evaluate('i=>i.decode()');assert asset.get_attribute('src').endswith('-lock.svg')
    assert not errors,errors;browser.close();print('Passed OS switching, file override, phone fallback and both packed examples.')
srv.shutdown();srv.server_close()
