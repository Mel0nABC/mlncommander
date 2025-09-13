# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from css.explorer_css import Css_explorer_manager
import gi
import asyncio

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Gio, GObject, Pango  # noqa: E402


class Appearance(Gtk.Box):

    def __init__(self, win: Gtk.ApplicationWindow):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # APPEARANCE

        # General

        self.GENERAL_TITLE = _("Opciones generales de apariencia")
        self.ENABLE_CSS_TITLE = _("Activar decoración en css")
        self.SWITCH_CSS_STATUS = win.config.SWITCH_CSS_STATUS

        # Application colors

        self.BACKGROUND_APP_TITLE = _("Aplicación")
        self.BACKGROUND_APP_TITLE_COLOR = _("Fondo de la aplicación")

        # background entrys text

        self.BACKGROUND_ENTRY_TITLE = _("Entrada de ruta")
        self.BACKGROUND_ENTRY_TITLE_COLOR = _("Fondo de la entrada")

        # Background colors text
        self.BACKGROUND_EXPLORER_TITLE = _("Exploradores")
        self.BACKGROUND_EXPLORER_LEFT = _("Fondo explorador izquierdo")
        self.BACKGROUND_EXPLORER_RIGHT = _("Fondo explorador derecho")

        # Search colors text
        self.SEARCH_COLORS_TITLE = _("Colores del sistema de búsqueda")
        self.SEARCH_BACKGROUND = _("Color de fondo")
        self.SEARCH_FONT_COLOR = _("Color texto")

        # Buttons text
        self.BACKGROUND_BUTTONS_TITLE = _("Color de los botones")
        self.BACKGROUND_BUTTONS_LABEL = _("Fondo de los botones")

        # Font text

        self.FONT_SELECT_TITLE = _("Seleccion de fuente")
        self.FONT_SELECT_LABEL = _("Fuente")
        self.FONT_SELECT_COLOR = _("Color")

        # Fav button

        self.BACKGROUND_FAV_TITLE = _("Color de los botones de favoritos")
        self.BACKGROUND_FAV_LABEL = _("Fondo de los botones")

        # Reset
        self.BTN_RST_LABEL = _("Resetear")

        # Colors

        self.COLOR_BACKGROUND_APP = win.config.COLOR_BACKGROUND_APP
        self.COLOR_ENTRY = win.config.COLOR_ENTRY
        self.COLOR_EXPLORER_LEFT = win.config.COLOR_EXPLORER_LEFT
        self.COLOR_EXPLORER_RIGHT = win.config.COLOR_EXPLORER_RIGHT
        self.COLOR_BUTTON = win.config.COLOR_BUTTON
        self.COLOR_FAV_BUTTON = win.config.COLOR_FAV_BUTTON
        self.COLOR_BACKGROUND_SEARCH = win.config.COLOR_BACKGROUND_SEARCH
        self.COLOR_SEARCH_TEXT = win.config.COLOR_SEARCH_TEXT
        self.FONT_STYLE = win.config.FONT_STYLE
        self.FONT_STYLE_COLOR = win.config.FONT_STYLE_COLOR

        self.win = win
        # self.css_manager = Css_explorer_manager(self.win)
        self.css_manager = self.win.css_manager
        self.btn_color_list = []

        # Configure margin Box
        self.set_margin_top(20)
        self.set_margin_end(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)

        grid_enable_css = Gtk.Grid(column_spacing=10, row_spacing=5)

        lbl_general = self.create_label_for_title_section(self.GENERAL_TITLE)

        lbl_enable_css = self.create_label_for_title_section(
            self.ENABLE_CSS_TITLE
        )

        self.switch_css = Gtk.Switch.new()
        self.switch_css.set_active(self.SWITCH_CSS_STATUS)
        self.switch_css.set_hexpand(True)
        self.switch_css.set_halign(Gtk.Align.CENTER)

        self.switch_css.connect("state-set", self.on_press_switch_css)
        grid_enable_css.attach(lbl_general, 0, 0, 1, 1)
        grid_enable_css.attach(lbl_enable_css, 1, 1, 1, 1)
        grid_enable_css.attach(self.switch_css, 2, 1, 1, 1)

        self.append(grid_enable_css)

        self.grid = Gtk.Grid(column_spacing=10, row_spacing=5)

        # Background application

        lbl_back_app_title = self.create_label_for_title_section(
            self.BACKGROUND_APP_TITLE
        )

        lbl_application_background = self.create_label(
            self.BACKGROUND_APP_TITLE_COLOR
        )

        btn_color_app = self.create_btn_color("btn_color_app")

        self.grid.attach(lbl_back_app_title, 0, 0, 1, 1)
        self.grid.attach(lbl_application_background, 1, 1, 1, 1)
        self.grid.attach(btn_color_app, 2, 1, 1, 1)

        self.append(self.grid)

        # Background entrys

        lbl_back_entry_title = self.create_label_for_title_section(
            self.BACKGROUND_ENTRY_TITLE
        )

        lbl_application_background = self.create_label(
            self.BACKGROUND_ENTRY_TITLE_COLOR
        )

        btn_color_entry = self.create_btn_color("btn_color_entry")

        self.grid.attach(lbl_back_entry_title, 0, 2, 1, 1)
        self.grid.attach(lbl_application_background, 1, 3, 1, 1)
        self.grid.attach(btn_color_entry, 2, 3, 1, 1)

        # Background explorers

        lbl_explorer_title = self.create_label_for_title_section(
            self.BACKGROUND_EXPLORER_TITLE
        )

        lbl_explorer_left = self.create_label(self.BACKGROUND_EXPLORER_LEFT)

        btn_color_explorer_left = self.create_btn_color(
            "btn_color_explorer_left"
        )

        lbl_explorer_right = self.create_label(self.BACKGROUND_EXPLORER_RIGHT)

        btn_color_explorer_right = self.create_btn_color(
            "btn_color_explorer_right"
        )

        self.grid.attach(lbl_explorer_title, 0, 4, 1, 1)
        self.grid.attach(lbl_explorer_left, 1, 5, 1, 1)
        self.grid.attach(btn_color_explorer_left, 2, 5, 1, 1)
        self.grid.attach(lbl_explorer_right, 1, 6, 1, 1)
        self.grid.attach(btn_color_explorer_right, 2, 6, 1, 1)

        # Search section

        lbl_search_title = self.create_label_for_title_section(
            self.SEARCH_COLORS_TITLE
        )

        lbl_search_background = self.create_label(self.SEARCH_BACKGROUND)

        btn_color_background_search = self.create_btn_color(
            "btn_color_background_search"
        )

        lbl_search_font = self.create_label(self.SEARCH_FONT_COLOR)

        btn_color_search_text = self.create_btn_color("btn_color_search_text")

        self.grid.attach(lbl_search_title, 0, 7, 1, 1)
        self.grid.attach(lbl_search_background, 1, 8, 1, 1)
        self.grid.attach(btn_color_background_search, 2, 8, 1, 1)
        self.grid.attach(lbl_search_font, 1, 9, 1, 1)
        self.grid.attach(btn_color_search_text, 2, 9, 1, 1)

        # Set color button

        lbl_button_title = self.create_label_for_title_section(
            self.BACKGROUND_BUTTONS_TITLE
        )

        lbl_button_background = self.create_label(
            self.BACKGROUND_BUTTONS_LABEL
        )

        btn_color_background_buttons = self.create_btn_color(
            "btn_color_background_buttons"
        )

        self.grid.attach(lbl_button_title, 0, 10, 1, 1)
        self.grid.attach(lbl_button_background, 1, 11, 1, 1)
        self.grid.attach(btn_color_background_buttons, 2, 11, 1, 1)

        # Font selector

        lbl_font_title = self.create_label_for_title_section(
            self.FONT_SELECT_TITLE
        )

        lbl_font_type = self.create_label(self.FONT_SELECT_LABEL)

        self.font_dialog = Gtk.FontDialog.new()
        self.font_dialog.connect("notify::font-desc", self.set_font)
        self.btn_font = Gtk.FontDialogButton.new(self.font_dialog)
        self.font_desc = Pango.FontDescription.from_string(self.FONT_STYLE)
        self.btn_font.set_font_desc(self.font_desc)
        self.btn_font.connect("notify::font-desc", self.set_font)

        lbl_font_color = self.create_label(self.FONT_SELECT_COLOR)
        btn_color_font_color = self.create_btn_color("btn_color_font_color")

        self.grid.attach(lbl_font_title, 0, 12, 1, 1)
        self.grid.attach(lbl_font_type, 1, 13, 1, 1)
        self.grid.attach(self.btn_font, 2, 13, 1, 1)
        self.grid.attach(lbl_font_color, 1, 14, 1, 1)
        self.grid.attach(btn_color_font_color, 2, 14, 1, 1)

        # Fav button

        lbl_fav_title = self.create_label_for_title_section(
            self.BACKGROUND_FAV_TITLE
        )

        lbl_fav_background = self.create_label(self.BACKGROUND_FAV_LABEL)

        btn_color_background_fav_buttons = self.create_btn_color(
            "btn_color_background_fav_buttons"
        )

        self.grid.attach(lbl_fav_title, 0, 15, 1, 1)
        self.grid.attach(lbl_fav_background, 1, 16, 1, 1)
        self.grid.attach(btn_color_background_fav_buttons, 2, 16, 1, 1)

        # Button reset

        btn_rst = Gtk.Button(label=self.BTN_RST_LABEL)
        btn_rst.set_margin_top(20)
        btn_rst.set_hexpand(True)
        btn_rst.get_style_context().add_class("button")
        btn_rst.connect("clicked", self.reset_css_values)

        self.append(btn_rst)

        self.connect("realize", self.on_realize)

    def on_realize(self, widget: Gtk.Widget) -> None:
        if not self.SWITCH_CSS_STATUS:
            self.grid.set_sensitive(False)

    def set_font(
        self, button: Gtk.FontDialogButton, pspec: GObject.GParamSpec
    ) -> None:
        if self.win.ENABLE_CSS:
            font_desc = button.get_font_desc()
            if font_desc:
                self.FONT_STYLE = font_desc.to_string()
                self.css_manager.load_css_font(
                    font_desc, self.FONT_STYLE_COLOR
                )

    def set_color(
        self, button: Gtk.ColorButton, pspec: GObject.GParamSpec
    ) -> None:

        if self.SWITCH_CSS_STATUS:
            color = button.get_rgba().to_string()
            name = button.get_name()

            if name == "btn_color_explorer_left":
                self.COLOR_EXPLORER_LEFT = color
            elif name == "btn_color_explorer_right":
                self.COLOR_EXPLORER_RIGHT = color
            elif name == "btn_color_background_search":
                self.COLOR_BACKGROUND_SEARCH = color
            elif name == "btn_color_search_text":
                self.COLOR_SEARCH_TEXT = color
            elif name == "btn_color_app":
                self.COLOR_BACKGROUND_APP = color
                self.css_manager.load_css_app_background(
                    self.COLOR_BACKGROUND_APP
                )
            elif name == "btn_color_background_buttons":
                self.COLOR_BUTTON = color
                self.css_manager.load_css_buttons(
                    self.COLOR_BUTTON, self.COLOR_FAV_BUTTON
                )
            elif name == "btn_color_entry":
                self.COLOR_ENTRY = color
                self.css_manager.load_css_entrys(self.COLOR_ENTRY)
            elif name == "btn_color_font_color":
                self.FONT_STYLE_COLOR = color
                font_desc = Pango.FontDescription.from_string(self.FONT_STYLE)
                self.css_manager.load_css_font(
                    font_desc, self.FONT_STYLE_COLOR
                )
            elif name == "btn_color_background_fav_buttons":
                self.COLOR_FAV_BUTTON = color
                self.css_manager.load_css_buttons(
                    self.COLOR_BUTTON, self.COLOR_FAV_BUTTON
                )

            self.css_manager.load_css_explorer_background(
                self.COLOR_EXPLORER_LEFT, self.COLOR_EXPLORER_RIGHT
            )

    def set_color_dialog_button(self, button: Gtk.ColorDialogButton) -> None:

        color = Gdk.RGBA()
        name = button.get_name()

        if name == "btn_color_explorer_left":
            color.parse(self.COLOR_EXPLORER_LEFT)
        elif name == "btn_color_explorer_right":
            color.parse(self.COLOR_EXPLORER_RIGHT)
        elif name == "btn_color_background_search":
            color.parse(self.COLOR_BACKGROUND_SEARCH)
        elif name == "btn_color_search_text":
            color.parse(self.COLOR_SEARCH_TEXT)
        elif name == "btn_color_app":
            color.parse(self.COLOR_BACKGROUND_APP)
        elif name == "btn_color_background_buttons":
            color.parse(self.COLOR_BUTTON)
        elif name == "btn_color_entry":
            color.parse(self.COLOR_ENTRY)
        elif name == "btn_color_font_color":
            color.parse(self.FONT_STYLE_COLOR)
        elif name == "btn_color_background_fav_buttons":
            color.parse(self.COLOR_FAV_BUTTON)

        button.set_rgba(color)

    def create_label_for_title_section(self, text_label: str) -> Gtk.Box:
        """
        Create label for title section
        """
        label = Gtk.Label()
        label.set_markup(text_label)
        label.set_halign(Gtk.Align.START)

        return label

    def create_label(self, label_text: str) -> Gtk.Label:
        label = Gtk.Label(label=label_text)
        label.set_size_request(200, -1)
        label.set_xalign(0.0)
        return label

    def create_btn_color(self, btn_name: str) -> Gtk.ColorDialogButton:
        color_dialog = Gtk.ColorDialog()
        btn_color = Gtk.ColorDialogButton.new(color_dialog)
        btn_color.set_name(btn_name)
        self.set_color_dialog_button(btn_color)
        btn_color.connect("notify::rgba", self.set_color)
        btn_color.set_hexpand(True)
        btn_color.set_halign(Gtk.Align.CENTER)
        self.btn_color_list.append(btn_color)
        return btn_color

    def reset_css_values(self, button: Gtk.Button):
        if self.SWITCH_CSS_STATUS:
            self.switch_css.set_active(False)
            self.SWITCH_CSS_STATUS = False
            self.COLOR_BACKGROUND_APP = (
                Css_explorer_manager.PREDE_COLOR_BACKGROUND_APP
            )

            self.COLOR_ENTRY = Css_explorer_manager.PREDE_COLOR_ENTRY

            self.COLOR_EXPLORER_LEFT = (
                Css_explorer_manager.PREDE_COLOR_EXPLORER_LEFT
            )
            self.COLOR_EXPLORER_RIGHT = (
                Css_explorer_manager.PREDE_COLOR_EXPLORER_RIGHT
            )

            self.COLOR_BUTTON = Css_explorer_manager.PREDE_COLOR_BUTTON

            self.COLOR_BACKGROUND_SEARCH = (
                Css_explorer_manager.PREDE_COLOR_BACKGROUND_SEARCH
            )
            self.COLOR_SEARCH_TEXT = (
                Css_explorer_manager.PREDE_COLOR_SEARCH_TEXT
            )
            self.FONT_STYLE = Css_explorer_manager.PREDE_FONT_STYLE
            self.FONT_STYLE_COLOR = Css_explorer_manager.PREDE_FONT_STYLE_COLOR
            self.COLOR_FAV_BUTTON = Css_explorer_manager.PREDE_COLOR_FAV_BUTTON

            self.css_manager.load_css_app_background(
                Css_explorer_manager.PREDE_COLOR_BACKGROUND_APP
            )

            self.css_manager.load_css_entrys(
                Css_explorer_manager.PREDE_COLOR_ENTRY
            )

            self.css_manager.load_css_explorer_background(
                Css_explorer_manager.PREDE_COLOR_EXPLORER_LEFT,
                Css_explorer_manager.PREDE_COLOR_EXPLORER_RIGHT,
            )

            self.css_manager.load_css_buttons(
                Css_explorer_manager.PREDE_COLOR_BUTTON,
                Css_explorer_manager.PREDE_COLOR_FAV_BUTTON,
            )

            font_desc = Pango.FontDescription.from_string(
                Css_explorer_manager.PREDE_FONT_STYLE
            )

            self.css_manager.load_css_font(
                font_desc, Css_explorer_manager.PREDE_FONT_STYLE_COLOR
            )

            self.font_desc = Pango.FontDescription.from_string(self.FONT_STYLE)
            self.btn_font.set_font_desc(self.font_desc)

            for btn in self.btn_color_list:
                self.set_color_dialog_button(btn)

    def on_press_switch_css(self, switch: Gtk.Switch, state: bool) -> None:

        if state:
            self.css_manager.load_css()
            self.grid.set_sensitive(True)
        else:
            asyncio.ensure_future(self.on_alarm())

    def on_response_alarm(self, dialog: Gtk.AlertDialog, task: Gio.Task):
        response = dialog.choose_finish(task)

        if not response:  # Accept
            self.SWITCH_CSS_STATUS = False
            self.win.stop_to_close()
            self.css_manager.unload_css_and_restart()
        else:
            self.switch_css.set_active(True)

    async def on_alarm(self):
        alert = Gtk.AlertDialog()
        alert.set_message(
            _(
                (
                    "Si se desactiva el css, tienes"
                    " que reiniciar la aplicación, ¿Continuar?"
                )
            )
        )
        alert.set_buttons(["Aceptar", "Cancelar"])
        alert.set_cancel_button(0)
        alert.set_default_button(1)
        await alert.choose(self.win, None, self.on_response_alarm)
