# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from css.explorer_css import Css_explorer_manager
from utilities.file_manager import File_manager
from pathlib import Path
import threading
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Gio  # noqa E402


class ContextMenu(Gtk.Window):

    def __init__(
        self,
        main_window: Gtk.Widget,
        x: float,
        y: float,
        width: float,
        height: float,
        file_context: bool,
        explorer: "explorer",  # noqa: F821
        path_list=None,
    ):
        super().__init__()

        self.main_window = main_window
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.file_context = file_context
        self.explorer = explorer
        self.path_list = path_list

        # windows transparent

        self.set_size_request(width, height)
        self.set_transient_for(main_window)
        self.set_decorated(False)
        self.set_can_focus(True)
        self.set_focusable(True)

        self.close_contextual_menu_1 = None
        self.close_contextual_menu_2 = None
        self.close_contextual_menu_3 = None

        self.close_contextual_menu_1_handler_id = None
        self.close_contextual_menu_2_handler_id = None
        self.close_contextual_menu_3_handler_id = None

        # Menu visible, container

        peprimetral_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )

        self.main_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )

        peprimetral_box.append(self.main_box)

        self.main_box.set_spacing(0)

        motion_menu = Gtk.EventControllerMotion()
        motion_menu.connect("enter", self.disable_gesture_click)
        motion_menu.connect("leave", self.enable_gestures_click)
        self.main_box.add_controller(motion_menu)

        if file_context:
            self.create_file_context_menu()
        else:
            self.create_explorer_context_menu()

        # To visibility menu container (box) and set en x,y position
        frame = Gtk.Frame.new()
        frame.set_child(peprimetral_box)

        # For add widgete on x,y position
        fixed = Gtk.Fixed()
        fixed.put(frame, x, y)

        self.set_child(fixed)

        self.enable_gestures_click()

        # Event controller to control keys
        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self.on_key_press)
        self.add_controller(key_controller)

        # Focus event
        self.focus_event = Gtk.EventControllerFocus()
        self.focus_event.connect("leave", self.lost_focus)
        self.add_controller(self.focus_event)

        # Load CSS

        css_explorer_manager = Css_explorer_manager(self.main_window)
        css_explorer_manager.load_css_context_menu()

        # Menu container, set transparent on css
        self.get_style_context().add_class("contextual_window")
        self.get_style_context().add_class("font")
        self.get_style_context().add_class("font-color")

        peprimetral_box.get_style_context().add_class("contextual_menu")

        self.main_box.get_style_context().add_class("contextual_content")

        self.present()

    def enable_gestures_click(self, widget: Gtk.Widget = None) -> None:

        self.close_contextual_menu_1 = Gtk.GestureClick()
        self.close_contextual_menu_1.set_button(1)
        self.close_contextual_menu_1_handler_id = (
            self.close_contextual_menu_1.connect(
                "pressed", self.close_contextual_click
            )
        )

        self.close_contextual_menu_2 = Gtk.GestureClick()
        self.close_contextual_menu_2.set_button(2)
        self.close_contextual_menu_2_handler_id = (
            self.close_contextual_menu_2.connect(
                "pressed", self.close_contextual_click
            )
        )

        self.close_contextual_menu_3 = Gtk.GestureClick()
        self.close_contextual_menu_3.set_button(3)
        self.close_contextual_menu_3_handler_id = (
            self.close_contextual_menu_3.connect(
                "pressed", self.close_contextual_click
            )
        )

        self.add_controller(self.close_contextual_menu_1)
        self.add_controller(self.close_contextual_menu_2)
        self.add_controller(self.close_contextual_menu_3)

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
        file_list_btn = {
            "Propiedades": self.get_properties,
            "Propiedades2": self.get_properties,
            "Propiedades3": self.get_properties,
            "Propiedades4": self.get_properties,
            "Propiedades5": self.get_properties,
            "Propiedades6": self.get_properties,
        }
        for key in file_list_btn.keys():

            btn = Gtk.Button.new_with_label(key)
            btn.get_style_context().add_class("button")
            btn.connect("clicked", file_list_btn[key])
            self.main_box.append(btn)

    def create_explorer_context_menu(self) -> None:
        for i in range(5):

            def btn_action(button):
                print("HOLA BOTON:")
                self.destroy()

            btn = Gtk.Button.new_with_label(f"BOTON - {i}")
            btn.connect("clicked", btn_action)
            self.main_box.append(btn)

    def close_contextual_click(self, gesture, n_press, x, y) -> None:
        # btn_num = gesture.get_button()
        # if btn_num == 1 or btn_num == 2:
        #     self.destroy()
        #     return

        self.destroy()

    def on_key_press(
        self,
        controller: Gtk.EventControllerKey,
        keyval: int,
        keycode: int,
        state: Gdk.ModifierType,
    ) -> None:
        """
        Manages the keys pressed to close context menu
        """
        self.destroy()

    def lost_focus(self, event: Gtk.EventControllerFocus) -> None:
        """
        Lost focus, close contextual menu
        """
        self.destroy()

    def get_properties(self, button: Gtk.Button) -> None:
        self.destroy()

        # spinner = Gtk.Spinner()
        # self.main_window.main_vertical_box.append(spinner)

        def properties_work(path_list: list[Path]) -> None:
            # spinner.start()

            folders = 0
            files = 0
            total_size = 0

            for path in path_list:
                print(path)
                result = File_manager.get_dir_or_file_size(path)
                folders += result["folders"]
                files += result["files"]
                total_size += result["size"]

            print(f"Folders: {folders}")
            print(f"Files: {folders}")
            print(f"Total size: {total_size}")
            # spinner.stop()

        threading.Thread(
            target=properties_work, args=(self.path_list,)
        ).start()
