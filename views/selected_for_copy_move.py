import gi
from gi.repository import Gtk, Gio
from entity.File_or_directory_info import File_or_directory_info
import asyncio

gi.require_version("Gtk", "4.0")


class Selected_for_copy_move(Gtk.Dialog):

    def __init__(
        self,
        parent,
        explorer_src,
        explorer_dst,
        selected_items,
        btn_src,
    ):
        super().__init__(
            title=f"Listo para {str.lower(btn_src)} ..",
            transient_for=parent,
            modal=True,
        )
        self.parent = parent
        self.selected_items = selected_items
        self.explorer_src = explorer_src
        self.explorer_dst = explorer_dst
        self.list_files_show = False

        horizontal = parent.horizontal
        vertical = parent.vertical

        self.horizontal_size = horizontal / 5
        self.vertical_size = vertical / 8

        self.on_default_size()

        self.box = self.get_content_area()

        self.vertical_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        self.vertical_box.set_margin_top(20)
        self.vertical_box.set_margin_end(20)
        self.vertical_box.set_margin_bottom(20)
        self.vertical_box.set_margin_start(20)
        self.vertical_box.set_hexpand(True)
        self.vertical_box.set_vexpand(True)

        lbl_dst = Gtk.Label(label="Destino:")
        lbl_dst.set_halign(Gtk.Align.START)

        entry_dst = Gtk.Entry()
        entry_dst.set_text(str(self.explorer_dst.actual_path))
        entry_dst.set_hexpand(True)

        entry_dst.connect("activate", self.start_copy)

        self.vertical_box.append(lbl_dst)
        self.vertical_box.append(entry_dst)

        horizonntal_box_btn = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        btn_show_files = Gtk.Button(
            label=f"Archivos ({len(self.selected_items)})"
        )
        horizonntal_box_btn.append(btn_show_files)
        horizonntal_box_btn.set_halign(Gtk.Align.START)

        horizontal_box_btn_sec = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        horizontal_box_btn_sec.set_halign(Gtk.Align.END)

        btn_copy = Gtk.Button(label=btn_src)
        btn_cancel = Gtk.Button(label="Cancelar")

        horizontal_box_btn_sec.append(btn_copy)
        horizontal_box_btn_sec.append(btn_cancel)

        horizonntal_btns = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        horizonntal_btns.set_margin_top(20)
        horizonntal_btns.set_margin_end(20)
        horizonntal_btns.set_margin_bottom(20)
        horizonntal_box_btn.set_hexpand(True)

        horizonntal_btns.append(horizonntal_box_btn)
        horizonntal_btns.append(horizontal_box_btn_sec)

        self.vertical_box.append(horizonntal_btns)

        self.box.append(self.vertical_box)

        btn_show_files.connect("clicked", self.show_copy_list)
        btn_copy.connect("clicked", self.start_copy)
        btn_cancel.connect("clicked", self.on_exit, self)

        self.response = None
        self.future = asyncio.get_event_loop().create_future()
        self.connect("response", self._on_response)

        self.present()

    def show_copy_list(self, button):
        if not self.list_files_show:
            items = Gio.ListStore.new(File_or_directory_info)
            for i in self.selected_items:
                items.append(File_or_directory_info(i))

            factory = Gtk.SignalListItemFactory()

            factory.connect(
                "setup",
                lambda factory, item: item.set_child(
                    Gtk.Label(xalign=0)
                ),
            )
            factory.connect(
                "bind",
                lambda factory, item: item.get_child().set_text(
                    str(item.get_item().get_property("path"))
                ),
            )

            selection = Gtk.NoSelection.new(model=items)

            list_view = Gtk.ListView.new(
                model=selection, factory=factory
            )

            self.scroll = Gtk.ScrolledWindow()
            self.scroll.set_child(list_view)
            self.scroll.set_vexpand(True)
            self.scroll.set_margin_top(20)
            self.scroll.set_margin_end(20)
            self.scroll.set_margin_bottom(20)
            self.scroll.set_margin_start(20)

            self.vertical_box.append(self.scroll)
            self.set_default_size(
                self.horizontal_size, self.vertical_size * 3
            )
            self.list_files_show = True
        else:
            self.list_files_show = False
            self.vertical_box.remove(self.scroll)
            self.on_default_size()

    def on_exit(self, button, window):
        self.response = False
        self.close()

    def start_copy(self, button):
        self.response = True
        self.close()

    def _on_response(self, dialog, response_id):
        if not self.future.done():
            self.future.set_result(self.response)
        self.destroy()

    async def wait_response_async(self):
        response = await self.future
        return response

    def on_default_size(self):
        self.set_default_size(
            self.horizontal_size, self.vertical_size
        )
