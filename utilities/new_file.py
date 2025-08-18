# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from controls.Actions import Actions
from pathlib import Path
from views.new_file_dialog import NewFileDialog
from views.explorer import Explorer
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

        self.new_file = NewFileDialog(self.win, explorer_src, self)

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
            return True

        return True
