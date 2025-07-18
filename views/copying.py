import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib
from pathlib import Path
import threading, asyncio, time


class Copying(Gtk.Dialog):

    def __init__(self, parent, src_info, dst_info):
        super().__init__(
            title="Copiando ..",
            transient_for=parent,
            modal=True,
        )

        self.src_info = src_info
        self.dst_info = dst_info
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(self.box)
        self.set_default_size(500, 60)

        self.lbl_src = Gtk.Label(label="SRC")
        self.lbl_src.set_margin_top(20)
        self.lbl_src.set_margin_end(20)
        self.lbl_src.set_margin_start(20)

        self.lbl_dst = Gtk.Label(label="DST")
        self.lbl_dst.set_margin_top(20)
        self.lbl_dst.set_margin_end(20)
        self.lbl_dst.set_margin_start(20)

        self.lbl_size = Gtk.Label(label="0 bytes")
        self.lbl_size.set_margin_top(20)
        self.lbl_size.set_margin_end(20)
        self.lbl_size.set_margin_start(20)

        self.btn_cancel = Gtk.Button(label="Cancelar")
        self.btn_cancel.connect("clicked", self.cancel_copying)
        self.btn_cancel.set_margin_top(20)
        self.btn_cancel.set_margin_end(20)
        self.btn_cancel.set_margin_bottom(20)
        self.btn_cancel.set_margin_start(20)

        self.box.append(self.lbl_src)
        self.box.append(self.lbl_dst)
        self.box.append(self.lbl_size)
        self.box.append(self.btn_cancel)

        self.dialog_response = False
        self.future = asyncio.get_event_loop().create_future()
        self.connect("response", self._on_response)
        self.present()

    def update_labels(self):
        # ESTA función se ejecuta en el hilo principal (vía idle_add)
        try:
            self.lbl_src.set_text(str(self.src_info))
            self.lbl_dst.set_text(str(self.dst_info))
            src_size = f"{self.src_info.stat().st_size}"
            dst_size = f"{self.dst_info.stat().st_size}"
            self.lbl_size.set_text(f"{src_size}/{dst_size} bytes")
            if src_size == dst_size:
                self.dialog_response = True
                GLib.idle_add(self.response, Gtk.ResponseType.OK)

        except Exception as e:
            # print("Error")
            self.lbl_src.set_text(str(self.src_info))
            self.lbl_dst.set_text("Obteniendo destino ..")
            self.lbl_size.set_text("Caldulando ...")
            print(e)

    def cancel_copying(self, button):
        self.dialog_response = False
        GLib.idle_add(self.response, Gtk.ResponseType.OK)

    def _on_response(self, dialog, response_id):
        if not self.future.done():
            self.future.set_result(self.dialog_response)
        self.destroy()

    async def wait_response_async(self):
        response = await self.future
        return response
