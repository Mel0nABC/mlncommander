# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from functools import partial
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk  # noqa: E402


class UtilsForWindow:

    def set_event_key_to_close(
        self, to_close: Gtk.Window, to_set_event: Gtk.Widget
    ) -> None:

        _ESCAPE = Gdk.keyval_name(Gdk.KEY_Escape)  # Escape

        def on_key_pressed(
            to_close: Gtk.Window,
            event: Gtk.EventControllerKey,
            keyval: int,
            keycode: int,
            state: Gdk.ModifierType,
        ) -> None:
            key_pressed_name = Gdk.keyval_name(keyval)
            if key_pressed_name == _ESCAPE:
                to_close.destroy()

        event_key = Gtk.EventControllerKey.new()
        event_key.connect("key_pressed", partial(on_key_pressed, to_close))
        to_set_event.add_controller(event_key)
