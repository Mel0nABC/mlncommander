# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
import asyncio
from asyncio import Future
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


class ConfirmWindow(Gtk.Window):
    def __init__(self, parent: Gtk.ApplicationWindow):
        super().__init__(
            transient_for=parent,
            modal=True,
        )

        header = Gtk.HeaderBar()
        header.set_title_widget(
            Gtk.Label(label=_("Solicitud de confirmación"))
        )
        self.set_titlebar(header)

        # Load css

        self.get_style_context().add_class("app_background")
        self.get_style_context().add_class("font")
        self.get_style_context().add_class("font-color")

        horizontal = parent.horizontal

        self.set_default_size(horizontal / 10, -1)

        vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vertical_box.set_margin_top(20)
        vertical_box.set_margin_end(20)
        vertical_box.set_margin_bottom(20)
        vertical_box.set_margin_start(20)

        self.set_child(vertical_box)

        text = _("Si aceptas, cancelaras el proceso actual, ¿Continuar?")
        question_label = Gtk.Label.new(text)

        vertical_box.append(question_label)

        grid = Gtk.Grid(column_spacing=10, row_spacing=5)
        grid.set_margin_top(20)

        grid.set_hexpand(True)
        grid.set_halign(Gtk.Align.CENTER)

        vertical_box.append(grid)

        self.btn_accept = Gtk.Button(label=_("Sí"))
        self.btn_accept.set_name("True")
        self.btn_cancel = Gtk.Button(label=_("No"))
        self.btn_cancel.set_name("False")

        grid.attach(self.btn_accept, 0, 0, 1, 1)
        grid.attach(self.btn_cancel, 1, 0, 1, 1)

        self.btn_accept.connect("clicked", self.get_selected_option)
        self.btn_cancel.connect("clicked", self.get_selected_option)

        self.response_bool = None
        self.future = asyncio.get_event_loop().create_future()

        self.present()

    def get_selected_option(self, botton: Gtk.Button) -> None:
        """
        Set True or False for response_async.
        """
        if botton.get_name() == "True":
            self.response_bool = True
        else:
            self.response_bool = False

        if not self.future.done():
            self.future.set_result(self.response_bool)

    async def wait_response_async(self) -> Future[str]:
        """
        To get response
        """
        response = await self.future
        self.destroy()
        return response
