# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT

from utilities.i18n import _
from utilities.compression import CompressionManager
from controls.actions import Actions
from views.explorer import Explorer
from views.password_entry import PasswordWindow
from pathlib import Path
from multiprocessing import Queue
import threading
import gi
import time

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib  # noqa : E402


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
        self.present()

    def uncompress(self, button: Gtk.Button) -> None:

        if not self.extract_activate:
            self.extract_activate = True
            button.set_label(label=_("Cancelar"))
            t = threading.Thread(target=self.start_uncompress)
            t.start()
        else:
            self.stop_uncompress = True
            self.compression_manager.stop_uncompress()
            button.set_sensitive(False)

    def start_uncompress(self) -> None:
        output_text = _("Para más información pulse sobre los icono.")
        for file in self.selected_items:

            if self.stop_uncompress:
                continue

            GLib.idle_add(self.add_new_label, file)
            q = Queue()

            self.compression_manager.uncompress(file, self.dst_dir, q)

            if self.stop_uncompress:
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

        info_label = Gtk.Label.new(output_text)
        info_label.set_margin_top(20)
        GLib.idle_add(self.vertical_files.append, info_label)
        GLib.idle_add(self.dst_explorer._reeconnect_controller)
        GLib.idle_add(self.btn_extract.set_sensitive, False)
        GLib.idle_add(self.btn_extract.set_label, _("Extraer"))

    def add_new_label(self, file: Path) -> None:
        horizontal_file = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        horizontal_file.set_margin_top(10)

        label = Gtk.Label.new()
        label.set_hexpand(True)
        label.set_halign(Gtk.Align.START)
        label.set_text(str(file))

        horizontal_file.append(label)

        self.label_rsp = Gtk.Label.new()
        self.label_rsp.set_text("0%")
        self.label_rsp.set_margin_end(30)

        horizontal_file.append(self.label_rsp)

        self.vertical_files.append(horizontal_file)

    def update_labels(self, response: dict, file: Path) -> None:

        if not response:
            self.label_rsp.set_text(_("Proceso detenido"))
            self.dst_explorer.load_new_path(self.dst_dir)
            return

        if response["status"]:
            self.label_rsp.set_text("✅")
        else:
            self.label_rsp.set_text("❌")

        gesture = Gtk.GestureClick.new()
        gesture.connect(
            "pressed",
            self.show_msg_alert,
            self.win,
            _(f"{response["msg"]}\n\n{file}"),
        )
        self.label_rsp.add_controller(gesture)

        self.dst_explorer.load_new_path(self.dst_dir)

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

    def on_exit(self, button: Gtk.Button) -> None:
        self.destroy()

    def set_percent(self, percent):
        GLib.idle_add(self.label_rsp.set_text, percent)

    def get_archivo_password(self, to_work):
        GLib.idle_add(self.create_password_window, to_work)

    def create_password_window(self, to_work):
        PasswordWindow(self, to_work)
