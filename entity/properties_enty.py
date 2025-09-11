# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.file_manager import File_manager
from pathlib import Path
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GObject  # noqa E402


class PropertiesEnty(GObject.Object):

    __gtype_name__ = "PropertiesEnty"

    path = GObject.Property(type=GObject.TYPE_STRING)
    permissions = GObject.Property(type=GObject.TYPE_STRING)
    user_name = GObject.Property(type=GObject.TYPE_STRING)
    group_name = GObject.Property(type=GObject.TYPE_STRING)
    sticky = GObject.Property(type=GObject.TYPE_STRING)
    recursive = GObject.Property(type=GObject.TYPE_BOOLEAN, default=False)

    def __init__(
        self,
        path: Path,
        permissions: str,
        user_name: str,
        group_name: str,
        recursive: bool = False,
    ):
        super().__init__()

        self.path = path
        self.permissions = permissions
        self.permissions_list = list(permissions)
        self.user_name = user_name
        self.group_name = group_name
        self.sticky = ""
        self.recursive = recursive
        self.labels_list = []
        self.checks_btn_list = []
        self.old_user_name = user_name
        self.old_group_name = group_name

    def set_permissions_list(self, permissions_list: list) -> bool:
        self.permissions_list = permissions_list
        self.permissions = "".join(self.permissions_list)
        return True

    def set_changes_permissions(self, coordinate: str, checked: bool) -> None:
        divid = coordinate.split("=")
        index = int(divid[0])
        letter = divid[1]
        if not checked:
            letter = "-"
        else:
            letter = divid[1]
            if letter == "-":
                if index in [0, 3, 6]:
                    letter = "r"
                elif index in [1, 4, 7]:
                    letter = "w"
                elif index in [3, 5, 8]:
                    letter = "x"
        self.permissions_list[index] = letter
        self.set_sticky(self.sticky)
        return self.set_permissions_list(self.permissions_list)

    def set_sticky(self, sticky: str) -> True:
        self.sticky = sticky

        u = self.permissions_list[2]
        g = self.permissions_list[5]
        o = self.permissions_list[8]

        if not u == "-":
            if "u" in self.sticky.lower():
                self.permissions_list[2] = "s"
            else:
                self.permissions_list[2] = "x"
        if not g == "-":
            if "g" in self.sticky.lower():
                self.permissions_list[5] = "s"
            else:
                self.permissions_list[5] = "x"
        if not o == "-":
            if "o" in self.sticky.lower():
                self.permissions_list[8] = "t"
            else:
                self.permissions_list[8] = "x"

        return self.set_permissions_list(self.permissions_list)

    def set_recursive(self, recursive: bool) -> bool:
        old_recursive = self.recursive
        self.recursive = recursive
        return not old_recursive == self.recursive

    def set_owner(self, new_owner: str) -> bool:
        old_user_name = self.user_name
        self.user_name = new_owner
        return not old_user_name == self.user_name

    def set_group(self, new_group: str) -> bool:
        old_group_name = self.group_name
        self.group_name = new_group
        return not old_group_name == self.user_name

    def to_dict(self):
        return {
            "path": self.path,
            "permissions": self.permissions,
            "user_name": self.user_name,
            "group_name": self.group_name,
            "sticky": self.sticky,
            "recursive": self.recursive,
        }

    def save_data_permissions(self) -> dict:

        permission_list = []
        n = 0
        for i in [3, 6, 9]:
            permission_list.append(self.permissions[n:i])
            n = i

        return File_manager.change_permissions(
            Path(self.path), permission_list, self.recursive
        )

    def filter_data_owners_changed(self) -> dict:
        if (
            self.old_user_name == self.user_name
            and self.old_group_name == self.group_name
        ):
            return True

        return False
