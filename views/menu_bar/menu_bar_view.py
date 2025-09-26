# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from views.menu_bar.file.preferences.preferences_options import (
    Preferences,
)
from views.properties.properties import Properties
import subprocess
import gi
from gi.repository import Gtk, Gio  # noqa: E402

gi.require_version("Gtk", "4.0")


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

        # Menu bar to insert in vertical main box, on main_window.Window class
        self.menubar = Gtk.PopoverMenuBar.new_from_model(self)

        self.create_file_submenu()
        self.create_help_submenu()

    def exit(self, action: Gio.SimpleAction, parameter) -> None:
        self.win.exit()

    def create_file_submenu(self) -> None:

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

        # Option Preferences
        menu_propieties = Gio.Menu()
        menu_propieties.append(_("Propiedades"), "win.propieties")
        action_propieties = Gio.SimpleAction.new("propieties", None)
        action_propieties.connect("activate", self.open_propieties)
        self.win.add_action(action_propieties)
        menu_file.append_section(None, menu_propieties)

        # Option Exit
        menu_exit = Gio.Menu()
        menu_exit.append(_("Salir"), "win.exit")
        action_exit = Gio.SimpleAction.new("exit", None)
        action_exit.connect("activate", self.exit)
        self.win.add_action(action_exit)
        menu_file.append_section(None, menu_exit)

    def open_preferences(
        self, action: Gio.SimpleAction = None, parameter=None
    ) -> None:

        if not self.preferences:
            self.preferences = Preferences(self.win, self)

    def open_propieties(
        self, action: Gio.SimpleAction = None, parameter=None
    ) -> None:
        explorer = self.win.get_explorer_focused()
        path_list = explorer.get_selected_items_from_explorer()[1]
        Properties(self.win, path_list)

    def create_help_submenu(self) -> None:

        # Menu help, for menu bar
        menu_help = Gio.Menu()
        self.append_submenu(_("Ayuda"), menu_help)

        menu_shortcuts = Gio.Menu()
        menu_shortcuts.append(_("Atajos de teclado"), "win.help")
        action_help = Gio.SimpleAction.new("help", None)
        action_help.connect("activate", self.shortcut_window)
        self.win.add_action(action_help)
        menu_help.append_section(None, menu_shortcuts)

        menu_about = Gio.Menu()
        menu_about.append(_("Acerca de mlnCommander"), "win.about")
        action_about = Gio.SimpleAction.new("about", None)
        action_about.connect("activate", self.about_window)
        self.win.add_action(action_about)
        menu_help.append_section(None, menu_about)

        menu_log = Gio.Menu()
        menu_log.append(_("Abrir log"), "win.log")
        action_log = Gio.SimpleAction.new("log", None)
        action_log.connect("activate", self.open_log)
        self.win.add_action(action_log)
        menu_help.append_section(None, menu_log)

    def shortcut_window(self, action: Gio.SimpleAction, parameter):
        from views.menu_bar.help.shortcuts_help import ShortCutsHelp

        ShortCutsHelp(self.win)

    def about_window(self, action: Gio.SimpleAction, parameter):
        from views.menu_bar.help.about import About

        About(self.win)

    def open_log(self, action: Gio.SimpleAction, parameter):
        print("OPEN LOG")
        try:
            log_file = f"{self.win.APP_USER_PATH}/log/mlncommander.log"
            subprocess.run(["xdg-open", log_file])
        except Exception:
            self.show_msg_alert(
                self.parent,
                _(
                    f"""Ha ocurrido algun problema al intentar ejecutar el
                    archivo:\n{log_file}"""
                ),
            )