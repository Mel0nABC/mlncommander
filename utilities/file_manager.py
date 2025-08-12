from entity.File_or_directory_info import File_or_directory_info
from pathlib import Path
import gi
import shutil

gi.require_version("Gtk", "4.0")
from gi.repository import Gio  # noqa: E402


class File_manager:

    def get_path_list(path: Path) -> Gio.ListStore:
        """
        Returns io.ListStore of files and directorys from path "path"
        """
        list_content = Gio.ListStore.new(File_or_directory_info)

        try:
            if not path == Path("/"):
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

    def check_free_space(self, item_list: list, dst_dir: Path) -> bool:
        """
        Check if have space on destination location
        for copy or move all files and directorys
        """
        total_size = 0

        for item in item_list:
            if item.is_dir():
                for archivo in item.rglob("*"):
                    total_size += archivo.stat().st_size
            else:
                total_size += item.stat().st_size

        dst_free_size = shutil.disk_usage(dst_dir).free

        if dst_free_size < total_size:
            return False

        return True
