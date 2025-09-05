# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT

from utilities.i18n import _
from utilities.compression import CompressionManager
from controls.actions import Actions
from views.explorer import Explorer
from views.password_entry import PasswordWindow
from views.confirm_window import ConfirmWindow
from pathlib import Path
from multiprocessing import Queue
import asyncio
import secrets
import string
import threading
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib  # noqa : E402


class CompressWindow(Gtk.Window):
    def __init__(
        self, win, selected_items: list, dst_explorer: Explorer, dst_dir: Path
    ):
        super().__init__(transient_for=win)

        # Load css

        header = Gtk.HeaderBar()
        header.set_title_widget(Gtk.Label(label=_("Comprimir ficheros")))
        self.set_titlebar(header)

        self.get_style_context().add_class("app_background")
        self.get_style_context().add_class("font")
        self.get_style_context().add_class("font-color")

        self.win = win
        self.action = Actions()
        self.compression_manager = CompressionManager(self)
        self.EXEC_SEVEN_Z_TYPE = self.compression_manager.EXEC_SEVEN_Z_TYPE
        self.selected_items = selected_items
        self.dst_explorer = dst_explorer
        self.dst_dir = dst_dir
        self.set_default_size(win.horizontal / 6, win.vertical / 8)
        self.compress_activate = False
        self.stop_compress = False
        self.compress_popen = None
        self.progress = None
        self.in_background = False

        self.vertical_main = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )

        self.set_child(self.vertical_main)

        self.vertical_main.set_margin_top(20)
        self.vertical_main.set_margin_end(20)
        self.vertical_main.set_margin_bottom(20)
        self.vertical_main.set_margin_start(20)

        text = _("Lista de rutas a comprimir")
        self.dst_label = Gtk.Label.new()
        self.dst_label.set_hexpand(True)
        self.dst_label.set_text(f"{text}:")
        self.dst_label.set_halign(Gtk.Align.START)
        self.dst_label.set_margin_bottom(20)

        self.vertical_main.append(self.dst_label)

        self.vertical_files = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        self.vertical_files.set_margin_top(20)

        for path in self.selected_items:
            src = Gtk.Label.new()
            src.set_hexpand(True)
            src.set_text(str(path))
            src.set_halign(Gtk.Align.START)
            self.vertical_files.append(src)

        self.vertical_main.append(self.vertical_files)

        # set output file name
        label_file_name = Gtk.Label.new(_("Nombre del archivo"))
        self.file_name_entry = Gtk.Entry.new()

        # drop down file type
        drop_down_list = [".7z", ".xz", ".zip", ".gz", ".bz2", ".tar", ".wim"]
        label_type_file = Gtk.Label.new(_("Tipo de archivo"))
        self.drop_drow = Gtk.DropDown.new_from_strings(drop_down_list)

        # compression value
        label_lvl = Gtk.Label.new(_("Nivel de compresión"))
        self.spin_button = Gtk.SpinButton.new_with_range(0, 9, 1)

        # set password
        label_entry = Gtk.Label.new(_("Contraseña"))
        self.password_entry_1 = Gtk.PasswordEntry.new()
        self.password_entry_1.set_show_peek_icon(True)
        self.password_entry_2 = Gtk.PasswordEntry.new()
        self.password_entry_2.set_show_peek_icon(True)

        # multithreading compression
        label_multithread = Gtk.Label.new(_("Multi hilo para comprimir"))
        self.multithread_checkbox = Gtk.CheckButton.new()

        # Multi volumen
        label_multipart = Gtk.Label.new(_("Tamaño volumen\nmulti parte"))
        self.spin_button_size = Gtk.SpinButton.new_with_range(0, 9999, 1)
        self.drop_size_dict = {
            "Bytes": "b",
            "KBytes": "k",
            "MBytes": "m",
            "GigaBytes": "g",
        }
        drop_size_type = list(self.drop_size_dict.keys())
        self.drop_drown_size_type = Gtk.DropDown.new_from_strings(
            drop_size_type
        )

        self.grid = Gtk.Grid(column_spacing=20, row_spacing=5)
        self.grid.set_margin_top(20)
        self.grid.set_hexpand(True)
        self.grid.set_halign(Gtk.Align.CENTER)

        width = 1
        height = 1

        self.grid.attach(label_file_name, 0, 0, width, height)
        self.grid.attach(self.file_name_entry, 1, 0, width, height)

        self.grid.attach(label_lvl, 0, 1, width, height)
        self.grid.attach(self.spin_button, 1, 1, width, height)

        self.grid.attach(label_type_file, 0, 2, width, height)
        self.grid.attach(self.drop_drow, 1, 2, width, height)

        self.grid.attach(label_entry, 0, 3, width, height)
        self.grid.attach(self.password_entry_1, 1, 3, width, height)
        self.grid.attach(self.password_entry_2, 1, 4, width, height)

        self.grid.attach(label_multipart, 0, 5, width, height)
        self.grid.attach(self.spin_button_size, 1, 5, width, height)
        self.grid.attach(self.drop_drown_size_type, 2, 5, width, height)

        self.grid.attach(label_multithread, 0, 6, width, height)
        self.grid.attach(self.multithread_checkbox, 1, 6, width, height)

        self.vertical_main.append(self.grid)

        self.horizontal_button = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        self.horizontal_button.set_hexpand(True)
        self.horizontal_button.set_vexpand(True)
        self.horizontal_button.set_halign(Gtk.Align.END)
        self.horizontal_button.set_valign(Gtk.Align.END)
        self.horizontal_button.set_margin_top(20)

        self.btn_extract = Gtk.Button(label=_("Comprimir"))
        self.btn_extract.connect("clicked", self.compress)
        self.btn_cancel = Gtk.Button(label=_("Cerrar"))
        self.btn_cancel.connect("clicked", self.on_exit)
        self.btn_background = Gtk.Button(label=_("Minimizar"))
        self.btn_background.set_sensitive(False)
        self.btn_background.connect("clicked", self.to_background)

        self.horizontal_button.append(self.btn_extract)
        self.horizontal_button.append(self.btn_cancel)
        self.horizontal_button.append(self.btn_background)

        self.vertical_main.append(self.horizontal_button)

        self.connect("close-request", self.on_close_window)

        self.present()

    def compress(self, button: Gtk.Button) -> None:
        if not self.compress_activate:
            self.btn_background.set_sensitive(True)
            file_name = self.file_name_entry.get_text().strip()
            file_name = file_name.replace(" ", "")

            if not file_name:
                text = _("Debe introducir un nombre de archivo")
                GLib.idle_add(self.action.show_msg_alert, self.win, text)
                return

            if (
                self.password_entry_1.get_text()
                != self.password_entry_2.get_text()
            ):
                text = _("La contraseña establecida es diferente")
                GLib.idle_add(self.action.show_msg_alert, self.win, text)
                return

            if not self.progress:
                self.progress = Gtk.ProgressBar.new()
                self.progress.set_hexpand(True)
                self.progress.set_show_text(True)
                self.progress.set_margin_top(20)
                self.progress.set_margin_start(20)
                self.progress.set_margin_end(20)

            self.vertical_main.insert_child_after(self.progress, self.grid)
            self.stop_compress = False
            self.compress_activate = True
            button.set_label(label=_("Cancelar"))
            t = threading.Thread(target=self.start_compress)
            t.start()
        else:

            if self.compress_popen:
                # destroy = False, not destroy window
                destroy = False
                self.verify_on_exit(destroy)

    def disable_grid_pannel(self):
        for i in range(6):
            for widget in self.grid.get_child_at(1, i):
                widget.set_sensitive(False)

        self.grid.get_child_at(2, 5).set_sensitive(False)

    def enable_grid_pannel(self):
        for i in range(6):
            for widget in self.grid.get_child_at(1, i):
                widget.set_sensitive(True)

        self.grid.get_child_at(2, 5).set_sensitive(True)

    def start_compress(self) -> None:

        self.disable_grid_pannel()

        file_name = self.file_name_entry.get_text().strip()
        file_name = file_name.replace(" ", "")
        compression_lvl = self.spin_button.get_value_as_int()
        file_type = self.drop_drow.get_model().get_string(
            self.drop_drow.get_selected()
        )
        file_type = file_type.replace(".", "")
        compression_type = file_type
        password = self.password_entry_1.get_text()
        volumen_size = self.spin_button_size.get_value_as_int()
        volumen_size_type = self.drop_drown_size_type.get_model().get_string(
            self.drop_drown_size_type.get_selected()
        )
        volumen_size_type = self.drop_size_dict[volumen_size_type]

        multithread = self.multithread_checkbox.get_active()

        if multithread:
            multithread = "on"
        else:
            multithread = "off"

        path_list = [str(path) for path in self.selected_items]

        if file_type == "gz":
            compression_type = "gzip"

        if file_type == "bz2":
            compression_type = "bzip2"

        cmd = [
            self.EXEC_SEVEN_Z_TYPE,
            "a",
            f"-t{compression_type}",
            f"-mx={compression_lvl}",
            f"-mmt={multithread}",
            "-y",
        ]

        if password:
            cmd.append(f"-p{password}")

        if volumen_size:
            multipart_output = f"-v{volumen_size}{volumen_size_type}"
            cmd.append(multipart_output)

        output_file = f"{file_name}.{file_type}"
        self.output_file_path = Path(f"{self.dst_dir}/{output_file}")

        while self.output_file_path.exists():
            text = "".join(
                secrets.choice(string.ascii_letters + string.digits)
                for _ in range(1)
            )
            self.output_file_path = Path(
                f"{self.dst_dir}/{file_name}{text}.{file_type}"
            )
        self.file_name_entry.set_text(self.output_file_path.stem)

        cmd.append(str(self.output_file_path))

        cmd = cmd + path_list

        self.compression_manager.compress_work(
            self,
            self.win,
            self.progress,
            cmd,
            file_name,
            output_file,
            self.dst_explorer,
        )

        self.enable_grid_pannel()

        if self.in_background:
            self.horizontal_button.remove(self.btn_extract)

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
        """
        Make a question, no auto close
        """
        if self.compress_popen:
            self.verify_on_exit(True)
            return

        self.destroy()
        self.finish_background()
        self.win.key_connect()

    def verify_on_exit(self, destroy: bool) -> bool:

        mm = ConfirmWindow(self.win)

        async def response():
            response = await mm.wait_response_async()
            if response:
                self.stop_compress = True
                self.compress_popen.kill()
                if destroy:
                    GLib.idle_add(self.destroy)
                    GLib.idle_add(self.win.key_connect)
                else:
                    GLib.idle_add(self.btn_extract.set_label, _("Comprimir"))
                    self.compress_activate = False

        asyncio.ensure_future(response())

    def set_percent(self, percent: str) -> None:
        GLib.idle_add(self.label_rsp.set_text, percent)

    def get_archivo_password(self, to_work: Queue, file: Path) -> None:
        GLib.idle_add(self.create_password_window, to_work, file)

    def create_password_window(self, to_work: Queue, file: Path):
        PasswordWindow(self, to_work, file)

    def to_background(self, button: Gtk.Button = None) -> None:
        self.win.key_connect()
        self.in_background = True
        self.set_child(None)
        self.vertical_main.remove(self.grid)
        self.vertical_main.remove(self.vertical_files)
        self.vertical_main.set_margin_bottom(0)
        self.dst_label.set_margin_bottom(0)
        self.progress.set_margin_top(0)
        self.progress.set_margin_bottom(0)
        self.horizontal_button.set_margin_top(0)
        self.horizontal_button.remove(self.btn_background)
        self.horizontal_button.set_vexpand(False)
        text = _("Comprimiendo")
        self.dst_label.set_text(f"{text}: {str(self.output_file_path)}")

        # self.vertical_main.set_size_request(-1, -1)
        self.vertical_main.get_style_context().add_class("to_down_explorer")

        if self.dst_explorer.name == "explorer_1":
            self.vertical_main.set_margin_end(self.win.scroll_margin / 2)
            self.vertical_main.set_margin_start(self.win.scroll_margin)
            self.vertical_main.get_style_context().add_class(
                "explorer_background_left"
            )
        else:
            self.vertical_main.set_margin_end(self.win.scroll_margin)
            self.vertical_main.set_margin_start(self.win.scroll_margin / 2)
            self.vertical_main.get_style_context().add_class(
                "explorer_background_right"
            )

        self.win.to_down_explorer(self.dst_explorer.name, self.vertical_main)
        self.hide()

    def finish_background(self) -> None:
        self.win.finish_to_down_explorer(
            self.dst_explorer.name, self.vertical_main
        )
