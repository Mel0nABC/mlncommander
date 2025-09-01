# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from views.confirm_window import ConfirmWindow
import time
import gi
import asyncio
from pathlib import Path
from gi.repository import Gtk, GLib, Pango

gi.require_version("Gtk", "4.0")


class Transfering(Gtk.Window):

    def __init__(
        self,
        parent: Gtk.ApplicationWindow,
        action_to_exec: str,
        dst_explorer: Gtk.Window,
    ):
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
        self.win = parent
        self.dst_explorer = dst_explorer
        self.src_size = 0
        self.dst_size = 0
        self.old_dst_size = 0
        self.src_info = None
        self.dst_info = None
        self.time_file = None

        self.grid = Gtk.Grid(column_spacing=10, row_spacing=1)
        self.grid.set_hexpand(True)
        self.set_child(self.grid)

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
        self.btn_cancel.connect("clicked", self.verify_on_exit)
        self.btn_cancel.set_margin_top(margin)
        self.btn_cancel.set_margin_end(margin)
        self.btn_cancel.set_margin_start(margin)

        self.btn_background = Gtk.Button(label=_("Minimizar"))
        self.btn_background.connect("clicked", self.to_background)
        self.btn_background.set_margin_top(margin)
        self.btn_background.set_margin_end(margin)
        self.btn_background.set_margin_bottom(margin)
        self.btn_background.set_margin_start(margin)

        self.grid.attach(self.lbl_src, 0, 0, 1, 1)
        self.grid.attach(self.lbl_dst, 0, 1, 1, 1)
        self.grid.attach(self.lbl_size, 0, 2, 1, 1)
        self.grid.attach(self.progress_box, 0, 3, 1, 1)
        self.grid.attach(self.btn_cancel, 0, 4, 1, 1)
        self.grid.attach(self.btn_background, 0, 5, 1, 1)

        self.window_response = False
        self.future = asyncio.get_event_loop().create_future()
        self.connect("close-request", self.on_close_window)

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

    def on_close_window(self, signal) -> bool:
        """
        When push X for close window, make a question, no auto close
        """
        self.verify_on_exit()
        return True

    async def wait_response_async(self) -> bool:
        """
        Response on close window
        """
        response = await self.future
        self.destroy()
        return response

    def verify_on_exit(self, button: Gtk.Button = None) -> bool:

        mm = ConfirmWindow(self.win)

        async def response():
            response = await mm.wait_response_async()
            if response:
                self.window_response = False
                if not self.future.done():
                    self.future.set_result(self.window_response)

        asyncio.ensure_future(response())

    def on_finish_close(self) -> None:
        self.finish_background()
        self.destroy()

    def to_background(self, button: Gtk.Button) -> None:
        if self.grid is not None:

            self.set_child(None)

            self.grid.get_style_context().add_class("to_down_explorer")

            self.lbl_dst.set_margin_top(0)
            self.lbl_dst.set_margin_end(0)
            self.lbl_dst.set_margin_bottom(0)
            self.lbl_dst.set_margin_start(0)

            self.lbl_size.set_margin_top(self.win.scroll_margin)
            self.lbl_size.set_margin_end(0)
            self.lbl_size.set_margin_bottom(0)
            self.lbl_size.set_margin_start(0)

            self.lbl_size.set_width_chars(20)

            self.progress.set_margin_top(self.win.scroll_margin)
            self.progress.set_margin_end(0)
            self.progress.set_margin_bottom(0)
            self.progress.set_margin_start(0)

            # self.progress.set_hexpand(False)

            self.btn_cancel.set_margin_top(0)
            self.btn_cancel.set_margin_end(0)
            self.btn_cancel.set_margin_bottom(0)
            self.btn_cancel.set_margin_start(0)

            self.btn_cancel.set_label("X")
            self.btn_cancel.set_size_request(-1, -1)
            self.btn_cancel.set_hexpand(False)
            self.btn_cancel.set_halign(Gtk.Align.END)

            self.grid.set_margin_top(self.win.scroll_margin)

            if self.dst_explorer.name == "explorer_1":
                self.grid.set_margin_end(self.win.scroll_margin / 2)
                self.grid.set_margin_start(self.win.scroll_margin)
                self.grid.get_style_context().add_class(
                    "explorer_background_left"
                )
            else:
                self.grid.set_margin_end(self.win.scroll_margin)
                self.grid.set_margin_start(self.win.scroll_margin / 2)
                self.grid.get_style_context().add_class(
                    "explorer_background_right"
                )

            self.grid.set_hexpand(False)
            self.grid.remove(self.lbl_src)
            self.grid.remove(self.btn_background)
            self.grid.remove(self.lbl_dst)
            self.grid.remove(self.lbl_size)
            self.grid.remove(self.progress_box)
            self.grid.remove(self.btn_cancel)

            self.grid.attach(self.lbl_dst, 0, 1, 1, 2)
            self.grid.attach(self.btn_cancel, 1, 1, 1, 2)
            self.grid.attach(self.progress_box, 0, 3, 1, 2)
            self.grid.attach(self.lbl_size, 1, 3, 1, 2)

        GLib.idle_add(
            self.win.to_down_explorer, self.dst_explorer.name, self.grid
        )
        self.hide()

    def finish_background(self) -> None:
        GLib.idle_add(
            self.win.finish_to_down_explorer, self.dst_explorer.name, self.grid
        )
