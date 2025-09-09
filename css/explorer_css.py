# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
import gi
from gi.repository import Gtk, Gdk, Pango  # noqa: F401

gi.require_version("Gtk", "4.0")


class Css_explorer_manager:

    PREDE_COLOR_BACKGROUND_APP = "#353535"
    PREDE_COLOR_ENTRY = "#2d2d2d"
    PREDE_COLOR_EXPLORER_LEFT = "#222226"
    PREDE_COLOR_EXPLORER_RIGHT = "#222226"
    PREDE_COLOR_BUTTON = "#393939"
    PREDE_COLOR_FAV_BUTTON = "#222226"
    PREDE_COLOR_BACKGROUND_SEARCH = "rgb(0,0,0)"
    PREDE_COLOR_SEARCH_TEXT = "rgb(246,211,45)"
    PREDE_FONT_STYLE = "Adwaita Sans 12"
    PREDE_FONT_STYLE_COLOR = "white"

    def __init__(self, win: Gtk.ApplicationWindow):
        self.win = win

    def load_css_app_background(self, app_background_color: str) -> None:
        """
        Set application background color (all window)
        """
        css = f"""
            .app_background{{
                background-color: {app_background_color};
                border-radius: 10pt;
            }}
        """.encode()

        self.set_css_to_provider(css)

    def load_css_explorer_background(
        self, color_explorer_left: str, color_explorer_right: str
    ) -> None:
        """
        Sets the text color when using the search function for files
        or directories
        """
        css = f"""
            columnview cell{{
                padding: 0;
            }}
            columnview cell image{{
                padding: 2px;
            }}
            columnview cell label{{
                padding: 2px;
            }}
            .image-preview{{
                border-radius: 10px;
                padding: 10px;
            }}

            .to_down_explorer{{
                border-radius: 10px;
                padding: 10px;
                font-size: 12px;
            }}
            .column_view_borders{{
                border-radius:10px;
            }}

            .explorer_background_left{{
                background-color: {color_explorer_left};
            }}

            .explorer_background_right{{
                background-color: {color_explorer_right};
            }}

        """.encode()

        self.set_css_to_provider(css)

    def load_css_entrys(self, color_entry: str) -> None:
        """
        Set color to all entrys
        """
        css = f"""
            .entry{{
                background-color: {color_entry};
            }}

        """.encode()

        self.set_css_to_provider(css)

    def load_css_buttons(
        self, color_button: str = None, color_fav_button: str = None
    ) -> None:
        """
        Set color to all button
        """
        css = f"""
            .fav{{
                background-image: none;
                background-color: {color_fav_button};
            }}
            .button{{
                background-image: none;
                background-color: {color_button};
                transition: background-color 0.3s ease; /* animación suave */
            }}

            .button:hover{{
                filter: brightness(80%);
            }}
        """.encode()

        self.set_css_to_provider(css)

    def load_css_context_menu(self) -> None:
        """
        Set color to all button
        """
        css = """
            .contextual_window{
                background-color: transparent;
            }
            .contextual_menu{
                background-color: #353535;
                border-radius: 5pt;
            }
            .contextual_content{
                padding: 10px;
                margin:10px;
                border-radius:5pt;
                background-color: #222226;
            }
            .contextual_content button{
                margin: 0px;
                min-width: 200px;
            }
        """.encode()

        self.set_css_to_provider(css)

    def load_css_search(
        self, color_background_search: str, color_search_text: str
    ) -> None:
        """
        Sets the background color when using the search function for files
         or directories
        """

        css = f"""
            .background_search *{{
                    background-color: {color_background_search};
                    color: {color_search_text};
                }}
        """.encode()

        self.set_css_to_provider(css)

    def pango_weight_to_css(self, weight: int) -> str:
        mapping = {
            Pango.Weight.THIN: "100",
            Pango.Weight.ULTRALIGHT: "200",
            Pango.Weight.LIGHT: "300",
            Pango.Weight.SEMILIGHT: "350",
            Pango.Weight.BOOK: "380",
            Pango.Weight.NORMAL: "400",
            Pango.Weight.MEDIUM: "500",
            Pango.Weight.SEMIBOLD: "600",
            Pango.Weight.BOLD: "700",
            Pango.Weight.ULTRABOLD: "800",
            Pango.Weight.HEAVY: "900",
            Pango.Weight.ULTRAHEAVY: "950",
        }
        return mapping.get(weight, "400")

    def load_css_font(
        self, font_desc: Gtk.FontDialogButton, font_style_color: str
    ) -> None:
        """
        Sets app font
        """
        family = font_desc.get_family()
        size = font_desc.get_size() / Pango.SCALE
        weight = self.pango_weight_to_css(font_desc.get_weight())
        style = (
            "italic"
            if font_desc.get_style() == Pango.Style.ITALIC
            else "normal"
        )
        css = f"""
            .border-style{{
                border: solid 1pt {font_style_color};
                border-radius: 20pt;
                margin: 20pt;
            }}

            .font-color *{{
                color: {font_style_color};
            }}

            .font{{
                font-family: "{family}";
                font-size: {size}pt;
                font-weight: {weight};
                font-style: {style};
            }}
        """.encode()
        self.set_css_to_provider(css)

    def set_font_size_explorer(self, size: int) -> bool:
        """
        Changes the text size of the file and directory list in Explorer
        """

        if self.font_size_explorer == size:
            return True

        old_size = self.font_size_explorer
        self.font_size_explorer = size

        if old_size != self.font_size_explorer:
            return True

        return False

    def set_background_search_text_color(self, color: str) -> bool:
        """
        Change the text color of the file and directory search engine
        """

        if self.COLOR_SEARCH_TEXT == color:
            return True

        old_color = self.COLOR_SEARCH_TEXT
        self.COLOR_SEARCH_TEXT = color

        if old_color != self.COLOR_SEARCH_TEXT:
            return True

        return False

    def set_background_search_color(self, color: str) -> bool:
        """
        Change the background color of the file and directory search engine
        """
        if self.COLOR_BACKGROUND_SEARCH == color:
            return True

        old_color = self.COLOR_BACKGROUND_SEARCH
        self.COLOR_BACKGROUND_SEARCH = color

        if old_color != self.COLOR_BACKGROUND_SEARCH:
            return True

        return False

    def set_css_to_provider(self, css_code: str) -> None:
        """
        Create a provider for CSS and load the provided CSS code.
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css_code)

        # Gtk.StyleContext.add_provider_for_display(
        #     self.win.get_display(),
        #     provider,
        #     Gtk.STYLE_PROVIDER_PRIORITY_USER,
        # )
