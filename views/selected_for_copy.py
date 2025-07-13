import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk, Gio, GObject
from entity.File_or_directory_info import File_or_directory_info


class Selected_for_copy(Gtk.Dialog):

    def __init__(self, parent, action, explorer_src, explorer_dst, selected_items):
        super().__init__(
            title="Lista para copiar",
            transient_for=parent,
            modal=True,
        )

        self.parent = parent
        self.selected_items = selected_items
        self.explorer_src = explorer_src
        self.explorer_dst = explorer_dst
        self.action = action

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

        lbl_dst = Gtk.Label(label="Destino a copiar:")
        lbl_dst.set_halign(Gtk.Align.START)

        entry_dst = Gtk.Entry()
        entry_dst.set_text(str(self.explorer_dst.actual_path))
        entry_dst.set_hexpand(True)

        self.vertical_box.append(lbl_dst)
        self.vertical_box.append(entry_dst)

        horizonntal_box_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        btn_show_files = Gtk.Button(label=f"Archivos ({len(self.selected_items)})")
        horizonntal_box_btn.append(btn_show_files)
        horizonntal_box_btn.set_halign(Gtk.Align.START)

        horizontal_box_btn_sec = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        horizontal_box_btn_sec.set_halign(Gtk.Align.END)

        btn_copy = Gtk.Button(label="Copiar")
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

        btn_show_files.connect("clicked", self.show_copy_list)
        btn_copy.connect("clicked", self.start_copy)
        btn_cancel.connect("clicked", self.on_exit, self)

        self.show()

    def on_exit(self, button, window):
        window.destroy()

    def show_copy_list(self, button):
        items = Gio.ListStore.new(File_or_directory_info)
        for i in self.selected_items:
            items.append(i)
            print(i.path)

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

    def start_copy(self, button):
        # Cuando sólo se copia un archivo o un directorio
        if len(self.selected_items) == 1:
            self.action.copy_one_file_dir(
                self.explorer_src, self.explorer_dst, self.parent, self.selected_items
            )
        else:
            # Cuando se copian varios arcivos o directorios
            self.action.copy_multi_file_dir(
                self.parent, self.explorer_src, self.explorer_dst
            )

        self.explorer_dst.load_new_path(self.explorer_dst.actual_path)
        self.destroy()
