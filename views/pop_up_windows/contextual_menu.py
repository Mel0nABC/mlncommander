# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from functools import partial
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Gio  # noqa E402


class ContextBox(Gtk.Box):

    def __init__(
        self,
        main_window: Gtk.Widget,
        file_context: bool,
        explorer: "explorer",  # noqa: F821
        popover: Gtk.Popover,
        path_list: list,
        explorer_src,
        explorer_dst,
    ):
        super().__init__()

        self.main_window = main_window
        self.file_context = file_context
        self.explorer = explorer
        self.path_list = path_list
        self.popover = popover
        self.explorer_src = explorer_src
        self.explorer_dst = explorer_dst

        self.close_contextual_menu_1 = None
        self.close_contextual_menu_2 = None
        self.close_contextual_menu_3 = None

        self.close_contextual_menu_1_handler_id = None
        self.close_contextual_menu_2_handler_id = None
        self.close_contextual_menu_3_handler_id = None

        # Menu visible, container
        self.main_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )

        self.append(self.main_box)

        self.main_box.set_spacing(0)

        if file_context:
            self.create_file_context_menu()
        else:
            self.create_explorer_context_menu()

    def disable_gesture_click(self, widget, x, y) -> None:

        self.close_contextual_menu_1.disconnect(
            self.close_contextual_menu_1_handler_id
        )
        self.close_contextual_menu_2.disconnect(
            self.close_contextual_menu_2_handler_id
        )
        self.close_contextual_menu_3.disconnect(
            self.close_contextual_menu_3_handler_id
        )

    def rename(self, button: Gtk.Button) -> None:
        from utilities.rename import Rename_Logic

        rename_logic = Rename_Logic()
        rename_logic.on_rename(self.explorer_src, self.main_window)
        self.popover.popdown()

    def copy(self, button: Gtk.Button) -> None:
        from utilities.my_copy_or_move import MyCopyMove

        my_copy_move = MyCopyMove()
        my_copy_move.on_copy_or_move(
            self.explorer_src,
            self.explorer_dst,
            None,
            self.main_window,
            _("copiar"),
            True,
            False,
        )
        self.popover.popdown()

    def move(self, button: Gtk.Button) -> None:
        from utilities.my_copy_or_move import MyCopyMove

        my_copy_move = MyCopyMove()
        my_copy_move.on_copy_or_move(
            self.explorer_src,
            self.explorer_dst,
            None,
            self.main_window,
            _("mover"),
            False,
            False,
        )
        self.popover.popdown()

    def duplicate(self, button: Gtk.Button) -> None:
        from utilities.my_copy_or_move import MyCopyMove

        my_copy_move = MyCopyMove()

        # Duplicar
        my_copy_move.on_copy_or_move(
            self.explorer_src,
            self.explorer_dst,
            None,
            self.main_window,
            _("copiar"),
            True,
            True,
        )
        self.popover.popdown()

    def delete(self, button: Gtk.Button) -> None:
        from utilities.remove import Remove

        remove = Remove()
        remove.on_delete(
            self.explorer_src, self.explorer_dst, self.main_window
        )
        self.popover.popdown()

    def get_properties(self, button: Gtk.Button) -> None:
        from views.properties.properties import Properties

        Properties(self.main_window, self.path_list)
        self.popover.popdown()

    def copy_text_path(self, button: Gtk.Button) -> None:
        """
        Copy to clipboard all absolute path
        """
        self.clipboard = Gdk.Display.get_default().get_clipboard()

        output_text = ""
        for path in self.path_list:
            output_text += f"{str(path)}\n"

        self.clipboard.set(output_text)
        self.popover.popdown()

    def create_file_context_menu(self) -> None:
        mirror_str = ""
        if self.explorer_src.name == "explorer_1":
            mirror_str = _("Espejo -->")
        else:
            mirror_str = _("<-- Espejo")

        file_list_btn = {
            _("Renombrar"): self.rename,
            _("Copiar"): self.copy,
            _("Mover"): self.move,
            _("Eliminar"): self.delete,
            _("Duplicar"): self.duplicate,
            _("Propiedades"): self.get_properties,
            mirror_str: self.explorer_mirror,
            _("Copiar rutas"): self.copy_text_path,
        }

        self.create_actions_btn(file_list_btn)

    def create_actions_btn(self, file_list_btn: list) -> None:

        for key in file_list_btn.keys():
            self.btn = Gtk.Button.new_with_label(key)
            self.btn.connect("clicked", partial(file_list_btn[key]))
            self.main_box.append(self.btn)

    def create_explorer_context_menu(self) -> None:
        mirror_str = ""
        if self.explorer_src.name == "explorer_1":
            mirror_str = _("Espejo -->")
        else:
            mirror_str = _("<-- Espejo ")
        file_list_btn = {
            _("Nuevo fichero"): self.new_file,
            _("Nueva carpeta"): self.new_folder,
            mirror_str: self.explorer_mirror,
            _("Seleccionar todo"): self.select_all,
        }

        self.create_actions_btn(file_list_btn)

    def new_file(self, button: Gtk.Button) -> None:
        from utilities.new_file import NewFile

        new_file = NewFile()
        new_file.on_new_file(self.explorer_src, self.main_window)
        self.popover.popdown()

    def new_folder(self, button: Gtk.Button) -> None:
        from utilities.create import Create

        create = Create()
        create.on_create_dir(
            self.explorer_src, self.explorer_dst, self.main_window
        )
        self.popover.popdown()

    def explorer_mirror(self, button: Gtk.Button) -> None:

        mirroring_path = self.explorer_src.actual_path

        self.explorer_dst.load_new_path(mirroring_path)

        self.popover.popdown()

    def select_all(self, button: Gtk.Button) -> None:
        self.explorer_src.selection.select_all()
        self.popover.popdown()
