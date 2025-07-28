from entity.File_or_directory_info import File_or_directory_info
import gi

# gi.require_version("Gtk", "4.0")
from gi.repository import Gio, Gtk
from pathlib import Path


class File_manager:

    def get_path_list(path: Path):
        list_content = Gio.ListStore.new(File_or_directory_info)

        try:
            back_row = File_or_directory_info(path="..")
            back_row.type = "BACK"
            back_row.size = ".."
            back_row.date_created_str = ".."
            back_row.permissions = ".."

            list_content.append(back_row)

            ordered_list = sorted(
                path.iterdir(), key=lambda x: getattr(x, "name"), reverse=not True
            )

            for content in ordered_list:
                new_info = File_or_directory_info(content.absolute())
                list_content.append(new_info)

            return list_content
        except Exception as e:
            print(f"Excepción {e}")
        return list_content
