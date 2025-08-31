# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT

from utilities.i18n import _
from utilities.compression import CompressionManager
from controls.actions import Actions
from views.explorer import Explorer
from views.password_entry import PasswordWindow
from views.confirm_window import ConfirmWindow
from multiprocessing import Queue
from pathlib import Path
import asyncio
import threading
import gi
import time

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Pango  # noqa : E402


class UncompressWindow(Gtk.Window):
    def __init__(
        self, win, selected_items: list, dst_explorer: Explorer, dst_dir: Path
    ):
        super().__init__(title=_("Descomprimir ficheros"), transient_for=win)
        self.win = win
        self.action = Actions()
        self.compression_manager = CompressionManager(self)
        self.selected_items = selected_items
        self.dst_explorer = dst_explorer
        self.dst_dir = dst_dir
        self.set_default_size(win.horizontal / 6, win.vertical / 8)
        self.extract_activate = False

        self.stop_uncompress = False

        self.vertical_main = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        self.vertical_main.set_margin_top(20)
        self.vertical_main.set_margin_end(20)
        self.vertical_main.set_margin_bottom(20)
        self.vertical_main.set_margin_start(20)

        text = _("Ruta destino")
        dst_label = Gtk.Label.new()
        dst_label.set_text(f"{text}: {dst_dir}")

        self.vertical_main.append(dst_label)

        self.set_child(self.vertical_main)

        self.vertical_files = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        self.vertical_files.set_margin_top(20)

        horizontal_button = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        horizontal_button.set_hexpand(True)
        horizontal_button.set_vexpand(True)
        horizontal_button.set_halign(Gtk.Align.END)
        horizontal_button.set_valign(Gtk.Align.END)
        horizontal_button.set_margin_top(20)

        self.btn_extract = Gtk.Button(label=_("Extraer"))
        self.btn_extract.connect("clicked", self.uncompress)
        btn_cancel = Gtk.Button(label=_("Cerrar"))
        btn_cancel.connect("clicked", self.on_exit)

        horizontal_button.append(self.btn_extract)
        horizontal_button.append(btn_cancel)
        self.vertical_main.append(self.vertical_files)
        self.vertical_main.append(horizontal_button)

        self.connect("close-request", self.on_close_window)

        self.present()

    def uncompress(self, button: Gtk.Button) -> None:

        if not self.extract_activate:
            self.extract_activate = True
            button.set_label(label=_("Cancelar"))
            t = threading.Thread(target=self.start_uncompress)
            t.start()
        else:
            self.verify_on_exit(False)

    def start_uncompress(self) -> None:
        output_text = _("Para más información pulse sobre los icono.")

        list_files = self.selected_items

        for file in list_files:

            if self.stop_uncompress:
                continue

            GLib.idle_add(self.add_new_label, file)
            q = Queue()

            self.compression_manager.uncompress(file, self.dst_dir, q)

            if self.stop_uncompress:
                self.compression_manager.delete_last_uncompress()
                output_text = _(
                    (
                        "Has finalizado el proceso de descompresión\n"
                        "El último archivo estará corrupto.\n"
                        "Si hay iconos, pulsando en ellos podrás"
                        " ver información"
                    )
                )
                GLib.idle_add(self.update_labels, None, file)
            else:
                response = q.get()
                GLib.idle_add(self.update_labels, response, file)
            time.sleep(0.1)

        self.on_stop_uncompress()
        info_label = Gtk.Label.new(output_text)
        info_label.set_margin_top(20)
        GLib.idle_add(self.vertical_files.append, info_label)
        GLib.idle_add(self.btn_extract.set_sensitive, False)
        GLib.idle_add(self.btn_extract.set_label, _("Extraer"))

    def add_new_label(self, file: Path) -> None:

        grid = Gtk.Grid(column_spacing=200, row_spacing=10)

        label_src = Gtk.Label.new()
        label_src.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        # label_src.set_hexpand(True)
        label_src.set_halign(Gtk.Align.START)
        label_src.set_text(str(file))

        grid.attach(label_src, 0, 0, 1, 1)

        self.label_finish_status = Gtk.Label.new()
        self.label_finish_status.set_text("    ")

        grid.attach(self.label_finish_status, 1, 0, 1, 1)

        self.vertical_files.append(grid)
        self.progress_bar = Gtk.ProgressBar.new()
        self.progress_bar.set_hexpand(True)
        self.progress_bar.set_show_text(True)
        self.vertical_files.append(self.progress_bar)
        self.vertical_files.append(
            Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        )

    def update_labels(self, response: dict, file: Path) -> None:

        if not response:
            self.label_finish_status.set_text(_("Proceso detenido"))
            self.dst_explorer.load_new_path(self.dst_dir)
            return

        if response["status"]:
            self.label_finish_status.set_text("✅")
            GLib.idle_add(self.progress_bar.set_fraction, 1)
        else:
            self.label_finish_status.set_text("❌")
            GLib.idle_add(self.progress_bar.set_fraction, 0)

        gesture = Gtk.GestureClick.new()
        gesture.connect(
            "pressed",
            self.show_msg_alert,
            self.win,
            _(f"{response["msg"]}\n\n{file}"),
        )
        self.label_finish_status.add_controller(gesture)

        self.dst_explorer.load_new_path(self.dst_dir)

    def on_stop_uncompress(self) -> None:
        self.extract_activate = False
        self.stop_uncompress = True
        self.compression_manager.stop_uncompress()

    def show_msg_alert(
        self,
        gesture: Gtk.GestureClick,
        n_press: int,
        x: float,
        y: float,
        win: Explorer,
        msg: str,
    ) -> None:
        self.action.show_msg_alert(self.win, msg)

    def on_close_window(self, signal) -> bool:
        """
        When push X for close window, make a question, no auto close
        """
        self.on_exit()
        return True

    def on_exit(self, button: Gtk.Button = None) -> None:
        if self.extract_activate:
            self.verify_on_exit(True)
            return

        self.destroy()
        self.win.key_connect()
        return True

    def verify_on_exit(self, destroy: bool) -> bool:

        mm = ConfirmWindow(self.win)

        async def response():
            response = await mm.wait_response_async()
            if response:
                self.on_stop_uncompress()
                if destroy:
                    GLib.idle_add(self.destroy)
                    GLib.idle_add(self.win.key_connect)

        asyncio.ensure_future(response())

    def set_percent(self, percent):
        GLib.idle_add(self.progress_bar.set_fraction, percent / 100)

    def get_archivo_password(self, to_work: Queue, file: Path):
        GLib.idle_add(self.create_password_window, to_work, file)

    def create_password_window(self, to_work: Queue, file: Path):
        PasswordWindow(self, to_work, file)
