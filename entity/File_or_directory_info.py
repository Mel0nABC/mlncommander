import stat
from pathlib import Path
from datetime import datetime
import gi
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

        # Filtrado si es un syslink y si existe su destino.
        if self.is_sys_link and not self.path_file.exists():
            # Es un syslink pero su destino no está disponible o no existe.
            self.type = "LN BREAK"
            self.size = "0 bytes"
            self.date_created_str = "01/01/1970 00:00"
            self.permissions = "l---------"
        else:
            # Archivos o carpetas normales, incluye syslink que funcionan
            self.permissions: str = stat.filemode(self.path_file.stat().st_mode)
            _date_created = datetime.fromtimestamp(self.path_file.stat().st_ctime)
            self.date_created_str: str = _date_created.strftime("%d/%m/%Y %H:%M")
            if self.is_directory:
                self.size = "DIR"
                self.type = "DIR"
            else:
                self.KBYTES = 1024
                self.size = self.path_file.stat().st_size
                self.type = "FILE"

                int_size_bytes = int(self.size)

                if int_size_bytes >= self.KBYTES:

                    int_size_kbytes = int_size_bytes / self.KBYTES

                    if int_size_kbytes > self.KBYTES:
                        if int_size_kbytes % self.KBYTES == 0:
                            self.size = (
                                f"{str(int(int_size_kbytes/self.KBYTES))} Mbytes"
                            )
                        else:
                            self.size = (
                                f"{str(round(int_size_kbytes/self.KBYTES,2))} Mbytes"
                            )
                    else:
                        self.size = f"{str(round(int_size_kbytes,2))} kbytes"

                else:
                    self.size = f"{str(self.size)} bytes"

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
