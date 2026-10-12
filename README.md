# YabaSanshiro-spruce

Cross-compiled [YabaSanshiro](https://github.com/devmiyax/yabause) standalone builds for [spruceOS](https://github.com/spruceUI/spruceOS).

## Builds

| Build | Output | Devices | Base |
|-------|--------|---------|------|
| Universal | `yabasanshiro-aarch64.tar.gz` | Brick, TSP, TSPS, Flip, Pixel2 | Ubuntu 20.04 (glibc 2.31) |

## Usage

```bash
# Trigger a build
gh workflow run build-all.yml

# Download the output
gh release download beta-main -p "yabasanshiro-aarch64.tar.gz"
```

## Output structure

```
yabasanshiro         # YabaSanshiro standalone binary
libs/                # Required shared libraries (non-device-provided)
```

## Frame limiter

Upstream retro_arena always runs YabaSanshiro's own 60 Hz limiter (50 Hz for PAL games), on top of vsync.
`patches/framelimit-option.patch` makes it configurable:

| Where | Values |
|-------|--------|
| `-fl N` / `--frame_limit N` | `0` normal speed (default), `1` off, `2` double speed |
| In-game Config menu, "Frame limit" (per game, saved in `~/.yabasanshiro/<game>.config`) | Default (follows `-fl`), Normal speed, Off, Double speed |

With the limiter off, vsync alone paces the game, and the limiter no longer sleeps and spins to the next frame
every frame. Auto frame skip also stops, because it runs inside the limiter, so a game that cannot keep up
slows down instead of skipping frames. Without `-fl` or a per-game setting, behaviour is unchanged.
