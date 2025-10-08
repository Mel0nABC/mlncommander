# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from views.menu_bar.file.preferences.directory import Directory
from views.menu_bar.file.preferences.general import General
from views.menu_bar.file.preferences.appearance import Appearance
from views.menu_bar.file.preferences.shortcuts import Shortcuts
from utilities.utilities_for_window import UtilsForWindow
from entity.config import ConfigEntity
from controls.actions import Actions
import shutil
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


class Preferences(Gtk.Window):

    def __init__(self, win: Gtk.ApplicationWindow, parent: Gtk.Widget):
        super().__init__(transient_for=win)

        self.GENERAL_LABEL_BTN = _("General")
        self.DIRECTORY_LABEL_BTN = _("Directorios")
        self.APPEARANCE_LABEL_BTN = _("Apariencia")
        self.SHORCUTS_LABEL_BTN = _("Atajos de teclado")

        self.BTN_ACCEPT_LABEL = _("Aceptar")
        self.BTN_CANCEL_LABEL = _("Cancel")

        self.vertical_button_box = None
        self.vertical_option_box = None
        self.horizontal_option_box = None
        self.horizontal_option_btn = None

        header = Gtk.HeaderBar()
        header.set_title_widget(Gtk.Label(label=_("Preferencias")))
        self.set_titlebar(header)

        UtilsForWindow().set_event_key_to_close(self, self)

        # Load css

        self.get_style_context().add_class("app_background")
        self.get_style_context().add_class("font")
        self.get_style_context().add_class("font-color")

        self.win = win
        self.actions = Actions()

        # Sections

        self.general = General(self.win, self)
        self.directory_box = Directory(self.win, self)
        self.appearance = Appearance(self.win, self)
        self.shortcuts_view = Shortcuts(self.win, self)

        self.set_default_size(self.win.horizontal / 4, self.win.vertical / 2)

        # Contain vertical button box and main option screen
        self.horizontal_main = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        self.horizontal_main.set_margin_top(20)
        self.horizontal_main.set_margin_end(20)
        self.horizontal_main.set_margin_bottom(20)
        self.horizontal_main.set_margin_start(20)

        self.set_child(self.horizontal_main)

        self.create_vertical_buttoms()
        self.create_right_box()
        self.create_option_box()
        self.create_accept_cancel_buttons()
        self.create_general()

        self.present()

        # Signals

        self.connect("close-request", self.on_close)

    def create_vertical_buttoms(self) -> None:
        # Box for buttons
        self.vertical_button_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        self.vertical_button_box.set_vexpand(True)

        general_btn = Gtk.Button(label=self.GENERAL_LABEL_BTN)
        general_btn.get_style_context().add_class("button")
        general_btn.connect("clicked", self.create_general)
        directory_btn = Gtk.Button(label=self.DIRECTORY_LABEL_BTN)
        directory_btn.get_style_context().add_class("button")
        directory_btn.connect("clicked", self.create_directory)
        appearance_btn = Gtk.Button(label=self.APPEARANCE_LABEL_BTN)
        appearance_btn.get_style_context().add_class("button")
        appearance_btn.connect("clicked", self.create_appearance)
        shortcuts_btn = Gtk.Button(label=self.SHORCUTS_LABEL_BTN)
        shortcuts_btn.get_style_context().add_class("button")
        shortcuts_btn.connect("clicked", self.create_shorcuts)

        self.vertical_button_box.set_margin_top(40)
        self.vertical_button_box.append(general_btn)
        self.vertical_button_box.append(directory_btn)
        self.vertical_button_box.append(appearance_btn)
        self.vertical_button_box.append(shortcuts_btn)
        self.horizontal_main.append(self.vertical_button_box)

    def create_right_box(self) -> None:
        self.vertical_option_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        self.vertical_option_box.set_vexpand(True)
        self.horizontal_main.append(self.vertical_option_box)

    def create_option_box(self) -> None:
        # Where the multiple screens are displayed
        self.horizontal_option_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        self.horizontal_option_box.set_margin_top(20)
        self.horizontal_option_box.set_margin_end(20)
        self.horizontal_option_box.set_margin_bottom(20)
        self.horizontal_option_box.set_margin_start(20)
        self.horizontal_option_box.set_hexpand(True)
        self.horizontal_option_box.set_vexpand(True)
        self.horizontal_option_box.get_style_context().add_class(
            "border-style"
        )
        self.vertical_option_box.append(self.horizontal_option_box)

    def create_accept_cancel_buttons(self) -> None:

        # box for accept or cancel buttons
        self.horizontal_option_btn = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        self.horizontal_option_btn.set_hexpand(True)
        self.horizontal_option_btn.set_halign(Gtk.Align.END)

        btn_accept = Gtk.Button(label=self.BTN_ACCEPT_LABEL)
        btn_accept.get_style_context().add_class("button")
        btn_accept.connect("clicked", self.on_accept)

        btn_cancel = Gtk.Button(label=self.BTN_CANCEL_LABEL)
        btn_cancel.get_style_context().add_class("button")
        btn_cancel.connect("clicked", self.on_exit)

        self.horizontal_option_btn.append(btn_accept)
        self.horizontal_option_btn.append(btn_cancel)

        self.vertical_option_box.append(self.horizontal_option_btn)

    def on_exit(self, button: Gtk.Button = None) -> None:
        """
        Close preferencesc window
        """
        if self.win.config.SWITCH_CSS_STATUS:
            self.win.load_css_application()
        self.on_close()

    def on_accept(self, button: Gtk.Button) -> None:
        """
        Confirm changes.
        """
        exec_split = self.directory_box.TERMINAL_COMMAND.split(" ")

        if len(exec_split) != 2:
            self.actions.show_msg_alert(
                self.win,
                _("Debes especificar <commando --flag_directorio_de_trabajo"),
            )
            return

        exec_file = exec_split[0]
        # exec_flag = exec_split[1]
        response = shutil.which(exec_file)

        if not response:
            self.actions.show_msg_alert(
                self.win, _("El ejecutable de terminal no existe.")
            )
            return

        config = ConfigEntity()

        # GENERAL
        config.SWITCH_COPY_STATUS = self.general.SWITCH_COPY_STATUS
        config.SWITCH_MOVE_STATUS = self.general.SWITCH_MOVE_STATUS
        config.SWITCH_DUPLICATE_STATUS = self.general.SWITCH_DUPLICATE_STATUS
        config.SWITCH_COMPRESS_STATUS = self.general.SWITCH_COMPRESS_STATUS
        config.SWITCH_UNCOMPRESS_STATUS = self.general.SWITCH_UNCOMPRESS_STATUS
        config.LANGUAGE = self.general.LANGUAGE

        # DIRECTORYS

        config.FAV_PATH_LIST_1 = self.win.explorer_1.fav_path_list
        config.FAV_PATH_LIST_2 = self.win.explorer_2.fav_path_list
        config.SHOW_DIR_LAST = self.directory_box.SHOW_DIR_LAST
        config.EXP_1_PATH = self.directory_box.EXP_1_PATH
        config.EXP_2_PATH = self.directory_box.EXP_2_PATH
        config.SWITCH_IMG_STATUS = self.directory_box.SWITCH_IMG_STATUS
        config.SWITCH_WATCHDOG_STATUS = (
            self.directory_box.SWITCH_WATCHDOG_STATUS
        )
        config.TERMINAL_COMMAND = self.directory_box.TERMINAL_COMMAND

        # APPEARANCE
        config.SWITCH_CSS_STATUS = self.appearance.SWITCH_CSS_STATUS
        config.COLOR_BACKGROUND_APP = self.appearance.COLOR_BACKGROUND_APP
        config.COLOR_ENTRY = self.appearance.COLOR_ENTRY
        config.COLOR_EXPLORER_LEFT = self.appearance.COLOR_EXPLORER_LEFT
        config.COLOR_EXPLORER_RIGHT = self.appearance.COLOR_EXPLORER_RIGHT
        config.COLOR_BUTTON = self.appearance.COLOR_BUTTON
        config.COLOR_FAV_BUTTON = self.appearance.COLOR_FAV_BUTTON
        config.COLOR_BACKGROUND_SEARCH = (
            self.appearance.COLOR_BACKGROUND_SEARCH
        )
        config.COLOR_SEARCH_TEXT = self.appearance.COLOR_SEARCH_TEXT
        config.FONT_STYLE = self.appearance.FONT_STYLE
        config.FONT_STYLE_COLOR = self.appearance.FONT_STYLE_COLOR
        config.THEME_NAME = self.appearance.THEME_NAME

        # Save shortcuts values.
        self.win.shortcuts.save_yaml_config(self.shortcuts_view.store)
        self.win.shortcuts.recharge_yaml_shortcuts()

        self.win.save_config_file(config)
        self.on_close()

    def on_close(self, widget: Gtk.Widget = None) -> None:
        self.destroy()
        self.win.get_explorer_focused().grab_focus()

    def change_box(self, button: Gtk.Button, actual_box: Gtk.Box) -> None:
        """
        Method to change visible option
        """

        old_child = self.horizontal_option_box.get_first_child()

        if old_child:

            if old_child.get_name() == actual_box.get_name():
                return

            self.horizontal_option_box.remove(old_child)

        self.horizontal_option_box.append(actual_box)

    def create_general(self, button: Gtk.Button = None) -> None:
        """
        Create windows for general option
        """
        self.change_box(button, self.general)

    def create_directory(self, button: Gtk.Button) -> None:
        """
        Create windows for directory option
        """
        self.change_box(button, self.directory_box)

    def create_appearance(self, button: Gtk.Button) -> None:
        """
        Create windows for appearance option
        """
        self.change_box(button, self.appearance)

    def create_shorcuts(self, button: Gtk.Button) -> None:
        """
        Create windows for appearance option
        """
        self.change_box(button, self.shortcuts_view)
