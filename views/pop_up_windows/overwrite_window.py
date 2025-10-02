# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from entity.file_or_directory_info import File_or_directory_info
from utilities.utilities_for_window import UtilsForWindow
from views.mlncommander_explorer import Explorer
import asyncio
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


class OverwriteWindow(Gtk.Window):
    def __init__(
        self,
        parent: Gtk.ApplicationWindow,
        src_info: Explorer,
        dst_info: Explorer,
    ):
        super().__init__(transient_for=parent, modal=True, decorated=False)

        UtilsForWindow().set_event_key_to_close(self, self)

        # Load css

        self.get_style_context().add_class("app_background")
        self.get_style_context().add_class("font")
        self.get_style_context().add_class("font-color")

        self.src_info = File_or_directory_info(src_info)
        self.dst_info = File_or_directory_info(dst_info)
        self.response = None

        horizontal = parent.horizontal
        vertical = parent.vertical

        self.set_default_size(horizontal / 5, vertical / 5)

        vertical_main = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        self.set_child(vertical_main)

        vertical_box_info = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )

        vertical_box_info.set_margin_top(20)
        vertical_box_info.set_margin_start(20)

        src_label_text = f"Origen: {self.src_info.path_file}"
        src_label = Gtk.Label.new(_(src_label_text))
        src_label.set_halign(Gtk.Align.START)
        size_src_label_text = f"Tamaño: {self.src_info.size}"
        size_src_label = Gtk.Label.new(_(_(size_src_label_text)))
        size_src_label.set_halign(Gtk.Align.START)
        date_src_label_text = f"Fecha: {self.src_info.date_created_str}"
        date_src_label = Gtk.Label.new(_(date_src_label_text))
        date_src_label.set_halign(Gtk.Align.START)
        perm_src_label_txt = f"Permisos: {self.src_info.permissions}"
        perm_src_labe = Gtk.Label.new(_(perm_src_label_txt))
        perm_src_labe.set_halign(Gtk.Align.START)

        dst_label_text = f"Destino: {self.dst_info.path_file}"
        dst_label = Gtk.Label.new(_(dst_label_text))
        dst_label.set_margin_top(20)
        dst_label.set_halign(Gtk.Align.START)
        size_dst_label_text = f"Tamaño: {self.dst_info.size}"
        size_dst_label = Gtk.Label.new(_(size_dst_label_text))
        size_dst_label.set_halign(Gtk.Align.START)
        date_dst_label_text = f"Fecha: {self.dst_info.date_created_str}"
        date_dst_label = Gtk.Label.new(_(date_dst_label_text))
        date_dst_label.set_halign(Gtk.Align.START)
        perm_dst_label_text = f"Permisos: {self.dst_info.permissions}"
        perm_dst_label = Gtk.Label.new(_(perm_dst_label_text))
        perm_dst_label.set_halign(Gtk.Align.START)

        vertical_box_info.append(src_label)
        vertical_box_info.append(size_src_label)
        vertical_box_info.append(date_src_label)
        vertical_box_info.append(perm_src_labe)

        vertical_box_info.append(dst_label)
        vertical_box_info.append(size_dst_label)
        vertical_box_info.append(date_dst_label)
        vertical_box_info.append(perm_dst_label)

        vertical_main.append(vertical_box_info)

        self.btn_cancel = Gtk.Button(label=_("Cancelar"))
        self.btn_skip = Gtk.Button(label=_("Omitir"))
        self.btn_over_old = Gtk.Button(label=_("Reemplazar si es más antiguo"))
        self.btn_over_size = Gtk.Button(
            label=_("Reemplazar si el tamaño es diferente")
        )
        self.btn_rename = Gtk.Button(label=_("Renombrar"))
        self.btn_overwrite = Gtk.Button(label=_("Reemplazar"))

        self.btn_cancel.set_name("cancel")
        self.btn_skip.set_name("skip")
        self.btn_over_old.set_name("overwrite_date")
        self.btn_over_size.set_name("overwrite_diff")
        self.btn_rename.set_name("rename")
        self.btn_overwrite.set_name("overwrite")

        self.btn_cancel.connect("clicked", self.set_opcion_seleccionada)
        self.btn_skip.connect("clicked", self.set_opcion_seleccionada)
        self.btn_over_old.connect("clicked", self.set_opcion_seleccionada)
        self.btn_over_size.connect("clicked", self.set_opcion_seleccionada)
        self.btn_rename.connect("clicked", self.set_opcion_seleccionada)
        self.btn_overwrite.connect("clicked", self.set_opcion_seleccionada)

        self.check_all = Gtk.CheckButton.new_with_label(_("Aplicar a todo"))
        self.check_all.set_margin_top(20)
        self.check_all.set_halign(Gtk.Align.END)

        self.vertical_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )

        self.vertical_box.set_margin_top(20)
        self.vertical_box.set_margin_bottom(20)
        self.vertical_box.set_margin_start(20)
        self.vertical_box.set_margin_end(20)

        self.vertical_box.append(self.btn_skip)
        self.vertical_box.append(self.btn_overwrite)
        self.vertical_box.append(self.btn_over_old)
        self.vertical_box.append(self.btn_over_size)
        self.vertical_box.append(self.btn_rename)
        self.vertical_box.append(self.btn_cancel)
        self.vertical_box.append(self.check_all)

        vertical_main.append(self.vertical_box)

        self.future = asyncio.get_event_loop().create_future()

        self.present()

    def set_opcion_seleccionada(self, botton: Gtk.Button) -> None:

        botton_pressed = botton.get_name()

        if botton_pressed == "cancel":
            self.response = {
                "response": "cancel",
                "all_files": self.check_all.get_active(),
            }

        if botton_pressed == "skip":
            self.response = {
                "response": "skip",
                "all_files": self.check_all.get_active(),
            }

        if botton_pressed == "overwrite":
            self.response = {
                "response": "overwrite",
                "all_files": self.check_all.get_active(),
            }

        if botton_pressed == "overwrite_date":
            self.response = {
                "response": "overwrite_date",
                "all_files": self.check_all.get_active(),
            }

        if botton_pressed == "overwrite_diff":
            self.response = {
                "response": "overwrite_diff",
                "all_files": self.check_all.get_active(),
            }

        if botton_pressed == "rename":
            self.response = {
                "response": "rename",
                "all_files": self.check_all.get_active(),
            }

        if not self.future.done():
            self.future.set_result(self.response)

    async def wait_response_async(self) -> None:
        """
        Set response on close dialog
        """
        response = await self.future
        self.destroy()
        return response
