import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class Css_explorer_manager:

    def __init__(self, win):
        self.win = win
        self.font_size_explorer = 15
        self.background_search_text_color = "yellow"
        self.background_search_color = "black"
        self.font_bold_explorer = "bold"

    def set_css_to_provider(self, css_code: str):
        """
        Create a provider for CSS and load the provided CSS code.
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css_code)

        Gtk.StyleContext.add_provider_for_display(
            self.win.get_display(), provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    def load_css_background_search(self):
        """
        Sets the background color when using the search function for files or directories
        """

        css = f"""
            .background-search {{
                color: {self.background_search_text_color};
                background-color: {self.background_search_color};
                font-weight:bold;
            }}
        """.encode()

        self.set_css_to_provider(css)

    def load_css_explorer_text(self):
        """
        Sets the text color when using the search function for files or directories
        """

        css = f"""
            .explorer_text_size{{
                font-size: {self.font_size_explorer}px;
                font-weight:{self.font_bold_explorer};
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

        if self.background_search_text_color == color:
            return True

        old_color = self.background_search_text_color
        self.background_search_text_color = color

        if old_color != self.background_search_text_color:
            return True

        return False

    def set_background_search_color(self, color: str) -> bool:
        """
        Change the background color of the file and directory search engine
        """
        if self.background_search_color == color:
            return True

        old_color = self.background_search_color
        self.background_search_color = color

        if old_color != self.background_search_color:
            return True

        return False
