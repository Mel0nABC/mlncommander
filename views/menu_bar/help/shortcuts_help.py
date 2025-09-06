# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


class ShortCutsHelp(Gtk.Window):

    def __init__(self, win):
        super().__init__(transient_for=win)
        header = Gtk.HeaderBar()
        header.set_title_widget(
            Gtk.Label(label=_("Descripción de los atajos de teclado"))
        )

        self.get_style_context().add_class("app_background")
        self.get_style_context().add_class("font")
        self.get_style_context().add_class("font-color")

        self.set_titlebar(header)
        self.set_size_request(300, 300)
        self.present()
