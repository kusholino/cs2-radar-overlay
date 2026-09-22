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
