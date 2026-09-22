"""Windows global hotkeys for controlling the desktop-only overlay."""

from __future__ import annotations

import ctypes
import ctypes.wintypes
from collections.abc import Callable

from PySide6.QtCore import QAbstractNativeEventFilter, QByteArray


WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
VK_F8 = 0x77
VK_F9 = 0x78
VK_Q = 0x51


class GlobalHotkeys(QAbstractNativeEventFilter):
    """Register app-only global hotkeys through the Windows API."""

    def __init__(self, on_hud_toggle: Callable[[], None], on_lock_toggle: Callable[[], None], on_quit: Callable[[], None]) -> None:
        super().__init__()
        self._on_hud_toggle = on_hud_toggle
        self._on_lock_toggle = on_lock_toggle
        self._on_quit = on_quit
        self._user32 = ctypes.windll.user32
        self._registered: list[int] = []

    def register(self) -> None:
        hotkeys = (
            (1, 0, VK_F8, self._on_hud_toggle),
            (2, 0, VK_F9, self._on_lock_toggle),
            (3, MOD_CONTROL | MOD_ALT, VK_Q, self._on_quit),
        )
        for hotkey_id, modifiers, key, _ in hotkeys:
            if self._user32.RegisterHotKey(None, hotkey_id, modifiers, key):
                self._registered.append(hotkey_id)

    def unregister(self) -> None:
        for hotkey_id in self._registered:
            self._user32.UnregisterHotKey(None, hotkey_id)
        self._registered.clear()

    def nativeEventFilter(self, event_type: QByteArray, message: object) -> tuple[bool, int]:
        if event_type not in (b"windows_generic_MSG", b"windows_dispatcher_MSG"):
            return False, 0
        try:
            message_address = int(message)  # type: ignore[arg-type]
            msg = ctypes.wintypes.MSG.from_address(message_address)
        except (TypeError, ValueError):
            return False, 0
        if msg.message != WM_HOTKEY:
            return False, 0
        callbacks = {1: self._on_hud_toggle, 2: self._on_lock_toggle, 3: self._on_quit}
        callback = callbacks.get(int(msg.wParam))
        if callback is not None:
            callback()
            return True, 0
        return False, 0


__all__ = ["GlobalHotkeys"]
