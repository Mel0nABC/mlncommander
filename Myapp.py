from views.main_window import Window
from gi.repository import Gtk, Gio
from controls import Actions


class App(Gtk.Application):
    def __init__(self):
        super().__init__()
        action_exit = Gio.SimpleAction.new("exit", None)
        action_exit.connect("activate", Actions.on_exit)
        self.add_action(action_exit)

    def do_activate(self):
        win = Window(self)
        win.present()

    def get_application(self):
        return self.win
