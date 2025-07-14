import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk
from pathlib import Path


class Copying(Gtk.Dialog):

    def __init__(self, parent, explorer_src, explorer_dst, selected_items):
        super().__init__(
            title="Copiando ..",
            transient_for=parent,
            modal=True,
        )

        self.explorer_src = explorer_src
        self.explorer_dst = explorer_dst
        self.selected_items = selected_items

        self.box = self.get_content_area()
        self.set_default_size(500, 60)

        self.lbl_info = Gtk.Label(label="Hola")
        self.lbl_info.set_margin_top(20)
        self.lbl_info.set_margin_end(20)
        self.lbl_info.set_margin_bottom(20)
        self.lbl_info.set_margin_start(20)

        self.box.append(self.lbl_info)

        print("CREADA VENTANA COPIAR")

    def set_file_path(self, path: Path):
        print(f"TIPO FILE PATH: {type(path)}")
        self.lbl_info.set_text(str(path))

    async def copy_proccess(self, src_file, dst_file):
        print("COpy proccess")
        copy_proccess = Copying(self.parent)
        copy_proccess.show()
        for i in range(1000):
            await time.sleep(1)
            print(i)
