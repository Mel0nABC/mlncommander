# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
# from utilities.i18n import _
from css.explorer_css import Css_explorer_manager
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GObject, Pango  # noqa: E402


class Appearance(Gtk.Box):

    def __init__(self, win: Gtk.ApplicationWindow):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        from views.menu_bar.file.preferences.preferences_options import (
            Preferences,
        )

        self.win = win
        self.css_manager = Css_explorer_manager(self.win)
        self.btn_color_list = []

        # Configure margin Box
        self.set_margin_top(20)
        self.set_margin_end(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)

        grid = Gtk.Grid(column_spacing=10, row_spacing=5)

        # Background application

        lbl_back_app_title = self.create_label_for_title_section(
            Preferences.BACKGROUND_APP_TITLE
        )

        lbl_application_background = self.create_label(
            Preferences.BACKGROUND_APP_TITLE_COLOR
        )

        btn_color_app = self.create_btn_color("btn_color_app")

        grid.attach(lbl_back_app_title, 0, 0, 1, 1)
        grid.attach(lbl_application_background, 1, 1, 1, 1)
        grid.attach(btn_color_app, 2, 1, 1, 1)

        self.append(grid)

        # Background entrys

        lbl_back_entry_title = self.create_label_for_title_section(
            Preferences.BACKGROUND_ENTRY_TITLE
        )

        lbl_application_background = self.create_label(
            Preferences.BACKGROUND_ENTRY_TITLE_COLOR
        )

        btn_color_entry = self.create_btn_color("btn_color_entry")

        grid.attach(lbl_back_entry_title, 0, 2, 1, 1)
        grid.attach(lbl_application_background, 1, 3, 1, 1)
        grid.attach(btn_color_entry, 2, 3, 1, 1)

        # Background explorers

        lbl_explorer_title = self.create_label_for_title_section(
            Preferences.BACKGROUND_EXPLORER_TITLE
        )

        lbl_explorer_left = self.create_label(
            Preferences.BACKGROUND_EXPLORER_LEFT
        )

        btn_color_explorer_left = self.create_btn_color(
            "btn_color_explorer_left"
        )

        lbl_explorer_right = self.create_label(
            Preferences.BACKGROUND_EXPLORER_RIGHT
        )

        btn_color_explorer_right = self.create_btn_color(
            "btn_color_explorer_right"
        )

        grid.attach(lbl_explorer_title, 0, 4, 1, 1)
        grid.attach(lbl_explorer_left, 1, 5, 1, 1)
        grid.attach(btn_color_explorer_left, 2, 5, 1, 1)
        grid.attach(lbl_explorer_right, 1, 6, 1, 1)
        grid.attach(btn_color_explorer_right, 2, 6, 1, 1)

        # Search section

        lbl_search_title = self.create_label_for_title_section(
            Preferences.SEARCH_COLORS_TITLE
        )

        lbl_search_background = self.create_label(
            Preferences.SEARCH_BACKGROUND
        )

        btn_color_background_search = self.create_btn_color(
            "btn_color_background_search"
        )

        lbl_search_font = self.create_label(Preferences.SEARCH_FONT_COLOR)

        btn_color_search_text = self.create_btn_color("btn_color_search_text")

        grid.attach(lbl_search_title, 0, 7, 1, 1)
        grid.attach(lbl_search_background, 1, 8, 1, 1)
        grid.attach(btn_color_background_search, 2, 8, 1, 1)
        grid.attach(lbl_search_font, 1, 9, 1, 1)
        grid.attach(btn_color_search_text, 2, 9, 1, 1)

        # Set color button

        lbl_button_title = self.create_label_for_title_section(
            Preferences.BACKGROUND_BUTTONS_TITLE
        )

        lbl_button_background = self.create_label(
            Preferences.BACKGROUND_BUTTONS_LABEL
        )

        btn_color_background_buttons = self.create_btn_color(
            "btn_color_background_buttons"
        )

        grid.attach(lbl_button_title, 0, 10, 1, 1)
        grid.attach(lbl_button_background, 1, 11, 1, 1)
        grid.attach(btn_color_background_buttons, 2, 11, 1, 1)

        # Font selector

        lbl_font_title = self.create_label_for_title_section(
            Preferences.FONT_SELECT_TITLE
        )

        lbl_font_type = self.create_label(Preferences.FONT_SELECT_LABEL)

        self.font_dialog = Gtk.FontDialog.new()
        self.font_dialog.connect("notify::font-desc", self.set_font)
        self.btn_font = Gtk.FontDialogButton.new(self.font_dialog)
        self.font_desc = Pango.FontDescription.from_string(
            Preferences.FONT_STYLE
        )
        self.btn_font.set_font_desc(self.font_desc)
        self.btn_font.connect("notify::font-desc", self.set_font)

        lbl_font_color = self.create_label(Preferences.FONT_SELECT_COLOR)
        btn_color_font_color = self.create_btn_color("btn_color_font_color")

        grid.attach(lbl_font_title, 0, 12, 1, 1)
        grid.attach(lbl_font_type, 1, 13, 1, 1)
        grid.attach(self.btn_font, 2, 13, 1, 1)
        grid.attach(lbl_font_color, 1, 14, 1, 1)
        grid.attach(btn_color_font_color, 2, 14, 1, 1)

        # Fav button

        lbl_fav_title = self.create_label_for_title_section(
            Preferences.BACKGROUND_FAV_TITLE
        )

        lbl_fav_background = self.create_label(
            Preferences.BACKGROUND_FAV_LABEL
        )

        btn_color_background_fav_buttons = self.create_btn_color(
            "btn_color_background_fav_buttons"
        )

        grid.attach(lbl_fav_title, 0, 15, 1, 1)
        grid.attach(lbl_fav_background, 1, 16, 1, 1)
        grid.attach(btn_color_background_fav_buttons, 2, 16, 1, 1)

        # Button reset

        btn_rst = Gtk.Button(label=Preferences.BTN_RST_LABEL)
        btn_rst.set_margin_top(20)
        btn_rst.set_hexpand(True)
        btn_rst.get_style_context().add_class("button")
        btn_rst.connect("clicked", self.reset_css_values)

        self.append(btn_rst)

    def set_font(
        self, button: Gtk.FontDialogButton, pspec: GObject.GParamSpec
    ) -> None:
        from views.menu_bar.file.preferences.preferences_options import (
            Preferences,
        )

        font_desc = button.get_font_desc()
        if font_desc:
            Preferences.FONT_STYLE = font_desc.to_string()
            self.css_manager.load_css_font(
                font_desc, Preferences.FONT_STYLE_COLOR
            )

    def set_color(
        self, button: Gtk.ColorButton, pspec: GObject.GParamSpec
    ) -> None:
        from views.menu_bar.file.preferences.preferences_options import (
            Preferences,
        )

        color = button.get_rgba().to_string()
        name = button.get_name()

        if name == "btn_color_explorer_left":
            Preferences.COLOR_EXPLORER_LEFT = color
        elif name == "btn_color_explorer_right":
            Preferences.COLOR_EXPLORER_RIGHT = color
        elif name == "btn_color_background_search":
            Preferences.COLOR_BACKGROUND_SEARCH = color
        elif name == "btn_color_search_text":
            Preferences.COLOR_SEARCH_TEXT = color
        elif name == "btn_color_app":
            Preferences.COLOR_BACKGROUND_APP = color
            self.css_manager.load_css_app_background(
                Preferences.COLOR_BACKGROUND_APP
            )
        elif name == "btn_color_background_buttons":
            Preferences.COLOR_BUTTON = color
            self.css_manager.load_css_buttons(
                Preferences.COLOR_BUTTON, Preferences.COLOR_FAV_BUTTON
            )
        elif name == "btn_color_entry":
            Preferences.COLOR_ENTRY = color
            self.css_manager.load_css_entrys(Preferences.COLOR_ENTRY)
        elif name == "btn_color_font_color":
            Preferences.FONT_STYLE_COLOR = color
            font_desc = Pango.FontDescription.from_string(
                Preferences.FONT_STYLE
            )
            self.css_manager.load_css_font(
                font_desc, Preferences.FONT_STYLE_COLOR
            )
        elif name == "btn_color_background_fav_buttons":
            Preferences.COLOR_FAV_BUTTON = color
            self.css_manager.load_css_buttons(
                Preferences.COLOR_BUTTON, Preferences.COLOR_FAV_BUTTON
            )

        self.css_manager.load_css_explorer_background(
            Preferences.COLOR_EXPLORER_LEFT, Preferences.COLOR_EXPLORER_RIGHT
        )

    def set_color_dialog_button(self, button: Gtk.ColorDialogButton) -> None:
        from views.menu_bar.file.preferences.preferences_options import (
            Preferences,
        )

        color = Gdk.RGBA()
        name = button.get_name()

        if name == "btn_color_explorer_left":
            Preferences.COLOR_EXPLORER_LEFT = (
                self.win.config.COLOR_EXPLORER_LEFT
            )
            color.parse(Preferences.COLOR_EXPLORER_LEFT)
        elif name == "btn_color_explorer_right":
            Preferences.COLOR_EXPLORER_RIGHT = (
                self.win.config.COLOR_EXPLORER_RIGHT
            )
            color.parse(Preferences.COLOR_EXPLORER_RIGHT)
        elif name == "btn_color_background_search":
            Preferences.COLOR_BACKGROUND_SEARCH = (
                self.win.config.COLOR_BACKGROUND_SEARCH
            )
            color.parse(Preferences.COLOR_BACKGROUND_SEARCH)
        elif name == "btn_color_search_text":
            Preferences.COLOR_SEARCH_TEXT = self.win.config.COLOR_SEARCH_TEXT
            color.parse(Preferences.COLOR_SEARCH_TEXT)
        elif name == "btn_color_app":
            Preferences.COLOR_BACKGROUND_APP = (
                self.win.config.COLOR_BACKGROUND_APP
            )
            color.parse(Preferences.COLOR_BACKGROUND_APP)
        elif name == "btn_color_background_buttons":
            Preferences.COLOR_BUTTON = self.win.config.COLOR_BUTTON
            color.parse(Preferences.COLOR_BUTTON)
        elif name == "btn_color_entry":
            Preferences.COLOR_ENTRY = self.win.config.COLOR_ENTRY
            color.parse(Preferences.COLOR_ENTRY)
        elif name == "btn_color_font_color":
            Preferences.FONT_STYLE_COLOR = self.win.config.FONT_STYLE_COLOR
            color.parse(Preferences.FONT_STYLE_COLOR)
        elif name == "btn_color_background_fav_buttons":
            Preferences.COLOR_FAV_BUTTON = self.win.config.COLOR_FAV_BUTTON
            color.parse(Preferences.COLOR_FAV_BUTTON)

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
        btn_color.connect("notify::rgba", self.set_color)
        self.set_color_dialog_button(btn_color)
        btn_color.set_hexpand(True)
        btn_color.set_halign(Gtk.Align.CENTER)
        self.btn_color_list.append(btn_color)
        return btn_color

    def reset_css_values(self, button: Gtk.Button):
        from views.preferences.preferences_options import Preferences

        Preferences.COLOR_BACKGROUND_APP = (
            Css_explorer_manager.PREDE_COLOR_BACKGROUND_APP
        )

        Preferences.COLOR_ENTRY = Css_explorer_manager.PREDE_COLOR_ENTRY

        Preferences.COLOR_EXPLORER_LEFT = (
            Css_explorer_manager.PREDE_COLOR_EXPLORER_LEFT
        )
        Preferences.COLOR_EXPLORER_RIGHT = (
            Css_explorer_manager.PREDE_COLOR_EXPLORER_RIGHT
        )

        Preferences.COLOR_BUTTON = Css_explorer_manager.PREDE_COLOR_BUTTON

        Preferences.COLOR_BACKGROUND_SEARCH = (
            Css_explorer_manager.PREDE_COLOR_BACKGROUND_SEARCH
        )
        Preferences.COLOR_SEARCH_TEXT = (
            Css_explorer_manager.PREDE_COLOR_SEARCH_TEXT
        )
        Preferences.FONT_STYLE = Css_explorer_manager.PREDE_FONT_STYLE
        Preferences.FONT_STYLE_COLOR = (
            Css_explorer_manager.PREDE_FONT_STYLE_COLOR
        )
        Preferences.COLOR_FAV_BUTTON = (
            Css_explorer_manager.PREDE_COLOR_FAV_BUTTON
        )

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

        self.font_desc = Pango.FontDescription.from_string(
            Preferences.FONT_STYLE
        )
        self.btn_font.set_font_desc(self.font_desc)

        for btn in self.btn_color_list:
            self.set_color_dialog_button(btn)
