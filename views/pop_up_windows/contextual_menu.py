# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Gio  # noqa E402


class ContextBox(Gtk.Box):

    def __init__(
        self,
        main_window: Gtk.Widget,
        file_context: bool,
        explorer: "explorer",  # noqa: F821
        popover: Gtk.Popover,
        path_list: list = None,
    ):
        super().__init__()

        self.main_window = main_window
        self.file_context = file_context
        self.explorer = explorer
        self.path_list = path_list
        self.popover = popover

        self.close_contextual_menu_1 = None
        self.close_contextual_menu_2 = None
        self.close_contextual_menu_3 = None

        self.close_contextual_menu_1_handler_id = None
        self.close_contextual_menu_2_handler_id = None
        self.close_contextual_menu_3_handler_id = None

        # Menu visible, container
        self.main_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )

        self.append(self.main_box)

        self.main_box.set_spacing(0)

        if file_context:
            self.create_file_context_menu()
        else:
            self.create_explorer_context_menu()

    def disable_gesture_click(self, widget, x, y) -> None:

        self.close_contextual_menu_1.disconnect(
            self.close_contextual_menu_1_handler_id
        )
        self.close_contextual_menu_2.disconnect(
            self.close_contextual_menu_2_handler_id
        )
        self.close_contextual_menu_3.disconnect(
            self.close_contextual_menu_3_handler_id
        )

    def create_file_context_menu(self) -> None:
        file_list_btn = {"Propiedades": self.get_properties}
        for key in file_list_btn.keys():
            btn = Gtk.Button.new_with_label(key)
            btn.connect("clicked", file_list_btn[key])
            self.main_box.append(btn)

    def create_explorer_context_menu(self) -> None:
        for i in range(5):

            def btn_action(button):
                print("HOLA BOTON:")

            btn = Gtk.Button.new_with_label(f"Btn test - {i}")
            btn.connect("clicked", btn_action)
            self.main_box.append(btn)

    def get_properties(self, button: Gtk.Button) -> None:
        from views.properties.properties import Properties

        Properties(self.main_window, self.path_list)
        self.popover.popdown()
