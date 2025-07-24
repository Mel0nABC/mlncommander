import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib
from pathlib import Path
import threading, asyncio, time


class Copying(Gtk.Dialog):

    def __init__(self, parent):
        super().__init__(
            title="Copiando ..",
            transient_for=parent,
            modal=True,
        )
        self.src_info = None
        self.dst_info = None
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(self.box)
        self.set_default_size(500, 60)

        self.lbl_src = Gtk.Label(label="SRC")
        self.lbl_src.set_halign(Gtk.Align.START)
        self.lbl_src.set_margin_top(20)
        self.lbl_src.set_margin_end(20)
        self.lbl_src.set_margin_start(20)

        self.lbl_dst = Gtk.Label(label="DST")
        self.lbl_dst.set_halign(Gtk.Align.START)
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
        # self.present()

    def set_labels(self, src_info, dst_info):
        self.src_info = src_info
        self.dst_info = dst_info

    def update_labels(self):
        # ESTA función se ejecuta en el hilo principal (vía idle_add)

        try:
            if self.src_info and self.dst_info:
                self.lbl_src.set_text(str(self.src_info))
                self.lbl_dst.set_text(str(self.dst_info))
                src_size_text = f"{self.src_info.stat().st_size}"
                dst_size_text = f"{self.dst_info.stat().st_size}"

                src_size = int(src_size_text)
                dst_size = int(dst_size_text)

                src_size = src_size / 1024 / 1024
                dst_size = dst_size / 1024 / 1024

                self.lbl_size.set_text(f"{src_size:.2f}/{dst_size:.2f} Mbytes")
                # if src_size == dst_size:
                #     self.dialog_response = True
                #     GLib.idle_add(self.response, Gtk.ResponseType.OK)

        except Exception as e:
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

    def close_copying(self):
        self.dialog_response = True
        GLib.idle_add(self.response, Gtk.ResponseType.OK)
