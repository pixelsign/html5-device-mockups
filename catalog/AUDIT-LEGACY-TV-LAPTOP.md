# Measurement audit: legacy frames, TVs and laptops

**2026-11-20 · 40 model IDs.** The source inventory is 27 legacy IDs (99 Sass variants), four modern TVs and nine current laptop records. The strongest evidence is for the modern display ratios and published body dimensions. Matching a device’s display ratio does **not** verify its bezel, cutouts, screen offset or stand shape.

**Correction:** Sony’s standard outside stand is approximately **1223 mm** wide, not 1170 mm. Only `sonyBravia8II55.geometry.span` was changed. Follow-up: corrected white Pixel frame height to 465 px after sampling the solid screen from y=45 through 410 inclusive; rotated the iPhone X portrait insets to match its landscape PNG, retaining a small overlap under the bezel. The legacy table below records the pre-fix audit.

## Legacy: 99 variants, 93 source PNGs

Inventory comes from `$devicesList` in [`devices.scss`](../src/scss/devices.scss), not the README or picker. Each row’s opening is `(W − left − right) × (H − top − bottom)` as in [the consuming Sass](../src/scss/device-mockups.scss). Checked the matching PNG dimensions and positive, in-bounds screen and enabled button rectangles for every row; four zero button insets mean disabled. All bounds pass. **98/99** declared canvas sizes agree with the source, after accounting for the six XS/XS Max landscape rows that rotate a portrait PNG −90°. Their rotated canvas and insets agree with the portrait rows. `P`/`L` below are selector names, not assumptions about the physical orientation of a computer or TV.

Openings are **artwork pixels**, not native pixels. The table shows every distinct opening per orientation across finishes. Error is the largest absolute relative difference between opening and reference **long:short** aspect across that ID’s rows; it is not a body-dimension error or a pass threshold. “Internal only” means the generation/size/SKU is not pinned down enough to promote an aspect match to a hardware measurement.

| Sass ID | Rows P/L | P opening(s) | L opening(s) | External display reference (native px); worst aspect error |
|---|---:|---|---|---|
| `galaxyS3` | 2/2 | 719×1280 | 1280×720 | [1280×720](https://www.samsungmobilepress.com/media-assets/galaxy-s-iii?tab=specs) (manufacturer index); 0.14% |
| `galaxyS5` | 3/3 | 1080×1920 | 1920×1080 | [1920×1080](https://www.samsung.com/sa_en/business/smartphones/galaxy-s/galaxy-s5-g900fd-ds-sm-g900fzbvksa/) (manufacturer); 0.00% |
| `galaxyTab4` | 2/0 | 1036×1646, 1036×1647 | — | [1280×800](https://www.gsmarena.com/samsung_officially_announces_galaxy_tab_4_series-news-8185.php) (family, secondary); 0.70% |
| `iMac` | 1/0 | 1693×952 | — | Internal only — no exact model/size. |
| `iPad` | 2/2 | 884×1177, 885×1177 | 1176×885 | Internal only — no exact model/size. |
| `iPadAir2` | 3/3 | 1536×2048 | 2048×1536 | [2048×1536](https://support.apple.com/en-us/112017) (manufacturer); 0.00% |
| `iPadPro` | 3/3 | 2047×2732, 2047×2731 | 2732×2047, 2732×2048 | Internal only — no exact model/size. |
| `iPhone6` | 3/3 | 751×1334 | 1333×750 | [1334×750](https://support.apple.com/en-us/111954) (manufacturer); 0.13% |
| `iPhone6Plus` | 3/3 | 1080×1920 | 1920×1080 | [1920×1080](https://support.apple.com/en-us/111940) (manufacturer); 0.00% |
| `iPhoneSE` | 4/4 | 640×1136 | 1136×640 | [1136×640](https://support.apple.com/en-us/112005) (manufacturer); 0.00% |
| `iPhone5` | 2/2 | 641×1136 | 1136×641 | [1136×640](https://support.apple.com/en-us/112016) (manufacturer); 0.16% |
| `Lumia930` | 2/2 | 1303×2314 | 2314×1303 | [1920×1080](https://web.archive.org/web/20150208113208/http:/www.microsoft.com/en/mobile/phone/lumia930/specifications/) (Microsoft, archived 2015-02-08); 0.11% |
| `Macbook` | 3/0 | 1442×902 | — | Internal only — no exact model/size. |
| `Macbook2015` | 3/0 | 1440×901 | — | [2304×1440](https://support.apple.com/en-us/112442) (manufacturer); 0.11% |
| `MacbookPro` | 1/0 | 923×577 | — | Internal only — no exact model/size. |
| `SamsungTV` | 1/0 | 1027×582 | — | Internal only — no exact model/size. |
| `Surface` | 1/0 | 1364×766 | — | Internal only — no exact model/size. |
| `Chromebook` | 1/0 | 2644×1499 | — | Internal only — no exact model/size. |
| `HtcOneM8` | 1/1 | 285×506 | 506×285 | [1920×1080](https://en.wikipedia.org/wiki/HTC_One_(M8)) (secondary); 0.13% |
| `HuaweiP8` | 1/1 | 1073×1920 | 1920×1073 | [1920×1080](https://m.gsmarena.com/huawei_p8-7006.php) (secondary); 0.65% |
| `SurfacePro3` | 0/1 | — | 3199×2133 | [2160×1440](https://support.microsoft.com/en-us/surface/models/surface-pro-3-specs-and-features) (manufacturer); 0.02% |
| `SurfaceStudio` | 1/0 | 3715×2487 | — | [4500×3000](https://support.microsoft.com/en-us/surface/models/surface-studio-1st-gen-diagrams-and-tech-specs) (1st-gen comparator); 0.42% |
| `iPhone7` | 5/5 | 760×1344, 266×479 | 1344×760, 479×266 | [1334×750](https://support.apple.com/en-us/111943) (manufacturer); 1.24% |
| `iPhoneX` | 1/1 | 626×1352 | 1344×634 | [2436×1125](https://support.apple.com/en-us/111864) (manufacturer); 2.10% |
| `iPhoneXS` | 3/3 | 862×1855 | 1855×862 | [2436×1125](https://support.apple.com/en-us/111881) (manufacturer); 0.62% |
| `iPhoneXSMax` | 3/3 | 950×2043 | 2043×950 | [2688×1242](https://support.apple.com/en-us/111880) (manufacturer); 0.63% |
| `Pixel` | 2/0 | 207×365 | — | [1920×1080](https://gsmarena.com/model-8346.php) (2016 comparator, secondary); 0.82% |

**Where the picture and the numbers diverge**

- `Pixel/portrait_white.png` is **229×465**, against **229×464** in Sass. The black PNG is 229×464. The declared opening is 207×365 for both; the extra raster row does not establish which inset to change.
- `iPhoneX` landscape: the Sass opening starts at (50,46) and is 1344×634. Flood-filling the center-connected region with PNG alpha <128 gives (47,51) to (1398,674), exclusive: **1351×623**. The portrait alpha region is 623×1351. The landscape image rotates the opening; the Sass insets do not. This can clip content on the long axis. The notched silhouette itself is not a rectangle.
- `iPhone7` red uses a lower-resolution PNG and a different opening than the other four finishes. `galaxyTab4`, `iPad`, and `iPadPro` also vary by finish. Do not normalize these rows solely because their IDs match.
- Exact button outlines, notch paths, and physical bezel widths are **not** externally verified. PNG dimensions include framing and sometimes a base or stand. Generic IDs such as `Macbook` and `SamsungTV` are not aliases for the specific later catalog records. The Galaxy Tab 4 comparison is family-level; the SE comparison uses the 2016 model, not later SE bodies.

## Modern TVs: front elevation in millimetres

In [televisions.json](tvs/televisions.json), `width × height` includes the tabletop stand; `width × panelHeight` excludes it. Span is the **outside** width of the feet/base (the renderer places the extremes at `(width ± span)/2`). All four screen rectangles are positive, exactly 16:9 and contained in the panel, not just in the overall frame. These checks do not establish precise active-area offsets. Each row gives the evidence for the dimensions separately from the illustration.

| Catalog ID and regional reference | With stand W×H | Without stand W×H | Span | What the reference supports |
|---|---:|---:|---:|---|
| `samsungFrame55LS03F` · [Samsung AT · QE55LS03FAUXXN](https://www.samsung.com/at/lifestyle-tvs/the-frame/ls03f-55-inch-art-store-black-qe55ls03fauxxn/) | 1237.9×743.4 | 1237.9×708.8 | 897.2 | Manufacturer lists both envelopes and 897.2×227.8 mm foot size; 3840×2160. |
| `lgOLED55C5` · [LG East Africa · OLED55C56LA](https://www.lg.com/eastafrica/tvs/lg-oled55c56la) | 1222×757 | 1222×703 | 470 | Both envelopes, 470×230 base and 3840×2160 are explicit in the indexed LG specifications; direct fetch was denied and the extracted page omitted the dimensions. Indexed evidence, not a full-page recheck. |
| `sonyBravia8II55` · [Sony UK · K-55XR8M2](https://www.sony.co.uk/electronics/support/televisions-projectors-oled-tvs-android-/k-55xr8m2/specifications) | 1224×722 | 1224×707 | 1223 | UK support dimensions (cm), converted to mm. Standard outside position, not the 783 mm-high soundbar position. Published outside width ≈122.3 cm supports the span correction. |
| `tcl55C7K` · [TCL AU · 55C7K PDF, p. 2](https://static-obg.tcl.com/content/dam/brandsite/region/australia/products/tv/c-series/c7k/downloads/55C7K_Specs.pdf) | 1226×760 | 1226×710 | 370 | Sheet lists both envelopes, 16:9 and 3840×2160. No base width in the dimensions table: **370 is illustrative**, not externally verified. |

No TV source establishes the catalog’s exact screen `x/y`, bezel thickness, corner radii or foot contours. A 55-inch class designation is not a 55.000-inch measured aperture. No screen size was changed to force that diagonal. `previewOS` remains Tizen / webOS / Google TV / Google TV, respectively.

## Current laptops: display, closed body and open artwork

[Laptop records](large/laptops.json) use illustration units for the open elevation. `measurements.bodyMm`, where present, means **closed width × depth × thickness**, not the open frame’s width and height. Compared the display and physical dimensions below with the linked manufacturer specifications; the screen rectangle fits the lid and the deck fits the frame for all nine. Native aspect error is `abs((opening W/H)/(native W/H) − 1) × 100`.

For a separate **image-derived**, not physical, check, the final column compares mid-lid width / full silhouette width in the catalog and the linked front reference. For Apple: JPEG pixels with grayscale absolute difference >8 from the corner background, bounding box and its middle scanline. For Surface: alpha >200. This can shift an edge by a pixel; agreement is evidence about projected proportions only, not a dimensioned drawing or validation of every camera, corner or seam.

| Catalog ID · manufacturer spec | Diagonal; native px | Catalog opening; aspect error | Closed W×D×T (mm) | Lid/full width: catalog / external image |
|---|---|---|---|---|
| [`MacBookNeo13A18Pro`](https://www.apple.com/macbook-neo/specs/) | 13.0″; 2408×1506 | 722.4×451.8; 0.0000% | 297.5×206.4×12.7 | 0.859 / [0.859](https://www.apple.com/v/macbook-neo/c/images/specs/display__gjwmz6l3m262_large_2x.jpg) |
| [`MacBookAir13M5`](https://www.apple.com/macbook-air/specs/) | 13.6″; 2560×1664 | 768×499.2; 0.0000% | 304.1×215×11.3 | 0.834 / [0.836](https://www.apple.com/v/macbook-air/specs/c/images/specs/13-inch/mba_13_display__cnk2rprvaas2_large_2x.jpg) |
| [`MacBookAir15M5`](https://support.apple.com/en-us/126321) | 15.3″; 2880×1864 | 864×559.2; 0.0000% | 340.4×237.6×11.5 | 0.854 / [0.854](https://www.apple.com/v/macbook-air/specs/c/images/specs/15-inch/mba_15_display__oz47vz6kmuai_large_2x.jpg) |
| [`MacBookPro14M6`](https://www.apple.com/macbook-pro/specs/) | 14.2″; 3024×1964 | 801.36×520.46; 0.0000% | 312.6×221.2×15.5 | 0.824 / [0.824](https://www.apple.com/v/macbook-pro/liquid-retina-xdr-display/specs/e/images/specs/14-inch/display_14_inch__db0ppp7h83ma_large_2x.jpg) |
| [`MacBookPro16M5Max`](https://www.apple.com/macbook-pro/specs/) | 16.2″; 3456×2234 | 915.84×592.01; 0.0000% | 355.7×248.1×16.8 | 0.846 / [0.845](https://www.apple.com/v/macbook-pro/liquid-retina-xdr-display/specs/e/images/specs/16-inch/display_16_inch__bn4z91heotxy_large_2x.jpg) |
| [`MacBookPro14ProledM5Pro`](https://www.apple.com/macbook-pro/proled-xdr-display/specs/) | 14.2″; 3024×1986 | 801.36×526.29; 0.0000% | 310.8×216.3×15 | 0.851 / [0.851](https://www.apple.com/v/macbook-pro/proled-xdr-display/b/images/specs/display_14_inch__dj3gn87hqg02_large_2x.jpg) |
| [`MacBookPro16ProledM5Pro`](https://www.apple.com/macbook-pro/proled-xdr-display/specs/) | 16.3″; 3472×2266 | 920.08×600.49; 0.0000% | 355.5×244.2×16 | 0.851 / [0.851](https://www.apple.com/v/macbook-pro/proled-xdr-display/b/images/specs/display_16_inch__d25b08sjpqs2_large_2x.jpg) |
| [`SurfaceLaptop138Gen8`](https://learn.microsoft.com/en-us/surface/tech-specs/surface-laptop-138inch-15inch-8thedition-snapdragon) | 13.8″; 2304×1536 | 771.84×514.56; 0.0000% | Not recorded | 0.853 / [0.851](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/b00-Surface-Laptop-Snapdragon-8Ed-HC-Front?wid=1600&fmt=png-alpha) |
| [`DellXPS13DX13260`](https://www.dell.com/en-us/shop/dell-laptops/new-xps-13-laptop/spd/xps13dx13260laptop) | 13.4″; 2560×1600 | 768×480; 0.0000% | 296.9×200.66×12.7 | 0.875 / not verified (reference denied) |

The seven Apple body triples agree after converting the published centimetres to millimetres. The two 16-inch Pro records use different panels and must not share an aperture. For Surface, the Snapdragon 8th Edition 13.8-inch spec verifies the display; there is no `bodyMm` triple to validate. For Dell, the DX13260 2.5K touch listing verifies the display and closed dimensions, but not the projected lid or deck. No laptop record was changed.

**Source-to-asset check, without rebuilding:** Across all 13 modern models, reconstructed the rectangles in [`_large.scss`](../src/scss/_large.scss) and [`_tvs.scss`](../src/scss/_tvs.scss) for all 29 finishes. Each matched its catalog rectangle to floating-point precision. The 29 landscape frame SVG viewBoxes match the declared outer sizes, and all 13 landscape mask viewBoxes match the opening sizes. This checks coordinate systems, not every painted pixel, generated package, or browser interaction. In particular, a frame viewBox can be correct while its stand is stale.
