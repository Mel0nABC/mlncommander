import gi
from gi.repository import Gtk

gi.require_version("Gtk", "4.0")


class Css_explorer_manager:

    def __init__(self, win: Gtk.ApplicationWindow):
        self.win = win

    def load_css_explorer_background(
        self, color_explorer_left: str, color_explorer_right: str
    ) -> None:
        """
        Sets the text color when using the search function for files
        or directories
        """

        css = f"""
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

    def load_css_app_background(self, app_background_color: str) -> None:
        """
        Sets the text color when using the search function for files
        or directories
        """
        css = f"""
            .app_background{{
                background-color: {app_background_color};
            }}

        """.encode()

        self.set_css_to_provider(css)

    def load_css_search(
        self,
        color_background_search: str,
        color_search_text: str,
        font_size_explorer: str,
        font_bold_explorer: str,
    ) -> None:
        """
        Sets the background color when using the search function for files
         or directories
        """

        css = f"""
            .background_search {{
                background-color: {color_background_search};
                color: {color_search_text};
                font-weight:bold;
                }}

            .explorer_text_size{{
                font-size: {font_size_explorer}px;
                font-weight:{font_bold_explorer};
            }}
        """.encode()

        self.set_css_to_provider(css)

    def set_css_to_provider(self, css_code: str) -> None:
        """
        Create a provider for CSS and load the provided CSS code.
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css_code)

        Gtk.StyleContext.add_provider_for_display(
            self.win.get_display(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER,
        )

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
