import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio


class Menu_bar:
    """
    Crea el menu bar de la aplicación.
    """

    def __init__(self):
        menu = Gio.Menu()

        file_menu = Gio.Menu()
        file_menu.append("Archivo", "app.file")
        file_menu.append("Exit", "app.exit")

        menu.append_submenu("Archivo", file_menu)
        self.menubar = Gtk.PopoverMenuBar.new_from_model(menu)

    def get_new_menu_bar(self) -> Gtk.PopoverMenuBar:
        return self.menubar
