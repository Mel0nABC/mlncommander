# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GObject  # noqa: E402


class Shortcut(GObject.Object):

    __gtype_name__ = "Shortcut"

    first_key = GObject.Property(type=GObject.TYPE_STRING, default="")
    second_key = GObject.Property(type=GObject.TYPE_STRING, default="")
    method = GObject.Property(type=GObject.TYPE_STRING, default="")
    description = GObject.Property(type=GObject.TYPE_STRING, default="")

    def __init__(
        self,
        explorer: "Explorer",  # noqa F821
        first_key: str,
        second_key: str,
        method: str,
        description: str,
    ):
        super().__init__()

        self.explorer = explorer
        self.first_key = first_key
        self.second_key = second_key
        self.method = method
        self.description = description

    def to_dict(self) -> dict:
        return {
            "first_key": self.first_key,
            "second_key": self.second_key,
            "method": self.method,
            "description": self.description,
        }
