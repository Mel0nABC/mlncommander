# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from pathlib import Path
from controls.actions import Actions
import time
import gi  # noqa: F401

from gi.repository import Gtk, GLib, Gio


class LogManager:

    def __init__(self, win: Gtk.ApplicationWindow):
        self.win = win
        self.action = Actions()
        from views.main_window import Window
        self.APP_USER_PATH = Window.APP_USER_PATH
        self.log_file = Path(f"{self.APP_USER_PATH}/log/mlncommander.log")
        self.date_str = time.strftime("%A, %d/%m/%Y - %H:%M:%S")

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
        self, operation: str,
        src_path: Path = None,
        dst_path: Path = None,
        propertyList: Gio.ListStore = None
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
                elif (operation == "DELETED" or operation == "CREATED"):
                    row = _(f"{operation}: {self.date_str} -- {src_path} \n")
                elif (operation == "PERMISSIONS"):
                    for item in propertyList:
                        row = _(
                                f"{operation}: {self.date_str} -- {item.path}:\n"  # noqa: E501
                                f"\t\tPERMISSIONS: {item.old_permissions} to {item.permissions}\n"  # noqa: E501
                                )
                elif (operation == "OWNER_GROUP"):
                    for item in propertyList:
                        row = _(
                                f"{operation}: {self.date_str} -- {item.path}:\n"  # noqa: E501
                                f"\t\tOWNER: {item.old_user_name} to {item.user_name}\n"  # noqa: E501
                                f"\t\tGROUP: {item.old_group_name} to {item.group_name}\n"  # noqa: E501
                                )

                file.write(row)
        except Exception as e:
            text = _("Algún problema ha ocurrido")
            print(f"{text}: {e}")
