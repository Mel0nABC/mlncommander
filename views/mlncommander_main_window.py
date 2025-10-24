# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from controls import action_keys
from controls import actions
from entity.config import ConfigEntity
from views.menu_bar.mlncommander_menu_bar_view import Menu_bar
from views.search_bar.mlncommander_pathbar import PathBar
from views.pop_up_windows.header import header
from views.mlncommander_explorer import Explorer
from utilities.my_copy_or_move import MyCopyMove
from utilities.create import Create
from utilities.remove import Remove
from utilities.new_file import NewFile
from utilities.file_manager import File_manager
from css.explorer_css import Css_explorer_manager
from controls.shortcuts_keys import Shortcuts_keys
from functools import partial
from pathlib import Path
import yaml
import os
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib, Pango, Gdk  # noqa E402


class Window(Gtk.ApplicationWindow):

    # Use XDG config user path.
    USER_HOME = ""
    try:
        USER_HOME = os.environ["XDG_CONFIG_HOME"]
    except KeyError:
        USER_HOME = Path(f"{os.environ["HOME"]}/.config")

    APP_USER_PATH = Path(f"{USER_HOME}/.mlncommander")

    def __init__(self, app: Gtk.Application, action: actions):
        super().__init__(application=app)

        # check app folder on user dir exist

        username = os.getlogin()

        if username in str(Window.APP_USER_PATH):
            if not Window.APP_USER_PATH.exists():
                Window.APP_USER_PATH.mkdir()
        self.app = app
        self.action = action
        self.key_controller_id = 0
        self.explorer_src = None
        self.explorer_dst = None
        self.entry_margin = 10
        self.horizontal_button_list_margin = 10
        self.horizontal_botton_menu = None
        self.scroll_margin = 10
        self.label_left_selected_files = None
        self.label_right_selected_files = None
        self.config = ConfigEntity()
        self.CONFIG_FILE = Path(f"{Window.APP_USER_PATH}/config.yaml")
        self.error_fav_path_shown = False
        self.horizontal_bottom = None
        self.menu_bar = None
        self.explorer_1 = None
        self.explorer_2 = None
        self.css_manager = Css_explorer_manager(self)

        # to use in watchdog
        self.write_error_msg_displayer = False

        # We load the configuration, to send necessary variables
        self.load_config_file()

        # We get information from the screen

        from utilities.screen_info import ScreenInfo

        self.horizontal = ScreenInfo.horizontal
        self.vertical = ScreenInfo.vertical

        self.set_default_size(self.horizontal / 2, self.vertical)

        self.set_titlebar(header().header)

        self.set_resizable(True)

        self.main_vertical_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )

        self.create_menu_bar()
        self.create_explorers()
        self.create_horizontal_button()

        self.set_child(self.main_vertical_box)

        # Event controller to control keys
        self.key_controller = Gtk.EventControllerKey.new()
        self.key_connect()
        self.add_controller(self.key_controller)

        # Load css
        if self.config.SWITCH_CSS_STATUS:
            self.load_css_application()

        def on_close(signal):
            self.action.close_with_question(win=self)
            return True

        self.connect("close-request", on_close)

    def load_css_application(self):
        # Load css
        self.get_style_context().add_class("app_background")
        self.get_style_context().add_class("font")
        self.get_style_context().add_class("font-color")

        self.add_fav_btn_1.get_style_context().add_class("button")
        self.add_fav_btn_2.get_style_context().add_class("button")
        self.del_fav_btn_1.get_style_context().add_class("button")
        self.del_fav_btn_2.get_style_context().add_class("button")

        self.btn_F12.get_style_context().add_class("button")
        self.btn_F7.get_style_context().add_class("button")
        self.btn_F6.get_style_context().add_class("button")
        self.btn_F5.get_style_context().add_class("button")
        self.btn_F3.get_style_context().add_class("button")
        self.btn_F2.get_style_context().add_class("button")
        self.btn_F8.get_style_context().add_class("button")
        self.btn_F9.get_style_context().add_class("button")

        self.css_manager.load_css()

    def create_explorers(self):

        self.horizontal_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        self.horizontal_box.set_vexpand(True)
        self.horizontal_box.set_homogeneous(True)

        self.vertical_screen_1 = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        self.vertical_screen_1.set_vexpand(True)
        self.vertical_screen_2 = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        self.vertical_screen_2.set_vexpand(True)

        # Fav path start

        self.button_main_1 = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        self.button_main_1.set_margin_start(self.entry_margin)
        self.button_main_1.set_margin_end(self.entry_margin / 2)
        self.button_main_1.set_margin_bottom(self.entry_margin)

        self.button_main_1.set_hexpand(True)

        self.button_main_2 = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        self.button_main_2.set_margin_start(self.entry_margin / 2)
        self.button_main_2.set_margin_end(self.entry_margin)
        self.button_main_2.set_margin_bottom(self.entry_margin)

        self.button_main_2.set_hexpand(True)

        # Add btn

        self.add_fav_btn_1 = Gtk.Button.new_with_label("+")
        self.add_fav_btn_2 = Gtk.Button.new_with_label("+")

        self.add_fav_btn_1.set_hexpand(False)
        self.add_fav_btn_2.set_hexpand(False)

        # Del btn

        self.del_fav_btn_1 = Gtk.Button.new_with_label("-")
        self.del_fav_btn_2 = Gtk.Button.new_with_label("-")
        self.del_fav_btn_1.set_hexpand(False)
        self.del_fav_btn_2.set_hexpand(False)

        self.buttom_horizontal_1 = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        self.buttom_horizontal_1.set_hexpand(True)

        self.buttom_horizontal_2 = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        self.buttom_horizontal_2.set_hexpand(True)

        self.vertical_screen_1.append(self.button_main_1)
        self.vertical_screen_2.append(self.button_main_2)

        self.button_main_1.append(self.buttom_horizontal_1)
        self.button_main_2.append(self.buttom_horizontal_2)

        self.button_main_1.append(self.add_fav_btn_1)
        self.button_main_1.append(self.del_fav_btn_1)

        self.button_main_2.append(self.add_fav_btn_2)
        self.button_main_2.append(self.del_fav_btn_2)

        # Fav path final

        self.explorer_1 = Explorer(
            "explorer_1",
            self,
            self.config.EXP_1_PATH,
            Window.APP_USER_PATH,
            self.add_fav_btn_1,
        )

        self.explorer_2 = Explorer(
            "explorer_2",
            self,
            self.config.EXP_2_PATH,
            Window.APP_USER_PATH,
            self.add_fav_btn_2,
        )

        # Entrys section start

        self.search_str_entry = Gtk.Entry()  # Entry to show search text. Hiden
        self.search_str_entry.set_editable(False)

        self.path_bar_1 = PathBar(
            self,
            self.entry_margin,
            str(self.config.EXP_1_PATH),
            self.explorer_1,
        )
        self.path_bar_2 = PathBar(
            self,
            self.entry_margin,
            str(self.config.EXP_2_PATH),
            self.explorer_2,
        )

        self.vertical_screen_1.append(self.path_bar_1)
        self.vertical_screen_2.append(self.path_bar_2)

        # Entrys section final

        self.explorer_1.search_str_entry = self.search_str_entry
        self.explorer_2.search_str_entry = self.search_str_entry

        self.explorer_1.entry_box = self.path_bar_1
        self.explorer_2.entry_box = self.path_bar_2

        # load shortcuts
        self.shortcuts = Shortcuts_keys(self, self.explorer_1, self.explorer_2)
        self.shortcuts.charge_yaml_shortcuts()

        self.scroll_1 = Gtk.ScrolledWindow()
        self.scroll_1.set_policy(
            Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC
        )

        self.scroll_1.set_vexpand(True)
        self.scroll_1.set_hexpand(True)
        self.scroll_1.set_margin_end(self.scroll_margin / 2)
        self.scroll_1.set_margin_start(self.scroll_margin)
        self.scroll_1.set_child(self.explorer_1)

        self.scroll_2 = Gtk.ScrolledWindow()
        self.scroll_2.set_policy(
            Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC
        )
        self.scroll_2.set_vexpand(True)
        self.scroll_2.set_hexpand(True)
        self.scroll_2.set_margin_end(self.scroll_margin)
        self.scroll_2.set_margin_start(self.scroll_margin / 2)
        self.scroll_2.set_child(self.explorer_2)

        self.vertical_screen_1.append(self.scroll_1)
        self.vertical_screen_2.append(self.scroll_2)

        self.horizontal_box.append(self.vertical_screen_1)
        self.horizontal_box.append(self.vertical_screen_2)

        self.main_vertical_box.append(self.horizontal_box)

        # Signals and events area

        self.explorer_1.connect(
            "activate",
            self.action.on_doble_click_or_enter,
            self.explorer_1,
            self.path_bar_1.search_entry,
        )
        self.explorer_2.connect(
            "activate",
            self.action.on_doble_click_or_enter,
            self.explorer_2,
            self.path_bar_2.search_entry,
        )

        # fav buttons signals

        self.add_fav_btn_1.connect(
            "clicked",
            partial(self.shortcuts.add_fav_path, explorer=self.explorer_1),
        )

        self.add_fav_btn_2.connect(
            "clicked",
            partial(self.shortcuts.add_fav_path, explorer=self.explorer_2),
        )

        self.del_fav_btn_1.connect(
            "clicked",
            partial(self.shortcuts.del_fav_path, explorer=self.explorer_1),
        )

        self.del_fav_btn_2.connect(
            "clicked",
            partial(self.shortcuts.del_fav_path, explorer=self.explorer_2),
        )

    def create_menu_bar(self):
        self.menu_bar = Menu_bar(self)
        self.main_vertical_box.append(self.menu_bar.menubar)

    def create_horizontal_button(self):

        self.horizontal_botton_menu = Gtk.FlowBox(
            orientation=Gtk.Orientation.HORIZONTAL
        )  # Noqa E501
        self.horizontal_botton_menu.set_max_children_per_line(10)

        self.horizontal_botton_menu.set_margin_top(
            self.horizontal_button_list_margin
        )
        self.horizontal_botton_menu.set_margin_end(
            self.horizontal_button_list_margin
        )
        self.horizontal_botton_menu.set_margin_bottom(
            self.horizontal_button_list_margin
        )
        self.horizontal_botton_menu.set_margin_start(
            self.horizontal_button_list_margin
        )

        self.horizontal_botton_menu.set_selection_mode(Gtk.SelectionMode.NONE)

        self.btn_F2 = Gtk.Button(label=_("Renombrar < F2 >"))
        self.horizontal_botton_menu.append(self.btn_F2)

        self.btn_F3 = Gtk.Button(label=_("Nuevo Fichero < F3 >"))
        self.horizontal_botton_menu.append(self.btn_F3)

        self.btn_F5 = Gtk.Button(label=_("Copiar < F5 >"))
        self.horizontal_botton_menu.append(self.btn_F5)

        self.btn_F6 = Gtk.Button(label=_("Mover < F6 >"))
        self.horizontal_botton_menu.append(self.btn_F6)

        self.btn_F7 = Gtk.Button(label=_("Crear dir < F7 >"))
        self.horizontal_botton_menu.append(self.btn_F7)

        self.btn_F8 = Gtk.Button(label=_("Eliminar < F8 >"))
        self.horizontal_botton_menu.append(self.btn_F8)

        self.btn_F9 = Gtk.Button(label=_("Duplicar < F9 >"))
        self.horizontal_botton_menu.append(self.btn_F9)

        self.btn_F12 = Gtk.Button(label=_("Salir < F12 >"))
        self.horizontal_botton_menu.append(self.btn_F12)

        # Left label show selection info
        label_box_left = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        self.label_left_selected_files = Gtk.Label(label="--")
        label_box_left.append(self.label_left_selected_files)

        # Right label show selection info
        label_box_right = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        self.label_right_selected_files = Gtk.Label(label="--")

        label_box_right.append(self.label_right_selected_files)

        label_box_right.set_halign(Gtk.Align.END)

        self.horizontal_botton_menu.set_halign(Gtk.Align.CENTER)

        self.horizontal_bottom = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        self.horizontal_bottom.set_halign(Gtk.Align.CENTER)

        self.horizontal_bottom.append(label_box_left)
        self.horizontal_bottom.append(self.horizontal_botton_menu)
        self.horizontal_bottom.append(label_box_right)

        self.horizontal_bottom.set_margin_start(self.scroll_margin + 20)
        self.horizontal_bottom.set_margin_end(self.scroll_margin + 20)

        self.main_vertical_box.append(self.horizontal_bottom)

        # rename_logic = Rename_Logic()
        self.btn_F2.connect(
            "clicked",
            lambda btn: self.action.open_rename_dialog(
                self.explorer_src,
                self,
                self.explorer_src.popovermenu,
            ),
        )

        new_file = NewFile()
        self.btn_F3.connect(
            "clicked",
            lambda btn: new_file.on_new_file(self.explorer_src, self),
        )

        my_copy_move = MyCopyMove()
        self.btn_F5.connect(
            "clicked",
            lambda btn: my_copy_move.on_copy_or_move(
                self.explorer_src,
                self.explorer_dst,
                None,
                self,
                _("copiar"),
                False,
            ),
        )

        self.btn_F6.connect(
            "clicked",
            lambda btn: my_copy_move.on_copy_or_move(
                self.explorer_src,
                self.explorer_dst,
                None,
                self,
                _("mover"),
                False,
            ),
        )

        create = Create()
        self.btn_F7.connect(
            "clicked",
            lambda btn: create.on_create_dir(
                self.explorer_src, self.explorer_dst, self
            ),
        )
        remove = Remove()
        self.btn_F8.connect(
            "clicked",
            lambda btn: remove.on_delete(
                self.explorer_src, self.explorer_dst, self
            ),
        )

        self.btn_F9.connect(
            "clicked",
            lambda btn: my_copy_move.on_copy_or_move(
                self.explorer_src,
                self.explorer_dst,
                None,
                self,
                _("copiar"),
                True,
            ),
        )

        self.btn_F12.connect(
            "clicked", partial(self.action.close_with_question, win=self)
        )

        self.connect("realize", self.on_realize)

    def on_realize(self, widget: Gtk.Widget) -> None:
        """
        Set browser 1 (left) as default when starting the application
        """
        # LOAD DATA DIRECTORY
        self.explorer_1.load_new_path(self.explorer_1.actual_path)
        self.explorer_2.load_new_path(self.explorer_2.actual_path)

        # Load favorite folders
        self.explorer_1.fav_path_list = self.config.FAV_PATH_LIST_1
        self.explorer_2.fav_path_list = self.config.FAV_PATH_LIST_2
        self.load_botons_fav()

        # We set the initial focus to explorer_1, left
        self.action.set_explorer_to_focused(self.explorer_1, self)
        self.explorer_src = self.explorer_1
        self.explorer_dst = self.explorer_2

    def key_connect(self) -> None:

        self.key_controller_id = self.key_controller.connect(
            "key-pressed", action_keys.on_key_press, self, self.action
        )

    def key_disconnect(self) -> None:
        self.key_controller.disconnect(self.key_controller_id)

    def set_explorer_focused(
        self, explorer_focused: Explorer, explorer_unfocused: Explorer
    ) -> None:
        """
        Set focus on explorer
        """
        self.explorer_src = explorer_focused
        self.explorer_src.grab_focus()
        n_row = self.explorer_src.path_history[self.explorer_src.actual_path]
        self.explorer_src.scroll_to(n_row, None, self.explorer_src.flags)
        self.explorer_dst = explorer_unfocused

    def get_explorer_focused(self) -> Explorer:
        return [
            exp for exp in [self.explorer_1, self.explorer_2] if exp.focused
        ][0]

    def exit(self, win: Gtk.ApplicationWindow = None) -> None:
        """
        Close services, save configuration and close application
        """
        self.close()
        self.stop_to_close()
        self.destroy()

    def stop_to_close(self) -> None:

        if self.explorer_1.my_watchdog:
            self.explorer_1.my_watchdog.stop()

        if self.explorer_2.my_watchdog:
            self.explorer_2.my_watchdog.stop()

        if self.config.SHOW_DIR_LAST:
            self.config.EXP_1_PATH = str(self.explorer_1.actual_path)
            self.config.EXP_2_PATH = str(self.explorer_2.actual_path)

        self.save_config_file(self.config)

    def load_config_file(self) -> None:
        """
        load config file
        """
        # If no configuration exists, it creates it, with default options
        try:
            if not self.CONFIG_FILE.exists():
                self.config.create_new_config()
                with open(self.CONFIG_FILE, "w") as config_file:
                    yaml.dump(
                        self.config.to_dict(), config_file, sort_keys=False
                    )
            # We open configuration and load in variables.
            with open(self.CONFIG_FILE, "r+") as config_file:
                data = yaml.safe_load(config_file)

                # GENERAL

                self.config.LANGUAGE = data["LANGUAGE"]

                self.load_env_language()

                self.config.SWITCH_COPY_STATUS = data["SWITCH_COPY_STATUS"]
                self.config.SWITCH_MOVE_STATUS = data["SWITCH_MOVE_STATUS"]
                self.config.SWITCH_DUPLICATE_STATUS = data[
                    "SWITCH_DUPLICATE_STATUS"
                ]
                self.config.SWITCH_COMPRESS_STATUS = data[
                    "SWITCH_COMPRESS_STATUS"
                ]
                self.config.SWITCH_UNCOMPRESS_STATUS = data[
                    "SWITCH_UNCOMPRESS_STATUS"
                ]

                # DIRECTORYS

                self.config.FAV_PATH_LIST_1 = data["FAV_PATH_LIST_1"]
                self.config.FAV_PATH_LIST_2 = data["FAV_PATH_LIST_2"]

                EXP_1_PATH = Path(data["EXP_1_PATH"])
                result = File_manager().get_path_list(EXP_1_PATH)
                if result:
                    if not EXP_1_PATH.exists():
                        self.config.EXP_1_PATH = "/"
                    else:
                        self.config.EXP_1_PATH = data["EXP_1_PATH"]
                else:
                    self.config.EXP_1_PATH = Path("/")

                EXP_2_PATH = Path(data["EXP_2_PATH"])
                result = File_manager().get_path_list(EXP_2_PATH)
                if result:
                    if not EXP_2_PATH.exists():
                        self.config.EXP_2_PATH = "/"
                    else:
                        self.config.EXP_2_PATH = data["EXP_2_PATH"]
                else:
                    self.config.EXP_2_PATH = Path("/")

                self.config.SHOW_DIR_LAST = bool(data["SHOW_DIR_LAST"])
                self.config.SWITCH_IMG_STATUS = bool(data["SWITCH_IMG_STATUS"])
                self.config.SWITCH_WATCHDOG_STATUS = bool(
                    data["SWITCH_WATCHDOG_STATUS"]
                )
                self.config.TERMINAL_COMMAND = data["TERMINAL_COMMAND"]

                # APPEARANCE
                self.config.SWITCH_CSS_STATUS = data["SWITCH_CSS_STATUS"]
                self.config.COLOR_BACKGROUND_APP = data["COLOR_BACKGROUND_APP"]
                self.config.COLOR_EXPLORER_LEFT = data["COLOR_EXPLORER_LEFT"]
                self.config.COLOR_EXPLORER_RIGHT = data["COLOR_EXPLORER_RIGHT"]
                self.config.COLOR_BACKGROUND_SEARCH = data[
                    "COLOR_BACKGROUND_SEARCH"
                ]
                self.config.COLOR_ENTRY = data["COLOR_ENTRY"]
                self.config.COLOR_SEARCH_TEXT = data["COLOR_SEARCH_TEXT"]
                self.config.COLOR_BUTTON = data["COLOR_BUTTON"]
                self.config.COLOR_FAV_BUTTON = data["COLOR_FAV_BUTTON"]
                self.config.FONT_STYLE = data["FONT_STYLE"]
                self.config.FONT_STYLE_COLOR = data["FONT_STYLE_COLOR"]
                self.config.THEME_NAME = data["THEME_NAME"]

        except Exception as e:
            text = _(
                (
                    "Ha ocurrido algún error al abrir el archivo de configuración:\n\n"  # noqa : E501
                    f"{e}\n\n"
                    "Se carga una versión en memoria, no podrá guardar los cambios."  # noqa : E501
                )
            )
            self.action.show_msg_alert(self, text)

    def save_config_file(self, config: ConfigEntity) -> None:
        """
        Saves the settings to the current location
        where the browsers are located
        """
        try:
            self.config = config
            # Config is deleted and the entire configuration is saved.
            with open(self.CONFIG_FILE, "w") as config_file:
                yaml.dump(config.to_dict(), config_file, sort_keys=False)

        except Exception as e:
            text = _(
                (
                    "Ha ocurrido algún error al guardar el archivo de configuración:\n\n"  # noqa : E501
                    f"{e}\n\n"
                    "Se carga una versión en memoria, no podrá guardar los cambios."  # noqa : E501
                )
            )
            self.action.show_msg_alert(self, text)

    def get_other_explorer_with_name(self, name: str) -> Explorer:
        """
        Returns the browser that does not contain the passed name
        """
        for explorer in [self.explorer_1, self.explorer_2]:
            if explorer.name != name:
                return explorer

        return None

    def to_down_explorer(self, explorer_name: str, widget: Gtk.Widget) -> None:

        if explorer_name == "explorer_1":
            self.vertical_screen_1.append(widget)
        else:
            self.vertical_screen_2.append(widget)

    def finish_to_down_explorer(
        self, explorer_name: str, widget: Gtk.Widget
    ) -> None:

        if explorer_name == "explorer_1":
            self.vertical_screen_1.remove(widget)
        else:
            self.vertical_screen_2.remove(widget)

    def load_botons_fav(self) -> None:

        self.clear_botons_fav()

        def add_fav_btn(
            explorer: Explorer,
            button_horizontal_box: Gtk.Box,
            path: Path,
            position: int,
        ) -> Gtk.Button:
            text_lbl = f"[ {position+1} ] : {str(path)}"
            lbl = Gtk.Label.new(text_lbl)
            lbl.set_ellipsize(Pango.EllipsizeMode.START)
            btn = Gtk.Button.new()
            btn.set_child(lbl)
            btn.set_hexpand(False)
            btn.set_halign(Gtk.Align.START)
            btn.connect(
                "clicked",
                lambda btn: explorer.load_new_path(path),
            )

            button_horizontal_box.append(btn)
            explorer.fav_path_btn_list.append(btn)
            return btn

        self.path_fav_no_exist_list = []
        self.path_fav_no_read_permission = []

        def load_explorer_fav_button_list(
            explorer: "Explorer",
            button_horizontal_box: Gtk.Box,
        ) -> None:
            if explorer.fav_path_list:
                fav_path_list = enumerate(explorer.fav_path_list)
                for index, path_str in fav_path_list:
                    path = Path(path_str)

                    disable_btn = False

                    self.store = File_manager().get_path_list(path)

                    if not self.store:
                        self.path_fav_no_exist_list.append(path)
                        disable_btn = True
                    elif not os.access(path, os.R_OK):
                        self.path_fav_no_read_permission.append(path)
                        disable_btn = True

                    btn = add_fav_btn(
                        explorer, button_horizontal_box, path, index
                    )

                    if disable_btn:
                        btn.hide()

                    method = getattr(
                        self.shortcuts,
                        "change_fav_explorer_path",
                    )
                    self.shortcuts.add_shortcut(
                        explorer,
                        "<Alt>",
                        index + 1,
                        method,
                    )

        load_explorer_fav_button_list(
            self.explorer_1, self.buttom_horizontal_1
        )
        load_explorer_fav_button_list(
            self.explorer_2, self.buttom_horizontal_2
        )

        self.explorer_1.set_on_path_fav_button()
        self.explorer_2.set_on_path_fav_button()

        if self.error_fav_path_shown:
            return True

        if self.path_fav_no_exist_list or self.path_fav_no_read_permission:
            text = _(
                (
                    "No existen algunas rutas en favoritos"
                    " o no disponen de permiso de lectura:\n\n"
                )
            )

            if self.path_fav_no_exist_list:
                text += "No existe:\n\n"

            for path in self.path_fav_no_exist_list:
                text += f"      - {path}\n"

            if self.path_fav_no_read_permission:
                text += "\nSin permiso de lectura:\n\n"

            for path in self.path_fav_no_read_permission:
                text += f"      - {path}\n"

            text += _(
                (
                    "\nHan sido deshabilitadas para esta sesión.\n\n"
                    "Este mensaje sólo saldrá al iniciar la aplicación.\n\n"
                )
            )

            self.action.show_msg_alert(self, text)
            self.error_fav_path_shown = True

        return True

    def clear_botons_fav(self) -> None:

        self.explorer_1.fav_path_btn_list = None
        self.explorer_1.fav_path_btn_list = []

        self.explorer_2.fav_path_btn_list = None
        self.explorer_2.fav_path_btn_list = []

        for controller in self.shortcuts.fav_controller_list_exp_1:
            widget = controller.get_widget()
            widget.remove_controller(controller)
            self.shortcuts.fav_controller_list_exp_1.remove(controller)

        for controller in self.shortcuts.fav_controller_list_exp_2:
            widget = controller.get_widget()
            widget.remove_controller(controller)
            self.shortcuts.fav_controller_list_exp_2.remove(controller)

        child = None
        for button_box in [self.buttom_horizontal_1, self.buttom_horizontal_2]:
            child = button_box.get_first_child()
            while child is not None:
                child = button_box.get_first_child()
                if child:
                    button_box.remove(child)

        return True

    def reload_for_language(self) -> None:

        self.menu_bar.preferences.destroy()

        self.explorer_1.my_watchdog.stop()
        self.explorer_2.my_watchdog.stop()

        old_path_explorer_1 = self.explorer_1.actual_path
        old_path_explorer_2 = self.explorer_2.actual_path

        self.main_vertical_box.remove(self.menu_bar.menubar)
        self.main_vertical_box.remove(self.horizontal_box)
        self.main_vertical_box.remove(self.horizontal_bottom)

        self.create_menu_bar()
        self.create_explorers()
        self.create_horizontal_button()

        self.explorer_1.load_new_path(old_path_explorer_1)
        self.explorer_2.load_new_path(old_path_explorer_2)

        self.menu_bar.open_preferences()

    def load_env_language(self):
        if self.config.LANGUAGE == "gb" or self.config.LANGUAGE == "us":
            os.environ["LANG"] = "en_US.UTF-8"

        elif self.config.LANGUAGE == "es":
            os.environ["LANG"] = "es_ES.UTF-8"
