# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT

from utilities.i18n import _
from utilities.compressed_types import compressed_extensions
from entity.file_or_directory_info import File_or_directory_info
from utilities.file_manager import File_manager
from utilities.compression import CompressionManager
from pathlib import Path
import shutil
import subprocess
import shlex
import sys
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib  # noqa:")


class Actions:

    def __init__(self):
        self.parent = None
        self.EXEC_SEVEN_Z_TYPE = CompressionManager().validate_7zip_installed()

    def set_parent(self, parent: Gtk.ApplicationWindow) -> None:
        self.parent = parent

    def on_exit(self, action, param: Gtk.ApplicationWindow) -> None:
        """
        To exis application from file menu
        """
        sys.exit(0)

    def entry_change_path(
        self, entry: Gtk.Entry, explorer: "Explorer"  # noqa: F821
    ) -> None:
        """
        When changing directories by writing it by hand in the entry
        """
        path = Path(entry.get_text())
        self.change_path(explorer, path)
        win = explorer.get_root()
        self.set_explorer_to_focused(explorer, win)

    def on_doble_click_or_enter(
        self,
        column_view: "Explorer",  # noqa: F821
        position: int,
        explorer: "Explorer",  # noqa: F821
        entry: Gtk.Entry,
    ) -> None:
        """
        Double-click a directory row and navigate to it. Click '..'
        and move one directory forward in the path. It doesn't currently
        open files.
        """
        file_or_directory = explorer.selection.get_item(position)

        path = Path(file_or_directory.path_file)
        type_str = file_or_directory.type
        file_or_directory.is_compressed = self.is_path_compressed_file(path)
        is_compressed = file_or_directory.is_compressed

        if type_str == "FILE" or type_str == "LN BREAK" or is_compressed:
            subprocess.run(["xdg-open", path])
            # try:
            #     if self.is_path_compressed_file(path):
            #         self.change_path(explorer, path)
            #     else:
            #         subprocess.run(["xdg-open", path])
            # except Exception as e:
            #     self.show_msg_alert(
            #         self.parent,
            #         _(
            #             "Ha ocurrido algun problema al intentar ejecutar el"
            #             f"archivo:\n{path}\n"
            #             f"{e}"
            #         ),
            #     )
            return

        if path.name == "..":
            actual_path_str = str(explorer.actual_path)
            folders = actual_path_str.split("/")
            folders.pop()

            if len(folders) == 1:
                output_folder = "/"
            else:
                output_folder = ""

                for i in folders:
                    if not i == "":
                        output_folder += f"/{i}"

            path = Path(output_folder)

        self.change_path(explorer, path)

    def change_path(
        self,
        explorer: Gtk.ColumnView,
        path: Path,
    ) -> None:
        """
        Access another directory.
        """
        # if self.is_path_compressed_file(path):
        #     try:

        #         file_or_directory = File_or_directory_info(path, True)

        #         response = self.enter_compressed_file(
        #             file_or_directory, explorer
        #         )

        #         if response["status"]:
        #             list_store = response["msg"]
        #             GLib.idle_add(explorer.load_new_path, path, list_store)
        #         else:
        #             GLib.idle_add(
        #                 self.show_msg_alert, self.parent, response["msg"]
        #             )
        #         return

        #     except Exception as e:
        #         print(f"ERROR: {e}")
        #     return

        try:
            if not path.exists():
                raise FileNotFoundError()
            explorer.load_new_path(path)
        except FileNotFoundError:
            text = _(
                "¡Advertencia! El fichero o directorio de destino no existe"
            )
            GLib.idle_add(self.show_msg_alert, self.parent, text)

    def is_path_compressed_file(self, path: Path) -> bool:

        if path.is_dir():
            return False

        splited_path = str(path).split("/")

        index_result = None

        for index, value in enumerate(splited_path):
            if Path(value).suffix in compressed_extensions:
                index_result = index + 1
                break

        if not index_result:
            return False

        return True

    def enter_compressed_file(
        self,
        file_or_directory: File_or_directory_info,
        explorer: Gtk.ColumnView,
    ) -> dict:

        list_content = Gio.ListStore.new(File_or_directory_info)
        path = file_or_directory.path_file

        first_compressed_file = None
        for item in str(path).split("/"):
            tmp_path = Path(item)
            if tmp_path.suffix in compressed_extensions:
                first_compressed_file = item
                break

        compressed_file = (
            f"{str(path).split(first_compressed_file)[0]}"
            f"{first_compressed_file}"
        )
        compressed_path = str(path).split(first_compressed_file)[1].split("/")
        # delete None strings
        compressed_path = list(filter(None, compressed_path))

        temp_uncompress_folder = Path("/tmp/uncompress")

        if temp_uncompress_folder.exists():
            shutil.rmtree(temp_uncompress_folder)

        temp_uncompress_folder.mkdir()

        # In the will uncompressing file have some subfiles to uncompress
        if len(compressed_path):

            last_compressed_file_on_bucle = compressed_file

            compressed_path.insert(0, compressed_file)
            for index, sub in enumerate(compressed_path):
                print(f"ENTRA: {sub}")
                if not Path(sub).exists():
                    sub = f"/tmp/uncompress/{sub}"

                before_file = Path(compressed_path[index - 1])
                if not self.is_path_compressed_file(before_file) and index > 0:
                    print(f"{before_file} ---> ES UNA CARPETA")
                    sub = f"/tmp/uncompress/{before_file}/{sub}"

                if self.is_path_compressed_file(Path(sub)):
                    print("ARCHIVO COMPRIMIDO")
                    cmd = [
                        self.EXEC_SEVEN_Z_TYPE,
                        "x",
                        last_compressed_file_on_bucle,
                        "-so",
                    ]
                    with open(
                        f"/tmp/uncompress/{shlex.quote(Path(sub).name)}", "wb"
                    ) as file:
                        p = subprocess.run(cmd, stdout=file, check=True)
                else:
                    print("POSIBLE CARPETA")
                    cmd = [
                        self.EXEC_SEVEN_Z_TYPE,
                        "x",
                        last_compressed_file_on_bucle,
                        "-o/tmp/uncompress",
                    ]

                    p = subprocess.run(cmd, capture_output=True, text=True)

                last_compressed_file_on_bucle = sub

            # uncompress the last subfile
            last_compressed_file = f"/tmp/uncompress/{compressed_path[-1]}"
            if self.is_path_compressed_file(Path(last_compressed_file)):
                cmd = [
                    self.EXEC_SEVEN_Z_TYPE,
                    "l",
                    shlex.quote(last_compressed_file),
                ]
                p = subprocess.run(cmd, capture_output=True, text=True)
            else:
                path = Path(last_compressed_file)
                if path.is_dir():
                    for i in path.iterdir():
                        list_content.append(File_or_directory_info(i))

        else:
            print("DIRECTO PACA")
            cmd = [self.EXEC_SEVEN_Z_TYPE, "l", shlex.quote(compressed_file)]
            p = subprocess.run(cmd, capture_output=True, text=True)

        no_empty_str_list = None

        if p.returncode == 0:

            back_row = File_or_directory_info(path="..")
            back_row.type = "BACK"
            back_row.size = ".."
            back_row.date_created_str = ".."
            back_row.permissions = ".."

            list_content.insert(0, back_row)

            output_text = p.stdout
            flag = False

            for row in output_text.splitlines():

                if "-------------------" in row and not flag:
                    flag = True
                    continue

                if "-------------------" in row and flag:
                    flag = False
                    continue

                if flag:

                    date = row[0:19]

                    if not date.strip():
                        date = "???"

                    type_str = row[20:25]
                    if "d" in type_str.lower():
                        type_str = "DIR"
                    else:
                        type_str = "FILE"

                    size = row[26:38].strip()
                    if size == "0":
                        size = "DIR"
                    else:

                        size = File_manager().get_size_and_unit(int(size))

                    split_row = row.split(" ")

                    name = split_row[len(split_row) - 1]

                    if len(compressed_path):
                        last_file = "/tmp/uncompress/" f"{compressed_path[-1]}"
                    else:
                        last_file = compressed_file

                    cmd = ["7z", "l", "-slt", last_file]
                    p = subprocess.run(cmd, capture_output=True, text=True)

                    permissions = ""

                    if p.returncode == 0:
                        return_stdout = p.stdout

                        if "Attributes" in return_stdout:
                            permissions = return_stdout.split("Attributes = ")[
                                1
                            ][1:11]

                        elif "Mode" in return_stdout:
                            permissions = return_stdout.split("Mode = ")[1][
                                0:10
                            ]
                        else:
                            permissions = File_manager().get_permissions(path)[
                                "msg"
                            ]

                    path_filtered = Path(f"{path}/{name}")

                    zip_file_or_dir = File_or_directory_info(
                        path_filtered, True
                    )
                    zip_file_or_dir.permissions = permissions
                    zip_file_or_dir.type = type_str
                    zip_file_or_dir.size = size
                    zip_file_or_dir.date_created_str = date
                    zip_file_or_dir.is_compressed = True
                    zip_file_or_dir.full_path = (
                        explorer.entry_box.search_entry.get_text()
                    )

                    no_empty_str_list = list(filter(None, compressed_path))

                    self.delete_temp_files(no_empty_str_list)

                    compressed_path = list(filter(None, compressed_path))

                    if not compressed_path and "/" not in name:
                        list_content.append(zip_file_or_dir)

                    if compressed_path and name not in compressed_path:
                        list_content.append(zip_file_or_dir)

            return {
                "status": True,
                "msg": list_content,
            }

        else:

            # self.delete_temp_files(no_empty_str_list)

            text = p.stderr.strip()

            return {
                "status": False,
                "msg": _(
                    "Ha ocurrido algún error"
                    " al leer el archivo comprimido.\n\n"
                    f"{text}\n"
                ),
            }

    def delete_temp_files(self, no_empty_str_list: list[str]) -> None:
        for to_del in no_empty_str_list:
            if not to_del.isspace():
                path_to_del = Path(f"/tmp/{to_del}")
                if path_to_del.exists():
                    print(path_to_del)
                    # path_to_del.unlink()

    def show_msg_alert(
        self,
        parent: Gtk.ApplicationWindow,
        text_input: str,
        passwd: bool = None,
    ) -> None:
        """
        Generic alert message, the desired text is passed to it
        """
        # TODO: Change MessageDialog to AlertDialog, is deprecated
        dialog = Gtk.MessageDialog(
            transient_for=parent,
            modal=True,
            buttons=Gtk.ButtonsType.OK,
            message_type=Gtk.MessageType.WARNING,
            text=text_input,
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.get_style_context().add_class("app_background")
        dialog.get_style_context().add_class("font")
        dialog.get_style_context().add_class("font-color")
        dialog.present()

    def set_explorer_to_focused(
        self,
        explorer_to_focused: "Explorer",  # noqa: F821
        win: Gtk.ApplicationWindow,
    ) -> None:
        """
        Managing which browser has focus
        """
        explorer_left = win.explorer_1
        explorer_right = win.explorer_2

        try:
            if explorer_to_focused == explorer_left:
                explorer_left.focused = True
                explorer_right.focused = False
                selection = explorer_right.selection
                if selection:
                    selection.unselect_all()
                win.set_explorer_focused(explorer_left, explorer_right)

            else:
                explorer_right.focused = True
                explorer_left.focused = False
                selection = explorer_left.selection
                if selection:
                    selection.unselect_all()
                win.set_explorer_focused(explorer_right, explorer_left)
        except AttributeError as e:
            print(f"Error inicialización: {e}")

    def close_with_question(self, *args, win: Gtk.ApplicationWindow) -> None:

        win_dialog = Gtk.Window.new()
        win_dialog.set_title(_("Cerrando aplicación"))
        win_dialog.set_transient_for(win)
        win_dialog.set_modal(True)
        win_dialog.set_decorated(False)

        win_dialog.get_style_context().add_class("app_background")
        win_dialog.get_style_context().add_class("font")
        win_dialog.get_style_context().add_class("font-color")

        vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vertical_box.set_margin_top(20)
        vertical_box.set_margin_end(20)
        vertical_box.set_margin_bottom(20)
        vertical_box.set_margin_start(20)

        horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        horizontal_box.set_margin_top(10)
        horizontal_box.set_hexpand(True)
        horizontal_box.set_halign(Gtk.Align.CENTER)

        text = _("¿Confirma que quieres cerrar la aplicación?")
        label = Gtk.Label.new(text)

        btn_accept = Gtk.Button.new_with_label(_("Aceptar"))
        btn_accept.set_margin_end(30)
        btn_cancel = Gtk.Button.new_with_label(_("Cancelar"))

        horizontal_box.append(btn_accept)
        horizontal_box.append(btn_cancel)

        vertical_box.append(label)
        vertical_box.append(horizontal_box)

        win_dialog.set_child(vertical_box)

        def on_accept(button: Gtk.Button) -> None:
            win.exit()

        def on_cancel(button: Gtk.Button) -> None:
            win_dialog.destroy()

        btn_accept.connect("clicked", on_accept)
        btn_cancel.connect("clicked", on_cancel)

        win_dialog.present()

    def open_rename_dialog(
        self,
        explorer_src: Gtk.ColumnView,
        win: Gtk.ApplicationWindow,
        popovermenu: Gtk.PopoverMenu = None,
    ) -> None:
        from utilities.rename import Rename_Logic

        rename_logic = Rename_Logic()
        if popovermenu:
            popovermenu.unparent()
        rename_logic.on_rename(explorer_src, win)

    def open_terminal(self, explorer: Gtk.ColumnView) -> None:
        path = explorer.actual_path
        try:
            terminal_command = explorer.get_root().config.TERMINAL_COMMAND

            cmd = terminal_command.split(" ")
            cmd.append(path)

            p = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )

            if p.returncode != 0:
                error_text = _(
                    "Error al ejecutar la terminal, comprueba la bandera"
                )
                GLib.idle_add(self.show_msg_alert, self.parent, error_text)

        except Exception as e:
            print(f"Error al abrir terminal: {e}")
            text = _(f"Error al abrir la terminal: {e}")
            GLib.idle_add(self.show_msg_alert, self.parent, text)
