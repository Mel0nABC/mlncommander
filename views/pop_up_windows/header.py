# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk  # noqa: E402


class header:
    """
    Class that creates the header of the main window,
    so we acquire the details of the system theme.
    """

    def __init__(self):
        self.header = Gtk.HeaderBar()
        title = Gtk.Label(label="MLN Commander")
        self.header.set_title_widget(title)
        self.header.set_show_title_buttons(True)
