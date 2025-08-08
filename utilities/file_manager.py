from entity.File_or_directory_info import File_or_directory_info
from pathlib import Path
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio  # noqa: E402


class File_manager:

    def get_path_list(path: Path) -> Gio.ListStore:
        """
        Returns io.ListStore of files and directorys from path "path"
        """
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

    def custom_key(path: Path) -> tuple[int, str]:
        """
        Sort first list_content, '..' first, directorys on midle and files last
        """
        name = path.name
        if name == "..":
            group = 0
        elif path.is_dir():
            group = 1
        else:
            group = 2
        return (group, name.lower())
