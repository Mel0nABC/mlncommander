# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.log_manager import LogManager
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time
import gi  # noqa: F401

from gi.repository import Gtk, GLib


class My_watchdog:
    def __init__(
        self,
        win: Gtk.ApplicationWindow,
        path: Path,
        APP_USER_PATH: Path,
        explorer: "Explorer" = None,  # noqa: F821
    ) -> None:
        self.observer = Observer()
        self.path = Path(path)
        self.APP_USER_PATH = APP_USER_PATH
        self.explorer = explorer
        self.mihandler = None
        self.win = win

    def start(self):
        """
        Initialize watchdog
        """

        self.mihandler = MiHandler(self.win, self.path, self.explorer)
        self.observer.schedule(
            self.mihandler,
            path=self.path,
            recursive=False,
        )
        self.observer.start()

        try:
            while self.observer.is_alive():
                time.sleep(0.1)
                if not self.explorer.actual_path.exists():
                    GLib.idle_add(
                        self.explorer.load_new_path, self.path.parent
                    )
                else:
                    self.mihandler.compare_folder()

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """
        Stop watchdog
        """
        self.observer.stop()
        self.observer.join()


class MiHandler(FileSystemEventHandler):
    """
    Control diferent events handler
    """

    def __init__(
        self,
        win: Gtk.ApplicationWindow,
        path: Path,
        explorer: "Explorer",  # noqa: F821
    ):

        self.win = win
        self.log_manager = LogManager(self.win)
        self.explorer = explorer
        self.path = Path(path)
        self.list_path1 = list(self.path.iterdir())

    def compare_folder(self):
        from collections import Counter

        if not self.path.exists():
            self.load_new_path(self.path.parent)
            return

        list_path2 = list(self.path.iterdir())

        if not Counter(self.list_path1) == Counter(list_path2):
            self.load_new_path(self.path)
            self.list_path1 = list(self.path.iterdir())

    # def dispatch(self, event):
    #     print(event)
    #     self.last_event = event

    # def on_created(self, event) -> None:
    #     self.log_manager.print_status_on_log(_("CREADO"), event.src_path)
    #     self.load_new_path(self.path)

    # def on_deleted(self, event) -> None:
    #     self.log_manager.print_status_on_log(_("BORRADO"), event.src_path)
    #     self.load_new_path(self.path)

    # def on_modified(self, event) -> None:
    #     self.log_manager.print_status_on_log(_("MODIFICADO"), event.src_path)
    #     self.load_new_path(self.path)

    # def on_moved(self, event) -> None:
    #     self.log_manager.print_status_on_log(_("MOVIDO"), event.src_path)
    #     self.load_new_path(self.path)

    def load_new_path(self, path):
        path = Path(path)
        if path.exists():
            GLib.idle_add(self.explorer.load_new_path, path)
