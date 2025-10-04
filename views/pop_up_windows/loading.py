# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
import gi
from gi.repository import Gtk


gi.require_version("Gtk", "4.0")


class Loading(Gtk.Window):
    def __init__(
        self,
        parent: Gtk.ApplicationWindow,
    ):
        super().__init__(transient_for=parent, modal=True, decorated=False)

        # Load css

        self.get_style_context().add_class("app_background")
        self.get_style_context().add_class("font")
        self.get_style_context().add_class("font-color")

        self.set_size_request(100, 100)

        self.spinner = Gtk.Spinner.new()
        self.set_child(self.spinner)

    def start(self) -> None:
        self.spinner.start()
        self.present()

    def stop(self) -> None:
        self.spinner.stop()
        self.destroy()
