# /// script
# dependencies = ["playwright==1.56.0"]
# ///
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
root=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome');page=browser.new_page(reduced_motion='reduce');page.goto((root/'index.html').as_uri()+'#iPhoneX/portrait/black');groups=page.locator('#device-list fieldset');labels=groups.locator('legend').all_text_contents()
    assert 'iPhone' in labels and 'Samsung' in labels,labels
    ids=page.locator('#device-list input[name=device]').evaluate_all('(els)=>els.map(e=>e.value)');assert len(set(ids))==len(ids)
    for group in groups.all():
        dates=group.locator('time').evaluate_all('(els)=>els.map(e=>e.dateTime)');assert dates==sorted(dates,reverse=True),dates
    row=page.locator('.row[data-id=iPhoneX]');assert row.locator('time').get_attribute('datetime')=='2017-11-03';assert row.evaluate("e=>e.closest('fieldset').querySelector('legend').textContent")== 'iPhone'
    page.locator('#search').fill('2024');visible=page.locator('#device-list .row:visible');assert visible.count();assert all(t.startswith('2024') for t in visible.locator('time').evaluate_all('(els)=>els.map(e=>e.dateTime)'))
    print(f'Checked release dates within {len(labels)} family groups across {len(ids)} frames.');browser.close()
