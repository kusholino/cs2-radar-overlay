# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-09-22

### Added

- multi-monitor virtual-desktop calibration, including negative coordinates
- editable existing configurations with `--edit`
- named presets with `--preset`
- circle overlay mode and live calibration preview
- global overlay hotkeys for HUD, lock, and quit controls
- resilient `mss` to `ImageGrab` capture fallback

### Fixed

- repeated capture tracebacks when Windows `BitBlt` fails
- Windows native hotkey event pointer handling

## [0.1.0] - 2026-09-22

### Added

- initial desktop capture and overlay prototype
- configurable capture region and overlay geometry
- click-through and always-on-top window options
- configuration parsing via TOML
- basic performance tracking metadata
- documentation and CI workflow
- automated tests for configuration and validation behavior
