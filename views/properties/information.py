# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from utilities.screen_info import ScreenInfo
import gi
from gi.repository import Gtk

gi.require_version("Gtk", "4.0")


class Information:

    def __init__(self):
        self.hola = _("hola")

    def create_information(self) -> Gtk.Box:

        self.information_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5
        )

        self.information_box.append(
            Gtk.Label.new("INFORMACION ARCHIVOS Y CARPETAS")
        )

        ScreenInfo.horizontal

        self.information_box.set_size_request(1024, ScreenInfo.vertical * 0.6)
        self.information_box.set_margin_top(20)
        self.information_box.set_margin_end(20)
        self.information_box.set_margin_bottom(20)
        self.information_box.set_margin_start(20)

        return self.information_box
