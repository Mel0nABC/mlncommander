from entity.File_or_directory_info import File_or_directory_info
import gi


gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GLib
import asyncio

class Overwrite_dialog(Gtk.Dialog):
    def __init__(self, parent, src_info, dst_info):
        super().__init__(
            title="Elige una opción para sobre escribir",
            transient_for=parent,
            modal=True,
        )
        self.src_info = File_or_directory_info(src_info)
        self.dst_info = File_or_directory_info(dst_info)
        self.response = None

        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        geometry = monitor.get_geometry()
        horizontal = geometry.width
        vertical = geometry.height

        self.set_default_size(horizontal / 5, vertical / 5)

        # Área de contenido
        box = self.get_content_area()

        vertical_box_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vertical_box_info.set_margin_top(20)
        vertical_box_info.set_margin_start(20)

        src_label = Gtk.Label.new(f"Origen: {self.src_info.path_file}")
        src_label.set_halign(Gtk.Align.START)
        size_src_label = Gtk.Label.new(f"Tamaño: {self.src_info.size}")
        size_src_label.set_halign(Gtk.Align.START)
        date_src_label = Gtk.Label.new(f"Fecha: {self.src_info.date_created_str}")
        date_src_label.set_halign(Gtk.Align.START)
        perm_src_labe = Gtk.Label.new(f"Permisos: {self.src_info.permissions}")
        perm_src_labe.set_halign(Gtk.Align.START)

        dst_label = Gtk.Label.new(f"Destino: {self.dst_info.path_file}")
        dst_label.set_margin_top(20)
        dst_label.set_halign(Gtk.Align.START)
        size_dst_label = Gtk.Label.new(f"Tamaño: {self.dst_info.size}")
        size_dst_label.set_halign(Gtk.Align.START)
        date_dst_label = Gtk.Label.new(f"Fecha: {self.dst_info.date_created_str}")
        date_dst_label.set_halign(Gtk.Align.START)
        perm_dst_labe = Gtk.Label.new(f"Permisos: {self.dst_info.permissions}")
        perm_dst_labe.set_halign(Gtk.Align.START)

        vertical_box_info.append(src_label)
        vertical_box_info.append(size_src_label)
        vertical_box_info.append(date_src_label)
        vertical_box_info.append(perm_src_labe)

        vertical_box_info.append(dst_label)
        vertical_box_info.append(size_dst_label)
        vertical_box_info.append(date_dst_label)
        vertical_box_info.append(perm_dst_labe)

        box.append(vertical_box_info)

        self.boton1 = Gtk.Button(label="CANCELAR")
        self.boton2 = Gtk.Button(label="SALTAR")
        self.boton3 = Gtk.Button(label="REEMPLAZAR SI ES MÁS ANTIGUO")
        self.boton4 = Gtk.Button(label="REEMPLAZAR SI EL TAMAÑO ES DIFERENTE")
        self.boton5 = Gtk.Button(label="RENOMBRAR")
        self.boton6 = Gtk.Button(label="REEMPLAZAR")

        self.boton1.set_name("cancel")
        self.boton2.set_name("skip")
        self.boton3.set_name("overwrite_date")
        self.boton4.set_name("overwrite_diff")
        self.boton5.set_name("rename")
        self.boton6.set_name("overwrite")

        self.boton1.connect("clicked", self.get_opcion_seleccionada)
        self.boton2.connect("clicked", self.get_opcion_seleccionada)
        self.boton3.connect("clicked", self.get_opcion_seleccionada)
        self.boton4.connect("clicked", self.get_opcion_seleccionada)
        self.boton5.connect("clicked", self.get_opcion_seleccionada)
        self.boton6.connect("clicked", self.get_opcion_seleccionada)

        self.check_all = Gtk.CheckButton.new_with_label("Aplicar a todo")
        self.check_all.set_margin_top(20)
        self.check_all.set_halign(Gtk.Align.END)

        self.vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.vertical_box.set_margin_top(20)
        self.vertical_box.set_margin_bottom(20)
        self.vertical_box.set_margin_start(20)
        self.vertical_box.set_margin_end(20)

        self.vertical_box.append(self.boton2)
        self.vertical_box.append(self.boton6)
        self.vertical_box.append(self.boton3)
        self.vertical_box.append(self.boton4)
        self.vertical_box.append(self.boton5)
        self.vertical_box.append(self.boton1)
        self.vertical_box.append(self.check_all)

        box.append(self.vertical_box)

        self.future = asyncio.get_event_loop().create_future()
        self.connect("response", self._on_response)
        self.present()


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

        if botton_pressed == "overwrite":
            self.response = {
                "response": "overwrite",
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

    def _on_response(self, dialog, response_id):
        if not self.future.done():
            self.future.set_result(self.response)
        self.destroy()


    async def wait_response_async(self):
        response = await self.future
        return response
