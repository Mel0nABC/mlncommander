# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from controls.actions import Actions
from pathlib import Path
from views.pop_up_windows.rename_window import RenameWindow
from views.file_explorer.explorer import Explorer
import gi
import os
import asyncio
from asyncio import Future
import threading

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk  # noqa: E402


class Rename_Logic:

    def __init__(self):
        print("OBJETO RENAME")
        self.response = None
        self.action = Actions()

    def on_rename(
        self, explorer_src: Explorer, parent: Gtk.ApplicationWindow
    ) -> None:
        """
        Rename file or directory
        """
        print("ON RENAME")
        if not explorer_src:
            self.action.show_msg_alert(
                parent,
                """Debe seleccionar un archivo o carpeta
                 antes de intentar copiar.""",
            )
            return

        selected_items = explorer_src.get_selected_items_from_explorer()[1]

        if not selected_items:
            self.action.show_msg_alert(
                parent,
                """Debe seleccionar un archivo o carpeta
                 antes de intentar copiar.""",
            )
            return

        self.iterator_thread = threading.Thread(
            target=self.iterator_items,
            args=(parent, selected_items, explorer_src),
        )
        self.iterator_thread.start()

    def iterator_items(
        self,
        parent: Gtk.ApplicationWindow,
        selected_items: list,
        explorer_src: Explorer,
    ) -> None:
        """
        Allows multiple name changes
        """
        for src_info in selected_items:
            self.wait_event = threading.Event()

            def run_window(parent, src_info):
                asyncio.ensure_future(
                    self.create_response_window(parent, src_info)
                )

            GLib.idle_add(run_window, parent, src_info)
            self.wait_event.wait()

            if self.response is None or self.response == src_info.name:
                return

            if not self.response == src_info.name:
                new_path = Path(f"{src_info.parent}/{self.response}")
                if new_path.exists():
                    text = f"El archivo con nombre {new_path.name}, ya existe."
                    GLib.idle_add(self.action.show_msg_alert, parent, _(text))
                    continue
                os.rename(src_info, new_path)
                explorer_src.insert_log_line("RENAMED", src_info, new_path)

        GLib.idle_add(explorer_src.load_new_path, explorer_src.actual_path)
        GLib.idle_add(
            explorer_src.scroll_to,
            explorer_src.n_row,
            None,
            explorer_src.flags,
        )

    async def create_response_window(
        self, parent: Gtk.ApplicationWindow, src_info: Path
    ) -> None:
        """
        Create window to set new name
        """
        self.response = await self.create_rename_window(parent, src_info)
        self.wait_event.set()

    async def create_rename_window(
        self, parent: Gtk.ApplicationWindow, src_info: Path
    ) -> Future[str]:
        """
        Window rename
        """
        rename_window = RenameWindow(parent, str(src_info))
        return await rename_window.wait_response_async()
