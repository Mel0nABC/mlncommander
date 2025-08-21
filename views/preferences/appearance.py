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
        from views.preferences.preferences_options import Preferences

        self.win = win
        self.css_manager = Css_explorer_manager(self.win)

        # Configure margin Box
        self.set_margin_top(20)
        self.set_margin_end(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)

        # Background application

        self.background_horizontal_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        self.append(
            self.create_box_for_title_section(Preferences.BACKGROUND_APP_TITLE)
        )

        self.background_horizontal_box_app = self.create_box_for_color_btn()

        self.background_horizontal_box_app.append(
            self.create_label(Preferences.BACKGROUND_APP_TITLE_COLOR)
        )
        self.background_horizontal_box_app.append(
            self.create_btn_color("btn_color_app")
        )

        self.append(self.background_horizontal_box_app)

        # Background entrys

        self.append(
            self.create_box_for_title_section(
                Preferences.BACKGROUND_ENTRY_TITLE
            )
        )

        self.background_horizontal_box_entry_color = (
            self.create_box_for_color_btn()
        )

        self.background_horizontal_box_entry_color.append(
            self.create_label(Preferences.BACKGROUND_ENTRY_TITLE_COLOR)
        )
        self.background_horizontal_box_entry_color.append(
            self.create_btn_color("btn_color_entry")
        )

        self.append(self.background_horizontal_box_entry_color)

        # Background explorers

        self.append(
            self.create_box_for_title_section(
                Preferences.BACKGROUND_EXPLORER_TITLE
            )
        )

        self.background_horizontal_box_1 = self.create_box_for_color_btn()

        self.background_horizontal_box_1.append(
            self.create_label(Preferences.BACKGROUND_EXPLORER_LEFT)
        )
        self.background_horizontal_box_1.append(
            self.create_btn_color("btn_color_explorer_left")
        )

        self.append(self.background_horizontal_box_1)

        self.background_horizontal_box_2 = self.create_box_for_color_btn()

        self.background_horizontal_box_2.append(
            self.create_label(Preferences.BACKGROUND_EXPLORER_RIGHT)
        )
        self.background_horizontal_box_2.append(
            self.create_btn_color("btn_color_explorer_right")
        )

        self.append(self.background_horizontal_box_2)

        # Search section

        self.append(
            self.create_box_for_title_section(Preferences.SEARCH_COLORS_TITLE)
        )

        self.background_horizontal_box_3 = self.create_box_for_color_btn()

        self.background_horizontal_box_3.append(
            self.create_label(Preferences.SEARCH_BACKGROUND)
        )
        self.background_horizontal_box_3.append(
            self.create_btn_color("btn_color_background_search")
        )

        self.append(self.background_horizontal_box_3)

        self.background_horizontal_box_4 = self.create_box_for_color_btn()

        self.background_horizontal_box_4.append(
            self.create_label(Preferences.SEARCH_FONT_COLOR)
        )
        self.background_horizontal_box_4.append(
            self.create_btn_color("btn_color_search_text")
        )

        self.append(self.background_horizontal_box_4)

        # Set color button

        self.append(
            self.create_box_for_title_section(
                Preferences.BACKGROUND_BUTTONS_TITLE
            )
        )

        self.background_horizontal_box_4 = self.create_box_for_color_btn()

        self.background_horizontal_box_4.append(
            self.create_label(Preferences.BACKGROUND_BUTTONS_LABEL)
        )
        self.background_horizontal_box_4.append(
            self.create_btn_color("btn_color_background_buttons")
        )

        self.append(self.background_horizontal_box_4)

        # Font selector

        self.append(
            self.create_box_for_title_section(Preferences.FONT_SELECT_TITLE)
        )

        self.background_horizontal_box_font_btn = (
            self.create_box_for_color_btn()
        )

        font_dialog = Gtk.FontDialog.new()
        font_dialog.connect("notify::font-desc", self.set_font)
        btn_font = Gtk.FontDialogButton.new(font_dialog)
        font_desc = Pango.FontDescription.from_string(Preferences.FONT_STYLE)
        btn_font.set_font_desc(font_desc)
        btn_font.connect("notify::font-desc", self.set_font)

        self.background_horizontal_box_font_btn.append(
            self.create_label(Preferences.FONT_SELECT_LABEL)
        )
        self.background_horizontal_box_font_btn.append(btn_font)

        self.append(self.background_horizontal_box_font_btn)

        # Font color selector
        self.background_horizontal_box_font_color = (
            self.create_box_for_color_btn()
        )

        self.background_horizontal_box_font_color.append(
            self.create_label(Preferences.FONT_SELECT_COLOT)
        )
        self.background_horizontal_box_font_color.append(
            self.create_btn_color("btn_color_font_color")
        )

        self.append(self.background_horizontal_box_font_color)

        btn_rst = Gtk.Button(label=Preferences.BTN_RST_LABEL)
        btn_rst.set_margin_top(20)
        btn_rst.set_hexpand(True)
        btn_rst.get_style_context().add_class("button")
        btn_rst.connect("clicked", self.reset_css_values)

        self.append(btn_rst)

    def set_font(
        self, button: Gtk.FontDialogButton, pspec: GObject.GParamSpec
    ) -> None:
        from views.preferences.preferences_options import Preferences

        font_desc = button.get_font_desc()
        if font_desc:
            Preferences.FONT_STYLE = font_desc.to_string()
            self.css_manager.load_css_font(
                font_desc, Preferences.FONT_STYLE_COLOR
            )

    def set_color(
        self, button: Gtk.ColorButton, pspec: GObject.GParamSpec
    ) -> None:
        from views.preferences.preferences_options import Preferences

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
            self.css_manager.load_css_buttons(Preferences.COLOR_BUTTON)
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

        self.css_manager.load_css_explorer_background(
            Preferences.COLOR_EXPLORER_LEFT, Preferences.COLOR_EXPLORER_RIGHT
        )

    def set_color_dialog_button(self, button: Gtk.ColorDialogButton) -> None:
        from views.preferences.preferences_options import Preferences

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

        button.set_rgba(color)

    def create_box_for_title_section(self, text_label: str) -> Gtk.Box:
        """
        Create box and label for title section
        """
        box_for_title = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        label = Gtk.Label()
        label.set_markup(f"<u>{text_label}</u>")
        box_for_title.append(label)
        box_for_title.set_margin_top(40)

        return box_for_title

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
        return btn_color

    def create_box_for_color_btn(self) -> Gtk.Box:
        box_for_color_btn = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        box_for_color_btn.set_margin_start(100)
        return box_for_color_btn

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
            Css_explorer_manager.PREDE_COLOR_BUTTON
        )

        font_desc = Pango.FontDescription.from_string(
            Css_explorer_manager.PREDE_FONT_STYLE
        )

        self.css_manager.load_css_font(
            font_desc, Css_explorer_manager.PREDE_FONT_STYLE_COLOR
        )
