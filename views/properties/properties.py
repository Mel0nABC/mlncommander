# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from views.properties.permissions import Permissions
from views.properties.information import Information
from utilities.screen_info import ScreenInfo
import gi
from gi.repository import Gtk, Gio, Gdk, GLib, GObject  # noqa E402

gi.require_version("Gtk", "4.0")


class Properties(Gtk.Window):
    def __init__(self, win: Gtk.Window, path_list: list):
        super().__init__()

        header = Gtk.HeaderBar()
        header.set_title_widget(
            Gtk.Label(label=_("Propiedades de archivos y carpetas"))
        )
        self.set_size_request(
            ScreenInfo.horizontal * 0.33, ScreenInfo.vertical * 0.6
        )

        self.set_titlebar(header)

        self.set_vexpand(True)
        self.set_hexpand(True)
        self.set_resizable(True)

        self.win = win
        self.path_list = path_list

        main_vertical_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5
        )
        main_vertical_box.set_margin_top(20)
        main_vertical_box.set_margin_end(20)
        main_vertical_box.set_margin_bottom(20)
        main_vertical_box.set_margin_start(20)

        notebook = Gtk.Notebook.new()

        information = Information(self, self.path_list)

        permissions = Permissions(self, self.path_list, information)

        notebook.append_page(information, Gtk.Label.new(_("Información")))
        notebook.append_page(permissions, Gtk.Label.new(_("Permisos")))

        main_vertical_box.append(notebook)

        self.set_child(main_vertical_box)

        # Load css

        self.get_style_context().add_class("app_background")
        self.get_style_context().add_class("font")
        self.get_style_context().add_class("font-color")

        self.present()

        def on_unrealize(widget: Gtk.Window) -> None:
            explorer_1 = self.win.explorer_1
            explorer_2 = self.win.explorer_2

            explorer_1.load_new_path(explorer_1.actual_path)
            explorer_2.load_new_path(explorer_2.actual_path)

        self.connect("unrealize", on_unrealize)
