from views.main_window import Window
from controls.Actions import Actions
import sys, gi, os, time, asyncio
from pathlib import Path

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
        self.win.present()

    def get_application(self):
        return self.win

    def exit():
        print("test")


app = App()
app.run()
