from pathlib import Path
import gi
import asyncio

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib  # noqa: E402


class Deleting(Gtk.Dialog):

    def __init__(self, parent: Gtk.ApplicationWindow, src_info: Path):
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

    def update_labels(self, deleting_file: Path) -> None:
        """
        Force update labels with real information
        """
        try:
            self.lbl_src.set_text(str(deleting_file))
        except Exception:
            self.lbl_src.set_text(str(self.src_info))

    def cancel_deleting(self, button: Gtk.Button) -> None:
        """
        Close dialog and return False
        """
        self.dialog_response = False
        GLib.idle_add(self.response, Gtk.ResponseType.CANCEL)

    def _on_response(self, dialog, response_id) -> None:
        """
        Set response on close dialog
        """
        if not self.future.done():
            self.future.set_result(self.dialog_response)
        self.destroy()

    async def wait_response_async(self) -> bool:
        """
        Response on close dialog
        """
        response = await self.future
        return response

    def finish_deleting(self) -> None:
        """
        Set response on close dialog
        """
        self.dialog_response = True
        GLib.idle_add(self.response, Gtk.ResponseType.OK)
