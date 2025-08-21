# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from entity.config import ConfigEntity
from views.preferences.directory import Directory
from views.preferences.general import General
from views.preferences.appearance import Appearance
from views.preferences.shortcuts import Shortcuts
from css.explorer_css import Css_explorer_manager
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango  # noqa: E402


class Preferences(Gtk.Window):

    GENERAL_LABEL_BTN = _("General")
    DIRECTORY_LABEL_BTN = _("Directorios")
    APPEARANCE_LABEL_BTN = _("Apariencia")
    SHORCUTS_LABEL_BTN = _("Atajos de teclado")

    DIRECTORY_TITLE = _("Directorios de inicio")
    UTILIZATION_LAST_DIR = _("Utilizar últimos directorios usados.")
    UTILIZATION_SET_DIR = _("Utilizar siempre los mismos al iniciar.")
    SELECT_FILE_TITLE = _("Seleccionar archivo")
    LABEL_DIR_SELECT_LEFT = _("Directorio izquierdo:")
    LABEL_DIR_SELECT_RIGHT = _("Directorio derecho:")
    BTN_RST_LABEL = _("Resetear")
    BTN_ACCEPT_LABEL = _("Aceptar")
    BTN_CANCEL_LABEL = _("Cancel")
    EXP_1_PATH = ""
    EXP_2_PATH = ""
    SHOW_DIR_LAST = None
    SHOW_IMAGE_PREVIEW_LABEL = _(
        "Mostrar preview de la imagen al seleccionar:"
    )
    SWITCH_IMG_STATUS = None

    # Application colors

    BACKGROUND_APP_TITLE = _("Aplicación")
    BACKGROUND_APP_TITLE_COLOR = _("Fondo de la aplicación")

    # background entrys text

    BACKGROUND_ENTRY_TITLE = _("Entrada de ruta")
    BACKGROUND_ENTRY_TITLE_COLOR = _("Fondo de la entrada")

    # Background colors text
    BACKGROUND_EXPLORER_TITLE = _("Exploradores")
    BACKGROUND_EXPLORER_LEFT = _("Fondo explorador izquierdo")
    BACKGROUND_EXPLORER_RIGHT = _("Fondo explorador derecho")

    # Search colors text
    SEARCH_COLORS_TITLE = _("Colores del sistema de búsqueda")
    SEARCH_BACKGROUND = _("Color de fondo")
    SEARCH_FONT_COLOR = _("Color texto")

    # Buttons text
    BACKGROUND_BUTTONS_TITLE = _("Color de los botones")
    BACKGROUND_BUTTONS_LABEL = _("Fondo de los botones")

    # Font text

    FONT_SELECT_TITLE = _("Seleccion de fuente")
    FONT_SELECT_LABEL = _("Fuente")
    FONT_SELECT_COLOT = _("Color")

    # Colors

    COLOR_BACKGROUND_APP = None

    COLOR_ENTRY = None

    COLOR_EXPLORER_LEFT = None
    COLOR_EXPLORER_RIGHT = None

    COLOR_BACKGROUND_SEARCH = None
    COLOR_SEARCH_TEXT = None

    COLOR_BUTTON = None

    FONT_STYLE = None
    FONT_STYLE_COLOR = None

    def __init__(self, win: Gtk.ApplicationWindow, parent: Gtk.Widget):
        super().__init__(title=_("Preferencias"), transient_for=win)

        Preferences.SHOW_DIR_LAST = win.config.SHOW_DIR_LAST
        Preferences.SWITCH_IMG_STATUS = win.config.SWITCH_IMG_STATUS

        Preferences.COLOR_BACKGROUND_APP = win.config.COLOR_BACKGROUND_APP
        Preferences.COLOR_ENTRY = win.config.COLOR_ENTRY
        Preferences.COLOR_EXPLORER_LEFT = win.config.COLOR_EXPLORER_LEFT
        Preferences.COLOR_EXPLORER_RIGHT = win.config.COLOR_EXPLORER_RIGHT
        Preferences.COLOR_BUTTON = win.config.COLOR_BUTTON
        Preferences.COLOR_BACKGROUND_SEARCH = (
            win.config.COLOR_BACKGROUND_SEARCH
        )
        Preferences.COLOR_SEARCH_TEXT = win.config.COLOR_SEARCH_TEXT
        Preferences.FONT_STYLE = win.config.FONT_STYLE
        Preferences.FONT_STYLE_COLOR = win.config.FONT_STYLE_COLOR

        self.parent = parent
        self.win = win
        self.css_manager = Css_explorer_manager(self.win)
        self.select_directory_box_1 = None
        self.select_directory_box_2 = None
        self.shortcuts_view = None

        self.general = General(self.win)
        self.directory_box = Directory(self.win)
        self.appearance = Appearance(self.win)
        self.shortcuts_view = Shortcuts(self.win)

        self.set_default_size(self.win.horizontal / 4, self.win.vertical / 2)

        # Contain vertical button box and main option screen
        horizontal_main = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        horizontal_main.set_margin_top(20)
        horizontal_main.set_margin_end(20)
        horizontal_main.set_margin_bottom(20)
        horizontal_main.set_margin_start(20)

        self.set_child(horizontal_main)

        # Box for buttons
        vertical_button_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        vertical_button_box.set_vexpand(True)

        general_btn = Gtk.Button(label=Preferences.GENERAL_LABEL_BTN)
        general_btn.get_style_context().add_class("button")
        general_btn.connect("clicked", self.create_general)
        directory_btn = Gtk.Button(label=Preferences.DIRECTORY_LABEL_BTN)
        directory_btn.get_style_context().add_class("button")
        directory_btn.connect("clicked", self.create_directory)
        appearance_btn = Gtk.Button(label=Preferences.APPEARANCE_LABEL_BTN)
        appearance_btn.get_style_context().add_class("button")
        appearance_btn.connect("clicked", self.create_appearance)
        shortcuts_btn = Gtk.Button(label=Preferences.SHORCUTS_LABEL_BTN)
        shortcuts_btn.get_style_context().add_class("button")
        shortcuts_btn.connect("clicked", self.create_shorcuts)

        vertical_button_box.set_margin_top(40)
        vertical_button_box.append(general_btn)
        vertical_button_box.append(directory_btn)
        vertical_button_box.append(appearance_btn)
        vertical_button_box.append(shortcuts_btn)

        # Contain buttons for accept or cancel
        vertical_option_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        vertical_option_box.set_vexpand(True)

        # Where the multiple screens are displayed
        self.horizontal_option_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        self.horizontal_option_box.set_hexpand(True)
        self.horizontal_option_box.set_vexpand(True)
        self.horizontal_option_box.get_style_context().add_class(
            "border-style"
        )

        # box for accept or cancel buttons
        horizontal_option_btn = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        horizontal_option_btn.set_hexpand(True)
        horizontal_option_btn.set_halign(Gtk.Align.END)

        btn_accept = Gtk.Button(label=Preferences.BTN_ACCEPT_LABEL)
        btn_accept.get_style_context().add_class("button")
        btn_accept.connect("clicked", self.on_accept)

        btn_cancel = Gtk.Button(label=Preferences.BTN_CANCEL_LABEL)
        btn_cancel.get_style_context().add_class("button")
        btn_cancel.connect("clicked", self.on_exit)

        horizontal_option_btn.append(btn_accept)
        horizontal_option_btn.append(btn_cancel)

        vertical_option_box.append(self.horizontal_option_box)
        vertical_option_box.append(horizontal_option_btn)

        horizontal_main.append(vertical_button_box)
        horizontal_main.append(vertical_option_box)

        self.present()

        self.create_general()

        self.get_style_context().add_class("app_background")

        # Load css

        self.get_style_context().add_class("font-color")

        # Signals

        self.connect("close-request", self.on_close)

    def on_exit(self, button: Gtk.Button) -> None:
        """
        Close preferencesc window
        """

        self.css_manager.load_css_app_background(
            self.win.config.COLOR_BACKGROUND_APP
        )
        self.css_manager.load_css_buttons(self.win.config.COLOR_BUTTON)
        self.css_manager.load_css_entrys(self.win.config.COLOR_ENTRY)
        font_desc = Pango.FontDescription.from_string(
            self.win.config.FONT_STYLE
        )
        self.css_manager.load_css_font(
            font_desc, self.win.config.FONT_STYLE_COLOR
        )

        self.css_manager.load_css_explorer_background(
            self.win.config.COLOR_EXPLORER_LEFT,
            self.win.config.COLOR_EXPLORER_RIGHT,
        )

        self.on_close()

    def on_accept(self, button: Gtk.Button) -> None:
        """
        Confirm changes.
        """
        config = ConfigEntity()
        config.SHOW_DIR_LAST = Preferences.SHOW_DIR_LAST
        config.EXP_1_PATH = Preferences.EXP_1_PATH
        config.EXP_2_PATH = Preferences.EXP_2_PATH
        config.SWITCH_IMG_STATUS = Preferences.SWITCH_IMG_STATUS
        config.COLOR_BACKGROUND_APP = Preferences.COLOR_BACKGROUND_APP
        config.COLOR_ENTRY = Preferences.COLOR_ENTRY
        config.COLOR_EXPLORER_LEFT = Preferences.COLOR_EXPLORER_LEFT
        config.COLOR_EXPLORER_RIGHT = Preferences.COLOR_EXPLORER_RIGHT
        config.COLOR_BUTTON = Preferences.COLOR_BUTTON
        config.COLOR_BACKGROUND_SEARCH = Preferences.COLOR_BACKGROUND_SEARCH
        config.COLOR_SEARCH_TEXT = Preferences.COLOR_SEARCH_TEXT
        config.FONT_STYLE = Preferences.FONT_STYLE
        config.FONT_STYLE_COLOR = Preferences.FONT_STYLE_COLOR

        # Save shortcuts values.
        self.win.explorer_1.shortcuts.save_yaml_config(
            self.shortcuts_view.store
        )
        self.win.explorer_1.shortcuts.recharge_yaml_shortcuts()
        self.win.explorer_2.shortcuts.recharge_yaml_shortcuts()

        self.win.save_config_file(config)
        self.on_close()

    def on_close(self, widget: Gtk.Widget = None) -> None:
        self.destroy()
        self.parent.preferences = None

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
