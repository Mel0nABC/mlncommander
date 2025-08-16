from utilities.i18n import _
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio  # noqa: E402


class Menu_bar(Gio.Menu):
    """
    Create the application menu bar.
    """

    def __init__(self, win: Gtk.ApplicationWindow):
        super().__init__()
        self.win = win
        self.preferences = None

        main_menu = Gio.Menu()

        pref_menu = Gio.Menu()
        pref_menu.append(_("Preferencias"), "win.peferencias")

        exit_menu = Gio.Menu()
        exit_menu.append(_("Salir"), "win.exit")

        main_menu.append_section(None, pref_menu)
        main_menu.append_section(None, exit_menu)

        self.append_submenu(_("Archivo"), main_menu)
        self.menubar = Gtk.PopoverMenuBar.new_from_model(self)

        action_exit = Gio.SimpleAction.new("exit", None)
        action_exit.connect("activate", self.exit)

        action_preferences = Gio.SimpleAction.new("peferencias", None)
        action_preferences.connect("activate", self.open_preferences)

        self.win.add_action(action_exit)
        self.win.add_action(action_preferences)

    def exit(self, action, parameter):
        self.win.exit()

    def open_preferences(self, action, parameter):
        from views.preferences_options import Preferences

        if not self.preferences:
            self.preferences = Preferences(self.win, self)
