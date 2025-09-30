# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from pathlib import Path
from datetime import datetime
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GObject  # noqa: E402


class File_or_directory_info(GObject.Object):

    __gtype_name__ = "File_or_directory_info"

    path = GObject.Property(type=GObject.TYPE_STRING, default="")
    name = GObject.Property(type=GObject.TYPE_STRING, default="")
    is_directory = GObject.Property(type=GObject.TYPE_BOOLEAN, default=False)
    permissions = GObject.Property(type=GObject.TYPE_STRING, default="")
    date_created_str = GObject.Property(type=GObject.TYPE_STRING, default="")
    date_created_float = GObject.Property(type=GObject.TYPE_FLOAT)
    size = GObject.Property(type=GObject.TYPE_STRING, default="")
    size_number = GObject.Property(type=GObject.TYPE_INT)
    type_str = GObject.Property(type=GObject.TYPE_STRING, default="")
    is_sys_link = GObject.Property(type=GObject.TYPE_BOOLEAN, default=False)
    path_exist = GObject.Property(type=GObject.TYPE_BOOLEAN, default=True)

    def __init__(self, path: Path):
        super().__init__()
        self.path: str = path
        self.path_file = Path(path)
        self.name: str = self.path_file.name
        self.is_directory: bool = Path(path).is_dir()
        self.is_sys_link: bool = self.path_file.is_symlink()
        self.path_exist: bool = self.path_file.exists()
        self.selected = False

        self.filter_file_or_sys_link()

    def filter_file_or_sys_link(self) -> None:
        """
        Filters whether the file is a working syslink or not
        """

        # Filtered if it is a syslink and if its destination exists.
        if self.is_sys_link and not self.path_file.exists():
            # It is a syslink but its destination is not available or does
            # not exist.
            self.type = "LN BREAK"
            self.size = "0 bytes"
            self.date_created_str = "01/01/1970 00:00"
            self.permissions = "l---"
        else:
            from utilities.file_manager import File_manager

            response = File_manager().get_permissions(self.path_file)

            self.permissions = response["msg"]

            _date_created = datetime.fromtimestamp(
                self.path_file.stat().st_ctime
            )
            self.date_created_str: str = _date_created.strftime(
                "%d/%m/%Y %H:%M"
            )

            self.date_created_float = self.path_file.stat().st_ctime

            if self.is_directory:
                self.size = "DIR"
                self.type = "DIR"
            else:
                self.size = self.path_file.stat().st_size
                self.type = "FILE"
                self.size_number = int(self.size)
                self.size = File_manager().get_size_and_unit(int(self.size))
