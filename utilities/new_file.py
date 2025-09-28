# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from controls.actions import Actions
from pathlib import Path
from views.pop_up_windows.new_file_window import NewFileWindow
from views.mlncommander_explorer import Explorer
import gi
from utilities.access_control import AccessControl
from docx import Document  # docx
from odf.opendocument import (
    OpenDocumentText,
    OpenDocumentSpreadsheet,
)  # odt and ods
from openpyxl import Workbook  # xlsx

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


class NewFile:

    def __init__(self):
        self.response = None
        self.action = Actions()
        self.win = None
        self.new_file = None
        self.access_control = AccessControl()
        self.explorer_src = None

    def on_new_file(
        self, explorer_src: Explorer, win: Gtk.ApplicationWindow
    ) -> None:
        self.win = win

        """
        Open screen to create new file
        """

        if not explorer_src:
            self.action.show_msg_alert(
                win,
                (
                    _(
                        "Debe estar en un explorador antes"
                        " de poder crear el archivo"
                    )
                ),
            )
            return

        response = self.access_control.validate_src_write_unit(
            explorer_src.actual_path, self.win
        )

        if not response:
            return
        self.explorer_src = explorer_src
        self.new_file = NewFileWindow(self.win, explorer_src, self)

    def create_new_file(self, path: Path) -> bool:
        """
        Create new file
        """
        if path.exists():
            return False

        ext = path.suffix

        if ext == ".txt" or ext == ".csv":
            path.write_text("\n")

        if ext == ".docx":
            doc = Document()
            doc.save(path)

        if ext == ".odt":
            doc = OpenDocumentText()
            doc.save(path)

        if ext == ".xlsx":
            wb = Workbook()
            wb.save(path)

        if ext == ".ods":
            doc = OpenDocumentSpreadsheet()
            doc.save(path)

        if path.exists():
            self.explorer_src.insert_log_line("CREATED", path, None)
            return True

        return True
