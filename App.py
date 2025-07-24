from views.main_window import Window
from controls.Actions import Actions
import gi, os, time, asyncio

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib

import gbulb

gbulb.install()  # Esto integra asyncio con GTK


class App(Gtk.Application):
    def __init__(self):
        super().__init__()

    def do_activate(self):
        action = Actions()
        self.win = Window(self, action)
        action.set_parent(self.win)
        action_exit = Gio.SimpleAction.new("exit", None)
        action_exit.connect("activate", action.on_exit)
        self.add_action(action_exit)
        self.win.present()


    def get_application(self):
        return self.win


app = App()
app.run()
