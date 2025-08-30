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
import secrets
import string
import threading
import subprocess
import pty
import re
import os
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib  # noqa : E402


class CompressWindow(Gtk.Window):
    def __init__(
        self, win, selected_items: list, dst_explorer: Explorer, dst_dir: Path
    ):
        super().__init__(title=_("Comprimir ficheros"), transient_for=win)
        self.win = win
        self.action = Actions()
        self.compression_manager = CompressionManager(self)
        self.selected_items = selected_items
        self.dst_explorer = dst_explorer
        self.dst_dir = dst_dir
        self.set_default_size(win.horizontal / 6, win.vertical / 8)
        self.compress_activate = False
        self.stop_compress = False
        self.compress_popen = None
        self.progress = None

        self.vertical_main = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        self.vertical_main.set_margin_top(20)
        self.vertical_main.set_margin_end(20)
        self.vertical_main.set_margin_bottom(20)
        self.vertical_main.set_margin_start(20)

        text = _("Lista de rutas a comprimir")
        dst_label = Gtk.Label.new()
        dst_label.set_hexpand(True)
        dst_label.set_text(f"{text}:")
        dst_label.set_halign(Gtk.Align.START)
        dst_label.set_margin_bottom(20)

        self.vertical_main.append(dst_label)

        for path in self.selected_items:
            src = Gtk.Label.new()
            src.set_hexpand(True)
            src.set_text(str(path))
            src.set_halign(Gtk.Align.START)
            self.vertical_main.append(src)

        self.set_child(self.vertical_main)

        self.vertical_files = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        self.vertical_files.set_margin_top(20)

        # set output file name
        label_file_name = Gtk.Label.new(_("Nombre del archivo"))
        self.file_name_entry = Gtk.Entry.new()

        # drop down file type
        drop_down_list = [item["extension"] for item in self.load_yaml_types()]
        label_type_file = Gtk.Label.new(_("Tipo de archivo"))
        self.drop_drow = Gtk.DropDown.new_from_strings(drop_down_list)

        # compression value
        label_lvl = Gtk.Label.new(_("Nivel de compresión"))
        self.spin_button = Gtk.SpinButton.new_with_range(0, 9, 1)

        # set password
        label_entry = Gtk.Label.new(_("Contraseña"))
        self.password_entry = Gtk.Entry.new()

        # multithreading compression
        label_multithread = Gtk.Label.new(_("Multi hilo para comprimir"))
        self.multithread_checkbox = Gtk.CheckButton.new()

        # Multi volumen
        label_multipart = Gtk.Label.new(_("Compresión multi parte"))
        self.spin_button_size = Gtk.SpinButton.new_with_range(0, 9999, 1)
        drop_size_type = ["b", "k", "m", "g"]
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
        self.grid.attach(self.password_entry, 1, 3, width, height)

        self.grid.attach(label_multipart, 0, 4, width, height)
        self.grid.attach(self.spin_button_size, 1, 4, width, height)
        self.grid.attach(self.drop_drown_size_type, 2, 4, width, height)

        self.grid.attach(label_multithread, 0, 5, width, height)
        self.grid.attach(self.multithread_checkbox, 1, 5, width, height)

        self.vertical_main.append(self.grid)

        horizontal_button = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        horizontal_button.set_hexpand(True)
        horizontal_button.set_vexpand(True)
        horizontal_button.set_halign(Gtk.Align.END)
        horizontal_button.set_valign(Gtk.Align.END)
        horizontal_button.set_margin_top(20)

        self.btn_extract = Gtk.Button(label=_("Comprimir"))
        self.btn_extract.connect("clicked", self.compress)
        btn_cancel = Gtk.Button(label=_("Cerrar"))
        btn_cancel.connect("clicked", self.on_exit)

        horizontal_button.append(self.btn_extract)
        horizontal_button.append(btn_cancel)
        self.vertical_main.append(self.vertical_files)
        self.vertical_main.append(horizontal_button)

        self.present()

    def compress(self, button: Gtk.Button) -> None:
        if not self.compress_activate:
            file_name = self.file_name_entry.get_text().strip()
            file_name = file_name.replace(" ", "")

            if not file_name:
                text = _("Debe introducir un nombre de archivo")
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
            self.stop_compress = True
            if self.compress_popen:
                self.compress_popen.kill()
            button.set_label(label=_("Comprimir"))
            self.compress_activate = False
            self.vertical_main.remove(self.progress)

    def disable_grid_pannel(self):
        for i in range(5):
            for widget in self.grid.get_child_at(1, i):
                widget.set_sensitive(False)

        self.grid.get_child_at(2, 4).set_sensitive(False)

    def enable_grid_pannel(self):
        for i in range(5):
            for widget in self.grid.get_child_at(1, i):
                widget.set_sensitive(True)

        self.grid.get_child_at(2, 4).set_sensitive(True)

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
        password = self.password_entry.get_text()
        volumen_size = self.spin_button_size.get_value_as_int()
        volumen_size_type = self.drop_drown_size_type.get_model().get_string(
            self.drop_drown_size_type.get_selected()
        )

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
            "7z",
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
        output_file_path = Path(f"{self.dst_dir}/{output_file}")

        while output_file_path.exists():
            text = "".join(
                secrets.choice(string.ascii_letters + string.digits)
                for _ in range(1)
            )
            output_file_path = Path(
                f"{self.dst_dir}/{file_name}{text}.{file_type}"
            )
        self.file_name_entry.set_text(output_file_path.stem)

        cmd.append(str(output_file_path))

        cmd = cmd + path_list

        self.compress_work(cmd, file_name, output_file)

        self.enable_grid_pannel()

    def compress_work(
        self, cmd: str, file_name: str, output_file: str
    ) -> None:
        master_df, slave_fd = pty.openpty()
        self.compress_popen = subprocess.Popen(
            cmd, stdin=slave_fd, stdout=slave_fd, stderr=slave_fd, text=True
        )
        os.close(slave_fd)

        while self.compress_popen.poll() is None:
            try:
                output = os.read(master_df, 1024)
                if not output:
                    break
                texto = output.decode("utf-8")

                if "Everything is Ok" in texto:
                    GLib.idle_add(self.progress.set_fraction, 1)
                    GLib.idle_add(
                        self.dst_explorer.load_new_path, self.dst_dir
                    )

                match = re.search(r"(.{2})%", texto)
                if match:
                    fraction = int(match.group(1)) / 100
                    GLib.idle_add(self.progress.set_fraction, fraction)
                    if self.dst_explorer.actual_path == self.dst_dir:
                        GLib.idle_add(
                            self.dst_explorer.load_new_path, self.dst_dir
                        )
            except OSError:
                continue

        if self.stop_compress:
            GLib.idle_add(self.progress.set_fraction, 0)
            for i in self.dst_dir.iterdir():
                if file_name in str(i) and output_file in str(i):
                    i.unlink()
        else:
            GLib.idle_add(self.progress.set_fraction, 1)
            self.compress_activate = False
            self.stop_compress = False
            self.btn_extract.set_label(label=_("Comprimir"))

        self.compress_popen = None

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
        if self.compress_popen:
            self.verify_on_exit()
            return

        self.destroy()
        GLib.idle_add(self.win.key_connect)

    def verify_on_exit(self) -> bool:

        alert = Gtk.AlertDialog()
        alert.set_message(_("Si aceptas, cancelaras el proceso actual."))
        alert.set_buttons([_("Aceptar"), _("Cancelar")])

        alert.set_default_button(0)
        alert.set_cancel_button(1)

        def response(alertdialog: Gtk.AlertDialog, result: Gio.Task) -> bool:
            self.respuesta = alertdialog.choose_finish(result)
            if not self.respuesta:
                self.stop_compress = True
                self.compress_popen.kill()
                self.destroy()
                GLib.idle_add(self.win.key_connect)

        alert.choose(self, None, response)

    def set_percent(self, percent):
        GLib.idle_add(self.label_rsp.set_text, percent)

    def get_archivo_password(self, to_work: Queue, file: Path):
        GLib.idle_add(self.create_password_window, to_work, file)

    def create_password_window(self, to_work: Queue, file: Path):
        PasswordWindow(self, to_work, file)

    def load_yaml_types(self):
        import yaml

        with open("./files/7zinformation.yaml", "r") as f:
            formats = yaml.safe_load(f)

        return list(formats.values())
