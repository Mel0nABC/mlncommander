# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from entity.file_or_directory_info import File_or_directory_info
from utilities.utilities_for_window import UtilsForWindow
from views.mlncommander_explorer import Explorer
import asyncio
import gi
from gi.repository import Gtk, Gio


gi.require_version("Gtk", "4.0")


class Selected_for_delete(Gtk.Window):

    def __init__(
        self,
        parent: Gtk.ApplicationWindow,
        explorer_src: Explorer,
        selected_items: list,
    ):
        super().__init__(transient_for=parent, modal=True, decorated=False)

        UtilsForWindow().set_event_key_to_close(self, self)

        # Load css

        self.get_style_context().add_class("app_background")
        self.get_style_context().add_class("font")
        self.get_style_context().add_class("font-color")

        self.parent = parent
        self.selected_items = selected_items
        self.explorer_src = explorer_src

        horizontal = parent.horizontal
        vertical = parent.vertical

        self.horizontal_size = horizontal / 5
        self.vertical_size = vertical / 8

        self.set_default_size(self.horizontal_size, self.vertical_size)

        self.vertical_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )

        self.set_child(self.vertical_box)

        self.vertical_box.set_margin_top(20)
        self.vertical_box.set_margin_end(20)
        self.vertical_box.set_margin_bottom(20)
        self.vertical_box.set_margin_start(20)
        self.vertical_box.set_hexpand(True)
        self.vertical_box.set_vexpand(True)

        label_title = Gtk.Label(label=_("Lista para eliminar"))
        label_title.set_margin_bottom(10)
        self.vertical_box.append(label_title)

        lbl_src = Gtk.Label(
            label=_(
                "¿Eliminar permanentemente el/los archivo(s) e "
                + "directorio(s) seleccionado(s)?\n\nEsta operación no "
                + "puede deshacerse."
            )
        )
        lbl_src.set_halign(Gtk.Align.START)

        self.vertical_box.append(lbl_src)

        self.show_delete_list()

        horizonntal_box_btn = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        horizonntal_box_btn.set_halign(Gtk.Align.START)

        horizontal_box_btn_sec = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        horizontal_box_btn_sec.set_halign(Gtk.Align.END)

        btn_accept = Gtk.Button(label=_("Eliminar"))
        btn_cancel = Gtk.Button(label=_("Cancelar"))

        horizontal_box_btn_sec.append(btn_accept)
        horizontal_box_btn_sec.append(btn_cancel)

        horizonntal_btns = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        horizonntal_box_btn.set_hexpand(True)

        horizonntal_btns.append(horizonntal_box_btn)
        horizonntal_btns.append(horizontal_box_btn_sec)

        self.vertical_box.append(horizonntal_btns)

        btn_accept.connect("clicked", self.start_delete)
        btn_cancel.connect("clicked", self.on_exit, self)

        self.response = None
        self.future = asyncio.get_event_loop().create_future()

        self.present()
        btn_accept.grab_focus()

    def show_delete_list(self, button: Gtk.Button = None) -> None:
        """
        A new list is generated to show the
        items selected for delete.
        """
        items = Gio.ListStore.new(File_or_directory_info)
        for i in self.selected_items:
            items.append(File_or_directory_info(i))

        factory = Gtk.SignalListItemFactory()

        factory.connect(
            "setup",
            lambda factory, item: item.set_child(Gtk.Label(xalign=0)),
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
        scroll.set_margin_bottom(20)

        self.vertical_box.append(scroll)
        self.set_default_size(self.horizontal_size, self.vertical_size * 3)

    def on_exit(
        self, button: Gtk.Button, window: Gtk.ApplicationWindow
    ) -> None:
        """
        Set respose false
        """
        self.response = False
        if not self.future.done():
            self.future.set_result(self.response)

    def start_delete(self, button: Gtk.Button) -> None:
        """
        Set respose True
        """
        self.response = True
        if not self.future.done():
            self.future.set_result(self.response)

    async def wait_response_async(self) -> bool:
        """
        Response on close dialog
        """
        response = await self.future
        self.destroy()
        return response
