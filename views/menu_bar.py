import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio


class Menu_bar(Gio.Menu):
    """
    Create the application menu bar.
    """

    def __init__(self, win):
        super().__init__()
        self.win = win

        file_menu = Gio.Menu()
        file_menu.append("Archivo", "app.file")
        file_menu.append("Exit", "win.exit")

        self.append_submenu("Archivo", file_menu)
        self.menubar = Gtk.PopoverMenuBar.new_from_model(self)

        action_exit = Gio.SimpleAction.new("exit", None)
        action_exit.connect("activate", self.exit)
        self.win.add_action(action_exit)

    def get_new_menu_bar(self) -> Gtk.PopoverMenuBar:
        return self.menubar

    def exit(self, action, parameter):
        self.win.exit()
