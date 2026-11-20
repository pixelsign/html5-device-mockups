# /// script
# dependencies = ["playwright==1.56.0"]
# ///
"""The shell must not move off its screen when embedded in a centered host."""
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome');page=browser.new_page();page.goto((root/'index.html').as_uri());rows=page.evaluate('ALL_DEVICES.map(d=>[d.id,d.orientations,d.colors])');page.set_content('<div class="device-wrapper" style="width:239.5px;text-align:center"><div class="device"><div class="screen"></div></div></div>');page.add_style_tag(content=(root/'dist/device-mockups.min.css').read_text());result=page.evaluate('''rows=>{const d=document.querySelector('.device'),bad=[];let count=0;for(const [id,orientations,colors] of rows)for(const o of orientations)for(const c of colors){Object.assign(d.dataset,{device:id,orientation:o,color:c});const p=getComputedStyle(d,'::after');if(p.transform==='none' && (parseFloat(p.left)!==0 || parseFloat(p.top)!==0))bad.push([id,o,c,p.left,p.top]);count++}return [count,bad]}''',rows);browser.close();assert not result[1],f'{len(result[1])} misaligned frame variants: {result[1][:5]}';print(f'All {result[0]} variants checked for centered-host registration (rotated overlays retain their rotation offsets).')
