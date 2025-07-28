from entity.File_or_directory_info import File_or_directory_info
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GLib
import asyncio


class Rename_dialog(Gtk.Dialog):
    def __init__(self, parent, dst_info):
        super().__init__(
            title="Renombrando archivo",
            transient_for=parent,
            modal=True,
        )
        self.dst_info = File_or_directory_info(dst_info)
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
        dst_label = Gtk.Label.new(f"Destino: {self.dst_info.path_file}")
        dst_label.set_margin_top(20)
        dst_label.set_halign(Gtk.Align.START)
        size_dst_label = Gtk.Label.new(f"Tamaño: {self.dst_info.size}")
        size_dst_label.set_halign(Gtk.Align.START)
        date_dst_label = Gtk.Label.new(f"Fecha: {self.dst_info.date_created_str}")
        date_dst_label.set_halign(Gtk.Align.START)
        perm_dst_labe = Gtk.Label.new(f"Permisos: {self.dst_info.permissions}")
        perm_dst_labe.set_halign(Gtk.Align.START)

        vertical_box_info.append(dst_label)
        vertical_box_info.append(size_dst_label)
        vertical_box_info.append(date_dst_label)
        vertical_box_info.append(perm_dst_labe)

        self.entry_file_name = Gtk.Entry()
        self.entry_file_name.set_text(self.dst_info.name)
        self.entry_file_name.connect("activate",self.get_opcion_seleccionada)
        vertical_box_info.append(self.entry_file_name)

        box.append(vertical_box_info)

        self.boton1 = Gtk.Button(label="ACEPTAR")
        self.boton2 = Gtk.Button(label="CANCELAR")

        self.boton1.connect("clicked", self.get_opcion_seleccionada)
        # self.boton2.connect("clicked", self.exit)
        self.boton2.connect(
            "clicked", lambda btn: self.response(Gtk.ResponseType.CANCEL)
        )
        self.vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.vertical_box.set_margin_top(20)
        self.vertical_box.set_margin_bottom(20)
        self.vertical_box.set_margin_start(20)
        self.vertical_box.set_margin_end(20)

        self.vertical_box.append(self.boton1)
        self.vertical_box.append(self.boton2)

        box.append(self.vertical_box)

        self.response_text = None
        self.future = asyncio.get_event_loop().create_future()
        self.connect("response", self._on_response)
        self.present()

    def exit(self, button):
        self.destroy()

    def get_opcion_seleccionada(self, botton):
        self.response_text = self.entry_file_name.get_text()
        self.close()

    def _on_response(self, dialog, response_id):
        if not self.future.done():
            self.future.set_result(self.response_text)
        self.destroy()

    async def wait_response_async(self):
        response = await self.future
        return response
