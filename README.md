[![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/html5-device-mockups/Lobby)
[![GitHub release](https://img.shields.io/github/release/pixelsign/html5-device-mockups.svg)]()
[![Bower](https://img.shields.io/bower/v/html5-device-mockups.svg)]()
[![npm](https://img.shields.io/npm/v/html5-device-mockups.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

HTML5 device mockups v3 :iphone::computer:
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
* 86 different device images

Devices
-------

| Name | Filename | Orientations | Colors |
| --- | --- | --- | --- |
| Chromebook | Chromebook | portrait | black |
| Galaxy S3 | galaxyS3 | portrait, landscape | black, white |
| Galaxy S5 | galaxyS5 | portrait, landscape | black, white, gold |
| Galaxy Tab 4 | galaxyTab4 | portrait | black, white |
| HTC One M8 | HtcOneM8 | portrait, landscape | black |
| Huawei P8 | HuaweiP8 | portrait, landscape | gold |
| iMac | iMac | portrait | black |
| iPad | iPad | portrait, landscape | black, white |
| iPad Air 2 | iPadAir2 | portrait, landscape | black, white, gold |
| iPad Pro | iPadPro | portrait, landscape | black, white, gold |
| iPhone 6 | iPhone6 | portrait, landscape | black, white, gold |
| iPhone 6 Plus | iPhone6Plus | portrait, landscape | black, white, gold |
| iPhone SE | iPhoneSE | portrait, landscape | black, white, gold, pink |
| iPhone 5 | iPhone5 | portrait, landscape | black, white |
| iPhone 6 Hand | iPhone6Hand | portrait | black, white |
| iPhone 7 Hand | iPhone7Hand | portrait | black |
| iPhone 7 Hand 2 | iPhone7Hand_2 | portrait | black |
| iPhone 7 | iPhone7 | portrait, landscape | black, white, gold, pink, red |
| Lumia 930 | Lumia930 | portrait, landscape | black, white |
| Macbook | Macbook | portrait | black, white, gold |
| Macbook 2015 | Macbook2015 | portrait | black, white, gold |
| MacbookPro | Macbook2015 | portrait | black |
| Pixel | Pixel | portrait | black, white |
| Samsung TV | SamsungTV | portrait | black |
| Surface Pro 3 | SurfacePro3 | landscape | black |
| Surface Studio | SurfaceStudio | portrait | black |

## Integrating to your website:

### Bower
```
bower install html5-device-mockups
```

### npm
```
npm i html5-device-mockups
```

### Old traditional way
```
<link rel="stylesheet" type="text/css" href="dist/device-mockups.min.css">
```
## Usage

Use this example or grap the code from the HTML generator on our demo site:

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

## FAQ

"I can not control the height of the device"

<https://github.com/pixelsign/html5-device-mockups/issues/47>

Created by:
---

> Tomi Hiltunen
> * tomi@innovaniac.com
> * http://innovaniac.com


> Angelos Arnis
> * angelos.arnis@gmail.com
> * http://dribbble.com/pixelsign

> Benjamin Bortels
> * moin@benjaminbortels.de
> * https://benjaminbortels.de


Credits for the original graphical renderings of the devices
used in this package are found in a separate file which is
provided with this package.
