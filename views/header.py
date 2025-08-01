import gi
from gi.repository import Gtk, Gio


class header:
    """
    Clase que crea el header de la ventana principal, así adquirimos los detalles del tema del sistema.
    """

    def __init__(self):
        self.header = Gtk.HeaderBar()
        title = Gtk.Label(label="MLN Commander")
        self.header.set_title_widget(title)
        self.header.set_show_title_buttons(True)

    def get_new_header(self) -> Gtk.HeaderBar:
        return self.header
