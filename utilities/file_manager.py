from entity.File_or_directory_info import File_or_directory_info
import gi
from gi.repository import Gio
from pathlib import Path


class File_manager:

    def get_path_list(path: Path):
        try:
            list_content = Gio.ListStore.new(File_or_directory_info)
            back_row = File_or_directory_info(path="..")
            back_row.type = "BACK"
            back_row.size = ".."
            back_row.date_created_str = ".."
            back_row.permissions = ".."

            list_content.append(back_row)
            for i,content in enumerate(path.iterdir()):
                new_info = File_or_directory_info(content.absolute())
                list_content.append(new_info)
            # for i,content in enumerate(path.iterdir()):
            #     if i < 1000:
            #         new_info = File_or_directory_info(content.absolute())
            #         list_content.append(new_info)

        except Exception as e:
            print(f"Excepción {e}")
        return list_content
