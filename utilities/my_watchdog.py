# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
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

        self.mihandler = MiHandler(
            self.win, self.path, self.explorer, self.APP_USER_PATH
        )
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
        APP_USER_PATH: Path,
    ):
        from controls.actions import Actions

        self.win = win
        self.explorer = explorer
        self.path = Path(path)
        self.list_path1 = list(self.path.iterdir())
        self.log_file = Path(f"{APP_USER_PATH}/log/mlncommander.log")
        self.date_str = time.strftime("%A, %d/%m/%Y - %H:%M:%S")
        self.action = Actions()

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
    #     self.print_status_on_log(_("CREADO"), event.src_path)
    #     self.load_new_path(self.path)

    # def on_deleted(self, event) -> None:
    #     self.print_status_on_log(_("BORRADO"), event.src_path)
    #     self.load_new_path(self.path)

    # def on_modified(self, event) -> None:
    #     self.print_status_on_log(_("MODIFICADO"), event.src_path)
    #     self.load_new_path(self.path)

    # def on_moved(self, event) -> None:
    #     self.print_status_on_log(_("MOVIDO"), event.src_path)
    #     self.load_new_path(self.path)

    def load_new_path(self, path):
        path = Path(path)
        if path.exists():
            GLib.idle_add(self.explorer.load_new_path, path)

    def print_title_on_log(self) -> bool:
        try:

            if not self.log_file.parent.exists():
                self.log_file.parent.mkdir()

            if not self.log_file.exists():

                self.log_file.write_text(
                    _(
                        "##################################################\n"
                        "########## INICIALIZANDO ARCHIVO  DE LOG #########\n"
                        "##################################################\n"
                        f"######## {self.date_str}  ########\n"
                        "##################################################\n"
                    )
                )
            return True
        except Exception as e:
            print(f"ERROR: {e}")
            if not self.win.write_error_msg_displayer:
                GLib.idle_add(
                    self.action.show_msg_alert,
                    self.win,
                    _(("Error al escribir el log\n\n" f"{e}")),
                )
                self.win.write_error_msg_displayer = True
            return False

    def print_status_on_log(
        self, operation: str, src_path: Path, dst_path: Path = None
    ) -> None:

        if not self.print_title_on_log():
            return

        try:

            with open(self.log_file, "a", encoding="utf-8") as file:
                if (
                    operation == "RENAMED"
                    or operation == "COPIED"
                    or operation == "MOVED"
                    or operation == "DUPLICATED"
                ):
                    row = _(
                        f"{operation}: {self.date_str} -- {src_path} to {dst_path}\n"  # noqa: E501
                    )
                else:
                    # DELETED, CREATED
                    row = _(f"{operation}: {self.date_str} -- {src_path} \n")
                file.write(row)
        except Exception as e:
            text = _("Algún problema ha ocurrido")
            print(f"{text}: {e}")
