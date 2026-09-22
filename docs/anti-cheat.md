# Anti-cheat review notes

This technical description is provided so competitive platforms can independently evaluate the software. It is not a claim of authorization.

| Capability                  | Used |
| --------------------------- | ---- |
| Screen capture              | Yes  |
| CS2 process access          | No   |
| CS2 memory access           | No   |
| DLL injection               | No   |
| Game file modification      | No   |
| Entity detection            | No   |
| Player position extraction  | No   |
| Input automation            | No   |
| Network interception        | No   |
| Additional game information | No   |

## What the software does

The application captures a configurable desktop region, stores the pixel data, and re-renders it in a transparent overlay window. This operation is purely visual and does not infer anything about the game state.

## What the software does not do

This project does not:

- read CS2 process memory
- access the CS2 process itself
- inspect network packets
- read game files or configuration
- inject code or hook game APIs
- parse entity positions
- automate keyboard or mouse input
- modify CS2 content or files
- attempt to bypass anti-cheat controls

## Scope statement

The project intentionally remains in the realm of pixel capture and display. Any request to read internal game state, automate gameplay, or interact with the CS2 process is outside the defined scope of this software.
