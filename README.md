[![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/html5-device-mockups/Lobby)
[![GitHub release](https://img.shields.io/github/release/pixelsign/html5-device-mockups.svg)]()
[![Bower](https://img.shields.io/bower/v/html5-device-mockups.svg)]()
[![npm](https://img.shields.io/npm/v/html5-device-mockups.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

HTML5 device mockups v4 :iphone::computer:
====================

You can view the demo page here: <https://pixelsign.github.io/html5-device-mockups/>

Use on...
* Your website / splash screen

For...
* Displaying photos
* Displaying screenshots of your app(s)
* Displaying reference works / illustrations
* Displaying a content rotator / slideshow
* Embedding a JavaScript app inside the device
* Embedding a YouTube video

Why?
* Looks cool
* Attracts customers
* Makes your site look professional
* Give people the idea that your app/site works on mobile
* Give the impression that your illustrations are meant for web/mobile
* Lots of screenshots in just one "device"

Features:
* Maintains the device's aspect ratio when scaled
* Perfectly aligned screen content containers
* Some devices have "home button" layer defined for possible click event bindings
* Multiple color schemes
* Multiple orientations
* 27 legacy devices plus the modern SVG phone catalog. See the [coverage tracker](catalog/COVERAGE.md) for the exact models and backlog.
* Notched iPhones (X, XS, XS Max) clip screen content to the real screen shape, notch and corners included

Devices
-------

The [complete phone catalog](catalog/COVERAGE.md) lists modern device IDs. The table below covers the legacy library.

Devices marked **Obsolete** are long out of support and rarely seen any more. They still work and stay in the package for existing users.

| Name | Filename | Orientations | Colors | Status |
| --- | --- | --- | --- | --- |
| Chromebook | Chromebook | portrait | black | Obsolete |
| Galaxy S3 | galaxyS3 | portrait, landscape | black, white | Obsolete |
| Galaxy S5 | galaxyS5 | portrait, landscape | black, white, gold | Obsolete |
| Galaxy Tab 4 | galaxyTab4 | portrait | black, white | Obsolete |
| HTC One M8 | HtcOneM8 | portrait, landscape | black | Obsolete |
| Huawei P8 | HuaweiP8 | portrait, landscape | gold | Obsolete |
| iMac | iMac | portrait | black |  |
| iPad | iPad | portrait, landscape | black, white | Obsolete |
| iPad Air 2 | iPadAir2 | portrait, landscape | black, white, gold |  |
| iPad Pro | iPadPro | portrait, landscape | black, white, gold |  |
| iPhone 6 | iPhone6 | portrait, landscape | black, white, gold | Obsolete |
| iPhone 6 Plus | iPhone6Plus | portrait, landscape | black, white, gold | Obsolete |
| iPhone SE | iPhoneSE | portrait, landscape | black, white, gold, pink |  |
| iPhone 5 | iPhone5 | portrait, landscape | black, white | Obsolete |
| iPhone 7 | iPhone7 | portrait, landscape | black, white, gold, pink, red |  |
| iPhone X | iPhoneX | portrait, landscape | black |  |
| iPhone XS | iPhoneXS | portrait, landscape | silver, gold, spacegrey |  |
| iPhone XS Max | iPhoneXSMax | portrait, landscape | silver, gold, spacegrey |  |
| Lumia 930 | Lumia930 | portrait, landscape | black, white | Obsolete |
| Macbook | Macbook | portrait | black, white, gold |  |
| Macbook 2015 | Macbook2015 | portrait | black, white, gold |  |
| MacBook Pro | MacbookPro | portrait | black |  |
| Pixel | Pixel | portrait | black, white | Obsolete |
| Samsung TV | SamsungTV | portrait | black |  |
| Surface | Surface | portrait | black | Obsolete |
| Surface Pro 3 | SurfacePro3 | landscape | black |  |
| Surface Studio | SurfaceStudio | portrait | black |  |

## Integrating to your website:

### Bower
```
bower install html5-device-mockups
```

### npm

Version 4 is not on the npm registry yet: `npm i html5-device-mockups` still installs
3.2.1 from 2018. Until 4.0.0 is published there, install it straight from GitHub:

```
npm i github:pixelsign/html5-device-mockups#4.0.0
```

The files end up in `node_modules/html5-device-mockups/` as usual, so nothing else changes.

### Old traditional way
```
<link rel="stylesheet" type="text/css" href="dist/device-mockups.min.css">
```
## Usage

Use this example or grab the code from the HTML generator on our demo site:

```
<div class="device-wrapper">
  <div class="device" data-device="iPhone5" data-orientation="portrait" data-color="black">
    <div class="screen">
      <!-- PUT CONTENTS HERE -->
    </div>
    <div class="button">
      <!-- You can hook the "home button" to some JavaScript events or just remove it -->
    </div>
  </div>
</div>
```

## Building from source

The CSS in `dist/` is compiled from `src/scss/` with [Dart Sass](https://sass-lang.com/dart-sass/):

```
npm install
npm run build   # writes dist/device-mockups.css and dist/device-mockups.min.css
npm run watch   # rebuilds dist/device-mockups.css on change
```

### TV pack

Choose **TVs** in the demo for four 55-inch landscape frames and the original Samsung TV. The new [TV catalog](catalog/TVS.md) lists IDs and source specifications. Run `npm run bundle:tvs` for `dist/tvs.zip`, containing just the four new models, their stylesheet, and a working example. Serve the extracted directory with `python3 -m http.server 8000` and open `/example.html`. Use `data-orientation="landscape"` and `data-color="black"`; all four frames accept normal HTML, video, or permitted iframes inside `.screen`.

### Tablet and laptop pack

The [large-screen catalog](catalog/TABLETS-LAPTOPS.md) lists available iPads, Android tablets, Mac and Windows laptops, including valid device and finish IDs. Use the **Tablets** or **Laptops** filter on the demo to copy an embed. Tablets support portrait and landscape. Laptops use `data-orientation="landscape"`; their screens remain upright and interactive above the base.

Run `npm run bundle:large` for the standalone `dist/tablets-laptops.zip` with its own CSS, assets, source references and `example.html`. Serve the extracted directory with `python3 -m http.server 8000` and visit `http://localhost:8000/example.html`. Preserve the relative locations of `dist/large-only.min.css` and `device-mockups/`. On a larger display, override the library’s `.device-wrapper` max-width to choose a larger frame. For an existing installation using the full stylesheet, `npm run build` includes these devices without adding another stylesheet.

Add records to `catalog/large/*.json`, run `npm run build && npm run bundle:large && npm test`, then verify the gallery and interactive screens with `uv run --no-project tests/browser_large.py` (Chrome required).

### Modern phone pack

Run `npm run bundle:modern` (Node, Dart Sass from `npm install`, and Python 3). Unzip `dist/modern-phones.zip`, run `python3 -m http.server 8000` in the extracted directory, and visit `http://localhost:8000/example.html` (serve via HTTP so the browser can load external SVG masks). To embed one on your site, copy `dist/modern-only.min.css` and the `device-mockups/` folders you use, preserving their relative layout. Keep the license and any accompanying notices. The example markup is the same as the full library: replace the contents of `.screen` with your own HTML, video or permitted iframe. For an iframe, set `width:100%; height:100%; border:0` and provide a `title`. The demo picker script is not needed on your site. These local additions are not part of the older published v4 tag.

### Adding the next phone

Start with a record in `catalog/families/*.json` (`catalog/modern.json` is generated), not a new Sass selector. Its `width` and `height` are the complete portrait artwork bounds (including buttons); `screen` uses that same coordinate system. Edit the finish list, frame geometry and reference/license information. Use an original illustration or obtain explicit rights to redistribute the source art; the library license is not a substitute for those rights. `npm run build` generates the SVGs, both screen masks, responsive Sass geometry, and demo metadata. Run `npm test` and check both orientations with interactive screen content before adding the model to the coverage tracker. No downloaded manufacturer art is required by the build.

Legacy PNGs keep their existing geometry in `$devicesList` (`src/scss/devices.scss`) and their existing demo entries. Their build and public identifiers remain compatible.

To preview the demo page locally, serve the folder with any static server, e.g. `python3 -m http.server`.

Trademarks
---

Device and brand names, such as iPhone, iPad, MacBook, Galaxy, Pixel and Surface, are trademarks of their respective owners. They are used only to identify the device a frame depicts. This project is not affiliated with, sponsored or endorsed by Apple, Samsung, Google, Microsoft or any other manufacturer.

Created by:
---

> Tomi Hiltunen
> * tomi@innovaniac.com
> * http://innovaniac.com


> Angelos Arnis
> * angelos.arnis@gmail.com
> * https://arn.is/

> Benjamin Bortels
> * moin@benjaminbortels.de
> * https://benjaminbortels.de


Credits for the original graphical renderings of the devices
used in this package are found in a separate file which is
provided with this package.
