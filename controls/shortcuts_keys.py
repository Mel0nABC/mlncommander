# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from pathlib import Path
from entity.shortcut import Shortcut
from utilities.access_control import AccessControl
from utilities.compression import CompressionManager
from controls.actions import Actions
import shutil
import yaml
import gi


gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib  # noqa E402


class Shortcuts_keys:

    def __init__(self, win: Gtk.Window, explorer: "Explorer"):  # noqa F821

        from views.main_window import Window

        self.win = win
        self.compression_manager = CompressionManager(self.win)
        self.explorer = explorer
        self.action = Actions()
        self.SHORTCUT_FILE = Path(f"{Window.APP_USER_PATH}/shorcuts_file.yaml")
        self.controller_list = []

        if not self.SHORTCUT_FILE.exists():
            self.reset_shortcuts_config()

        self.charge_yrml_shortcuts()

    def load_yaml_config(self) -> list:
        with open(self.SHORTCUT_FILE, "r") as file:
            data = yaml.safe_load(file)
            return [
                Shortcut(
                    self.explorer,
                    d["first_key"],
                    d["second_key"],
                    d["method"],
                    d["description"],
                )
                for d in data
            ]

    def save_yaml_config(self, shortcuts_list: list) -> None:
        with open(self.SHORTCUT_FILE, "w") as file:
            yaml.dump([s.to_dict() for s in shortcuts_list], file, indent=4)

    def recharge_yaml_shortcuts(self):

        for controller in self.controller_list:
            self.explorer.remove_controller(controller)

        self.charge_yrml_shortcuts()

    def charge_yrml_shortcuts(self):
        self.list_shortcuts = self.load_yaml_config()
        for shortcut in self.list_shortcuts:
            method = getattr(self, shortcut.method)
            self.add_shortcut(
                self.explorer, shortcut.first_key, shortcut.second_key, method
            )

    def add_shortcut(
        self,
        explorer: "Explorer",  # noqa F821
        first_key: str,
        second_key: str,
        method,
    ) -> None:
        trigger = Gtk.ShortcutTrigger.parse_string(f"{first_key}{second_key}")
        action = Gtk.CallbackAction.new(method)
        shortcut = Gtk.Shortcut.new(trigger, action)
        controller = Gtk.ShortcutController.new()
        controller.add_shortcut(shortcut)
        explorer.add_controller(controller)
        self.controller_list.append(controller)

    def shortcut_mirroring_folder(self, widget, args) -> None:
        """
        Actions when shortcuts is utilized
        """
        # Disconnect key controller from main window
        self.win.key_disconnect()

        # Returns the browser that does not contain the passed name
        other_explorer = self.win.get_other_explorer_with_name(
            self.explorer.name
        )

        if not other_explorer:
            return

        selected_item = self.explorer.get_selected_items_from_explorer()[1]

        if not selected_item:
            other_explorer.load_data(self.explorer.actual_path.parent)

        if not selected_item:
            path = self.explorer.actual_path.parent
        else:
            path = selected_item[0]

        if selected_item:
            if not path.is_dir():
                path = path.parent

        other_explorer.load_data(path)

        GLib.idle_add(self.win.key_connect)

    def validate_7zip_installed(self):
        if not shutil.which("7z"):
            text = _(
                "No dispone de 7zip instalado para poder usar esta función."
            )
            self.action.show_msg_alert(
                self.win,
                text,
            )
            return False

        return True

    def unzip_file(self, widget, args):

        exec_uncompress_window = True
        # Disconnect key controller from main window
        self.win.key_disconnect()

        if not self.validate_7zip_installed():
            return

        selected_items = self.explorer.get_selected_items_from_explorer()[1]
        dst_explorer = self.win.get_other_explorer_with_name(
            self.explorer.name
        )
        dst_dir = dst_explorer.actual_path

        if not self.compression_manager.get_dst_suficient_space(
            selected_items, dst_dir
        ):
            self.action.show_msg_alert(
                self.win, _("No hay suficiente espacio en el destino.")
            )
            exec_uncompress_window = False

        list_files = self.explorer.get_selected_items_from_explorer()[1]

        ac = AccessControl()

        write_access = ac.validate_dst_write(
            list_files, None, dst_explorer, dst_dir, self.win
        )

        if not write_access:
            exec_uncompress_window = False

        from views.uncompress import UncompressWindow

        if exec_uncompress_window:
            UncompressWindow(self.win, selected_items, dst_explorer, dst_dir)

    def zip_file(self, widget, args):

        exec_uncompress_window = True
        # Disconnect key controller from main window
        self.win.key_disconnect()

        if not self.validate_7zip_installed():
            return

        selected_items = self.explorer.get_selected_items_from_explorer()[1]
        dst_explorer = self.win.get_other_explorer_with_name(
            self.explorer.name
        )
        dst_dir = dst_explorer.actual_path

        from utilities.file_manager import File_manager

        list_files = self.explorer.get_selected_items_from_explorer()[1]

        fm = File_manager()

        if not fm.check_free_space(list_files, dst_dir):

            self.action.show_msg_alert(
                self.win, _("No hay suficiente espacio en el destino.")
            )
            exec_uncompress_window = False

        ac = AccessControl()

        write_access = ac.validate_dst_write(
            list_files, None, dst_explorer, dst_dir, self.win
        )

        if not write_access:
            exec_uncompress_window = False

        from views.compress import CompressWindow

        if exec_uncompress_window:
            CompressWindow(self.win, selected_items, dst_explorer, dst_dir)
        else:
            GLib.idle_add(self.win.key_connect)

    def reset_shortcuts_config(self):
        shortcuts_dict = [
            Shortcut(
                self.explorer,
                "<Control>",
                "o",
                "shortcut_mirroring_folder",
                _("Muestra la carpeta en el otro explorador."),
            ),
            Shortcut(
                self.explorer,
                "<Control>",
                "p",
                "unzip_file",
                _("Para descomprimir archivos"),
            ),
            Shortcut(
                self.explorer,
                "<Control>",
                "i",
                "zip_file",
                _("Para comprimir archivos"),
            ),
        ]
        self.save_yaml_config(shortcuts_dict)
