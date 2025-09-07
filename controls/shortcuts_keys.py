# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from pathlib import Path
from entity.shortcut import Shortcut
from utilities.access_control import AccessControl
from utilities.compression import CompressionManager
from controls.actions import Actions
import yaml
import gi


gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib  # noqa E402


class Shortcuts_keys:

    def __init__(
        self,
        win: Gtk.Window = None,
        explorer_left: "Explorer" = None,  # noqa F821
        explorer_right: "Explorer" = None,  # noqa F821
    ):  # noqa F821

        from views.main_window import Window

        self.win = win
        self.compression_manager = CompressionManager(self.win)
        self.explorer_left = explorer_left
        self.explorer_right = explorer_right
        self.action = Actions()
        self.SHORTCUT_FILE = Path(f"{Window.APP_USER_PATH}/shorcuts_file.yaml")
        self.controller_list_exp_1 = []
        self.fav_controller_list_exp_1 = []
        self.controller_list_exp_2 = []
        self.fav_controller_list_exp_2 = []

        if not self.SHORTCUT_FILE.exists():
            self.reset_shortcuts_config()

    def load_yaml_config(self) -> list:
        try:
            with open(self.SHORTCUT_FILE, "r") as file:
                data = yaml.safe_load(file)
                return [
                    Shortcut(
                        d["first_key"],
                        d["second_key"],
                        d["method"],
                        d["description"],
                    )
                    for d in data
                ]
        except Exception as e:
            print(f"ERROR en LOAD YAML CONFIG: {e}")
            text = _(
                (
                    "Ha ocurrido algún error al abrir el archivo de configuración:\n\n"  # noqa : E501
                    f"{e}\n\n"
                    "Se carga una versión en memoria, no podrá guardar los cambios."  # noqa : E501
                )
            )
            self.action.show_msg_alert(self.win, text)
            return self.load_shortcuts_config_prede()

    def save_yaml_config(self, shortcuts_list: list) -> None:
        try:
            with open(self.SHORTCUT_FILE, "w") as file:
                yaml.dump(
                    [s.to_dict() for s in shortcuts_list], file, indent=4
                )

        except Exception as e:
            print(f"ERROR EN SAVE YAML CONFIG: {e}")
            text = _(
                (
                    "Ha ocurrido algún error al guardar el archivo de configuración:\n\n"  # noqa : E501
                    f"{e}\n\n"
                    "Cualquier cambio no se podrá conservar."  # noqa : E501
                )
            )
            self.action.show_msg_alert(self.win, text)

    def recharge_yaml_shortcuts(self):

        for controller in self.controller_list_exp_1:
            self.explorer_left.remove_controller(controller)

        for controller in self.controller_list_exp_2:
            self.explorer_right.remove_controller(controller)

        self.controller_list = []
        self.charge_yaml_shortcuts()

    def charge_yaml_shortcuts(self):
        self.list_shortcuts = self.load_yaml_config()
        for shortcut in self.list_shortcuts:
            method = getattr(self, shortcut.method)
            self.add_shortcut(
                self.explorer_left,
                shortcut.first_key,
                shortcut.second_key,
                method,
            )
            self.add_shortcut(
                self.explorer_right,
                shortcut.first_key,
                shortcut.second_key,
                method,
            )

    def add_shortcut(
        self,
        explorer: "Explorer",  # noqa F821
        first_key: str,
        second_key: str,
        method,
    ) -> None:

        from functools import partial

        trigger = Gtk.ShortcutTrigger.parse_string(f"{first_key}{second_key}")
        if first_key == "<Alt>":
            action = Gtk.CallbackAction.new(
                partial(method, index=second_key, explorer=explorer)
            )
        else:
            action = Gtk.CallbackAction.new(partial(method, explorer=explorer))

        shortcut = Gtk.Shortcut.new(trigger, action)
        controller = Gtk.ShortcutController.new()
        controller.add_shortcut(shortcut)
        explorer.add_controller(controller)

        if first_key == "<Alt>":
            if explorer.name == "explorer_1":
                self.fav_controller_list_exp_1.append(controller)
            else:
                self.fav_controller_list_exp_2.append(controller)
        else:
            if explorer.name == "explorer_1":
                self.controller_list_exp_1.append(controller)
            else:
                self.controller_list_exp_2.append(controller)

    def shortcut_mirroring_folder(
        self, widget: Gtk.Widget, *args, explorer: "explorer"  # noqa F821
    ) -> None:
        """
        Actions when shortcuts is utilized
        """
        # Disconnect key controller from main window
        self.win.key_disconnect()

        # Returns the browser that does not contain the passed name
        other_explorer = self.win.get_other_explorer_with_name(explorer.name)

        if not other_explorer:
            return

        selected_item = explorer.get_selected_items_from_explorer()[1]

        if not selected_item:
            other_explorer.load_data(explorer.actual_path.parent)

        if not selected_item:
            path = explorer.actual_path.parent
        else:
            path = selected_item[0]

        if selected_item:
            if not path.is_dir():
                path = path.parent

        other_explorer.load_data(path)

        GLib.idle_add(self.win.key_connect)

    def unzip_file(
        self, widget: Gtk.Widget, *args, explorer: "Explorer"  # noqa: F821
    ) -> None:
        exec_uncompress_window = True
        # Disconnect key controller from main window
        self.win.key_disconnect()

        selected_items = explorer.get_selected_items_from_explorer()[1]
        dst_explorer = self.win.get_other_explorer_with_name(explorer.name)
        dst_dir = dst_explorer.actual_path

        if not self.compression_manager.get_dst_suficient_space(
            selected_items, dst_dir
        ):
            self.action.show_msg_alert(
                self.win, _("No hay suficiente espacio en el destino.")
            )
            exec_uncompress_window = False

        list_files = explorer.get_selected_items_from_explorer()[1]

        ac = AccessControl()

        write_access = ac.validate_dst_write(
            list_files, None, dst_explorer, dst_dir, self.win
        )

        if not write_access:
            exec_uncompress_window = False

        from views.pop_up_windows.uncompress import UncompressWindow

        if exec_uncompress_window:
            UncompressWindow(self.win, selected_items, dst_explorer, dst_dir)

    def zip_file(
        self, widget: Gtk.Widget, *args, explorer: "Explorer"  # noqa: F821
    ):
        exec_uncompress_window = True
        # Disconnect key controller from main window
        self.win.key_disconnect()

        selected_items = explorer.get_selected_items_from_explorer()[1]
        dst_explorer = self.win.get_other_explorer_with_name(explorer.name)
        dst_dir = dst_explorer.actual_path

        from utilities.file_manager import File_manager

        list_files = explorer.get_selected_items_from_explorer()[1]

        fm = File_manager()

        if not fm.check_free_space(list_files, dst_dir):

            self.action.show_msg_alert(
                self.win, _("No hay suficiente espacio en el destino.")
            )
            exec_uncompress_window = False

        ac = AccessControl()

        write_access = ac.validate_dst_write(
            list_files, None, dst_explorer, dst_dir, self.win
        )

        if not write_access:
            exec_uncompress_window = False

        from views.pop_up_windows.compress import CompressWindow

        if exec_uncompress_window:
            CompressWindow(self.win, selected_items, dst_explorer, dst_dir)
        else:
            GLib.idle_add(self.win.key_connect)

    def add_fav_path(
        self,
        widget: Gtk.Widget,
        *args,
        explorer: "Explorer" = None,  # noqa : F821
    ) -> None:
        # Disconnect key controller from main window
        self.win.key_disconnect()

        actual_path = str(explorer.actual_path)

        if explorer.name == "explorer_1":
            fav_1 = self.win.config.FAV_PATH_LIST_1

            if len(fav_1) == 9:
                self.action.show_msg_alert(
                    self.win,
                    _("No puede añadir más favoritos al explorador izquierdo"),
                )
                return

            if actual_path not in fav_1:
                fav_1.append(actual_path)
                explorer.fav_path_list = self.win.config.FAV_PATH_LIST_1
            else:
                self.action.show_msg_alert(
                    self.win,
                    _(
                        (
                            f"El directorio: {actual_path}, ya está añadido"  # noqa:E501
                            f" a los favoritos de {explorer.name}"
                        )
                    ),
                )

        else:
            fav_2 = self.win.config.FAV_PATH_LIST_2

            if len(fav_2) == 9:
                self.action.show_msg_alert(
                    self.win,
                    _("No puede añadir más favoritos al explorador derecho"),
                )
                return

            if actual_path not in fav_2:
                fav_2.append(actual_path)
                explorer.fav_path_list = self.win.config.FAV_PATH_LIST_2
            else:
                self.action.show_msg_alert(
                    self.win,
                    _(
                        (
                            f"El directorio: {actual_path}, ya está añadido"  # noqa:E501
                            f" a los favoritos de {explorer.name}"
                        )
                    ),
                )

        self.win.save_config_file(self.win.config)
        self.win.load_botons_fav()
        GLib.idle_add(self.win.key_connect)

    def del_fav_path(
        self,
        widget: Gtk.Widget,
        *args,
        explorer: "Explorer" = None,  # noqa : F821
    ) -> None:
        # Disconnect key controller from main window
        self.win.key_disconnect()

        actual_path = str(explorer.actual_path)

        if explorer.name == "explorer_1":
            fav_1 = self.win.config.FAV_PATH_LIST_1
            if actual_path in fav_1:
                fav_1.remove(str(explorer.actual_path))
        else:
            fav_2 = self.win.config.FAV_PATH_LIST_2
            if actual_path in fav_2:
                fav_2.remove(str(explorer.actual_path))

        self.win.save_config_file(self.win.config)
        self.win.load_botons_fav()
        GLib.idle_add(self.win.key_connect)

    def change_fav_explorer_path(
        self,
        widget: Gtk.Widget,
        *args,
        index: str,
        explorer: "explorer" = None,  # noqa : F821
    ) -> bool:
        # Disconnect key controller from main window
        self.win.key_disconnect()
        if widget.fav_path_list:
            list_index = int(index) - 1
            path = Path(widget.fav_path_list[list_index])
            widget.load_new_path(path)

        GLib.idle_add(self.win.key_connect)
        return True

    def reset_shortcuts_config(self) -> None:
        shortcuts_dict = self.load_shortcuts_config_prede()
        self.save_yaml_config(shortcuts_dict)

    def exit(
        self, widget: Gtk.Widget, *args, explorer: "Explorer"  # noqa: F821
    ) -> None:
        self.win.exit()

    def show_shortcut(
        self, widget: Gtk.Widget, *args, explorer: "Explorer"  # noqa: F821
    ) -> None:
        from views.menu_bar.help.shortcuts_help import ShortCutsHelp

        ShortCutsHelp(self.win)

    def load_shortcuts_config_prede(self) -> list[Shortcut]:

        _("Muestra la carpeta en el otro explorador.")
        _("Para descomprimir archivos")
        _("Para comprimir archivos")
        _("Para añadir directorios en favoritos")
        _("Para eliminar directorios en favoritos")
        _("Salir de la aplicación")
        _("Muestra información sobre atajos de teclado")

        return [
            Shortcut(
                "<Control>",
                "o",
                "shortcut_mirroring_folder",
                "Muestra la carpeta en el otro explorador.",
            ),
            Shortcut(
                "<Control>",
                "p",
                "unzip_file",
                "Para descomprimir archivos",
            ),
            Shortcut(
                "<Control>",
                "i",
                "zip_file",
                "Para comprimir archivos",
            ),
            Shortcut(
                "<Control>",
                "f",
                "add_fav_path",
                "Para añadir directorios en favoritos",
            ),
            Shortcut(
                "<Control>",
                "d",
                "del_fav_path",
                "Para eliminar directorios en favoritos",
            ),
            Shortcut(
                "<Control>",
                "q",
                "exit",
                "Salir de la aplicación",
            ),
            Shortcut(
                "<Control>",
                "apostrophe",
                "show_shortcut",
                "Muestra información sobre atajos de teclado",
            ),
        ]
