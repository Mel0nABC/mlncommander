import stat
from pathlib import Path
from datetime import datetime
import gi, os

gi.require_version("Gtk", "4.0")
from gi.repository import GObject


class File_or_directory_info(GObject.Object):

    path = GObject.Property(type=str)
    name = GObject.Property(type=str)
    is_directory = GObject.Property(type=bool, default=False)
    permissions = GObject.Property(type=str)
    date_created_str = GObject.Property(type=str)
    size = GObject.Property(type=str)
    type = GObject.Property(type=str)
    is_sys_link = GObject.Property(type=bool, default=False)
    path_exist = GObject.property(type=bool, default=True)

    def __init__(self, path):
        super().__init__()
        self.path: str = path
        self.path_file = Path(path)
        self.name: str = self.path_file.name
        self.is_directory: bool = Path(path).is_dir()
        self.is_sys_link: bool = self.path_file.is_symlink()
        self.path_exist: bool = self.path_file.exists()
        self.selected = False
        self.KBYTES = 1024

        # Filtered if it is a syslink and if its destination exists.
        if self.is_sys_link and not self.path_file.exists():
            # It is a syslink but its destination is not available or does not exist.
            self.type = "LN BREAK"
            self.size = "0 bytes"
            self.date_created_str = "01/01/1970 00:00"
            self.permissions = "l---------"
        else:
            # Normal files or folders, including working syslinks
            self.permissions: str = stat.filemode(self.path_file.stat().st_mode)
            _date_created = datetime.fromtimestamp(self.path_file.stat().st_ctime)
            self.date_created_str: str = _date_created.strftime("%d/%m/%Y %H:%M")
            if self.is_directory:
                self.size = "DIR"
                self.type = "DIR"
            else:
                self.size = self.path_file.stat().st_size
                self.type = "FILE"

                self.size = self.get_size_and_unit(int(self.size))

    def get_absolute_path(self):
        return self.path

    def get_name(self):
        return self.name

    def get_is_directory(self):
        return self.is_directory

    def get_permissions(self):
        return self.permissions

    def get_create_date(self):
        return self.date_created_str

    def get_size(self):
        return self.size

    def get_size_and_unit(self, bytes_int: int) -> str:
        """
        Transforms bytes to the unit immediately preceding having decimal type 0.9 and assigns the unit
        """
        start = True
        count = 0
        unit = ""
        while start:

            if not bytes_int > self.KBYTES:
                start = False
                continue

            bytes_int = bytes_int / self.KBYTES
            if bytes_int > 1:
                count += 1
            else:
                start = False

        if count == 0:
            unit = "Bytes"

        if count == 1:
            unit = "KB"

        if count == 2:
            unit = "MB"

        if count == 3:
            unit = "GB"

        if count == 4:
            unit = "TB"

        return f"{round(bytes_int, 2)}{unit}"

    def __str__(self):
        output: str = ""
        if self.is_directory:
            output = "Directory"
        else:
            output = "File"

        return f"File_or_directory_info(type={output},name={self.path_file.name},size={self.size},date={self.date_created_str},permissions={self.permissions})"

    def __repr__(self):
        file_or_directory = ""
        if self.is_directory:
            file_or_directory = "directory"
        else:
            file_or_directory = "file"

        return f"File_or_directory_info(type={file_or_directory!r},name={self.path_file.name!r},size={self.size!r},date={self.date_created_str!r},permissions={self.permissions!r})"
