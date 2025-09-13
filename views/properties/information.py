# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from utilities.file_manager import File_manager
from entity.file_or_directory_info import File_or_directory_info
from pathlib import Path
import gi
from gi.repository import Gtk

gi.require_version("Gtk", "4.0")


class Information:

    def __init__(self, win: Gtk.Window, path_list: list[Path]):
        self.win = win
        self.path_list = path_list

    def create_information(self) -> Gtk.Box:

        self.information_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=0
        )

        self.information_box.set_margin_top(20)
        self.information_box.set_margin_end(20)
        self.information_box.set_margin_bottom(20)
        self.information_box.set_margin_start(20)

        self.information_box.append(self.add_header_resumen())
        self.information_box.append(self.add_list_path())
        self.information_box.append(self.create_bottom_menu())

        return self.information_box

    def add_header_resumen(self) -> Gtk.Box:

        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_box.set_margin_bottom(0)
        left_box.set_size_request(-1, 200)

        left_box.set_margin_bottom(20)

        left_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        left_content.set_margin_top(20)
        left_content.set_margin_end(20)
        left_content.set_margin_bottom(20)
        left_content.set_margin_start(20)

        title_label = Gtk.Label.new(_("Resumen total de las ubicaciones"))
        title_label.set_halign(Gtk.Align.START)
        title_label.set_margin_bottom(20)

        left_content.append(title_label)

        result_dict = File_manager.properties_path_list(self.path_list)

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

        left_content.append(grid)
        left_box.append(left_content)

        left_box.get_style_context().add_class("border-style")

        return left_box

    def add_list_path(self) -> Gtk.Box:

        window = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        window.get_style_context().add_class("border-style")
        window.set_vexpand(True)

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
        window.append(scrolled)

        for path in self.path_list:

            path_enty = File_or_directory_info(Path(path))
            result_dict = File_manager.properties_path(path_enty.path_file)

            main_box = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL, spacing=5
            )

            file_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
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

            content.append(main_box)

        return window

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
