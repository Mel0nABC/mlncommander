import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk, Gio, GObject
from entity.File_or_directory_info import File_or_directory_info
from views.copying import Copying
import asyncio


class Selected_for_delete(Gtk.Dialog):

    def __init__(self, parent, explorer_src, selected_items):
        super().__init__(
            title="Lista para eliminar",
            transient_for=parent,
            modal=True,
        )
        self.parent = parent
        self.selected_items = selected_items
        self.explorer_src = explorer_src

        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        geometry = monitor.get_geometry()
        horizontal = geometry.width
        vertical = geometry.height
        self.horizontal_size = horizontal / 5
        self.vertical_size = vertical / 8

        self.set_default_size(self.horizontal_size, self.vertical_size)

        self.box = self.get_content_area()

        self.vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.vertical_box.set_margin_top(20)
        self.vertical_box.set_margin_end(20)
        self.vertical_box.set_margin_bottom(20)
        self.vertical_box.set_margin_start(20)
        self.vertical_box.set_hexpand(True)
        self.vertical_box.set_vexpand(True)

        lbl_src = Gtk.Label(
            label="¿Eliminar permanentemente el/los archivo(s) e directorio(s) seleccionado(s)?\n\nEsta operación no puede deshacerse."
        )
        lbl_src.set_halign(Gtk.Align.START)

        self.vertical_box.append(lbl_src)

        self.show_delete_list()

        horizonntal_box_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        horizonntal_box_btn.set_halign(Gtk.Align.START)

        horizontal_box_btn_sec = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        horizontal_box_btn_sec.set_halign(Gtk.Align.END)

        btn_copy = Gtk.Button(label="Eliminar")
        btn_cancel = Gtk.Button(label="Cancelar")

        horizontal_box_btn_sec.append(btn_copy)
        horizontal_box_btn_sec.append(btn_cancel)

        horizonntal_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        horizonntal_btns.set_margin_top(20)
        horizonntal_btns.set_margin_end(20)
        horizonntal_btns.set_margin_bottom(20)
        horizonntal_box_btn.set_hexpand(True)

        horizonntal_btns.append(horizonntal_box_btn)
        horizonntal_btns.append(horizontal_box_btn_sec)

        self.vertical_box.append(horizonntal_btns)

        self.box.append(self.vertical_box)

        btn_copy.connect("clicked", self.start_delete)
        btn_cancel.connect("clicked", self.on_exit, self)

        self.response = None
        self.future = asyncio.get_event_loop().create_future()
        self.connect("response", self._on_response)

        self.present()

    def show_delete_list(self, button=None):
        items = Gio.ListStore.new(File_or_directory_info)
        for i in self.selected_items:
            items.append(File_or_directory_info(i))

        factory = Gtk.SignalListItemFactory()

        factory.connect(
            "setup", lambda factory, item: item.set_child(Gtk.Label(xalign=0))
        )
        factory.connect(
            "bind",
            lambda factory, item: item.get_child().set_text(
                str(item.get_item().get_property("path"))
            ),
        )

        selection = Gtk.NoSelection.new(model=items)

        list_view = Gtk.ListView.new(model=selection, factory=factory)

        scroll = Gtk.ScrolledWindow()
        scroll.set_child(list_view)
        scroll.set_vexpand(True)
        scroll.set_margin_top(20)
        scroll.set_margin_end(20)
        scroll.set_margin_bottom(20)
        scroll.set_margin_start(20)

        self.vertical_box.append(scroll)
        self.set_default_size(self.horizontal_size, self.vertical_size * 3)

    def on_exit(self, button, window):
        self.response = False
        self.close()

    def start_delete(self, button):
        self.response = True
        self.close()

    def _on_response(self, dialog, response_id):
        if not self.future.done():
            self.future.set_result(self.response)
        self.destroy()

    async def wait_response_async(self):
        response = await self.future
        return response
