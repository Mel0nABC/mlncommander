import gi
from gi.repository import Gtk, GLib
import asyncio

gi.require_version("Gtk", "4.0")


class Deleting(Gtk.Dialog):

    def __init__(self, parent, src_info):
        super().__init__(
            title="Eliminando  ..",
            transient_for=parent,
            modal=True,
        )
        self.src_info = src_info
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(self.box)
        self.set_default_size(500, 60)

        self.lbl_src = Gtk.Label(label="SRC")
        self.lbl_src.set_halign(Gtk.Align.START)
        self.lbl_src.set_margin_top(20)
        self.lbl_src.set_margin_end(20)
        self.lbl_src.set_margin_start(20)

        self.btn_cancel = Gtk.Button(label="Cancelar")
        self.btn_cancel.connect("clicked", self.cancel_deleting)
        self.btn_cancel.set_margin_top(20)
        self.btn_cancel.set_margin_end(20)
        self.btn_cancel.set_margin_bottom(20)
        self.btn_cancel.set_margin_start(20)

        self.box.append(self.lbl_src)
        self.box.append(self.btn_cancel)

        self.dialog_response = False
        self.future = asyncio.get_event_loop().create_future()
        self.connect("response", self._on_response)
        self.present()

    def update_labels(self, deleting_file):
        # ESTA función se ejecuta en el hilo principal (vía idle_add)
        try:
            self.lbl_src.set_text(str(deleting_file))
        except Exception:
            self.lbl_src.set_text(str(self.src_info))

    def cancel_deleting(self, button):
        self.dialog_response = False
        GLib.idle_add(self.response, Gtk.ResponseType.CANCEL)

    def _on_response(self, dialog, response_id):
        if not self.future.done():
            self.future.set_result(self.dialog_response)
        self.destroy()

    async def wait_response_async(self):
        response = await self.future
        return response

    def finish_deleting(self):
        self.dialog_response = True
        GLib.idle_add(self.response, Gtk.ResponseType.OK)
