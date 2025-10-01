# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from utilities.utilities_for_window import UtilsForWindow
import asyncio
import gi
from gi.repository import Gtk


gi.require_version("Gtk", "4.0")


class CreateDirWindow(Gtk.Window):
    def __init__(
        self,
        parent: Gtk.ApplicationWindow,
        explorer_src: "Explorer",  # noqa: F821
    ):
        super().__init__(
            transient_for=parent,
            modal=True,
        )

        header = Gtk.HeaderBar()
        header.set_title_widget(Gtk.Label(label=_("Creando directorio")))
        self.set_titlebar(header)

        UtilsForWindow().set_event_key_to_close(self, self)

        # Load css

        self.get_style_context().add_class("app_background")
        self.get_style_context().add_class("font")
        self.get_style_context().add_class("font-color")

        self.dst_info = explorer_src.actual_path

        horizontal = parent.horizontal
        vertical = parent.vertical

        self.set_default_size(horizontal / 5, vertical / 8)

        vertical_box_info = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        vertical_box_info.set_margin_top(20)
        vertical_box_info.set_margin_start(20)
        self.set_child(vertical_box_info)

        self.entry_file_name = Gtk.Entry()
        self.entry_file_name.connect("activate", self.get_selected_option)

        vertical_box_info.append(self.entry_file_name)

        self.btn_accept = Gtk.Button(label=_("Aceptar"))
        self.btn_cancel = Gtk.Button(label=_("Cancelar"))

        self.btn_accept.connect("clicked", self.get_selected_option)
        self.btn_cancel.connect("clicked", self.exit)

        self.vertical_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )

        self.vertical_box.set_margin_top(20)
        self.vertical_box.set_margin_bottom(20)
        self.vertical_box.set_margin_start(20)
        self.vertical_box.set_margin_end(20)

        self.vertical_box.append(self.btn_accept)
        self.vertical_box.append(self.btn_cancel)

        vertical_box_info.append(self.vertical_box)

        self.response_text = None
        self.future = asyncio.get_event_loop().create_future()
        self.present()

    def exit(self, button: Gtk.Button) -> None:
        """
        Close window on press cancel button
        """
        self.destroy()

    def get_selected_option(self, botton: Gtk.Button) -> None:
        """
        Set on variable entry value
        """
        self.response_text = self.entry_file_name.get_text()
        if not self.future.done():
            self.future.set_result(self.response_text)

        self.destroy()

    async def wait_response_async(self) -> None:
        """
        Response on close window
        """
        response = await self.future
        return response
