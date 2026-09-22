# Architecture

## Overview

The application is intentionally simple: it captures a desktop region, handles the pixel buffer, and presents a transparent copy in a new location. There is no game awareness, no process access, and no game-state parsing.

## Data flow

```text
Windows Desktop
      │
      ▼
Screen Capture
      │
      ▼
RGBA Pixel Buffer
      │
      ▼
Crop / Scale
      │
      ▼
PySide6 Overlay
      │
      ▼
Windows Desktop
```

## Screen capture

The source is a configurable rectangular region from the Windows desktop. The project supports desktop capture through Pillow's `ImageGrab` fallback and optionally uses `dxcam` when available to reduce capture latency. The application never targets the CS2 process; it only asks Windows for pixels from a rectangle on the display.

## Pixel processing

Captured pixels are treated as a plain RGBA image buffer. The application may crop or scale the source region to fit the configured overlay size while preserving aspect ratio by default. The code keeps the image processing minimal and avoids unnecessary copies.

## Overlay rendering

A borderless `QMainWindow` is used for the overlay. The window is configured to be transparent outside the image, optionally always-on-top, non-focus-stealing, and optionally click-through. The image is rendered as a `QPixmap` attached to a transparent label.

## Win32 interaction

The implementation relies on the standard Windows desktop environment and uses PySide6 window flags for:

- transparent background
- click-through mode
- always-on-top behavior
- borderless rendering
- non-focus window behavior

The project is not implemented with kernel drivers or any low-level process access.

## Configuration

The application reads a TOML configuration file. Geometry, opacity, click-through behavior, always-on-top, and target FPS are all configurable. This keeps the behavior explicit and reviewable.

## Dependencies

- PySide6: overlay windowing and rendering
- Pillow: image capture and pixel conversion
- dxcam: optional low-latency Windows capture path
- Python standard library: TOML parsing, timing, and configuration

## Security review notes

The data path remains entirely within the desktop pixel domain:

`desktop pixels -> capture -> RGBA buffer -> overlay -> desktop pixels`

No network calls, online services, memory access, or game-state logic are part of the intended architecture.
