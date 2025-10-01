# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from utilities.utilities_for_window import UtilsForWindow
from pathlib import Path
import App
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


class About(Gtk.Window):

    def __init__(self, win):
        super().__init__(transient_for=win)

        UtilsForWindow().set_event_key_to_close(self, self)

        self.win = win

        from utilities.screen_info import ScreenInfo

        self.horizontal = ScreenInfo.horizontal
        self.vertical = ScreenInfo.vertical

        height_percent = self.vertical / 5

        header = Gtk.HeaderBar()
        header.set_title_widget(Gtk.Label(label=_("Acerca de mlnCommander")))
        self.set_titlebar(header)

        self.get_style_context().add_class("app_background")
        self.get_style_context().add_class("font")
        self.get_style_context().add_class("font-color")

        path = Path(f"{App.APP_HOME}/icons/mlncommander_transparente.png")

        img_preview = Gtk.Image.new_from_file(str(path))
        img_preview.set_pixel_size(height_percent)

        text_about = _(
            "MlnCommander\n\n"
            "Versión: 1.0\n\n"
            "Descripción:\n\n"
            "MlnCommander es un explorador de archivos de doble explorador\n"
            "que permite gestionar tus carpetas y archivos de manera rápida\n"
            "y eficiente. Con una interfaz sencilla y funcional, facilita operaciones\n"  # noqa :E501
            "comunes como copiar, mover y borrar archivos, al mismo tiempo que ofrece\n"  # noqa :E501
            "una vista dual para mejorar la productividad.\n\n"
            "Autor: MeL0nABC\n\n"
            "Licencia: MIT\n\n"
            "Sitio web del Proyecto: https://github.com/MeL0nABC/mlncommander\n\n"  # noqa :E501
        )

        lbl_text = Gtk.Label.new(_(text_about))

        horizontal_main = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=30
        )
        horizontal_main.set_margin_top(20)
        horizontal_main.set_margin_end(20)
        horizontal_main.set_margin_bottom(20)
        horizontal_main.set_margin_start(20)

        vertical_right = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )

        vertical_left = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        vertical_left.set_valign(Gtk.Align.CENTER)
        vertical_left.set_halign(Gtk.Align.CENTER)
        vertical_left.append(img_preview)

        vertical_right.append(lbl_text)
        horizontal_main.append(vertical_left)
        horizontal_main.append(vertical_right)

        license_btn = Gtk.Button.new_with_label(_("Licencia"))
        license_btn.connect("clicked", self.show_license)

        vertical_right.append(license_btn)

        self.set_child(horizontal_main)

        self.present()

    def show_license(self, button: Gtk.Button = None):
        win = Gtk.Window.new()
        header = Gtk.HeaderBar()
        header.set_title_widget(Gtk.Label(label=_("Licencias")))

        win.get_style_context().add_class("app_background")
        win.get_style_context().add_class("font")
        win.get_style_context().add_class("font-color")

        win.set_titlebar(header)
        win.set_transient_for(self)

        vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vertical_box.set_margin_top(20)
        vertical_box.set_margin_end(20)
        vertical_box.set_margin_bottom(20)
        vertical_box.set_margin_start(20)
        vertical_box.set_size_request(1024, 768)

        win.set_child(vertical_box)
        win.present()

        scroll = Gtk.ScrolledWindow.new()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)

        text_view = Gtk.TextView.new()
        text_view.set_editable(False)
        text_buffer = text_view.get_buffer()

        scroll.set_child(text_view)
        vertical_box.append(scroll)

        license_path = Path(f"{App.APP_HOME}/LICENSES/")

        text = ""

        with open(f"{license_path}/MIT.txt", "r") as file:
            text += file.read()

        text += (
            "\n\n\n\n##########################################"
            "##################################################"
            "#####################\n\n\n\n"
        )

        for license in license_path.iterdir():
            with open(license, "r") as file:
                if not file == "MIT.txt":
                    text += file.read()

            text += (
                "\n\n\n\n##########################################"
                "##################################################"
                "#####################\n\n\n\n"
            )

        text_buffer.set_text(text)
