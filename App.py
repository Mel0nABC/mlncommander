from views.main_window import Window
from controls.Actions import Actions
import gbulb
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


gbulb.install()  # Integrate asyncio into Gtk


class App(Gtk.Application):

    def __init__(self):
        """
        Constructor
        """
        super().__init__(application_id="com.mel0n.mlncommander")

    def do_activate(self) -> None:
        """
        Initializes the application when the run() method is executed
        """
        action = Actions()
        self.window = Window(self, action)
        action.set_parent(self.window)
        self.window.present()
        self.window.set_explorer_initial()


app = App()
app.run()
