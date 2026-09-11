#!/usr/bin/env python3
"""Drop the main thread's late SDL_GL_MakeCurrent(wnd, nullptr) in retro_arena.

It runs after yabauseinit() has already handed the GL context to the render
thread. SDL forks that track the current context globally (the mali-fbdev SDL2
on the Anbernic XX) then see a null context on every SwapWindow from the render
thread, the surface bookkeeping advances but the thread keeps drawing into the
same buffer: the display alternates game frame and black. The context was
already released by VdpRevoke, so the call is redundant everywhere else."""

import re, sys

p = "yabause/src/retro_arena/main.cpp"
with open(p) as f:
    s = f.read()

# The call sits right before the thread-affinity #if, separated by a
# whitespace-only line. Anchor on the #if, tolerate the whitespace.
pat = re.compile(
    r"^[ \t]*SDL_GL_MakeCurrent\(wnd,\s*nullptr\);[ \t]*\n"
    r"(?=#if defined\(__RP64__\) \|\| defined\(__N2__\))",
    re.M,
)
s, n = pat.subn("", s)
if n != 1:
    sys.exit(f"fix-stray-makecurrent: expected 1 site, found {n}")
with open(p, "w") as f:
    f.write(s)
print("Removed the stray SDL_GL_MakeCurrent(wnd,nullptr) after yabauseinit")
