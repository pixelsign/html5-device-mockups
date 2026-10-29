"""Generate the screen masks for the notched iPhones (XS, XS Max).

The frame PNGs draw the screen as a flat light fill inside a black bezel, with the notch
cut into it. This traces that fill and writes an alpha mask the CSS applies to .screen,
so content is clipped to the real screen: notch, notch "ears" and corner curve.

Screen = every non-black pixel connected to the image centre (the speaker grille and
camera are islands inside the black notch, so they stay out).

The mask and the .screen box bleed BLEED px past the fill into the black bezel. When the
browser scales the frame and mask, boundary pixels blend whatever the frame has there;
with the bleed that is always black bezel, never the light fill, so no light edge shows.
A 1px half-alpha ring keeps the outline smooth.

usage:  python3 scripts/screen-masks.py
Writes device-mockups/<device>/{portrait,landscape}_mask.png and prints the screen insets
to use for that device in src/scss/devices.scss. Needs Pillow (pip install pillow).
"""
from collections import deque
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter

ROOT = Path(__file__).resolve().parent.parent / 'device-mockups'
DEVICES = ('iPhoneXS', 'iPhoneXSMax')
BLEED = 5  # px into the bezel; 3 still leaks light on the XS Max at 3x density
EDGE = 8   # anything brighter than near-black belongs to the screen


def screen_fill(path):
    im = Image.open(path).convert('L')
    W, H = im.size
    lum = im.load()
    fill = Image.new('L', (W, H), 0)
    f = fill.load()
    queue = deque([(W // 2, H // 2)])
    f[W // 2, H // 2] = 255
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < W and 0 <= ny < H and not f[nx, ny] and lum[nx, ny] > EDGE:
                f[nx, ny] = 255
                queue.append((nx, ny))
    return fill


def dilate(img, n):
    for _ in range(n):
        img = img.filter(ImageFilter.MaxFilter(3))
    return img


for device in DEVICES:
    # Every colour shares the same screen geometry, so any one frame will do.
    fill = screen_fill(ROOT / device / 'portrait_spacegrey.png')
    W, H = fill.size
    solid = dilate(fill, BLEED)
    ring = ImageChops.subtract(dilate(solid, 1), solid).point(lambda v: 128 if v else 0)
    alpha = ImageChops.lighter(solid, ring)

    left, top, right, bottom = solid.getbbox()
    crop = alpha.crop((left, top, right, bottom))
    mask = Image.merge('LA', (Image.new('L', crop.size, 255), crop))
    mask.save(ROOT / device / 'portrait_mask.png', optimize=True)
    mask.rotate(90, expand=True).save(ROOT / device / 'landscape_mask.png', optimize=True)  # frame is rotated -90deg

    t, r, b, l = top, W - right, H - bottom, left
    print(f'{device}  portrait  screen_top/right/bottom/left: {t}, {r}, {b}, {l}')
    print(f'{device}  landscape screen_top/right/bottom/left: {r}, {b}, {l}, {t}')
