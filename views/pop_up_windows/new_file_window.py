# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from utilities.utilities_for_window import UtilsForWindow
from controls.actions import Actions
from pathlib import Path
import asyncio
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


class NewFileWindow(Gtk.Window):
    def __init__(
        self,
        parent: Gtk.ApplicationWindow,
        src_dir: "Explorer",  # noqa: F821
        new_file: "NewFile",  # noqa: F821
    ):
        super().__init__(transient_for=parent, modal=True, decorated=False)

        UtilsForWindow().set_event_key_to_close(self, self)

        # Load css

        self.get_style_context().add_class("app_background")
        self.get_style_context().add_class("font")
        self.get_style_context().add_class("font-color")

        horizontal = parent.horizontal

        self.set_default_size(horizontal / 10, -1)

        self.actions = Actions()
        self.win = parent
        self.new_file = new_file
        self.src_dir = src_dir

        vertical_box_info = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )

        vertical_box_info.set_hexpand(True)
        vertical_box_info.set_vexpand(True)
        vertical_box_info.set_margin_top(20)
        vertical_box_info.set_margin_start(20)
        vertical_box_info.set_margin_end(20)

        horizontal_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        name_label = Gtk.Label.new(_("Nuevo archivo"))
        name_label.set_margin_bottom(10)

        vertical_box_info.append(name_label)
        self.entry_file_name = Gtk.Entry()
        self.entry_file_name.connect("activate", self.get_selected_option)
        self.entry_file_name.set_hexpand(True)

        horizontal_box.append(self.entry_file_name)
        # Extension list
        extensions = [
            "*.docx",  # Office Word
            "*.odt",  # libreoffice word
            "*.xlsx",  # Office Spreadsheets
            "*.ods",  # libreoffice Spreadsheets
            "*.txt",  # Plain text / RTF
            "*.csv",  # Tabular data
        ]

        extension_list = Gtk.StringList.new(extensions)
        self.extension_drop_down = Gtk.DropDown(model=extension_list)
        self.extension_drop_down.set_selected(0)
        horizontal_box.append(self.extension_drop_down)

        vertical_box_info.append(horizontal_box)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_margin_top(10)
        button_box.set_hexpand(True)
        button_box.set_halign(Gtk.Align.END)

        self.btn_accept = Gtk.Button(label=_("Aceptar"))
        self.btn_cancel = Gtk.Button(label=_("Cancelar"))

        self.btn_accept.connect("clicked", self.get_selected_option)
        self.btn_cancel.connect("clicked", self.exit)

        self.vertical_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )

        self.vertical_box.set_margin_top(20)
        self.vertical_box.set_margin_start(20)
        self.vertical_box.set_margin_end(20)

        button_box.append(self.btn_accept)
        button_box.append(self.btn_cancel)

        vertical_box_info.append(button_box)
        vertical_box_info.append(self.vertical_box)

        self.set_child(vertical_box_info)

        self.response_text = None
        self.future = asyncio.get_event_loop().create_future()

        self.present()

    def get_selected_option(self, botton: Gtk.Button) -> None:
        """
        On accept or press enter in entry, we confirm new name
        """
        self.response_text = self.entry_file_name.get_text()

        if not self.response_text:
            self.actions.show_msg_alert(
                self.win, "Debe indicar un nombre de un archivo."
            )
            return

        ext_name = (
            self.extension_drop_down.get_selected_item()
            .get_string()
            .lstrip("*")
        )
        file_name = f"{self.response_text}{ext_name}"

        path = Path(f"{self.src_dir.actual_path}/{file_name}")

        if path.exists():
            self.actions.show_msg_alert(self.win, _("El archivo ya existe."))
            return

        response = self.new_file.create_new_file(path)

        if not response:
            self.actions.show_msg_alert(
                self.win,
                _("Ha surgido algún problema al crear el archivo."),
            )
            return
        self.exit()
        self.src_dir.load_new_path(self.src_dir.actual_path)
        self.actions.set_explorer_to_focused(self.src_dir, self.win)

    def exit(self, botton: Gtk.Button = None) -> None:
        self.destroy()
