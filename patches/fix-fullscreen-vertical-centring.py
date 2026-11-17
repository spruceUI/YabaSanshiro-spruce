#!/usr/bin/env python3
"""Centre the picture vertically in fullscreen when the screen is taller than the game.

SetSaturnResolution (vidogl.c) keeps the game's aspect and letterboxes the rest.
Every branch halves the spare space to centre the picture except the two
fullscreen width-limited ones (screen taller than the game's aspect, rotated and
not rotated), which put all of it in originy. glViewport's origin is bottom-left,
so the picture ends up against the top of the screen with the whole gap below it.

It shows with the default ORIGINAL aspect on any 4:3 screen and a 352-wide game
(Sega Rally on a 640x480 screen: 73 px below, none above, instead of 36 and 36),
and much more on taller panels. u_viewport_offset (ygles.c, native resolution)
follows originy, so it stays consistent."""

import sys

p = "yabause/src/vidogl.c"
with open(p) as f:
    s = f.read()

sites = [
    ("_Ygl->originy = (GlHeight - GlWidth  * wrate);",
     "_Ygl->originy = (GlHeight - GlWidth  * wrate) / 2.0f;"),
    ("_Ygl->originy = (GlHeight - GlWidth  * hrate);",
     "_Ygl->originy = (GlHeight - GlWidth  * hrate) / 2.0f;"),
]
for old, new in sites:
    n = s.count(old)
    if n != 1:
        sys.exit(f"fix-fullscreen-vertical-centring: expected 1 '{old}', found {n}")
    s = s.replace(old, new)

with open(p, "w") as f:
    f.write(s)
print("Centred the fullscreen letterbox vertically in SetSaturnResolution")
