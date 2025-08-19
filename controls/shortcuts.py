# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from entity.shortcut import Shortcut
import json
import gi


gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Gio, GLib, Pango, GObject  # noqa E402


class Shortcuts_keys:

    def __init__(self, win: Gtk.Window, explorer: "Explorer"):  # noqa F821

        from views.main_window import Window

        self.SHORTCUT_FILE = f"{Window.APP_USER_PATH}/shorcuts_file.json"

        self.win = win
        self.explorer = explorer

        self.shortcuts_dict = [
            Shortcut(explorer, "<Control>", "o", "shortcut_mirroring_folder"),
            Shortcut(explorer, "<Control>", "p", "unzip_file"),
            Shortcut(explorer, "<Control>", "i", "zip_file"),
        ]
        self.save_json_config()

        for shortcut in self.load_json_config():
            method = getattr(self, shortcut.method)
            self.add_shortcut(
                self.explorer, shortcut.first_key, shortcut.second_key, method
            )

    def load_json_config(self) -> list:
        with open(self.SHORTCUT_FILE, "r") as file:
            data = json.load(file)
            return [
                Shortcut(
                    self.explorer, d["first_key"], d["second_key"], d["method"]
                )
                for d in data
            ]

    def save_json_config(self):

        with open(self.SHORTCUT_FILE, "w") as file:
            json.dump(
                [s.to_dict() for s in self.shortcuts_dict], file, indent=4
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
        self.shortcut = Gtk.Shortcut.new(trigger, action)
        controller = Gtk.ShortcutController.new()
        controller.add_shortcut(self.shortcut)
        explorer.add_controller(controller)

    def shortcut_mirroring_folder(self, *args) -> None:
        """
        Actions when shortcuts is utilized
        """
        # Disconnect key controller from main window
        self.win.key_controller.disconnect(self.win.key_controller_id)

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

        GLib.idle_add(self.explorer._reeconnect_controller)

    def unzip_file(self, *args):
        # Disconnect key controller from main window
        self.win.key_controller.disconnect(self.win.key_controller_id)
        print("UNZIP")
        GLib.idle_add(self.explorer._reeconnect_controller)

    def zip_file(self, *args):
        # Disconnect key controller from main window
        self.win.key_controller.disconnect(self.win.key_controller_id)
        print("ZIP")
        GLib.idle_add(self.explorer._reeconnect_controller)
