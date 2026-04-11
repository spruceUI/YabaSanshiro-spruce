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
