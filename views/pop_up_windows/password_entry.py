# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from utilities.utilities_for_window import UtilsForWindow
from pathlib import Path
from multiprocessing import Queue
import gi

from gi.repository import Gtk

gi.require_version("Gtk", "4.0")


class PasswordWindow(Gtk.Window):

    def __init__(self, win: Gtk.Window, to_work: Queue, file: Path):
        super().__init__(transient_for=win, modal=True, decorated=False)

        UtilsForWindow().set_event_key_to_close(self, self)

        # Load css

        self.get_style_context().add_class("app_background")
        self.get_style_context().add_class("font")
        self.get_style_context().add_class("font-color")

        self.result = None
        self.win = win
        self.to_work = to_work

        self.set_default_size(300, -1)

        vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vertical_box.set_margin_top(20)
        vertical_box.set_margin_end(20)
        vertical_box.set_margin_bottom(20)
        vertical_box.set_margin_start(20)

        self.set_child(vertical_box)

        src_label = Gtk.Label()
        src_label.set_text(str(file))
        src_label.set_margin_bottom(20)
        vertical_box.append(src_label)

        self.password = Gtk.PasswordEntry.new()
        self.password.connect("activate", self.on_accept)

        vertical_box.append(self.password)

        btn_accept = Gtk.Button(label=_("Aceptar"))
        btn_cancel = Gtk.Button(label=_("Cancel"))

        btn_accept.connect("clicked", self.on_accept)
        btn_cancel.connect("clicked", self.on_cancel)

        horizontal_button = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        horizontal_button.set_hexpand(True)
        horizontal_button.set_halign(Gtk.Align.CENTER)
        horizontal_button.set_margin_top(20)

        horizontal_button.append(btn_accept)
        horizontal_button.append(btn_cancel)

        vertical_box.append(horizontal_button)

        self.present()

    def on_accept(self, button: Gtk.Button):
        self.to_work.put({"status": True, "msg": self.password.get_text()})
        self.destroy()

    def on_cancel(self, button: Gtk.Button):
        self.to_work.put({"status": False, "msg": "Cancel"})
        self.destroy()
