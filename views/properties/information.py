# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from utilities.file_manager import File_manager
from entity.file_or_directory_info import File_or_directory_info
from pathlib import Path
import threading
import gi
from gi.repository import Gtk, GLib, Pango

gi.require_version("Gtk", "4.0")


class Information(Gtk.Box):

    def __init__(self, win: Gtk.Window, path_list: list[Path]):
        super().__init__()
        self.win = win
        self.path_list = path_list

        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_vexpand(True)
        self.set_hexpand(True)
        self.set_margin_top(20)
        self.set_margin_end(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)

        self.spinner_list = []
        self.lbl_loading_header_list = []

        self.header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.header_box.get_style_context().add_class("border-style")
        self.header_box.set_size_request(-1, 200)
        self.header_box.set_margin_bottom(20)
        self.header_box.set_vexpand(False)

        loading_header_box = self.add_loading_box()
        self.header_box.append(loading_header_box)

        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.list_box.get_style_context().add_class("border-style")
        self.list_box.set_vexpand(True)

        self.append(self.header_box)
        self.append(self.list_box)
        self.append(self.create_bottom_menu())

        self.header_thread = threading.Thread(
            target=self.add_header_resumen,
            args=(
                loading_header_box,
                self.lbl_loading_header_list[0],
            ),
        ).start()

        self.list_thread = threading.Thread(target=self.add_list_path).start()

    def add_header_resumen(
        self, loading_box: Gtk.Box, lbl_loading_header: Gtk.Label
    ) -> Gtk.Box:

        self.header_content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5
        )

        self.header_content.set_valign(Gtk.Align.CENTER)
        self.header_content.set_vexpand(True)

        title_label = Gtk.Label.new(_("Resumen total de las ubicaciones"))
        title_label.set_halign(Gtk.Align.START)
        title_label.set_margin_bottom(20)

        self.header_content.append(title_label)

        result_dict = File_manager.properties_path_list(
            self.path_list, lbl_loading_header
        )

        folders_str_lsb = Gtk.Label.new(_("Subcarpetas totales:"))
        files_str_lsb = Gtk.Label.new(_("Archivos totales:"))
        total_size_str_lsb = Gtk.Label.new(_("Tamaño total:"))

        folders_str_lsb.set_xalign(0.0)
        files_str_lsb.set_xalign(0.0)
        total_size_str_lsb.set_xalign(0.0)

        folders_str_lsb.set_width_chars(25)
        files_str_lsb.set_width_chars(25)
        total_size_str_lsb.set_width_chars(25)

        folders_lsb = Gtk.Label.new(str(result_dict["folders"]))
        files_lsb = Gtk.Label.new(str(result_dict["files"]))
        total_size_lsb = Gtk.Label.new(
            File_manager.get_size_and_unit(result_dict["total_size"])
        )

        grid = Gtk.Grid(column_spacing=10, row_spacing=5)

        grid.attach(folders_str_lsb, 0, 0, 1, 1)
        grid.attach(files_str_lsb, 0, 1, 1, 1)
        grid.attach(total_size_str_lsb, 0, 2, 1, 1)
        grid.attach(folders_lsb, 1, 0, 1, 1)
        grid.attach(files_lsb, 1, 1, 1, 1)
        grid.attach(total_size_lsb, 1, 2, 1, 1)

        grid.set_halign(Gtk.Align.CENTER)
        title_label.set_halign(Gtk.Align.CENTER)

        self.header_content.append(grid)

        GLib.idle_add(self.header_box.append, self.header_content)
        GLib.idle_add(self.header_box.remove, loading_box)

    def add_list_path(self) -> Gtk.Box:

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        content.set_halign(Gtk.Align.CENTER)

        scrolled = Gtk.ScrolledWindow.new()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        scrolled.set_margin_top(20)
        scrolled.set_margin_end(20)
        scrolled.set_margin_bottom(20)
        scrolled.set_margin_start(20)

        scrolled.set_child(content)
        GLib.idle_add(self.list_box.append, scrolled)

        for path in self.path_list:

            main_box = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL, spacing=5
            )

            content.append(main_box)

            loading_box = self.add_loading_box()
            loading_box.set_hexpand(True)
            loading_box.set_halign(Gtk.Align.CENTER)

            lbl_loading = loading_box.get_last_child()

            main_box.append(loading_box)

            file_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

            path_enty = File_or_directory_info(Path(path))
            result_dict = File_manager.properties_path(
                path_enty.path_file, lbl_loading
            )

            GLib.idle_add(main_box.remove, loading_box)

            file_box.set_margin_top(20)
            file_box.set_margin_end(20)
            file_box.set_margin_bottom(20)
            file_box.set_margin_start(20)
            file_box.set_vexpand(False)
            file_box.set_hexpand(False)
            file_box.set_valign(Gtk.Align.CENTER)
            file_box.set_halign(Gtk.Align.CENTER)

            icon_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

            path_lbl = Gtk.Label.new(str(path))
            path_lbl.set_wrap(True)
            path_lbl.set_max_width_chars(100)
            path_lbl.set_xalign(0)

            folders_str_lbl = Gtk.Label.new(_("Subcarpetas totales:"))
            files_str_lbl = Gtk.Label.new(_("Archivos totales:"))
            total_size_str_lbl = Gtk.Label.new(_("Tamaño total:"))

            folders_str_lbl.set_xalign(0.0)
            files_str_lbl.set_xalign(0.0)
            total_size_str_lbl.set_xalign(0.0)

            folders_str_lbl.set_width_chars(25)
            files_str_lbl.set_width_chars(25)
            total_size_str_lbl.set_width_chars(25)

            folders_lbl = Gtk.Label.new(str(result_dict["folders"]))
            files_lbl = Gtk.Label.new(str(result_dict["files"]))
            total_size_lbl = Gtk.Label.new(
                File_manager.get_size_and_unit(result_dict["total_size"])
            )

            permission_str_lbl = Gtk.Label.new(_("Permisos:"))
            permission_str_lbl.set_xalign(0.0)
            permission_str_lbl.set_width_chars(25)

            permission_lbl = Gtk.Label.new(
                File_manager.get_permissions(path_enty.path_file)["msg"]
            )

            grid = Gtk.Grid()

            grid.attach(folders_str_lbl, 0, 2, 1, 1)
            grid.attach(files_str_lbl, 0, 3, 1, 1)
            grid.attach(total_size_str_lbl, 0, 4, 1, 1)
            grid.attach(permission_str_lbl, 0, 5, 1, 1)
            grid.attach(folders_lbl, 1, 2, 1, 1)
            grid.attach(files_lbl, 1, 3, 1, 1)
            grid.attach(total_size_lbl, 1, 4, 1, 1)
            grid.attach(permission_lbl, 1, 5, 1, 1)

            from icons.icon_manager import IconManager

            icon_manager = IconManager(self.win)

            icon = None

            if path.is_dir():
                icon = icon_manager.get_folder_icon(path)
            else:
                icon = icon_manager.get_icon_for_file(str(path))

            image = Gtk.Image.new_from_paintable(icon)
            image.set_size_request(100, 100)
            image.set_margin_top(20)
            image.set_margin_end(20)
            image.set_margin_bottom(20)
            image.set_margin_start(20)
            image.set_vexpand(False)
            image.set_hexpand(False)
            image.set_valign(Gtk.Align.CENTER)
            image.set_halign(Gtk.Align.CENTER)

            file_box.append(path_lbl)
            file_box.append(grid)

            icon_box.append(image)

            main_box.append(icon_box)
            main_box.append(file_box)

        GLib.idle_add(self.list_box.append, self.header_content)

    def create_bottom_menu(self) -> Gtk.Box:

        horizontal_btn_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=5
        )

        horizontal_btn_box.set_halign(Gtk.Align.END)
        horizontal_btn_box.set_hexpand(True)
        horizontal_btn_box.set_margin_top(20)
        horizontal_btn_box.set_margin_start(20)

        btn_accept = Gtk.Button.new_with_label(_("Aceptar"))

        def on_accept(button: Gtk.Button):
            self.win.destroy()

        btn_accept.connect("clicked", on_accept)

        horizontal_btn_box.append(btn_accept)
        return horizontal_btn_box

    def add_loading_box(self) -> Gtk.Box:
        loading_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        spinner_header = Gtk.Spinner.new()
        spinner_header.set_size_request(50, 50)
        spinner_header.set_vexpand(True)
        spinner_header.set_valign(Gtk.Align.CENTER)
        spinner_header.start()

        lbl_loading_header = Gtk.Label.new(_("Cargando ..."))
        lbl_loading_header.set_ellipsize(Pango.EllipsizeMode.START)
        lbl_loading_header.set_max_width_chars(200)
        lbl_loading_header.set_margin_bottom(20)

        self.spinner_list.append(spinner_header)
        self.lbl_loading_header_list.append(lbl_loading_header)

        loading_box.append(spinner_header)
        loading_box.append(lbl_loading_header)

        return loading_box
