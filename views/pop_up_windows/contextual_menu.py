# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from utilities.file_manager import File_manager
from views.pop_up_windows.loading import Loading
from controls.actions import Actions
from pathlib import Path
import subprocess
import threading
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Xdp", "1.0")
gi.require_version("XdpGtk4", "1.0")
from gi.repository import Gtk, Gdk, Gio, GLib, Xdp, XdpGtk4  # noqa E402


class ContextBox(Gio.Menu):

    def __init__(
        self,
        main_window: Gtk.Widget,
        file_context: bool,
        explorer: "explorer",  # noqa: F821
        path_list: list,
        explorer_src,
        explorer_dst,
    ):
        super().__init__()

        self.main_window = main_window
        self.file_context = file_context
        self.explorer = explorer
        self.path_list = path_list
        self.explorer_src = explorer_src
        self.explorer_dst = explorer_dst
        self.action = Actions()
        self.fm = File_manager()

        if file_context:
            self.create_file_context_menu()
        else:
            self.create_explorer_context_menu()

    def create_file_context_menu(self) -> None:

        mirror_str = ""
        if self.explorer_src.name == "explorer_1":
            mirror_str = _("Espejo -->")
        else:
            mirror_str = _("<-- Espejo")

        file_list_btn = {
            mirror_str: self.explorer_mirror,
            _("Abrir"): self.open_file,
            _("Abrir con ..."): self.app_chooser,
            _("Mover"): self.move,
            _("Copiar"): self.copy,
            _("Duplicar"): self.duplicate,
            _("Eliminar"): self.delete,
            _("Renombrar"): self.rename,
            _("Copiar ruta"): self.copy_text_path,
            _("Comprimir"): self.zip_file,
            _("Descomprimir"): self.unzip_file,
            _("Seleccinar por ext"): self.select_for_extension,
            _("Montar"): self.mount_unit,
            _("Desmontar"): self.umount_unit,
            _("Propiedades"): self.get_properties,
        }

        self.set_options_and_actions(file_list_btn)

    def select_for_extension(self, *args) -> None:
        selection = self.explorer_src.get_selected_items_from_explorer()[1]

        if not selection:
            self.action.show_msg_alert(
                self.main_window, _("Debes seleccionar un archivo")
            )
            return

        path = selection[0]

        if path.is_dir():
            self.action.show_msg_alert(
                self.main_window, _("Debes seleccionar un archivo")
            )
            return

        origin_suffix = path.suffix

        for index, item in enumerate(self.explorer_src.selection):
            if item.path_file.suffix == origin_suffix:
                self.explorer_src.selection.select_item(index, False)

    def zip_file(self, *args) -> None:
        from controls.shortcuts_keys import Shortcuts_keys

        Shortcuts_keys(
            self.main_window, self.explorer_src, self.explorer_dst
        ).zip_file(explorer=self.explorer_src)

    def unzip_file(self, *args) -> None:
        from controls.shortcuts_keys import Shortcuts_keys

        Shortcuts_keys(
            self.main_window, self.explorer_src, self.explorer_dst
        ).unzip_file(explorer=self.explorer_src)

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

        self.set_options_and_actions(file_list_btn)

    def set_options_and_actions(self, file_list_btn: list) -> None:
        for key in file_list_btn.keys():

            method = file_list_btn[key]
            method_str = method.__func__.__name__

            action = Gio.SimpleAction.new(method_str, None)
            action.connect("activate", method)
            self.main_window.add_action(action)  # se registra en la ventana

            self.append(key, f"win.{method_str}")

    def rename(self, *args) -> None:
        from utilities.rename import Rename_Logic

        rename_logic = Rename_Logic()
        rename_logic.on_rename(self.explorer_src, self.main_window)

    def copy(self, *args) -> None:
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

    def move(self, *args) -> None:
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

    def duplicate(self, *args) -> None:
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

    def delete(self, *args) -> None:
        from utilities.remove import Remove

        remove = Remove()
        remove.on_delete(
            self.explorer_src, self.explorer_dst, self.main_window
        )

    def get_properties(self, *args) -> None:
        from views.properties.mlncommander_properties import Properties

        Properties(self.main_window, self.path_list)

    def copy_text_path(self, *args) -> None:
        """
        Copy to clipboard all absolute path
        """
        self.clipboard = Gdk.Display.get_default().get_clipboard()

        output_text = ""
        for path in self.path_list:
            output_text += f"{str(path)}\n"

        self.clipboard.set(output_text)

    def new_file(self, *args) -> None:
        from utilities.new_file import NewFile

        new_file = NewFile()
        new_file.on_new_file(self.explorer_src, self.main_window)

    def new_folder(self, *args) -> None:
        from utilities.create import Create

        create = Create()
        create.on_create_dir(
            self.explorer_src, self.explorer_dst, self.main_window
        )

    def explorer_mirror(self, *args) -> None:

        mirroring_path = self.explorer_src.actual_path

        self.explorer_dst.load_new_path(mirroring_path)

    def select_all(self, *args) -> None:
        self.explorer_src.selection.select_all()
        self.explorer_src.selection.unselect_item(0)

    def mount_unit(self, *args) -> None:

        response = self.mount_check()

        if not response["status"]:
            return

        if response["status"] == "mount":
            self.action.show_msg_alert(
                self.main_window, _("Esta carpeta ya está montada")
            )
            return

        path = response["msg"]

        loading = Loading(self.main_window)

        def on_waiting(
            main_window: Gtk.ApplicationWindow,
            explorer_src: Gtk.ColumnView,
            explorer_dst: Gtk.ColumnView,
            action: Actions,
            path: Path,
            loading: Gtk.Window,
        ):
            GLib.idle_add(loading.start)
            mount_response = self.fm.mount_or_umount(main_window, path, True)
            GLib.idle_add(loading.stop)

            if not mount_response["status"]:
                GLib.idle_add(
                    action.show_msg_alert,
                    main_window,
                    _(f"Error al montar: {mount_response["msg"]}"),
                )

            if explorer_dst.actual_path == explorer_src.actual_path:
                GLib.idle_add(
                    explorer_dst.load_new_path, explorer_dst.actual_path
                )

            GLib.idle_add(explorer_src.load_new_path, explorer_src.actual_path)

        threading.Thread(
            target=on_waiting,
            args=(
                self.main_window,
                self.explorer_src,
                self.explorer_dst,
                self.action,
                path,
                loading,
            ),
        ).start()

    def umount_unit(self, *args) -> None:

        response = self.mount_check()

        if not response["status"]:
            return

        if response["status"] == "fstab":
            self.action.show_msg_alert(
                self.main_window, _("Esta carpeta no está montada")
            )
            return
        path = response["msg"]

        loading = Loading(self.main_window)

        def on_waiting(
            main_window: Gtk.ApplicationWindow,
            explorer_src: Gtk.ColumnView,
            explorer_dst: Gtk.ColumnView,
            action: Actions,
            path: Path,
            loading: Gtk.Window,
        ):
            GLib.idle_add(loading.start)
            umount_response = self.fm.mount_or_umount(main_window, path, False)
            GLib.idle_add(loading.stop)
            if not umount_response["status"]:
                GLib.idle_add(
                    action.show_msg_alert,
                    main_window,
                    _(f"Error al desmontar: {umount_response["msg"]}"),
                )

            if not explorer_dst.actual_path == explorer_src.actual_path:
                if explorer_dst.actual_path.absolute().is_relative_to(
                    explorer_src.actual_path.absolute()
                ):
                    GLib.idle_add(
                        explorer_dst.load_new_path, explorer_src.actual_path
                    )

            GLib.idle_add(explorer_src.load_new_path, explorer_src.actual_path)

        threading.Thread(
            target=on_waiting,
            args=(
                self.main_window,
                self.explorer_src,
                self.explorer_dst,
                self.action,
                path,
                loading,
            ),
        ).start()

    def mount_check(self) -> dict:

        selected = self.explorer_src.get_selected_items_from_explorer()[1]

        if len(selected) > 1:
            self.action.show_msg_alert(
                self.main_window,
                _("Debes seleccionar sólo una carpeta"),
            )
            return

        path = selected[0]

        response = self.fm.get_type_from_mounts(path)

        if not response["status"]:
            self.action.show_msg_alert(
                self.main_window,
                _("Esta carpeta no dispone de una ruta de montaje"),
            )
            return {"status": False, "msg": "nothing"}

        response["msg"] = path

        return response

    def open_file(self, *args) -> None:

        path = self.path_list[0]

        if not path or path.is_dir():
            self.action.show_msg_alert(
                self.main_window,
                _("Debes seleccionar un archivo"),
            )
            return

        try:
            subprocess.run(["xdg-open", path])
        except Exception:
            self.show_msg_alert(
                self.parent,
                _(
                    f"""Ha ocurrido algun problema al intentar ejecutar el
                    archivo:\n{path}"""
                ),
            )

    def app_chooser(self, *args) -> None:

        path = self.path_list[0]

        if not path or path.is_dir() or not path.exists():
            self.action.show_msg_alert(
                self.main_window,
                _("Debes seleccionar un archivo"),
            )
            return

        portal = Xdp.Portal.initable_new()
        path = f"file://{path}"
        parent = XdpGtk4.parent_new_gtk(self.main_window)

        def on_uri_opened(portal, result, data=None) -> None:
            try:
                portal.open_uri_finish(result)
            except Exception as e:
                if e.domain != "g-io-error-quark":
                    self.action.show_msg_alert(
                        self.main_window,
                        _(f"Error al abrir el archivo: {e}"),
                    )

        GLib.idle_add(
            portal.open_uri,
            parent,
            path,
            Xdp.OpenUriFlags.ASK,
            None,
            on_uri_opened,
            None,
        )
