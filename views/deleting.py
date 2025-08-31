# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from pathlib import Path
import gi
import asyncio

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Pango  # noqa: E402


class Deleting(Gtk.Window):

    def __init__(self, parent: Gtk.ApplicationWindow, src_info: Path):
        super().__init__(
            title=_("Eliminando  .."),
            transient_for=parent,
            modal=True,
        )
        self.src_info = src_info
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(self.box)
        self.set_default_size(500, 60)

        self.lbl_src = Gtk.Label(label="SRC")
        self.lbl_src.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        self.lbl_src.set_halign(Gtk.Align.START)
        self.lbl_src.set_margin_top(20)
        self.lbl_src.set_margin_end(20)
        self.lbl_src.set_margin_start(20)

        self.btn_cancel = Gtk.Button(label=_("Cancelar"))
        self.btn_cancel.connect("clicked", self.cancel_deleting)
        self.btn_cancel.set_margin_top(20)
        self.btn_cancel.set_margin_end(20)
        self.btn_cancel.set_margin_bottom(20)
        self.btn_cancel.set_margin_start(20)

        self.box.append(self.lbl_src)
        self.box.append(self.btn_cancel)

        self.dialog_response = False
        self.future = asyncio.get_event_loop().create_future()

        self.present()

    def update_labels(self, deleting_file: Path) -> None:
        """
        Force update labels with real information
        """
        try:
            self.lbl_src.set_text(str(deleting_file))
        except Exception:
            self.lbl_src.set_text(str(self.src_info))

    def cancel_deleting(self, button: Gtk.Button) -> None:
        """
        Close dialog and return False
        """
        self.dialog_response = False

    def finish_deleting(self) -> None:
        """
        Set response on close dialog
        """
        self.dialog_response = True
        if not self.future.done():
            self.future.set_result(self.dialog_response)

    async def wait_response_async(self) -> bool:
        """
        Response on close dialog
        """
        response = await self.future
        self.destroy()
        return response
