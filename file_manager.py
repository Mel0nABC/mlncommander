import stat
from pathlib import Path
from datetime import datetime


class File_manager:

    def get_path_list(path: str):
        list_content = []
        for content in path.iterdir():
            new_info = File_or_directory_info(content.absolute())
            list_content.append(new_info)

        return list_content


class File_or_directory_info:
    def __init__(self, path):
        self.path: Path = Path(path)
        self.is_directory: bool = self.path.is_dir()
        self.permissions: str = stat.filemode(self.path.stat().st_mode)
        _date_created = datetime.fromtimestamp(self.path.stat().st_ctime)
        self.date_created_str: str = _date_created.strftime("%d/%m/%Y %H:%M")

    def get_absolute_path(self):
        return self.path

    def get_name(self):
        return self.path.name

    def get_is_directory(self):
        return self.is_directory

    def get_permissions(self):
        return self.permissions

    def get_create_date(self):
        return self.date_created_str

    def __str__(self):
        output: str = ""
        if self.is_directory:
            output = "Directory"
        else:
            output = "File"

        return f"{output} {i.get_absolute_path()} {i.get_permissions()} {i.get_create_date()}"

    def __repr__(self):
        file_or_directory = ""
        if self.is_directory:
            file_or_directory = "directory"
        else:
            file_or_directory = "file"

        return f"File_or_directory_info(name={self.path.name!r},permissions={self.permissions!r}, type={file_or_directory})"


path = Path("/media/Almacenamiento/Download")

for i in File_manager.get_path_list(path):
    print(i)
