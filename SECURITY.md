# Security policy

## Project safety boundaries

This project intentionally does not perform any of the following:

- process memory access
- CS2 process access
- code injection
- DLL injection
- game file modification
- network communication
- telemetry collection
- keyboard or mouse automation
- game-state parsing
- anti-cheat evasion

## Review guidance

To verify the scope from source code alone:

1. Inspect [src/radar_overlay/capture.py](src/radar_overlay/capture.py) and confirm the capture path is limited to desktop pixels.
2. Inspect [src/radar_overlay/config.py](src/radar_overlay/config.py) and confirm all settings are geometry and performance related.
3. Confirm there are no calls to the CS2 process, Steam APIs, or game memory libraries.
4. Confirm there are no network libraries or telemetry modules in the project.
5. Confirm the application only creates an overlay window and does not send input to the game.

## Data handling

The software does not upload, transmit, or store any game state, user input, or personal information. The only runtime data it manipulates is the pixel data from a selected screen region and a small configuration file.

## Reporting concerns

If you identify a security issue or a scope violation, please report it through the project’s issue tracker or a private contact channel established by the maintainers.
