# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from controls.actions import Actions
from pathlib import Path
from functools import partial
import os
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib, Pango, Gdk  # noqa E402


class PathBar(Gtk.Box):

    def __init__(
        self,
        win: Gtk.ApplicationWindow,
        entry_margin: int,
        path_text: str,
        explorer: Gtk.ColumnView,
    ):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self._ESCAPE = Gdk.keyval_name(Gdk.KEY_Escape)  # Escape
        self._KEY_DOWN = Gdk.keyval_name(Gdk.KEY_Down)  # Arrow down
        self.OS_SEP = os.sep

        self.win = win
        self.action = Actions()
        self.explorer = explorer
        self.menu = Gio.Menu()
        self.action_list: list[int] = []
        self.last_entry_total_chars = 0
        self.actual_path_temp = self.explorer.actual_path

        self.set_hexpand(True)
        self.entry_margin = entry_margin

        if explorer.name == "explorer_1":
            start_margin = self.entry_margin
            end_margin = self.entry_margin / 2
        else:
            start_margin = self.entry_margin / 2
            end_margin = self.entry_margin

        self.search_entry = Gtk.SearchEntry.new()
        self.search_entry.set_hexpand(True)
        self.search_entry.set_focusable(False)
        self.search_entry.set_margin_end(end_margin)
        self.search_entry.set_margin_bottom(self.entry_margin)
        self.search_entry.set_margin_start(start_margin)
        self.search_entry.get_style_context().add_class("entry")

        self.search_entry.set_editable(True)
        self.search_entry.set_can_target(True)
        self.search_entry.set_sensitive(True)

        self.append(self.search_entry)

        self.search_popover = Gtk.PopoverMenu.new_from_model()
        self.search_popover.get_style_context().add_class("contextual_menu")

        # Signal section

        # search_entry

        self.search_entry.connect(
            "activate", self.action.entry_change_path, self.explorer
        )

        self.on_changed_int = None

        focus_event_enter = Gtk.EventControllerFocus()
        focus_event_enter.connect(
            "enter",
            partial(self.add_backslash),
        )
        self.search_entry.add_controller(focus_event_enter)

        focus_event_enter = Gtk.EventControllerFocus()
        focus_event_enter.connect(
            "leave",
            partial(self.search_leave, explorer=self.explorer),
        )
        self.search_entry.add_controller(focus_event_enter)

        def on_key_press(
            controller: Gtk.EventControllerKey,
            keyval: int,
            keycode: int,
            state: Gdk.ModifierType,
        ) -> None:
            key_pressed_name = Gdk.keyval_name(keyval)

            if key_pressed_name == self._ESCAPE:
                self.explorer.grab_focus()
                return

            if key_pressed_name == self._KEY_DOWN:

                if not self.search_popover.has_focus():
                    self.search_popover.grab_focus()

        self.key_controller = Gtk.EventControllerKey.new()
        self.key_controller_id = self.key_controller.connect(
            "key-pressed", on_key_press
        )
        self.search_entry.add_controller(self.key_controller)

    def add_backslash(self, controller: Gtk.EventControllerFocus) -> None:
        if self.search_entry.get_text()[-1] != "/":
            self.change_entry_text(f"{self.search_entry.get_text()}/")

        self.win.key_disconnect()

    def on_changed(
        self, widget: Gtk.SearchEntry, explorer: Gtk.ColumnView
    ) -> None:

        entry_text = self.search_entry.get_text()
        new_text = entry_text.replace(f"{self.actual_path_temp}", "")
        new_text = new_text.replace("/", "")

        if not new_text:
            self.search_popover.popdown()
            self.last_entry_total_chars = 0
            return

        try:
            search = Path(entry_text).parent.iterdir()

            if entry_text[-1] == "/":
                self.search_popover.popdown()
                self.actual_path_temp = entry_text
                return

            list_dir_content = [
                item
                for item in search
                if item.is_dir() and new_text.lower() in str(item).lower()
            ]

        except FileNotFoundError:
            print("Except")
            return

        width = self.search_entry.get_width()

        startswith_list = [
            path.name
            for path in list_dir_content
            if path.name.lower().startswith(new_text.lower())
        ]

        if not startswith_list:
            return

        startswith_list.sort()

        if startswith_list:
            folder = startswith_list[0]
        else:
            folder = ""

        if self.actual_path_temp == Path("/"):
            path = Path(f"{self.actual_path_temp}{folder}")
        else:
            path = Path(f"{self.actual_path_temp}/{folder}")

        if self.last_entry_total_chars:
            if self.last_entry_total_chars >= len(entry_text):
                self.last_entry_total_chars = len(entry_text)
                return

        self.last_entry_total_chars = len(entry_text)

        position = self.search_entry.get_position()
        characters = self.search_entry.get_max_width_chars()

        if path.exists():
            self.change_entry_text(str(path))
            self.search_entry.select_region(position, characters)

        self.menu.remove_all()

        self.search_popover.set_menu_model(self.menu)

        for folder in startswith_list:
            folder_filtered = folder
            if "_" in folder:
                folder_filtered = folder.replace("_", "__")

            self.menu.append(folder_filtered, f"win.{folder}")
            action = Gio.SimpleAction.new(str(folder), None)
            action_id = action.connect(
                "activate", partial(self.menu_action, folder)
            )
            self.win.add_action(action)
            self.action_list.append(action_id)

        if startswith_list:
            self.search_popover.set_size_request(width + 20, 0)
            self.search_popover.set_has_arrow(False)
            self.search_popover.set_parent(self.search_entry)
            self.search_popover.set_autohide(False)
            self.search_popover.set_focusable(True)
            self.search_popover.popup()
        else:
            self.search_popover.popdown()
            self.last_entry_total_chars = 0

    def search_leave(
        self,
        controller: Gtk.EventControllerFocus,
        explorer: Gtk.ColumnView,
    ) -> None:
        self.action.set_explorer_to_focused(explorer, self.win)
        self.change_entry_text(str(self.explorer.actual_path))
        self.search_popover.popdown()
        self.last_entry_total_chars = 0
        self.win.key_connect()

    def menu_action(
        self,
        folder_path: Path,
        action: Gio.SimpleAction,
        parameter: any = None,
    ) -> None:

        if self.actual_path_temp == Path("/"):
            path = Path(f"{self.actual_path_temp}{folder_path}")
        else:
            path = Path(f"{self.actual_path_temp}/{folder_path}")

        self.change_entry_text(f"{str(path)}/")
        self.search_entry.set_position(-1)

    def change_entry_text(self, new_text: str, *args) -> None:

        if self.on_changed_int:
            self.search_entry.disconnect(self.on_changed_int)
            self.on_changed_int = None

        self.search_entry.set_text(new_text)

        if not self.on_changed_int:
            self.on_changed_int = self.search_entry.connect(
                "changed",
                partial(self.on_changed, explorer=self.explorer),
            )
