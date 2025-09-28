# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from controls.actions import Actions
from pathlib import Path

# from functools import partial
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib, Pango, Gdk  # noqa E402


class PathBar(Gtk.Box):

    def __init__(
        self, entry_margin: int, path_text: str, explorer: Gtk.ColumnView
    ):
        super().__init__()

        self.action = Actions()
        self.explorer = explorer

        self.set_hexpand(True)
        self.entry_margin = entry_margin

        self.searchEntry = Gtk.SearchEntry()
        self.searchEntry.set_hexpand(True)
        self.searchEntry.set_text(path_text)
        self.searchEntry.set_focusable(False)
        self.searchEntry.set_margin_end(self.entry_margin / 2)
        self.searchEntry.set_margin_bottom(self.entry_margin)
        self.searchEntry.set_margin_start(self.entry_margin)
        self.searchEntry.get_style_context().add_class("entry")

        self.append(self.searchEntry)

        self.searchEntry.connect(
            "activate", self.action.entry_change_path, self.explorer
        )

    def search_started(self, searchEntry, explorer):

        folder_search = searchEntry.get_text().split("/")[-1]
        list_content_path = Path(explorer.actual_path).iterdir()

        menu = Gio.Menu()

        dir_list = [
            menu.append(str(item))
            for item in list_content_path
            if item.is_dir()
            if folder_search in str(item)
        ]

        popoveroptions = Gtk.PopoverMenu.new_from_model(menu)
        popoveroptions.set_parent(searchEntry)
        popoveroptions.popup()

        searchEntry.grab_focus()

        print(dir_list)
        print(folder_search)

    # self.searchEntry.connect(
    #     "search-changed", partial(search_started, explorer=self.explorer_1)
    # )
