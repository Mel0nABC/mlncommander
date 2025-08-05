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

            # Sorted list with, .., directorys and files
            ordered_list = sorted(path.iterdir(), key=File_manager.custom_key)

            for content in ordered_list:
                new_info = File_or_directory_info(content.absolute())
                list_content.append(new_info)

            return list_content
        except Exception as e:
            print(f"Excepción {e}")
        return list_content

    @staticmethod
    def custom_key(p: Path):
        name = p.name
        if name == "..":
            group = 0
        elif p.is_dir():
            group = 1
        else:
            group = 2
        return (group, name.lower())
