# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
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

        # append_submenu -> bar section
        # append_section -> separated with horizontal bar
        # append -> create option list

        # Object to insert in vertical main box, on main_window.Window class
        self.menubar = Gtk.PopoverMenuBar.new_from_model(self)

        # Menu file, for menu bar
        menu_file = Gio.Menu()
        self.append_submenu(_("Archivo"), menu_file)

        # Option Preferences
        menu_preferences = Gio.Menu()
        menu_preferences.append(_("Preferencias"), "win.peferencias")
        action_preferences = Gio.SimpleAction.new("peferencias", None)
        action_preferences.connect("activate", self.open_preferences)
        self.win.add_action(action_preferences)
        menu_file.append_section(None, menu_preferences)

        # Option Exit
        menu_exit = Gio.Menu()
        menu_exit.append(_("Salir"), "win.exit")
        action_exit = Gio.SimpleAction.new("exit", None)
        action_exit.connect("activate", self.exit)
        self.win.add_action(action_exit)
        menu_file.append_section(None, menu_exit)

        # Menu help, for menu bar
        menu_help = Gio.Menu()
        self.append_submenu(_("Ayuda"), menu_help)

        menu_shortcuts = Gio.Menu()
        menu_shortcuts.append(_("Atajos de teclado"), "win.help")
        action_help = Gio.SimpleAction.new("help", None)
        action_help.connect("activate", self.help_window)
        self.win.add_action(action_help)
        menu_help.append_section(None, menu_shortcuts)

    def exit(self, action: Gio.SimpleAction, parameter) -> None:
        self.win.exit()

    def open_preferences(self, action: Gio.SimpleAction, parameter) -> None:
        from views.menu_bar.file.preferences.preferences_options import (
            Preferences,
        )

        if not self.preferences:
            self.preferences = Preferences(self.win, self)

    def help_window(self, action: Gio.SimpleAction, parameter):
        print("HOLA")
