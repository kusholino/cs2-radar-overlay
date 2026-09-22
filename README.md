# CS2 Radar Overlay

A minimal Windows desktop overlay that captures an arbitrary screen rectangle and re-displays it in a transparent overlay window. The project is intentionally limited to pixel capture and pixel re-display; it does not analyze CS2 or interact with the game process.

## Overview

The application follows a very small data flow:

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
PySide6 Overlay Window
      │
      ▼
Windows Desktop
```

It captures pixels already rendered on the desktop, preserves them as output, and places a transparent copy elsewhere. Nothing in the implementation reads process memory, process state, game files, network traffic, or input streams.

## Anti-Cheat Transparency

This application does not access Counter-Strike 2's process,
memory, files, network traffic, or internal game state.

It only captures pixels already rendered on the Windows desktop
and displays those pixels in another location.

This project does not claim that use of the software is permitted
by Valve, VAC, FACEIT, or any other competitive platform.
Users are responsible for checking the current rules of the
platform on which they use third-party software.

## Scope and boundaries

This project is intentionally restricted to:

- Windows desktop capture of an explicit source rectangle
- optional resizing and aspect-ratio preservation
- transparent borderless overlay rendering
- click-through and always-on-top options
- configurable coordinates and update rate
- multi-monitor virtual-desktop calibration and named presets
- runtime HUD and global overlay hotkeys

The project does not do any of the following:

- read CS2 process memory
- read CS2 files or configuration
- inject code into game processes
- hook game APIs
- parse game state
- automate input
- modify game files
- analyze entity positions
- interact with anti-cheat systems

## Requirements

- Windows 10/11
- Python 3.11+
- PySide6
- Pillow
- dxcam (preferred if available)
- mss (fast fallback when dxcam is unavailable)

## Quick start

1. Install Python 3.11+
2. Install the project in editable mode:

   ```powershell
   python -m pip install -e '.[dev]'
   ```

3. Copy the example configuration and adjust the capture and overlay geometry:

   ```powershell
   copy config.example.toml config.toml
   ```

4. Launch the app:

   ```powershell
   python -m radar_overlay.main --config config.toml
   ```

## Multi-monitor presets

Calibration spans the complete Windows virtual desktop, including monitors positioned left or above the primary display. Negative coordinates are supported for those layouts.

Save a calibrated setup as a named preset:

```powershell
python -m radar_overlay.main --calibrate --preset office-1440p --shape circle
```

This writes `presets/office-1440p.toml`. Load it later with:

```powershell
python -m radar_overlay.main --preset office-1440p
```

Use one preset per monitor arrangement or game resolution. The regular `config.toml` remains available as the default profile.

## Mouse calibration

Use the built-in selector when you do not want to enter coordinates manually:

```powershell
python -m radar_overlay.main --calibrate --config config.toml
```

1. Drag around the minimap on the CS2 screen.
2. Drag the second rectangle where the relocated minimap should appear and choose its size.
3. Adjust the preview: drag inside a selection to move it, or drag its edges/corners to resize it.
4. Check the two highlighted regions. Press `R` to redo both selections or `Enter` to save.
5. The selected regions are written to `config.toml` only after pressing `Enter`.

After calibration, start the normal command again. The overlay is click-through and locked in place; run `--calibrate` again to change its position or size. Press Escape during calibration to cancel.

## Overlay hotkeys

These global shortcuts control only this desktop overlay:

- `F8`: toggle the performance HUD
- `F9`: lock or unlock mouse click-through behavior
- `Ctrl+Alt+Q`: quit the overlay cleanly

They do not send input to CS2 and do not read or modify game state.

## Performance notes

The configured `target_fps` is an upper scheduling target. The achieved rate is limited by desktop capture, scaling, and Qt rendering. On the development machine, a 248x249 region measured approximately 143.6 Hz with the `mss` backend (300 captures in 2.089 seconds, 6.96 ms per capture). This means 300 Hz and 600 Hz are not achievable for that setup; the HUD reports the actual result.

The application uses per-monitor DPI-aware Qt behavior on Windows. A `SetProcessDpiAwarenessContext()` warning can appear when Windows or Qt has already selected the DPI context. It is non-fatal; if monitors use different scaling percentages, calibrate each layout with the virtual-desktop selector and save a separate preset.

## Configuration

The application reads a human-readable TOML file. Example values are in [config.example.toml](config.example.toml).

```toml
[capture]
x = 0
y = 0
width = 300
height = 300

[overlay]
x = 810
y = 1150
width = 300
height = 300
opacity = 1.0
click_through = true
always_on_top = true
show_fps = true
show_refresh_hz = true
show_capture_ms = false
show_render_ms = false

[performance]
target_fps = 300
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for the architecture overview, data flow, and dependency notes.

## Security and anti-cheat review

- [SECURITY.md](SECURITY.md)
- [docs/anti-cheat.md](docs/anti-cheat.md)

## Project status

This repository is currently at version 0.1.0.

## License

This project is licensed under the MIT license. See [LICENSE](LICENSE) for details.
