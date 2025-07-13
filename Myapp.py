from views.main_window import Window
from gi.repository import Gtk, Gio
from controls.Actions import Actions


class App(Gtk.Application):
    def __init__(self):
        super().__init__()

        

    def do_activate(self):
        win = Window(self)
        action = Actions(win)
        action_exit = Gio.SimpleAction.new("exit", None)
        action_exit.connect("activate", action.on_exit)
        self.add_action(action_exit)
        win.present()

    def get_application(self):
        return self.win
