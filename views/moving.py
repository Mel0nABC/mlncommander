# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from pathlib import Path
import asyncio
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib  # noqa: E402


class Moving(Gtk.Dialog):

    def __init__(self, parent: Gtk.ApplicationWindow):
        super().__init__(
            title=_("Moviendo .."),
            transient_for=parent,
            modal=True,
        )
        self.src_info = None
        self.dst_info = None
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(self.box)
        self.set_default_size(500, 60)

        self.lbl_src = Gtk.Label(label="SRC")
        self.lbl_src.set_halign(Gtk.Align.START)
        self.lbl_src.set_margin_top(20)
        self.lbl_src.set_margin_end(20)
        self.lbl_src.set_margin_start(20)

        self.lbl_dst = Gtk.Label(label="DST")
        self.lbl_dst.set_halign(Gtk.Align.START)
        self.lbl_dst.set_margin_top(20)
        self.lbl_dst.set_margin_end(20)
        self.lbl_dst.set_margin_start(20)

        self.lbl_size = Gtk.Label(label="0 bytes")
        self.lbl_size.set_margin_top(20)
        self.lbl_size.set_margin_end(20)
        self.lbl_size.set_margin_start(20)

        self.btn_cancel = Gtk.Button(label=_("Cancelar"))
        self.btn_cancel.connect("clicked", self.cancel_moving)
        self.btn_cancel.set_margin_top(20)
        self.btn_cancel.set_margin_end(20)
        self.btn_cancel.set_margin_bottom(20)
        self.btn_cancel.set_margin_start(20)

        self.box.append(self.lbl_src)
        self.box.append(self.lbl_dst)
        self.box.append(self.lbl_size)
        self.box.append(self.btn_cancel)

        self.dialog_response = False
        self.future = asyncio.get_event_loop().create_future()
        self.connect("response", self._on_response)

    def set_labels(self, src_info: Path, dst_info: Path) -> None:
        """
        Set labels to show moving info
        """
        self.src_info = src_info
        self.dst_info = dst_info
        self.lbl_src.set_text(str(self.src_info))
        self.lbl_dst.set_text(str(self.dst_info))
        self.src_size_text = f"{self.src_info.stat().st_size}"
        self.src_size = int(self.src_size_text)
        self.src_size = self.src_size / 1024 / 1024

    def update_labels(self, src_size_text: Path, dst_size_text: Path) -> None:
        """
        Force update labels with real information
        """
        try:
            if self.src_info and self.dst_info:
                self.lbl_src.set_text(str(self.src_info))
                self.lbl_dst.set_text(str(self.dst_info))

                self.src_size = int(src_size_text)
                self.dst_size = int(dst_size_text)

                self.src_size = self.src_size / 1024 / 1024
                self.dst_size = self.dst_size / 1024 / 1024

                self.lbl_size.set_text(
                    f"{self.src_size:.2f}/{self.dst_size:.2f} Mbytes"
                )

        except Exception as e:
            self.lbl_src.set_text(str(self.src_info))
            self.lbl_dst.set_text(_("Obteniendo destino .."))
            self.lbl_size.set_text(_("Caldulando ..."))
            print(e)

    # def update_labels(self) -> None:
    #     """
    #     Force update labels with real information
    #     """
    #     # This function is executed on the main thread (via idle_add)
    #     try:
    #         if self.dst_info:
    #             dst_size_text = f"{self.dst_info.stat().st_size}"
    #             dst_size = int(dst_size_text)
    #             dst_size = dst_size / 1024 / 1024
    #             self.lbl_size.set_text(
    #                 f"{self.src_size:.2f}/{dst_size:.2f} Mbytes"
    #             )
    #     except Exception as e:
    #         self.lbl_src.set_text(str(self.src_info))
    #         self.lbl_dst.set_text(_("Obteniendo destino .."))
    #         self.lbl_size.set_text(_("Caldulando ..."))
    #         print(e)

    def cancel_moving(self, button: Gtk.Button) -> None:
        """
        Stop dialog and send response False
        """
        self.dialog_response = False
        GLib.idle_add(self.response, Gtk.ResponseType.OK)

    def _on_response(self, dialog: Gtk.Dialog, response_id: str) -> None:
        """
        Set response on close dialog
        """
        if not self.future.done():
            self.future.set_result(self.dialog_response)
        self.destroy()

    async def wait_response_async(self) -> bool:
        """
        Response on close dialog
        """
        response = await self.future
        return response

    def close_moving(self) -> None:
        """
        Set response on close dialog
        """
        self.dialog_response = True
        GLib.idle_add(self.response, Gtk.ResponseType.OK)
