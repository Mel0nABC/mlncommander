import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk


class Overwrite_dialog(Gtk.Dialog):
    def __init__(self, parent):

        super().__init__(
            title="Elige una opción para sobre escribir",
            transient_for=parent,
            modal=True,
        )

        self.response = None

        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        geometry = monitor.get_geometry()
        horizontal = geometry.width
        vertical = geometry.height

        self.set_default_size(horizontal / 5, vertical / 5)

        self.add_buttons(
            "_Cancelar", Gtk.ResponseType.CANCEL, "_Aceptar", Gtk.ResponseType.OK
        )

        # Área de contenido
        box = self.get_content_area()

        self.boton1 = Gtk.Button(label="CANCELAR")
        self.boton2 = Gtk.Button(label="SALTAR")
        self.boton3 = Gtk.Button(label="REEMPLAZAR SI ES MÁS ANTIGUO")
        self.boton4 = Gtk.Button(label="REEMPLAZAR SI EL TAMAÑO ES DIFERENTE")
        self.boton5 = Gtk.Button(label="RENOMBRAR")

        self.boton1.set_name("cancel")
        self.boton2.set_name("skip")
        self.boton3.set_name("overwrite_date")
        self.boton4.set_name("overwrite_diff")
        self.boton5.set_name("rename")

        self.boton1.connect("clicked", self.get_opcion_seleccionada)
        self.boton2.connect("clicked", self.get_opcion_seleccionada)
        self.boton3.connect("clicked", self.get_opcion_seleccionada)
        self.boton4.connect("clicked", self.get_opcion_seleccionada)
        self.boton5.connect("clicked", self.get_opcion_seleccionada)

        self.check_all = Gtk.CheckButton.new_with_label("Aplicar a todo")
        self.check_all.set_margin_top(20)

        self.vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.vertical_box.set_margin_top(20)
        self.vertical_box.set_margin_bottom(20)
        self.vertical_box.set_margin_start(20)
        self.vertical_box.set_margin_end(20)

        self.vertical_box.append(self.boton1)
        self.vertical_box.append(self.boton2)
        self.vertical_box.append(self.boton3)
        self.vertical_box.append(self.boton4)
        self.vertical_box.append(self.boton5)
        self.vertical_box.append(self.check_all)

        box.append(self.vertical_box)

        # self.show()

        self.boton1.set_name("cancel")
        self.boton2.set_name("skip")
        self.boton3.set_name("overwrite_date")
        self.boton4.set_name("overwrite_diff")
        self.boton5.set_name("rename")

    def get_opcion_seleccionada(self, botton):

        botton_pressed = botton.get_name()

        if botton_pressed == "cancel":
            self.response = {
                "response": "cancel",
                "all_files": self.check_all.get_active(),
            }

        if botton_pressed == "skip":
            self.response = {
                "response": "skip",
                "all_files": self.check_all.get_active(),
            }

        if botton_pressed == "overwrite_date":
            self.response = {
                "response": "overwrite_date",
                "all_files": self.check_all.get_active(),
            }

        if botton_pressed == "overwrite_diff":
            self.response = {
                "response": "overwrite_diff",
                "all_files": self.check_all.get_active(),
            }

        if botton_pressed == "rename":
            self.response = {
                "response": "rename",
                "all_files": self.check_all.get_active(),
            }

        self.close()
