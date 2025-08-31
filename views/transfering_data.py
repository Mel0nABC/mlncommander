# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
import time
import gi
import asyncio
from pathlib import Path
from gi.repository import Gtk, Pango

gi.require_version("Gtk", "4.0")


class Transfering(Gtk.Window):

    def __init__(self, parent: Gtk.ApplicationWindow, action_to_exec: str):
        margin = 20

        title_str = ""

        if action_to_exec == "mover":
            title_str = _("Moviendo ..")
        else:
            title_str = _("Copiando ..")

        super().__init__(
            title=title_str,
            transient_for=parent,
            modal=True,
        )
        self.src_size = 0
        self.dst_size = 0
        self.old_dst_size = 0
        self.src_info = None
        self.dst_info = None
        self.time_file = None

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.set_child(self.box)
        self.set_default_size(500, 60)

        self.lbl_src = Gtk.Label(label="SRC")
        self.lbl_src.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        self.lbl_src.set_halign(Gtk.Align.START)
        self.lbl_src.set_margin_top(margin)
        self.lbl_src.set_margin_end(margin)
        self.lbl_src.set_margin_start(margin)

        self.lbl_dst = Gtk.Label(label="DST")
        self.lbl_dst.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        self.lbl_dst.set_halign(Gtk.Align.START)
        self.lbl_dst.set_margin_top(margin)
        self.lbl_dst.set_margin_end(margin)
        self.lbl_dst.set_margin_start(margin)

        self.lbl_size = Gtk.Label(label="0 bytes")
        self.lbl_size.set_margin_top(margin)
        self.lbl_size.set_margin_end(margin)
        self.lbl_size.set_margin_start(margin)

        self.progress_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        self.progress_box.set_hexpand(True)
        self.progress = Gtk.ProgressBar.new()
        self.progress.set_hexpand(True)
        self.progress.set_show_text(True)
        self.progress.set_margin_start(margin)
        self.progress.set_margin_end(margin)

        self.progress_box.append(self.progress)

        self.btn_cancel = Gtk.Button(label=_("Cancelar"))
        self.btn_cancel.connect("clicked", self.cancel_copying)
        self.btn_cancel.set_margin_top(margin)
        self.btn_cancel.set_margin_end(margin)
        self.btn_cancel.set_margin_bottom(margin)
        self.btn_cancel.set_margin_start(margin)

        self.box.append(self.lbl_src)
        self.box.append(self.lbl_dst)
        self.box.append(self.lbl_size)
        self.box.append(self.progress_box)
        self.box.append(self.btn_cancel)

        self.window_response = False
        self.future = asyncio.get_event_loop().create_future()
        self.connect("close-request", self.cancel_copying)

    def set_labels(self, src_info: Path, dst_info: Path) -> None:
        """
        Set labels to show copying info
        """
        self.time_file = time.time()
        self.src_info = src_info
        self.dst_info = dst_info

    def update_labels(self, src_size_text: Path, dst_size_text: Path) -> None:
        """
        Force update labels with real information
        """
        try:

            def update_worker():
                self.time_file = time.time()
                self.lbl_src.set_text(str(self.src_info))
                self.lbl_dst.set_text(str(self.dst_info))

                self.src_size = int(src_size_text)
                self.dst_size = int(dst_size_text)

                self.src_size = self.src_size / 1024 / 1024
                self.dst_size = self.dst_size / 1024 / 1024

                speed = self.dst_size - self.old_dst_size / 1024 / 1024
                speed = f"{round(speed, 2)} Mbytes/s"

                if speed == 0:
                    speed = _("Espere ...")

                self.lbl_size.set_text(f"{speed}")

                self.old_dst_size = int(dst_size_text)

                fraction = self.dst_size / self.src_size

                self.progress.set_fraction(fraction)

            time_now = time.time()
            if self.src_info and self.dst_info:

                if self.src_info.stat().st_size < 100485760:
                    update_worker()

                if (time_now - self.time_file) >= 1:
                    update_worker()

        except Exception as e:
            self.lbl_src.set_text(str(self.src_info))
            self.lbl_dst.set_text(_("Obteniendo destino .."))
            self.lbl_size.set_text(_("Caldulando ..."))
            print(e)

    def cancel_copying(self, button: Gtk.Button) -> None:
        """
        Set response on close window
        """
        self.window_response = False
        if not self.future.done():
            self.future.set_result(self.window_response)

    def close_copying(self) -> None:
        """
        Set response on close window
        """
        self.window_response = True
        if not self.future.done():
            self.future.set_result(self.window_response)

    async def wait_response_async(self) -> bool:
        """
        Response on close window
        """
        response = await self.future
        self.destroy()
        return response
