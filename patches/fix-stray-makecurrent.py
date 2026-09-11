#!/usr/bin/env python3
"""Drop the main thread's late SDL_GL_MakeCurrent(wnd, nullptr) in retro_arena.

It runs after yabauseinit() has already handed the GL context to the render
thread. SDL forks that track the current context globally (the mali-fbdev SDL2
on the Anbernic XX) then see a null context on every SwapWindow from the render
thread, the surface bookkeeping advances but the thread keeps drawing into the
same buffer: the display alternates game frame and black. The context was
already released by VdpRevoke, so the call is redundant everywhere else."""

p = "yabause/src/retro_arena/main.cpp"
with open(p) as f:
    s = f.read()

old = """  delete p;
  SDL_GL_MakeCurrent(wnd,nullptr);
#if defined(__RP64__) || defined(__N2__)"""
new = """  delete p;
#if defined(__RP64__) || defined(__N2__)"""
assert s.count(old) == 1, "stray MakeCurrent site not found exactly once"
with open(p, "w") as f:
    f.write(s.replace(old, new))
print("Removed the stray SDL_GL_MakeCurrent(wnd,nullptr) after yabauseinit")
