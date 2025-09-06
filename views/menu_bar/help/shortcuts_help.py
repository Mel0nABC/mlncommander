# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from controls.shortcuts_keys import Shortcuts_keys
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


class ShortCutsHelp(Gtk.Window):

    def __init__(self, win):
        super().__init__(transient_for=win)
        header = Gtk.HeaderBar()
        header.set_title_widget(
            Gtk.Label(label=_("Descripción de los atajos de teclado"))
        )

        self.win = win

        self.get_style_context().add_class("app_background")
        self.get_style_context().add_class("font")
        self.get_style_context().add_class("font-color")

        self.set_titlebar(header)

        main_margin = 50

        grid_right = Gtk.Grid(column_spacing=10, row_spacing=20)
        grid_left = Gtk.Grid(column_spacing=10, row_spacing=20)

        main_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        main_horizontal_box.set_margin_top(main_margin)
        main_horizontal_box.set_margin_end(main_margin)
        main_horizontal_box.set_margin_bottom(main_margin)
        main_horizontal_box.set_margin_start(main_margin)
        main_horizontal_box.append(grid_right)
        main_horizontal_box.append(grid_left)

        self.set_child(main_horizontal_box)

        shortcut_list = Shortcuts_keys().load_yaml_config()
        shortcut_dict = {str(short.method): short for short in shortcut_list}

        lbl_event_app = Gtk.Label.new(_("Eventos de aplicación"))
        lbl_event_explorer = Gtk.Label.new(_("Eventos de los explorador"))
        lbl_event_files = Gtk.Label.new(_("Acciones sobre ficheros y carpeta"))
        lbl_event_app.set_hexpand(False)

        lbl_event_app.set_halign(Gtk.Align.START)
        lbl_event_explorer.set_halign(Gtk.Align.START)
        lbl_event_files.set_halign(Gtk.Align.START)

        main_margin = 20

        lbl_event_app.set_margin_start(main_margin)
        lbl_event_app.set_margin_top(main_margin)
        lbl_event_app.set_margin_bottom(main_margin)

        lbl_event_explorer.set_margin_start(main_margin)
        lbl_event_explorer.set_margin_top(main_margin)
        lbl_event_explorer.set_margin_bottom(main_margin)

        lbl_event_files.set_margin_start(main_margin)
        lbl_event_files.set_margin_top(main_margin)
        lbl_event_files.set_margin_bottom(main_margin)

        exit_short = shortcut_dict["exit"]
        shortcut_mirroring_short = shortcut_dict["shortcut_mirroring_folder"]
        unzip_file_short = shortcut_dict["unzip_file"]
        zip_file_short = shortcut_dict["zip_file"]
        add_fav_path_short = shortcut_dict["add_fav_path"]
        del_fav_path_short = shortcut_dict["del_fav_path"]
        show_shortcut_short = shortcut_dict["show_shortcut"]

        grid_right.attach(lbl_event_app, 1, 0, 1, 1)
        grid_right.attach(
            self.create_buttons(
                "F10", description=_("Salir de la aplicación")
            ),
            1,
            1,
            1,
            1,
        )
        grid_right.attach(
            self.create_buttons(
                exit_short.first_key,
                exit_short.second_key,
                "+",
                exit_short.description,
            ),
            1,
            2,
            1,
            1,
        )
        grid_right.attach(
            self.create_buttons(
                show_shortcut_short.first_key,
                show_shortcut_short.second_key,
                "+",
                show_shortcut_short.description,
            ),
            1,
            3,
            1,
            1,
        )

        grid_right.attach(lbl_event_explorer, 1, 4, 1, 1)

        grid_right.attach(
            self.create_buttons(
                shortcut_mirroring_short.first_key,
                shortcut_mirroring_short.second_key,
                "+",
                shortcut_mirroring_short.description,
            ),
            1,
            5,
            1,
            1,
        )

        grid_right.attach(
            self.create_buttons(
                add_fav_path_short.first_key,
                add_fav_path_short.second_key,
                "+",
                add_fav_path_short.description,
            ),
            1,
            6,
            1,
            1,
        )

        grid_right.attach(
            self.create_buttons(
                del_fav_path_short.first_key,
                del_fav_path_short.second_key,
                "+",
                del_fav_path_short.description,
            ),
            1,
            7,
            1,
            1,
        )

        grid_right.attach(
            self.create_buttons(
                "Alt",
                "n",
                "+",
                _(
                    (
                        "Entrada al directorio de favoritos del explorador,\n"
                        "donde n, es un nº comprendido del 1 al 9"
                    )
                ),
            ),
            1,
            8,
            1,
            1,
        )

        grid_left.attach(lbl_event_files, 1, 9, 1, 1)

        grid_left.attach(
            self.create_buttons(
                "F2", description=_("Renombrar fichero o carpeta")
            ),
            1,
            10,
            1,
            1,
        )

        grid_left.attach(
            self.create_buttons(
                "F3", description=_("Crear nuevo fichero ofimática")
            ),
            1,
            11,
            1,
            1,
        )

        grid_left.attach(
            self.create_buttons(
                "F5", description=_("Copiar ficheros o carpetas")
            ),
            1,
            12,
            1,
            1,
        )

        grid_left.attach(
            self.create_buttons(
                "F6", description=_("Mover ficheros o carpetas")
            ),
            1,
            13,
            1,
            1,
        )

        grid_left.attach(
            self.create_buttons("F7", description=_("Crear directorio")),
            1,
            14,
            1,
            1,
        )

        grid_left.attach(
            self.create_buttons(
                "F8",
                "Supr",
                simbol="o",
                description=_("Borrar ficheros o directorios"),
            ),
            1,
            15,
            1,
            1,
        )

        grid_left.attach(
            self.create_buttons(
                "F9", description=_("Generar copia de ficheros o directorios")
            ),
            1,
            16,
            1,
            1,
        )

        grid_left.attach(
            self.create_buttons("F10", description=_("Cerrar la aplicación")),
            1,
            17,
            1,
            1,
        )

        grid_left.attach(
            self.create_buttons(
                zip_file_short.first_key,
                zip_file_short.second_key,
                "+",
                zip_file_short.description,
            ),
            1,
            18,
            1,
            1,
        )

        grid_left.attach(
            self.create_buttons(
                unzip_file_short.first_key,
                unzip_file_short.second_key,
                "+",
                unzip_file_short.description,
            ),
            1,
            19,
            1,
            1,
        )

        self.present()

    def create_buttons(
        self,
        first_key: str = None,
        second_key: str = None,
        simbol: str = None,
        description: str = None,
    ) -> Gtk.Box:

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        btn_box.set_size_request(250, -1)

        if first_key == "<Control>":
            first_key = "Ctrl"

        if second_key == "apostrophe":
            second_key = "?"

        margin = 20

        btn = Gtk.Button.new_with_label(_(first_key))
        btn.set_sensitive(False)
        btn.set_size_request(80, -1)
        btn.set_margin_end(margin)
        btn.set_margin_start(margin)

        btn_box.append(btn)

        if second_key:
            lbl = Gtk.Label.new(simbol)

            btn2 = Gtk.Button.new_with_label(_(second_key))
            btn2.set_sensitive(False)
            btn2.set_size_request(80, -1)
            btn2.set_margin_end(margin)
            btn2.set_margin_start(margin)

            btn_box.append(lbl)
            btn_box.append(btn2)

        lbl_description = Gtk.Label.new(description)

        main_box.append(btn_box)
        main_box.append(lbl_description)

        return main_box
